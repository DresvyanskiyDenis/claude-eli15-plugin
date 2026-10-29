# Motion and interaction

How an eli15 page moves and what the reader can do with it. The runtime lives in the
template's `ELI15 RUNTIME` script: keep it byte for byte, drive it with markup, and put
page logic in the `PAGE` script. Zero third-party JS.

## Principles

1. **Motion shows a change of state** — a backlog draining, a request travelling, a line
   regrouping. If nothing changes state, nothing moves.
2. **The reader holds the controls.** Steppers never autoplay a loop; Play replays on
   request. One interaction per figure, 1–3 controls.
3. **The default is the finished picture.** Base CSS shows the final state; JS hides parts
   and builds them up. No JS, print, reduced motion, `?motion=off`: the complete figure.
4. **Entrances happen once.** A stepper builds itself the first time it scrolls into view
   (about half a second per step); bars grow once. Nothing replays on scroll-back.
5. **Ambient motion is rare and calm.** At most one loop per page, only where it shows a
   rate (customers arriving). It runs only while on screen, the tab is visible and motion
   is allowed.

## Which interaction

| The reader should… | Use | Template example |
|---|---|---|
| vary one input and see every consequence | **live model**: slider + readout + figure redrawn by `render()` | Fig. 1 |
| follow a cause through ordered steps | **stepper** with numbered captions and tokens | Fig. 3 |
| compare two designs of one structure | **before / after toggle** | Fig. 4 |
| commit to a guess before the answer | **predict box** | "Guess first" |
| link a word in the prose to a part of a figure | **linked terms** (`.ref`) | Fig. 1 caption |
| see a change in size land | **growing bars** (`.grow`) | Fig. 2 |
| feel a rate | **ambient loop** via `ELI15.ambient` | arrivals in Fig. 1 |

A page carries at least one live model, stepper or toggle (the check fails without one)
and exactly one predict box.

## Live model

```html
<div class="controls">
  <label class="slider c-busy">How busy is the barista?
    <input id="busy" type="range" min="10" max="95" step="1" value="80" aria-describedby="hero-read">
    <output id="busy-out" for="busy">80%</output></label>
</div>
<p class="readout" id="hero-read" aria-live="polite">At <b class="term c-busy" id="s-busy">80%</b> busy, …</p>
<p class="try"><b>Try</b>drag from 50% to 90%. <b>Notice</b>the wait grows 9 times.</p>
```

- The `PAGE` script holds one pure `model(input)` that returns every number, and one
  `render()` that writes them into the SVG attributes and the readout. Call `render()` on
  `input` and once at load. Prose, readout and chart then cannot disagree.
- The markup's initial values are the `value=` state, so the no-JS page is correct. Ship
  every element of that default picture in the markup; the script only moves, recolours
  and toggles classes. An element the script creates on load is missing without JS and in
  print.
- Put the controls above the picture they drive, so the slider and the figure share the
  first screen at 1280 × 800.
- Label the slider with the question the reader is asking ("How busy is the barista?"),
  not the variable name. Give it the concept colour of the input.
