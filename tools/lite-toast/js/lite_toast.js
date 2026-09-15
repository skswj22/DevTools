/**
 * LiteToast - Pure Vanilla JS (ES5)
 * 의존성 없음, CSS 자동 주입, 초경량 토스트 메시지 라이브러리.
 */
(function (root) {
    'use strict';

    var CONTAINER_ID = 'lite-toast-container';
    var STYLE_ID = 'lite-toast-style';
    var DEFAULT_DURATION = 3000;

    // --- CSS Styles ---
    var styles =
        "#" + CONTAINER_ID + " { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; display: flex; flex-direction: column; align-items: center; gap: 10px; }" +
        ".lite-toast { min-width: 250px; max-width: 80vw; padding: 12px 20px; border-radius: 8px; background: #333; color: #fff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: space-between; opacity: 0; transform: translateY(-20px); transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55); }" +
        ".lite-toast.show { opacity: 1; transform: translateY(0); }" +
        ".lite-toast.hide { opacity: 0; transform: translateY(-20px); }" +

        // Themes
        ".lite-toast-success { background: #4CAF50; color: #fff; }" +
        ".lite-toast-error { background: #F44336; color: #fff; }" +
        ".lite-toast-warning { background: #FF9800; color: #fff; }" +
        ".lite-toast-info { background: #2196F3; color: #fff; }" +

        // Icon
        ".lite-toast-icon { margin-right: 10px; font-weight: bold; font-size: 16px; }";

    function LiteToast() { }

    // --- Internal Helpers ---

    function injectStyles() {
        if (document.getElementById(STYLE_ID)) return;
        var style = document.createElement('style');
        style.id = STYLE_ID;
        style.type = 'text/css';
        if (style.styleSheet) style.styleSheet.cssText = styles;
        else style.appendChild(document.createTextNode(styles));
        document.head.appendChild(style);
    }

    function getContainer() {
        var container = document.getElementById(CONTAINER_ID);
        if (!container) {
            container = document.createElement('div');
            container.id = CONTAINER_ID;
            document.body.appendChild(container);
        }
        return container;
    }

    function createToastElement(message, type) {
        var el = document.createElement('div');
        el.className = 'lite-toast lite-toast-' + type;

        var iconChar = '';
        switch (type) {
            case 'success': iconChar = '✔'; break;
            case 'error': iconChar = '✖'; break;
            case 'warning': iconChar = '⚠'; break;
            case 'info': iconChar = 'ℹ'; break;
        }

        if (iconChar) {
            var icon = document.createElement('span');
            icon.className = 'lite-toast-icon';
            icon.innerText = iconChar;
            el.appendChild(icon);
        }

        var text = document.createElement('span');
        text.innerText = message;
        el.appendChild(text);

        return el;
    }

    // --- Public API ---

    LiteToast.success = function (msg, duration) { this.show(msg, 'success', duration); };
    LiteToast.error = function (msg, duration) { this.show(msg, 'error', duration); };
    LiteToast.warning = function (msg, duration) { this.show(msg, 'warning', duration); };
    LiteToast.info = function (msg, duration) { this.show(msg, 'info', duration); };

    LiteToast.show = function (message, type, duration) {
        injectStyles();
        var container = getContainer();
        var toast = createToastElement(message, type || 'default');

        container.appendChild(toast);

        // Trigger reflow for animation
        void toast.offsetWidth;
        toast.className += ' show';

        var time = duration || DEFAULT_DURATION;

        setTimeout(function () {
            toast.className = toast.className.replace('show', 'hide');
            setTimeout(function () {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300); // Wait for transition
        }, time);
    };

    root.LiteToast = LiteToast;

})(window);
