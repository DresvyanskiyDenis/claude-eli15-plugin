# Releases

Every version, dev or stable, adds one explain-diff page under `docs/explanations/` and a row here, newest first. A dev version is a SemVer pre-release (`0.1.0-alpha.N`) published with `gh release create --prerelease`; its page covers the diff from the previous tag of either channel. A stable version (`0.1.0`) covers the diff from the previous stable tag; the first version covers the diff from the empty tree.

| Version | Channel | Date | Highlights | What changed |
|---|---|---|---|---|
| 0.1.0-alpha.2 | dev | 2026-10-29 | Status hues kept 30° from concept hues, hidden toggle states skipped by screen readers, end-to-end gate test | [explainer](explanations/2026-10-29-v0.1.0-alpha.2.html), [CHANGELOG](../plugins/eli15/CHANGELOG.md) |
| 0.1.0-alpha.1 | dev | 2026-10-29 | First plugin release: page kit (live model, stepper, toggle, predict box), ship check with screenshot tiles, Stop-hook gate | [explainer](explanations/2026-10-29-v0.1.0-alpha.1.html), [CHANGELOG](../plugins/eli15/CHANGELOG.md) |

## Cut a release

1. On a `feature/…` branch from `main`, set `version` in `plugins/eli15/.claude-plugin/plugin.json` (the marketplace entry carries none) and add the version's section to `plugins/eli15/CHANGELOG.md`.
2. Write the explain-diff page for `<base>...<main tip>` as `docs/explanations/<YYYY-MM-DD>-v<version>.html` and add its row above.
3. Gates: `uv run --with pytest pytest -q plugins/eli15/hooks/scripts`, `uv run plugins/eli15/skills/eli15/scripts/check.py plugins/eli15/skills/eli15/assets/template.html --allow-demo`, `claude plugin validate .`.
4. Merge into `main`, then `git tag v<version> && git push origin main v<version>` and `gh release create v<version> --verify-tag --notes-file <notes>` (add `--prerelease` for a dev version).
5. Installed copies pick it up with `claude plugin marketplace update claude-eli15-plugin && claude plugin update eli15@claude-eli15-plugin`.
