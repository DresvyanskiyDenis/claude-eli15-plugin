# Explainer craft

What to say and in what order. How it looks is `visual-system.md`; how it moves is
`motion-and-interaction.md`.

## The reader

A smart adult who does not work in this field: a manager, a colleague from another team, a
stakeholder deciding whether to fund or block something. They reason well about cost, risk
and cause in their own domain; they have not spent time in yours. They can hold a mechanism
in their head if you build it in order. What insults them: baby words for ideas they would
grasp in one sentence, an analogy that never pays off in the real mechanism, a page that
hides every tradeoff and every unknown "because it's for non-experts".

What loses them: a wall of text between small figures, a term used before it is defined,
three new ideas in one paragraph, a figure they have to decode instead of read.

## ELI5 vs ELI15

| Axis | ELI5 | ELI15 |
|---|---|---|
| Vocabulary | Everyday words only | Plain words first, then the real term once it is earned |
| Analogy | The analogy is the explanation | The analogy is a bridge; the mechanism is the destination |
| Numbers | "A lot", "a little" | Real numbers, real units, real thresholds |
| Mechanism | "It just works that way" | The step that causes the effect |
| Tradeoffs | One happy path | At least one cost named next to the benefit |
| Unknowns | Never mentioned | Stated plainly: "nobody has solved X yet" |
| The reader afterwards | Feels they understood | Can ask a sharp follow-up or make the call |

Before/after:

- ELI5: "The computer checks if two people wrote the same thing." → ELI15: "Git only flags a
  collision when two edits touch the same line. Two agents can each rewrite a whole page
  from a stale read, touch no shared line, and git merges both cleanly, reporting success
  while one person's fix disappears."
- ELI5: "Busy cafés have long lines." → ELI15: "From 80% to 90% busy, the barista's load
  grows by an eighth and the wait more than doubles, from 8 to 18 minutes, because only
  spare time clears a backlog and spare time halved."

## Concept shapes

Every topic has a dominant shape. The shape decides the hero figure (the first screen) and
the interaction that carries it. Classify before outlining; most topics have one dominant
shape and borrow a second for one section.

| Shape | The reader's question | Hero figure | Interaction |
|---|---|---|---|
| **Mechanism** | How does it work, step by step? | The causal chain drawn as the real thing (parts, flows), not as labelled boxes | Stepper with tokens riding the paths |
| **System** | What are the parts and who talks to whom? | Annotated architecture, every arrow labelled with a verb | Linked terms that light parts; stepper for one request's path |
| **Quantity** | How big, how fast, where does it break? | A live model: the scene plus its curve, a marker on the curve | Slider with a readout sentence |
| **Abstract** | What *is* it? | One concrete example, then the same example as a diagram, then the notation | Toggle concrete ↔ abstract; formula in `<details>` |
| **Decision** | Which should we pick? | The same structure under each option, the difference highlighted | Before/after toggle; paired bars for the cost |
| **History** | How did we get here? | A timeline with the turning points as events, not dates alone | Stepper along the timeline |
| **Comparison** | How do A and B differ? | Small multiples on one scale, or one shape that morphs | Toggle; paired bars against a reference |

A quantity topic explained with a flow chart, or a mechanism explained with a bar chart, is
the most common reason a page feels flat. Ask what the reader would want to *do* with the
idea — vary a number, follow a request, pick an option — and give them that control.

## The explanation ladder

Order the page this way and do not skip a rung. Each rung is the reader's motive for the
next one.

1. **The situation.** The concrete scene — who, what, when — before any concept. In the
   hero, it is the picture itself.
2. **The surprise or failure.** What goes wrong, as it actually appears. This is where the
   predict box goes: let the reader guess wrong first.
3. **Why the obvious fix fails.** Name the fix a smart reader proposes in five seconds,
   then show where it breaks. Skip this and the reader silently objects to everything after.
4. **The mechanism.** The real causal chain, in the field's own terms, now that the reader
   wants it. Usually the stepper.
5. **The tradeoff.** What the fix costs, not only what it buys. Usually the toggle.
6. **What we chose, or what to do.** A decision stated as a decision.
7. **What is still open.** Limits of the model, unsolved parts, what would change the answer.

Sections map to rungs loosely: a small topic folds 2 and 3 together; a big one gives the
mechanism two sections.

## Techniques that teach

Use most of these on every page. They come from learning research (prediction, active
control, concreteness fading) and from the best explorable explanations.

