#!/usr/bin/env python3
"""Discover sibling orca agent panes and classify them by agent type.

Run this FIRST, from inside an orca terminal, at the start of any orca_co-op
session. Every value it prints (handles, worktree) changes per session, so the
roster must be rebuilt live each time rather than hardcoded.

Output: JSON with self_handle, worktree, and a roster of the OTHER panes in the
same worktree, each tagged with a best-guess role. Roles are heuristic (from the
pane's title + terminal preview), so treat "unknown" and surprising guesses as
things to confirm by reading the pane (orca terminal read) or asking the user.

Usage:
  python roster.py            # panes in my worktree (default)
  python roster.py --all      # every pane orca knows about
"""
import json
import os
import re
import subprocess
import sys

# Emit UTF-8 too: pane previews carry emoji (⚠, 🏁, ◑), which crash the default
# Windows console codepage (cp949) on print.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def orca(*args):
    # Force UTF-8: orca emits emoji/Korean, but Windows defaults subprocess text
    # decoding to the ANSI codepage (cp949 here), which crashes on those bytes.
    r = subprocess.run(["orca", *args], capture_output=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"`orca {' '.join(args)}` failed: {r.stderr.strip() or r.stdout.strip()}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"`orca {' '.join(args)}` did not return JSON:\n{r.stdout[:500]}")


def role_of(term):
    """Agent type for a pane. Prefer orca's own `agentIdentity` (authoritative —
    it drives the app's UI and was 100% accurate in testing); fall back to the
    title/preview heuristic only when orca hasn't tagged the pane (bare shell, or
    an agent orca doesn't recognize)."""
    ident = (term.get("agentIdentity") or "").strip().lower()
    if ident:
        # Normalize orca's id to this skill's role vocabulary (agy == Antigravity).
        return "agy" if ident == "antigravity" else ident
    return classify(term)


def classify(term):
    """Fallback heuristic when `agentIdentity` is absent: best-guess role from a
    pane's title + preview text.

    Order matters: check the most specific fingerprints first. agy (Antigravity
    CLI running Gemini) and codex advertise themselves in their banner/preview;
    Claude Code is the fallback among agent panes. Anything with no fingerprint
    is 'unknown' so the caller knows to look closer instead of trusting a guess.
    """
    s = (term.get("title", "") + " " + term.get("preview", "")).lower()
    if "antigravity" in s or "gemini" in s:
        return "agy"
    if "opencode" in s:
        return "opencode"
    if "ask codex" in s or "gpt-" in s or "codex cli" in s:
        return "codex"
    if "claude" in s or "esc to interrupt" in s:
        return "claude"
    return "unknown"


def main():
    if os.environ.get("TERM_PROGRAM") != "Orca":
        sys.exit("Not inside an orca terminal (TERM_PROGRAM != 'Orca'). "
                 "orca_co-op only works from a pane running inside the orca app.")

    self_handle = os.environ.get("ORCA_TERMINAL_HANDLE", "")
    worktree = os.environ.get("ORCA_WORKTREE_ID", "")
    show_all = "--all" in sys.argv[1:]

    data = orca("terminal", "list", "--json")
    terms = data["result"]["terminals"]

    roster = []
    for t in terms:
        h = t["handle"]
        if h == self_handle:
            continue
        if not show_all and worktree and t.get("worktreeId") != worktree:
            continue
        preview = " ".join((t.get("preview", "") or "").split())[:160]
        roster.append({
            "handle": h,
            "role": role_of(t),
            "identity": t.get("agentIdentity", ""),  # orca's own tag ('' if untagged)
            "title": t.get("title", ""),
            "connected": t.get("connected"),
            "writable": t.get("writable"),
            "worktreeId": t.get("worktreeId", ""),
            "preview": preview,  # last line of the pane; confirm role against this
        })

    print(json.dumps({
        "self_handle": self_handle,
        "worktree": worktree,
        "roster": roster,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
