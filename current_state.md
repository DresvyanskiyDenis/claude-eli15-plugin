# Current state

| Area | State |
|---|---|
| Skill (`plugins/eli15/skills/eli15/`) | done: SKILL.md, three references, the template (kit CSS, runtime, café demo), check.py, reference images |
| Ship gate (`plugins/eli15/hooks/`) | done: PostToolUse tracking, Stop/SubagentStop check with a 3-block cap per page, tests in `hooks/scripts/test_gate.py` |
| Release process | `docs/releases.md` and one explain-diff page per version; no docs site and no CI yet |

Known limits: the gate does not see pages written only through Bash; check.py needs Chrome or Chromium and has run only on macOS.
