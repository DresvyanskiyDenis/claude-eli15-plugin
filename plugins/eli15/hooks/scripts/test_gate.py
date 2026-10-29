"""Gate tests. The unit tests fake check.py; the last test runs the real one and skips
without uv or Chrome."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import gate
import pytest

PAGE = "<html><head></head><body><script>/* ELI15 RUNTIME */</script></body></html>"


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "STATE", tmp_path / "state")
    monkeypatch.setattr(gate, "find_uv", lambda: "uv")
    results = []
    monkeypatch.setattr(gate, "run_check", lambda uv, page: results.pop(0))
    page = tmp_path / "topic.html"
    page.write_text(PAGE)
    return page, results


def write(page, agent=None, name="Write"):
    ev = {"hook_event_name": "PostToolUse", "session_id": "s1", "tool_name": name,
          "tool_input": {"file_path": str(page)}}
    if agent:
        ev["agent_id"] = agent
    gate.remember(ev)


def stop(agent=None):
    ev = {"hook_event_name": "SubagentStop" if agent else "Stop", "session_id": "s1"}
    if agent:
        ev["agent_id"] = agent
    return gate.gate(ev) or {}


FAIL = (False, ["FAIL  desktop: label overlaps"], "Look at /x/eli15-check/topic/light.png\nRESULT: FAIL")


def test_nothing_pending_is_silent(env):
    assert stop() == {}


def test_ignores_other_files(env, tmp_path):
    page, _ = env
    plain = tmp_path / "plain.html"
    plain.write_text("<html></html>")
    write(plain)
    write(tmp_path / "notes.md")
    template = tmp_path / "skills" / "eli15" / "assets" / "template.html"
    template.parent.mkdir(parents=True)
    template.write_text(PAGE)
    write(template)
    assert stop() == {}


def test_pass_clears_and_tells_user(env):
    page, results = env
    write(page)
    results.append((True, [], "RESULT: PASS"))
    assert stop() == {"systemMessage": "eli15 check passed: topic.html"}
    assert stop() == {}


def test_fail_blocks_with_lines_then_gives_up(env):
    page, results = env
    write(page)
    for n in (1, 2, 3):
        results.append(FAIL)
        res = stop()
        assert res["decision"] == "block"
        assert f"try {n} of 3" in res["reason"] and "label overlaps" in res["reason"]
        assert "/x/eli15-check/topic" in res["reason"]
    results.append(FAIL)
    res = stop()
    assert "decision" not in res and "still fails" in res["systemMessage"]
    assert stop() == {}


def test_subagent_pages_are_checked_at_its_own_stop(env):
    page, results = env
    write(page, agent="a1", name="Edit")
    assert stop() == {}
    results.append(FAIL)
    assert stop(agent="a1").get("decision") == "block"


def test_check_that_cannot_run_is_reported_not_blocked(env):
    page, results = env
    write(page)
    results.append((None, [], "check.py: Chrome not found"))
    res = stop()
    assert "decision" not in res and "Chrome not found" in res["systemMessage"]


def test_missing_uv_is_loud(env, monkeypatch):
    page, _ = env
    monkeypatch.setattr(gate, "find_uv", lambda: None)
    write(page)
    assert "uv not found" in stop()["systemMessage"]


def test_bad_stdin_exits_zero():
    script = Path(gate.__file__).resolve()
    r = subprocess.run([sys.executable, str(script)], input="not json", capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout == ""


def test_hooks_json_points_at_this_script():
    hooks = json.loads((Path(gate.__file__).parent.parent / "hooks.json").read_text())["hooks"]
    for event in ("PostToolUse", "Stop", "SubagentStop"):
        args = hooks[event][0]["hooks"][0]["args"]
        assert args == ["${CLAUDE_PLUGIN_ROOT}/hooks/scripts/gate.py"]


def test_real_check_blocks_the_template_and_passes_a_clean_copy(tmp_path):
    """Hook JSON through gate.py, the real check.py and Chrome: the template's demo text
    blocks the stop, the same page with the demo words swapped passes."""
    if not gate.find_uv():
        pytest.skip("uv not installed")
    template = (gate.SKILL / "assets" / "template.html").read_text()
    raw, clean = tmp_path / "raw.html", tmp_path / "clean.html"
    raw.write_text(template)
    clean.write_text(re.sub(r"barista|caf[eé]",
                            lambda m: "server" if m.group(0).lower() == "barista" else "shop", template, flags=re.I))
    env = {**os.environ, "TMPDIR": str(tmp_path)}

    def hook(ev):
        ev = {"session_id": "e2e", "cwd": str(tmp_path), **ev}
        r = subprocess.run([sys.executable, str(Path(gate.__file__).resolve())], input=json.dumps(ev),
                           capture_output=True, text=True, env=env, timeout=600)
        return json.loads(r.stdout) if r.stdout else {}

    for page in (raw, clean):
        hook({"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": str(page)}})
    res = hook({"hook_event_name": "Stop"})
    if "could not run" in res.get("systemMessage", ""):
        pytest.skip(res["systemMessage"])
    assert res.get("decision") == "block"
    assert "raw.html" in res["reason"] and "demo text" in res["reason"]
    assert "eli15 check passed: clean.html" in res["systemMessage"]