- **Live model first.** The hero lets the reader change the one input that matters and see
  every consequence update: the picture, the curve, and the sentence under it.
  No measured quantity to drive it? Derive the curve from the source's stated defaults
  (sizes, limits, prices), draw the side nobody has measured hollow and dashed, and say so
  on the figure: "illustrative, no break-even measured". Never invent a number to fill it.
- **Try / Notice.** Under every live figure, one line: what to try, and what to notice.
  "Try: drag from 50% to 90%. Notice: the load grows 1.8 times; the wait grows 9 times."
  It turns a toy into a lesson.
- **Predict, then reveal.** One per page, on the most counter-intuitive number. The reader
  commits to a guess, then sees the answer and why most people guess wrong. No scores, no
  quizzes, no "Correct!" banners.
- **Visual before formula.** The figure builds the intuition; the formula comes after, in
  one plain sentence (`average wait = drink time × busy ÷ spare`) and in full, as MathML,
  inside `<details>`.
- **Concreteness fading.** Concrete example → the same example as a diagram → the general
  rule. Never start with the general rule.
- **Failure first.** Show the broken version before the fix; a myth note crosses out the
  wrong belief and states what happens instead.
- **Worked tiny example.** Run the mechanism once with small, real numbers the reader can
  check in their head (5 people, 2 minutes each).
- **Progressive depth.** The main path stays short; derivations, edge cases and "where
  this comes from" go in `<details>`. A reader who opens none of them still gets the argument.
- **A recap that carries forward.** Three to four numbered claims with their numbers, then
  one question the reader can ask about their own situation.

## Analogy discipline

An analogy earns its place only when the real mechanism is hard to picture on first
exposure and the analogy's *structure* matches it, not just its mood. Cash it out: the
next sentence names the real mechanism in real terms. Retire it the moment it would have
to lie to keep working; a stretched analogy leaves the reader believing something false.

Often the best "analogy" is a small, real instance of the thing itself: a café queue for
queueing theory, a three-page wiki for a merge conflict. Then there is nothing to cash out.

## Naming the sharp edges

The page is not finished until it states what breaks, what is still open and what nobody
has solved, as plain facts with a number or a source:

- Good: "30–40% of any wiki goes stale within six months. Plan for it."
- Bad: "There might be some challenges around freshness we may need to think about."

Name the failure concretely, give the number, say what is being done about it — or that
nothing is.

## Sentence rules

- One idea per sentence, active voice, a concrete subject. "The team decided", not "the
  decision emerged".
- Concrete over abstract: "cut deploy time from 40 minutes to 4", not "improved efficiency".
- No binary contrasts ("This isn't X, it's Y"), no colon reveals ("The secret: …"), no
  importance puffery ("a pivotal moment"), no weasel attribution ("experts agree"), no
  fake-strong verbs ("serves as a hub for").
- No throat-clearing openers, no recap endings ("In conclusion"), no cute closing metaphor.
- **Headings are claims**, not topics: "Spare time is the only thing that clears a backlog",
  not "Mechanism". The eyebrow above it names the rung ("The mechanism").
- **Captions state what the figure proves**, with its numbers, so a skimmer gets the point
  from the caption alone.
- A term is introduced in plain words at first use and coloured as its concept; after that,
  use the same word every time. Synonyms read as new concepts.

## Page shape

1. **Header:** eyebrow (topic · angle), the title as the claim with the key term coloured,
   a lead of two sentences that already contains the main number, one meta line with the
   model's assumptions.
2. **Hero figure** in the first viewport: the live model for the title's claim.
3. **Terms strip:** the 2–5 concepts, each in its colour, one line each.
4. **Sections**, each about one screen: eyebrow, heading-claim, one to three short
   paragraphs, one figure (two is the ceiling), optionally one note and one `<details>`.
5. **Recap box:** the claims to remember, then the question to ask next.
6. **Sources:** where every number comes from, including "computed by `model()` in this
   page's source".

## Self-check

Answer each by looking at the page:

1. Does the first screen show the answer as a picture with a control on it?
2. Does every technical term get a plain clause at or before first use, and one colour?
3. Is there a real number with a unit, a cost or tradeoff, and an open question?
4. Is there exactly one predict box, on the most counter-intuitive fact?
5. Does every live figure have a Try / Notice line and a readout sentence?
6. Does every analogy get cashed out in the same section?
7. Do headings and captions alone reconstruct the argument?
8. Does any section run longer than a screen, or put two new ideas in one paragraph? Split it.
9. For each section without a figure: what does prose do better here? "I did not think of
   one" is not a reason; try the figure router in `visual-system.md`.
10. Does the close land on a decision or a question, not a restatement?
