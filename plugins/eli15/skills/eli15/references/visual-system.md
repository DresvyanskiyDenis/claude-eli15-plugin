# Visual system

How an eli15 page looks. Every rule here is implemented in `assets/template.html`; when
this file and the template disagree, the template wins. Read the template for the markup,
this file for the reasons and the choices.

## Non-negotiables

- **Concept colours carry meaning.** Two to five hues, one per idea the reader must track,
  used for that idea everywhere. Neutral ink for everything else.
- **Status colours are only status.** `--ok`, `--warn`, `--risk` mean right, caution and
  wrong. Never use them as a concept colour, never use a concept colour for status.
- **The first viewport is the answer as a picture.** Title, lead, and the top of the hero
  figure are visible at 1280×800 without scrolling.
- **Labels sit on the marks.** Label a line at its end, a bar inside or beside it, an arrow
  with its verb. A legend only when marks crowd (Fig. 5 of the template), and then it
  repeats the numbers.
- **Every figure has a caption that states its claim with numbers**, and every SVG has
  `role="img"` plus an `aria-label` that says the same thing in a sentence.
- **Without JS and in print, every figure shows its finished picture.** The default CSS is
  the final state; JS only adds the build-up.

## Type

| Role | Font | Where |
|---|---|---|
| Display | Fraunces 650, optical size on | `h1`, `h2`, `h3`, `.t-big` numbers in figures |
| Body | IBM Plex Sans 400/500/600 | prose, SVG labels, buttons |
| Numbers | IBM Plex Mono 500/600, tabular | `.num`, `.t-num`, readouts, eyebrows, figure numbers |

Body is 1.125rem/1.62 at 68ch. SVG text is 15px (`.t-s` 13px, `.t-cap` 11.5px uppercase
mono) **in viewBox units**, so size the viewBox so that text renders at 13–16 CSS px on
desktop: a viewBox about as wide as the figure's on-screen width (≈ 960 for `.wide`,
≈ 680 for text width, ≈ 480 for half of the hero grid).

## Colour

**Neutrals** come from the kit: `--bg`, `--surface`, `--sunk`, `--ink`, `--ink-2`,
`--ink-3`, `--line`, `--line-2`, each a `light-dark()` pair. Warm paper in light, blue-grey
in dark.

**Concepts** are defined per page in the `PAGE CONCEPTS and page CSS` block, the first
block of the style. Any CSS rule of your own goes there too, never inside the kit. The block
comes before the kit, so a page rule that only ties a kit rule's specificity loses; prefix it
with `main` (`main h3 { … }`). Each concept is a token and a class:

```css
--c-arrive: light-dark(oklch(54% 0.16 252), oklch(74% 0.12 252));
.c-arrive { --k: var(--c-arrive); }
```

- Name the variable for the idea (`--c-wait`), not the hue (`--c-pink`).
- Light mode L 52–64%, dark mode L 72–80%, chroma 0.10–0.20, same hue in both.
- Space hues at least 60° apart on the oklch wheel, and keep them 30° or more away from
  `--risk` (28) unless the concept *is* the bad outcome (the template's `--c-wait` at 352
  is deliberately close: waiting is the cost).
- Order them by the story: the input the reader controls, the mechanism, the outcome.

**How components take a colour:** put `.c-name` on any element or SVG group; it sets
`--k`, and the kit reads `--k` everywhere:

| Class | Effect |
|---|---|
| `.term` | coloured, semi-bold word in prose |
| `svg .k` / `.fk` | text / shape fill in the concept colour |
| `svg .sk` | stroke only (lines, rings) |
| `svg .tk` | tinted box: 14% fill, full stroke |
| `.terms > div.c-x` | the dot and the term in the terms strip |
| `.slider.c-x` | the slider thumb and its output |
| `.bar-grp.c-x` | both bars and the multiplier |
| `.note.key.c-x` | a key-idea callout in that concept's colour |

**Tints use `color-mix(in srgb, …)`.** Mixing in oklch toward a near-white surface shifts
the hue (blue and teal tints turn pink); srgb keeps it.

## Layout

`.page` is a grid with three tracks: `text` (68ch, the default for every child), `wide`
(1120px, add class `wide`) and `full`. Figures that need width break out with
`.fig.wide`; prose never does. Sections are separated by space (4.5rem), not rules or cards.

- **Hero:** `.hero-grid` puts the scene (left, viewBox ≈ 480 wide) beside its chart
  (right, ≈ 460 wide); on a phone it stacks. Below it: controls, readout, Try/Notice,
  caption.
- **One screen per section.** Eyebrow, heading-claim, at most three short paragraphs, one
  figure, then optionally a note and a `<details>`.
- **Phone (≤ 760px):** wide figures go edge to edge. A wide SVG in a `.frame` keeps a
  minimum width set by `--min-phone` and scrolls sideways inside its frame; set it to about
  0.875 × the viewBox width so `.t-cap` (11.5px) labels stay ≥ 10px (0.8 is enough when the
  smallest label is `.t-s`, 13px). Better: design hero figures to fit
  ≈ 480 viewBox units so they need no scroll, and label them at 15px or more: on a phone
  such a figure renders at about 0.7 of its viewBox width, and `.t-s` (13px) drops below
  10px.
- **Big numbers:** a `.t-big` (46px) needs about 30px from its baseline to the baseline of
  the line under it, as in the template; less and the two collide on a phone.

## Components

All of these are in the template; copy the markup from there.

