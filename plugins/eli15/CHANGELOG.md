# Changelog

## Unreleased

### Changed

- `SKILL.md`: a page with no quantity to drag drops `model()`; a stepper or a toggle is its
  interactive figure.
- `references/visual-system.md`: a page's own grid item that holds code needs `min-width: 0`,
  or the phone scrolls sideways.
- Template: `--warn` moves to hue 90 (dark 100) and `--ok` to 145, so every concept hue sits
  at least 30° from every status hue. Before, busy orange and warn were 20° apart (15° in dark).
  `references/visual-system.md` states the rule and the free hue range.
- `references/visual-system.md`: status in a figure carries a mark or a word (✓ ✗ ↯ "risk"),
  never colour alone.
- `references/explainer-craft.md`: a PR or release explainer keeps its repo's section order;
  the predict box goes in the quiz and the recap box is optional.

### Fixed

- Template: the hidden side of a before/after toggle turns `visibility: hidden` after it
  fades, so screen readers no longer read both states.
- `check.py`: the demo-text check ignores words inside inline `<code>`, so a page may name
  the template's demo terms in code.

### Added

- `hooks/scripts/test_gate.py`: an end-to-end test pipes hook JSON through `gate.py` into the
  real `check.py` and Chrome. The raw template blocks on demo text; a copy with the demo words
  swapped passes. It skips without uv or Chrome.

## 0.1.0-alpha.1

First release as a plugin. Before this, eli15 was a standalone skill in Denis's `claude-config`.
Its pages were correct but flat: one accent colour, boxes in a row, text walls between small
figures.

### Added

- `assets/template.html`, a finished page that holds the kit by example. Every page is a copy of
  it.
  - Kit CSS: concept colours as oklch tokens that switch with light and dark, a three-track page
    grid, figure cards, a terms strip, notes, the predict box, paired bars, the recap box, and
    print and reduced-motion rules.
  - Runtime, with no dependencies:
    - steppers that build once on entry, with tokens riding SVG paths and a keyboard-driven player;
    - before/after toggles;
    - predict-then-reveal;
    - linked terms;
    - growing bars;
    - ambient motion that runs only on screen;
    - a page-wide pause and a theme switch;
    - URL parameters `?theme`, `?motion=off`, `?step`, `?state`.
- `scripts/check.py`, the ship check.
  - Static rules: self-contained, accessible SVGs, kit present, no leftover demo text, an
    interactive figure required.
  - A headless-Chrome audit at 1280 and 390 px through every step, every toggle state and both
    ends of every slider. It catches overlapping or escaping SVG labels, sideways scroll, JS
    errors, and phone fonts below 10 px.
  - Screenshot tiles to look at: light, dark, phone, no-JS, alternate states (every toggle
    flipped, every stepper on step 1), the first screen and print page 1.
- `references/motion-and-interaction.md`, which covers when and how a page moves.
- `assets/reference-good.png` and `assets/reference-rejected.png`, the bar and the old output,
  to compare against before shipping.
- A ship gate (`hooks/hooks.json`, `hooks/scripts/gate.py`).
  - PostToolUse notes each eli15 page Claude writes.
  - Stop and SubagentStop run the check on those pages and block on a FAIL, up to three tries
    per page.
  - When it cannot check, it tells the user rather than staying silent.

### Changed

- `SKILL.md` was rewritten around four rules: the figures are the explanation; simplify the
  telling, never the claims; the reader acts; every concept owns one colour.
  - Its procedure classifies the concept shape first, which picks the hero figure and its
    interaction.
  - The default length went from 6–9 sections to 4–7.
- `references/explainer-craft.md` was rewritten. It adds concept shapes, the explanation ladder,
  techniques that teach (live model, Try/Notice, predict, concreteness fading) and analogy
  discipline.
- `references/visual-system.md` was rewritten. Semantic concept colours replace the single accent.
  It adds a figure router of 13 patterns and a never-list.
