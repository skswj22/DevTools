/**
 * Lite Gantt Chart - Pure Vanilla JS (ES5)
 * 의존성 없음, 경량화, IE11 호환.
 */

(function (root) {
    'use strict';

    // CSS 스타일 주입 (무지개 색상 버전)
    var SIDEBAR_WIDTH = 140;
    var PADDING = 20;

    // 미디어 쿼리 등 CSS 문자열 정의
    var baseStyles =
        ".gantt-container { position: relative; width: 100%; background-color: #f9f9f9; border: 1px solid #e0e0e0; padding: 0; box-sizing: border-box; overflow-x: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }" +
        ".gantt-timeline { position: relative; height: 30px; border-bottom: 1px solid #ccc; width: calc(100% - " + SIDEBAR_WIDTH + "px); margin-left: " + SIDEBAR_WIDTH + "px; z-index: 20; }" +
        ".gantt-year-divider { position: absolute; top: 0; bottom: 0; border-left: 1px solid #ccc; }" +
        ".gantt-year-marker { position: absolute; bottom: 0; font-size: 12px; color: #666; height: 100%; display: flex; align-items: center; justify-content: center; transform: translateX(-50%); }" +
        ".gantt-grid { position: absolute; top: 30px; left: " + SIDEBAR_WIDTH + "px; width: calc(100% - " + SIDEBAR_WIDTH + "px); height: calc(100% - 30px); pointer-events: none; z-index: 0; }" +
        ".gantt-grid-line { position: absolute; top: 0; bottom: 0; border-left: 1px dashed #e0e0e0; }" +
        ".gantt-row { position: relative; height: 24px; margin-bottom: 0; border-bottom: 1px solid #eee; width: 100%; display: block; z-index: 10; }" +
        ".gantt-label { position: absolute; left: 0; top: 0; width: " + SIDEBAR_WIDTH + "px; height: 100%; line-height: 24px; font-size: 13px; font-weight: bold; color: #333; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; padding-right: 10px; padding-left: 10px; box-sizing: border-box; z-index: 10; }" +
        ".gantt-chart-area { position: relative; margin-left: " + SIDEBAR_WIDTH + "px; height: 100%; }" +
        ".gantt-bar { position: absolute; top: 4px; height: 16px; background-color: #4CAF50; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); cursor: pointer; box-sizing: border-box; transition: opacity 0.2s; }" +
        ".gantt-bar:hover { opacity: 0.9; z-index: 5; }" +
        ".gantt-arrow-right { position: absolute; right: -6px; top: 50%; margin-top: -4px; width: 0; height: 0; border-top: 4px solid transparent; border-bottom: 4px solid transparent; border-left: 6px solid; }" +
        ".gantt-tooltip { position: absolute; background: #333; color: #fff; padding: 8px 12px; border-radius: 4px; font-size: 12px; pointer-events: none; opacity: 0; transition: opacity 0.2s; z-index: 100; white-space: nowrap; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }" +
        ".gantt-tooltip.visible { opacity: 1; }";

    var mobileStyles =
        "@media (max-width: 600px) {" +
        "  .gantt-timeline { margin-left: 30%; width: 70%; }" +
        "  .gantt-label { width: 30%; }" +
        "  .gantt-chart-area { margin-left: 30%; }" +
        "  .gantt-grid { left: 30%; width: 70%; }" +
        "}";

    var styles = baseStyles + mobileStyles;

    // ----- [Constructor] -----
    function LiteGantt(elementId, data) {
        this.containerId = elementId;
        this.internalData = data || [];

        // 인스턴스 생성 시 스타일 주입 (최초 1회만 적용됨)
        LiteGantt.injectStyles();
    }

    // Static Method: 스타일 주입 (공유)
    LiteGantt.injectStyles = function () {
        var styleId = 'lite-gantt-styles';
        if (document.getElementById(styleId)) return;

        var style = document.createElement('style');
        style.id = styleId;
        style.type = 'text/css';
        if (style.styleSheet) {
            style.styleSheet.cssText = styles;
        } else {
            style.appendChild(document.createTextNode(styles));
        }
        document.getElementsByTagName('head')[0].appendChild(style);
    };

    // ----- [Instance Methods] -----

    /**
     * 데이터 추가
     */
    LiteGantt.prototype.add = function (label, start, end) {
        this.internalData.push({
            label: label,
            start: start,
            end: end
        });
    };

    /**
     * 렌더링
     */
    LiteGantt.prototype.render = function () {
        var container = document.getElementById(this.containerId);
        if (!container) {
            console.error('Gantt container not found: ' + this.containerId);
            return;
        }

        container.innerHTML = '';
        container.className += ' gantt-container';

        // 1. 데이터 처리
        var parsedData = [];
        var minDate = new Date();
        var maxDate = new Date(0);
        var targetData = this.internalData;

        if (!targetData || targetData.length === 0) {
            container.innerHTML = '<p>No data available</p>';
            return;
        }

        for (var i = 0; i < targetData.length; i++) {
            var item = targetData[i];
            var start = new Date(item.start);
            var end = item.end ? new Date(item.end) : new Date();
            var isPresent = !item.end;

            if (start < minDate) minDate = start;
            if (end > maxDate) maxDate = end;

            parsedData.push({
                original: item,
                start: start,
                end: end,
                isPresent: isPresent,
                durationMonths: this.getMonthDiff(start, end)
            });
        }

        // 날짜 범위 확장
        minDate = new Date(minDate.getFullYear(), 0, 1);
        maxDate = new Date(maxDate.getFullYear() + 1, 0, 1);

        var totalTime = maxDate.getTime() - minDate.getTime();
        if (totalTime <= 0) totalTime = 1;

        // 2. 타임라인 헤더 생성
        var timeline = this.createElement('div', 'gantt-timeline');
        var startYear = minDate.getFullYear();
        var endYear = maxDate.getFullYear();

        // 3. 그리드 레이어 생성
        var grid = this.createElement('div', 'gantt-grid');

        for (var y = startYear; y <= endYear; y++) {
            var yearDate = new Date(y, 0, 1);

            if (yearDate >= minDate && yearDate <= maxDate) {
                var yearStartTime = yearDate.getTime();

                var gridPos = (yearStartTime - minDate.getTime()) / totalTime * 100;
                if (gridPos > 100) gridPos = 100;

                var headerDivider = this.createElement('div', 'gantt-year-divider');
                headerDivider.style.left = gridPos + '%';
                timeline.appendChild(headerDivider);

                var gridLine = this.createElement('div', 'gantt-grid-line');
                gridLine.style.left = gridPos + '%';
                grid.appendChild(gridLine);

                if (yearDate < maxDate) {
                    var yearEndTime = new Date(y + 1, 0, 1).getTime();
                    var yearMidTime = (yearStartTime + yearEndTime) / 2;
                    var labelPos = (yearMidTime - minDate.getTime()) / totalTime * 100;

                    var marker = this.createElement('div', 'gantt-year-marker', y.toString());
                    marker.style.left = labelPos + '%';
                    timeline.appendChild(marker);
                }
            }
        }
        container.appendChild(timeline);
        container.appendChild(grid);

        // 4. 툴팁
        var tooltip = document.querySelector('.gantt-tooltip');
        if (!tooltip) {
            tooltip = this.createElement('div', 'gantt-tooltip');
            document.body.appendChild(tooltip);
        }

        // 5. 행 렌더링
        for (var j = 0; j < parsedData.length; j++) {
            var pItem = parsedData[j];
            var row = this.createElement('div', 'gantt-row');

            // label
            var text = pItem.original.label || pItem.original.company || '';
            var labelDiv = this.createElement('div', 'gantt-label', text);
            labelDiv.title = text;
            row.appendChild(labelDiv);

            var chartArea = this.createElement('div', 'gantt-chart-area');

            var startTime = pItem.start.getTime();
            var endTime = pItem.end.getTime();

            var leftPercent = (startTime - minDate.getTime()) / totalTime * 100;
            var widthPercent = (endTime - startTime) / totalTime * 100;

            var color = this.getRainbowColor(j, parsedData.length);

            var bar = this.createElement('div', 'gantt-bar');
            bar.style.left = leftPercent + '%';
            bar.style.width = widthPercent + '%';
            bar.style.backgroundColor = color;

            if (pItem.isPresent) {
                var arrow = this.createElement('div', 'gantt-arrow-right');
                arrow.style.borderLeftColor = color;
                bar.appendChild(arrow);
            }

            var self = this;
            (function (item, el) {
                el.addEventListener('mouseenter', function (e) {
                    var dateStr = self.formatDate(item.start) + ' - ' + (item.isPresent ? 'Present' : self.formatDate(item.end));
                    var durationStr = '(' + item.durationMonths + '개월)';
                    var title = item.original.label || item.original.company || '';
                    tooltip.innerHTML = '<strong>' + title + '</strong><br>' +
                        dateStr + ' ' + durationStr;
                    tooltip.className = 'gantt-tooltip visible';
                });

                el.addEventListener('mousemove', function (e) {
                    tooltip.style.left = (e.pageX + 10) + 'px';
                    tooltip.style.top = (e.pageY + 10) + 'px';
                });

                el.addEventListener('mouseleave', function () {
                    tooltip.className = 'gantt-tooltip';
                });
            })(pItem, bar);

            chartArea.appendChild(bar);
            row.appendChild(chartArea);
            container.appendChild(row);
        }
    };

    // Helper methods
    LiteGantt.prototype.getMonthDiff = function (d1, d2) {
        var months;
        months = (d2.getFullYear() - d1.getFullYear()) * 12;
        months -= d1.getMonth();
        months += d2.getMonth();
        return months <= 0 ? 0 : months;
    };

    LiteGantt.prototype.formatDate = function (date) {
        var m = date.getMonth() + 1;
        return date.getFullYear() + '.' + (m < 10 ? '0' + m : m);
    };

    LiteGantt.prototype.getRainbowColor = function (index, total) {
        var hue;
        if (!total || total < 2) {
            hue = (index * 20) % 360;
        } else {
            hue = (index / total) * 360;
        }
        return 'hsl(' + hue + ', 70%, 50%)';
    };

    LiteGantt.prototype.createElement = function (tag, className, text) {
        var el = document.createElement(tag);
        if (className) el.className = className;
        if (text) el.innerText = text;
        return el;
    };

    // Global Exposure
    root.LiteGantt = LiteGantt;

})(window);