| Component | Markup | Use for |
|---|---|---|
| Figure card | `figure.fig` (+ `.wide`) › content › `figcaption` with `span.fig-n` | every figure |
| Scroll frame | `div.frame style="--min: 720px; --min-phone: 780px"` around a wide SVG | wide SVGs |
| Terms strip | `dl.terms.wide` › `div.c-x` › `dt` + `dd` | the 2–5 concepts, after the hero; also a 2–4 column comparison strip |
| Live controls | `div.controls` › `label.slider.c-x` › `input[type=range]` + `output` | the live model |
| Readout | `p.readout[aria-live=polite]` with `b.term.c-x[id]` numbers | the sentence that updates |
| Try / Notice | `p.try` › `<b>Try</b>… <b>Notice</b>…` | under every live figure |
| Predict box | `div.predict` › `p.q` + `div.choices` (`button[data-right]`) + `details` | the one surprise |
| Paired bars | `div.bars.grow[style="--ref: .42"]` › `div.bar-grp.c-x` › `.bar.was` + `.bar.now` | before/after magnitudes against a dashed reference |
| Notes | `div.note.myth` (crossed-out belief + `.tag.fact`), `.note.watch`, `.note.key.c-x` | a misconception, a caveat, the key idea |
| Limits list | `ul.limits` › `li` › `span` › `<b>claim.</b> consequence` (the `span` keeps both in one grid cell) | where the model breaks |
| Depth | `details` › `summary` + content, MathML for formulas | derivations, edge cases |
| Recap | `div.recap-box` › eyebrow, `h2`, `ol`, `p.next` | the close |
| Sources | `section.sources` | every number's origin |

## SVG vocabulary

| Class / element | What it draws |
|---|---|
| `.ax` | axis lines, ground lines |
| `.gr` | dashed grid lines |
| `.guide` | dashed guides from a marker to its axes, in the concept colour |
| `.ln` | data lines, 3px, round caps; add `.sk` for the concept colour |
| `.sunk` | recessed shapes: doors, wells, empty containers |
| `.tk` | a box that belongs to a concept |
| `g.dim` | a dimension line: bar + end ticks + label, for "this span is N" |
| `<defs><g id>` + `<use href>` | repeated figures (people, servers, documents) |
| `<marker>` arrowhead in `--ink-3` | arrows; every arrow also gets a verb label |

Hand-draw with real coordinates on a grid: shared baselines, even gaps, labels never
crossing marks. Draw the thing itself when it has a shape (a line of people, a stack of
pages, a pipe), boxes only when the parts are abstract.

## Figure router

Pick the pattern from what the point *is*, before drawing:

| The point is… | Pattern | Interaction |
|---|---|---|
| a value that responds to an input | **live chart**: curve, a marker on it, guides to both axes, the scene beside it | slider |
| ordered stages, cause → effect | **mechanism stepper**: the parts drawn once, each step lights the next part, a token rides each path | stepper |
| how much something changed | **paired bars** against the old value's dashed reference, multiplier in the label | `.grow` |
| a part of a whole, "X of Y" | **proportion bar** or a 10×10 waffle, the dropped part as a dashed outline | none |
| a limit that cuts a population | **threshold cut**: a bar crossed by a dashed rule, the discarded side hollow | slider moves the rule |
| two options for one structure | **before / after**: the same shape twice in one SVG, the delta moving | toggle |
| one cause, several consequences | **fan-out**: one node, 3–4 labelled arrows | stepper reveals each |
| what rests on what, what is checked | **layer stack**: horizontal bands, hollow where not covered | linked terms |
| a feedback loop with a gap | **broken loop**: 3–4 nodes in a cycle, the missing arc dashed and labelled | stepper |
| a value between a floor and a bar | **scale with markers**: one axis, baseline / target / actual ticks | none |
| change over time | **timeline** with events as marks, spans as dimension lines | stepper |
| several cases of one rule | **small multiples**: the same mini-figure 3–4 times, one scale | toggle highlights one |
| who talks to whom | **system map**: components, verb-labelled arrows, the hot path in the concept colour | linked terms + stepper for one request |
| messages between parties, in order | **sequence diagram**: one lifeline per party, a labelled arrow per message top to bottom, a token riding each arrow, a "who sees this" strip beneath | stepper, one message per step |

Two rules across all of them. **A hollow shape is information**: what was dropped, skipped
or never checked shows as a dashed outline, not as nothing. **A schematic says so** in its
caption ("bursts are illustrative"), or the figure becomes an invented statistic.

## The never-list

These are what made the old pages read as generated, and what check.py warns about:

- Inter, Roboto, or the system UI font as the display face; violet or blue-purple as the
  default accent; one accent colour for every concept.
- Gradients, gradient text, glass (`backdrop-filter`), glow, drop shadows on figures.
- Emoji as icons or bullet markers; a thick coloured left border on a card.
- Boxes-in-a-row as the only diagram; a figure that restates the paragraph above it.
- Unlabelled arrows; a legend for two lines; axis ticks without units.
- Text in an SVG below 13px at the drawn scale; sentences inside a figure (they belong in
  the caption).
- `vh` units, autoplaying loops, animations that run while off screen.

## What to look for in the tiles

The check measures overlaps, overflow, scroll and font size. It cannot judge these; you do:

1. **First screen:** does it show the answer as a picture, with the control visible?
2. **Colour:** can you name each concept from its colour alone, in light and in dark?
3. **Hierarchy:** does each figure have one obvious first thing to look at?
4. **Density:** are there runs of more than three paragraphs with no figure, note or
   details between them?
5. **Phone:** does the hero fit without sideways scroll? Are the controls reachable?
6. **No-JS and print:** does every figure show its complete picture?
7. **Side by side with `reference-good.png` and `reference-rejected.png`:** which does it
   resemble?