- The readout is a full sentence with the numbers bold and coloured; it is `aria-live`.
- Clamp what the figure can draw (the template caps the line at 12 people and adds "+N more
  outside"), and keep the slider's range inside where the model is valid.

## Stepper

```html
<figure class="fig wide stepper">
  <div class="frame">
    <svg …>
      <g data-s="1">…</g>                               <!-- visible from step 1 on -->
      <path class="ln sk draw" d="…" pathLength="1" data-s="2"/>   <!-- draws itself on step 2 -->
      <text data-s="3-3">…</text>                       <!-- only on step 3 -->
      <circle class="tok fk" r="6" data-tok="2">        <!-- rides a path when step 2 is entered -->
        <animateMotion dur="1.1s" begin="indefinite" fill="freeze"><mpath href="#p50"/></animateMotion>
      </circle>
    </svg>
  </div>
  <ol class="step-caps"><li>Step 1 caption.</li><li>…</li></ol>
  <figcaption>…</figcaption>
</figure>
```

- One `<li>` per step; the runtime counts them and builds the player (‹ Play range ›).
- `data-s="k"` shows a part from step k on; `data-s="a-b"` only from a to b. Ranged parts
  are hidden in the no-JS picture, so the last step must not need them.
- `.draw` plus `pathLength="1"` makes a line draw itself when its step turns on.
- A token (`.tok[data-tok=k]`) rides an `<mpath>` once when step k is entered going
  forward. Define the path in `<defs>` and reuse it.
- Write captions that carry the numbers; a reader stepping with the keyboard hears each one
  (`aria-live`). Arrow keys step when the figure has focus; captions are clickable.
- 3–6 steps. `data-interval="2600"` on the figure sets the Play speed in ms.

## Before / after toggle

```html
<figure class="fig wide" data-state="before">
  <div class="seg" role="group" aria-label="Line layout" data-toggle>
    <button type="button" class="btn" data-state="before" aria-pressed="true">Two separate lines</button>
    <button type="button" class="btn" data-state="after" aria-pressed="false">One shared line</button>
  </div>
  <svg …><g class="only-before row-a">…</g><g class="only-after row-s">…</g></svg>
</figure>
```

- The two states are always named `before` and `after`: the runtime, the kit CSS and the
  check know only those. Put the reader's words on the buttons, not in `data-state`.
- The figure's `data-state` in the markup is what no-JS and print show; pick the state
  that makes the stronger point alone.
- `.only-before` / `.only-after` fade; parts in both states stay. A label that differs
  between states is two `<text>` elements, one per class: a class on a `<tspan>` does not
  fade. To make the change
  visible as movement, give groups a transform per state in the page CSS block, as the
  template does for `.row-a`, `.row-b`, `.row-s` (`figure[data-state="after"] .row-a { transform: … }`).
- Button labels name the options in the reader's words.

## Predict, then reveal

```html
<div class="predict">
  <p class="q"><span class="tag">Guess first</span>The question, with its numbers.</p>
  <div class="choices" role="group" aria-label="Your guess">
    <button type="button" class="btn">about 2 min</button>
    <button type="button" class="btn" data-right>about 18 min</button>
  </div>
  <details><summary>Show the answer</summary><p>The answer, why most people guess wrong, and where the page shows it.</p></details>
</div>
```

Three choices: the intuitive wrong answer, a plausible middle, the right one. Picking one
marks it, marks the right one and opens the answer. No score. Without JS it is a question
with a `<details>` answer.

## Linked terms

`<span class="ref c-wait" data-ref="line" tabindex="0">line</span>` in prose or a caption;
`data-ref="line"` on the SVG group it names. Hover or focus marks that group and dims the
figure's other `[data-ref]` parts, so give every nameable part a `data-ref`. Use it in
captions of busy figures and system maps.

## Growing bars

`.bars.grow` with `--ref` (the old value's share of the track) and each bar's `--w`. The
`.now` bars start at the reference width and grow once to their value when half the
figure is visible. Under reduced motion they render at their value.

## Ambient loop

```js
ELI15.ambient(figureElement, start, stop);
```

`start` begins the loop (for example a `setTimeout` chain calling `element.animate()`),
`stop` clears it. The runtime calls them as the figure enters or leaves the screen, as the
tab hides, and as motion is paused. Tie the loop's speed to the model (the template sends
customers at the arrival rate the slider sets), so the motion is data, not decoration.

## Page tools and URL parameters

The fixed toolbar holds **Pause motion** and **Light / dark**; both choices persist in
`localStorage`. URL parameters set a state for screenshots, links and review:

| Parameter | Effect |
|---|---|
| `?theme=dark` / `light` | force a theme |
| `?motion=off` | pause all motion; steppers open on their last step, bars at full size |
| `?step=2` | every stepper opens on step 2, with no entrance build |
| `?state=after` | every toggle opens in that state |

`window.ELI15` exposes `steppers` (each with `show(k)`, `n`, `stop()`), `still()` and
`ambient()`; the check script uses them to audit every step and state.

## Reduced motion and print

- `prefers-reduced-motion: reduce` sets `animation: none; transition: none` on everything,
  and the runtime treats the page as still: steppers show their last step, bars their
  value, ambient loops never start, SVG animations pause. Never the `0.01ms` duration
  trick; it still fires every animation event.
- `beforeprint` puts every stepper on its last step, grows every bar and opens every
  `<details>`. Print CSS hides the toolbar, players, controls and tokens, and keeps
  figures and notes from splitting across pages.
- Every control is a real `<button>` or `<input>` with a visible focus ring; the stepper
  figure is focusable and steps with the arrow keys.

## Timing

| Motion | Duration | Easing |
|---|---|---|
| step part fade / rise | 450ms | `--ease` (`cubic-bezier(.2,.7,.2,1)`) |
| line draw | 1.1s | linear |
| token ride | 1.1s | SMIL default |
| entrance build | 520ms per step | — |
| bar grow | 1s | `--ease` |
| toggle regroup | 450–550ms | `--ease` |

Keep page-specific motion inside these ranges; nothing over 1.5s, nothing that bounces.
