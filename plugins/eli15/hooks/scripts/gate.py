#!/usr/bin/env python3
"""eli15 ship gate: no eli15 page Claude wrote gets past the end of a turn unchecked.

PostToolUse (Write|Edit|MultiEdit): remember each .html file that carries the ELI15 runtime.
Stop / SubagentStop: run the skill's check.py on the pages that agent touched. A FAIL blocks
the stop with the failures, so Claude fixes them; after MAX_BLOCKS failed tries on one page
the gate lets the stop through and tells the user. Stdlib only, runs on the system python3.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "skills" / "eli15"
CHECK = SKILL / "scripts" / "check.py"
MARK = "ELI15 RUNTIME"
MAX_BLOCKS = 3
MAX_LINES = 20
CHECK_TIMEOUT = 240
STATE = Path(tempfile.gettempdir()) / "eli15-gate"
# GUI-launched Claude Code may not see the shell's PATH
UV_FALLBACKS = ("~/.local/bin/uv", "~/.cargo/bin/uv", "/opt/homebrew/bin/uv", "/usr/local/bin/uv")


def safe(s: str) -> str:
    return re.sub(r"[^\w.-]", "_", s) or "_"


def pending_dir(ev: dict, key: str) -> Path:
    return STATE / safe(ev.get("session_id") or "nosession") / safe(key)


def remember(ev: dict) -> None:
    raw = (ev.get("tool_input") or {}).get("file_path") or ""
    if not raw.endswith(".html"):
        return
    path = Path(ev.get("cwd") or ".", raw).resolve()
    if path.as_posix().endswith("skills/eli15/assets/template.html"):
        return
    try:
        if MARK not in path.read_text(encoding="utf-8", errors="ignore"):
            return
    except OSError:
        return
    d = pending_dir(ev, ev.get("agent_id") or "main")
    d.mkdir(parents=True, exist_ok=True)
    entry = d / (hashlib.sha1(str(path).encode()).hexdigest()[:16] + ".json")
    if not entry.exists():
        entry.write_text(json.dumps({"path": str(path), "blocks": 0}))


def find_uv() -> str | None:
    found = shutil.which("uv")
    if found:
        return found
    for p in UV_FALLBACKS:
        p = os.path.expanduser(p)
        if os.access(p, os.X_OK):
            return p
    return None


def run_check(uv: str, page: str) -> tuple[bool | None, list[str], str]:
    """(passed, FAIL lines, output). passed is None when the check itself could not run."""
    try:
        r = subprocess.run([uv, "run", "--quiet", str(CHECK), page], capture_output=True, text=True,
                           timeout=CHECK_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, [], f"timed out after {CHECK_TIMEOUT}s"
    out = r.stdout + r.stderr
    if "RESULT: PASS" in out:
        return True, [], out
    if "RESULT: FAIL" in out:
        return False, [ln for ln in out.splitlines() if ln.startswith("FAIL")], out
    return None, [], out.strip()[-600:]


def tiles(out: str) -> str:
    """The renders directory check.py printed, so the reason can point Claude at the tiles."""
    m = re.search(r"(/\S+/eli15-check/[^/\s]+)/", out)
    return m.group(1) if m else ""


def gate(ev: dict) -> dict | None:
    key = ev.get("agent_id") if ev.get("hook_event_name") == "SubagentStop" else "main"
    d = pending_dir(ev, key or "main")
    entries = sorted(d.glob("*.json")) if d.is_dir() else []
    if not entries:
        return None
    uv = find_uv()
    if not uv:
        return {"systemMessage": f"eli15 gate: uv not found, {len(entries)} page(s) not checked. "
                                 "Install uv (brew install uv) and re-run the check."}
    reasons, notes = [], []
    for entry in entries:
        st = json.loads(entry.read_text())
        page = st["path"]
        if not Path(page).exists():
            entry.unlink()
            continue
        passed, fails, out = run_check(uv, page)
        name = Path(page).name
        if passed:
            entry.unlink()
            notes.append(f"eli15 check passed: {name}")
        elif passed is None:
            entry.unlink()
            notes.append(f"eli15 gate: the check could not run on {name}: {out}")
        elif st["blocks"] >= MAX_BLOCKS:
            entry.unlink()
            notes.append(f"eli15 gate: {name} still fails the check after {MAX_BLOCKS} fixes; "
                         f"let it through. Run: uv run {CHECK} {page}")
        else:
            st["blocks"] += 1
            entry.write_text(json.dumps(st))
            shown = fails[:MAX_LINES] + ([f"… {len(fails) - MAX_LINES} more"] if len(fails) > MAX_LINES else [])
            where = tiles(out)
            reasons.append(
                f"eli15 check failed on {page} (try {st['blocks']} of {MAX_BLOCKS}):\n" + "\n".join(shown)
                + f"\nFix them, re-run `uv run {CHECK} {page}`"
                + (f", then Read the tiles in {where}" if where else "") + " before you finish.")
    res: dict = {}
    if notes:
        res["systemMessage"] = "\n".join(notes)
    if reasons:
        res["decision"] = "block"
        res["reason"] = "\n\n".join(reasons)
    return res or None


def main() -> int:
    try:
        ev = json.load(sys.stdin)
    except ValueError:
        return 0
    if ev.get("hook_event_name") == "PostToolUse":
        remember(ev)
        return 0
    res = gate(ev)
    if res:
        print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
