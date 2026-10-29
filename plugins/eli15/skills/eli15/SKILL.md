---
name: eli15
description: Explain any topic to someone who does not know it, as one self-contained, interactive HTML page whose figures carry the explanation — a live model the reader can drag, step-through diagrams, before/after toggles, a predict-then-reveal question — with the real numbers, failure mode, tradeoff and open questions kept in. Replaces the eli5 skill. Use when the user types /eli15 or /eli5 <topic>, says "explain like I'm five" or "like I'm 5", asks for a dead-simple picture explainer of how something works, asks for an explainer page for their team, a manager or a stakeholder, or says an explainer came out too simple or too blunt.
argument-hint: "[topic or path to the source document]"
---

# eli15

Explain like the reader is fifteen: old enough to hold a mechanism in their head, young
enough that nothing may be assumed. The output is **one `.html` file on disk**, opened by
double-click, that a manager reads in ten minutes and afterwards can argue about the topic.

Topic: $ARGUMENTS

## The bar

1. **The figures are the explanation.** The first screen answers the title as a picture
   the reader can move. A reader who skips every paragraph and reads only headings,
   figures and captions still gets the argument.
2. **Simplify the telling, never the claims.** Plain words, short sentences, every term
   introduced before use — and still the number, the failure mode, the tradeoff and the
   open question. Those four are what the reader came for.
3. **The reader acts.** They drag a slider and watch the consequence, step through a
   mechanism at their own pace, flip a before/after, commit to a guess before the answer.
   Motion shows a change of state; it never decorates.
4. **Every concept owns one colour**, the same in the prose, the terms strip and every
   figure, so the eye links the word to the shape without a legend.

`assets/reference-rejected.png` is what this skill used to produce: correct, flat, one
accent colour, boxes in a row. `assets/reference-good.png` is the bar. Look at both
before the first page and again before you ship.

## Files

| File | Read it for |
|---|---|
| `${CLAUDE_SKILL_DIR}/assets/template.html` | **The kit, by example.** A finished page (café queue) using every component. Copy it; never write the CSS or runtime from scratch. |
| `${CLAUDE_SKILL_DIR}/references/explainer-craft.md` | What to say: concept shapes, the ladder, techniques, analogies, sentence rules, self-check. |
| `${CLAUDE_SKILL_DIR}/references/visual-system.md` | How it looks: concept colours, layout, component catalogue, figure router, SVG rules, the never-list. |
| `${CLAUDE_SKILL_DIR}/references/motion-and-interaction.md` | How it moves: live model, stepper, toggle, predict, linked terms, ambient loops, URL params, reduced motion, print. |
| `${CLAUDE_SKILL_DIR}/scripts/check.py` | The ship check: static rules, a headless-Chrome audit, and screenshot tiles to look at. |

## Register dial

A request phrased as "explain like I'm five" lands here. Serve it, do not correct it.
Move the dial, never the floor:

- **Simplest.** Three to four sections, a figure in every one, shortest sentences. Still
  one live figure, one predict box, and the four claims above.
- **Default.** Four to seven sections, as `explainer-craft.md` describes.

Length follows the topic. Padding a small topic is the same failure as flattening a big one.

## Procedure

1. **Get the substance.** Read the source document fully, or research the topic until you
   can state the mechanism, one number, one tradeoff and one open question without
   hedging. An explainer written from a summary explains the summary.
2. **Classify the shape, name the one thing.** Pick the concept shape (mechanism, system,
   quantity, abstract, decision, history, comparison) from `explainer-craft.md`; it decides
   the hero figure and its interaction. Write the one sentence the reader must leave with.
3. **Plan the page in your head, section by section:** the heading as a claim, the figure
   and the single thing it proves, its interaction (if any), and which concept colours it
   uses. Name 2–5 concepts and give each a colour. Choose the surprise for the predict box.
4. **Copy the template** next to the source: `cp ${CLAUDE_SKILL_DIR}/assets/template.html
   <out>.html`, then Read the copy whole once. Keep the `ELI15 KIT` CSS and the
   `ELI15 RUNTIME` script byte for byte. Replace the `<title>`, the `PAGE CONCEPTS and page
   CSS` block (your own CSS rules go there too), everything inside `<main>`, and the `PAGE`
   script. No café survives: the check fails on leftover demo words.
5. **Draw.** Hero first, then each section's figure, choosing the pattern from the figure
   router in `visual-system.md` before drawing. Compute numbers in the `PAGE` script from
   one `model()` function, so the prose, the readout and the chart cannot disagree. No
   quantity to drag? Drop `model()`; a stepper or a toggle is the interactive figure.
6. **Check:** `uv run ${CLAUDE_SKILL_DIR}/scripts/check.py <out>.html`. Fix every FAIL;
   fix each WARN or say in the report why it stays. The plugin's stop hook runs the same
   check on every eli15 page you wrote and sends you back on a FAIL; it is the net, not
   the step.
7. **Look.** Read every tile the check prints: light, dark, phone, no-JS, the alternate
   states (every toggle flipped, every stepper on step 1), the first screen, print page 1. Hold them next to both reference images. If the
   page looks closer to the rejected one — one hue, boxes in a row, text walls between
   small figures — redraw before polishing. Re-run the check after every fix.
8. **Open it** (`open <out>.html`) and report the path with the honesty metric.

## Output contract

- **A file, never an Artifact**, written next to its source material. Publish an
  Artifact only if explicitly asked.
- One file, no build step, zero third-party JavaScript. Google Fonts by `<link>` is the
  only network request allowed; without it the page falls back to system fonts.
- Figures are hand-written inline SVG or the kit's HTML bars. No images, no chart libraries.
- Works on a phone, in dark mode, with reduced motion, without JavaScript, and on paper.
  Without JS and in print every figure shows its finished picture.

## Honesty metric

Close the report with three lists, the third never empty: what you **verified** (ran the
check, looked at a tile, recomputed a number), what you **took from the source** (read it,
did not re-derive), and what is **unverified** (claims you could not check, tiles you did
not look at, browsers you did not try). An explainer that hides its own uncertainty
teaches the wrong lesson on the first page.
