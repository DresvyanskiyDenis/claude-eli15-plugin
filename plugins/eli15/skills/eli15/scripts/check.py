# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10"]
# ///
"""Ship check for an eli15 page.

    uv run <skill dir>/scripts/check.py PAGE.html [--allow-demo] [--no-render] [--out DIR]

1. Static rules on the source (self-contained, accessible, kit present, no demo text left).
2. Headless Chrome audit at 1280 and 390 px, through every stepper step, every toggle state
   and every slider at its min and max: SVG labels that overlap or leave their figure,
   page-wide horizontal scroll, JS errors.
3. Screenshots, split into tiles you can Read: light, dark, phone, no-JS, alternate states
   (every toggle flipped, every stepper on step 1), the first screen, page 1 of the print PDF.
Exit status 1 when any FAIL is printed.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

ERR_HOOK = (
    "<script>window.__eli15errs=[];"
    "addEventListener('error',e=>__eli15errs.push(String(e.message)));"
    "addEventListener('unhandledrejection',e=>__eli15errs.push(String(e.reason)));</script>"
)

AUDIT_JS = r"""<script>
addEventListener('load', () => document.fonts.ready.then(() => setTimeout(() => {
  const root = document.documentElement;
  const out = { errors: window.__eli15errs || [], overlaps: [], outside: [], fonts: [], overflow: [] };
  root.classList.add('motion-off');
  const visible = el => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) return false;
    }
    return true;
  };
  const figName = svg => {
    const f = svg.closest('figure');
    return (f && (f.querySelector('.fig-n')?.textContent.trim() || f.id)) || 'svg outside a figure';
  };
  const say = t => '"' + t.textContent.trim().replace(/\s+/g, ' ').slice(0, 38) + '"';
  const seen = new Set();
  const add = (list, s) => { if (!seen.has(s)) { seen.add(s); list.push(s); } };
  const measure = (svg, where) => {
    const sr = svg.getBoundingClientRect();
    if (!sr.width) return;
    const vb = svg.viewBox && svg.viewBox.baseVal;
    const scale = vb && vb.width ? sr.width / vb.width : 1;
    const ts = [...svg.querySelectorAll('text')].filter(t => !t.closest('defs') && t.textContent.trim() && visible(t));
    const rs = ts.map(t => t.getBoundingClientRect());
    let min = Infinity;
    ts.forEach((t, i) => {
      const r = rs[i];
      min = Math.min(min, parseFloat(getComputedStyle(t).fontSize) * scale);
      if (r.left < sr.left - 2 || r.right > sr.right + 2 || r.top < sr.top - 2 || r.bottom > sr.bottom + 2)
        add(out.outside, `${figName(svg)} (${where}): ${say(t)} runs past the edge of its SVG`);
      for (let j = i + 1; j < ts.length; j++) {
        const q = rs[j];
        const w = Math.min(r.right, q.right) - Math.max(r.left, q.left);
        const h = Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top);
        if (w > 2 && h > 3) add(out.overlaps, `${figName(svg)} (${where}): ${say(t)} overlaps ${say(ts[j])}`);
      }
    });
    if (ts.length && where === 'final') out.fonts.push([figName(svg), +min.toFixed(1)]);
  };
  const svgsIn = el => [...el.querySelectorAll('svg')].filter(s => !s.parentElement.closest('svg'));
  svgsIn(document).forEach(s => measure(s, 'final'));
  for (const st of (window.ELI15 && ELI15.steppers) || []) {
    for (let k = 1; k < st.n; k++) { st.show(k, false, false); svgsIn(st.fig).forEach(s => measure(s, 'step ' + k)); }
    st.show(st.n, false, false);
  }
  for (const g of document.querySelectorAll('[data-toggle]')) {
    const btns = [...g.querySelectorAll('button[data-state]')];
    const first = btns.find(b => b.getAttribute('aria-pressed') === 'true') || btns[0];
    for (const b of btns) { if (b === first) continue; b.click(); svgsIn(g.closest('figure')).forEach(s => measure(s, 'state ' + b.dataset.state)); }
    first && first.click();
  }
  for (const inp of document.querySelectorAll('input[type="range"]')) {
    if (inp.closest('.player')) continue;
    const scope = inp.closest('figure') || document, was = inp.value;
    for (const v of [inp.min || '0', inp.max || '100']) {
      inp.value = v;
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      svgsIn(scope).forEach(s => measure(s, `${inp.id || 'slider'} at ${v}`));
    }
    inp.value = was;
    inp.dispatchEvent(new Event('input', { bubbles: true }));
  }
  out.scrollWidth = root.scrollWidth;
  out.width = innerWidth;
  if (root.scrollWidth > innerWidth + 1)
    for (const el of document.querySelectorAll('body *')) {
      if (el.closest('.frame') || out.overflow.length >= 6) continue;
      const r = el.getBoundingClientRect();
      if (r.right > innerWidth + 1) out.overflow.push(`<${el.tagName.toLowerCase()}${el.id ? ' id=' + el.id : ''}${typeof el.className === 'string' && el.className ? ' class=' + el.className : ''}> ends at ${Math.round(r.right)}px`);
    }
  const fig = document.querySelector('figure');
  out.firstFigureTop = fig ? Math.round(fig.getBoundingClientRect().top + scrollY) : null;
  out.height = root.scrollHeight;
  const s = document.createElement('script');
  s.type = 'application/json';
  s.id = 'eli15-audit';
  s.textContent = JSON.stringify(out).replace(/</g, '\\u003c');
  document.body.append(s);
  if (parent !== window) parent.postMessage(s.textContent, '*');
}, 400)));
</script>"""

# Chrome will not open a headless window narrower than 500 px, so phone views run in a 390 px iframe.
PHONE_WRAP = r"""<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff">
<iframe src="{src}" style="width:390px;height:{h}px;border:0;display:block"></iframe>
<script>addEventListener('message', e => {{ const s = document.createElement('script');
s.type = 'application/json'; s.id = 'eli15-audit'; s.textContent = e.data; document.body.append(s); }});</script>"""

# the alternate-states shot: every toggle in the state its markup does not open in
FLIP_JS = """<script>addEventListener('load', () => { for (const g of document.querySelectorAll('[data-toggle]')) {
  const b = [...g.querySelectorAll('button[data-state]')].find(b => b.getAttribute('aria-pressed') !== 'true');
  if (b) b.click(); } });</script>"""

DEMO = re.compile(r"barista|caf[eé]\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def static_checks(src: str, allow_demo: bool) -> tuple[list[str], list[str], dict]:
    fails, warns = [], []
    body = re.sub(r"<(script|style)\b.*?</\1>", "", src, flags=re.S | re.I)
    title = re.search(r"<title>\s*([^<]*?)\s*</title>", src, re.S)
    if not title or not title.group(1):
        fails.append("no <title>: the title is the claim, in under 70 characters")
    elif len(title.group(1)) > 70:
        warns.append(f"title is {len(title.group(1))} characters; keep it under 70")
    if "<h1" not in src:
        fails.append("no <h1>")
    if re.search(r"<script[^>]*\bsrc\s*=", src, re.I):
        fails.append("a <script src>: the page must run with zero third-party JS")
    for tag in re.findall(r"<link\b[^>]*>", src, re.I):
        if "stylesheet" in tag and "https://fonts.googleapis.com/" not in tag:
            fails.append(f"stylesheet not from Google Fonts: {tag[:90]}")
    if re.search(r"@import\s+(url\()?['\"]?(?!https://fonts\.googleapis\.com)", src):
        fails.append("@import of something other than Google Fonts")
    if re.search(r"<(img|video|audio|source|iframe|object|embed)\b[^>]*\bsrc\s*=\s*['\"]https?:", src, re.I):
        fails.append("remote media: inline it (SVG) or drop it")
    if "0.01ms" in src:
        fails.append("0.01ms reduced-motion hack: use animation: none and a final-state base style")
    if "prefers-reduced-motion" not in src:
        fails.append("no prefers-reduced-motion rule")
    n_fig, n_cap = len(re.findall(r"<figure\b", src)), len(re.findall(r"<figcaption\b", src))
    if n_fig != n_cap:
        fails.append(f"{n_fig} figures but {n_cap} figcaptions: every figure states its claim")
    for tag in re.findall(r"<svg\b[^>]*>", src):
        if 'aria-hidden="true"' in tag:
            continue
        ref = re.search(r'aria-labelledby="([^"]+)"', tag)
        named = bool(re.search(r'aria-label="[^"]{12,}"', tag)) or bool(
            ref and all(f'id="{i}"' in src for i in ref.group(1).split()))
        if 'role="img"' not in tag or not named:
            fails.append(f'svg without role="img" and a sentence-long aria-label (or an aria-labelledby '
                         f'naming existing ids): {tag[:80]}')
    for marker in ("ELI15 KIT", "ELI15 RUNTIME"):
        if marker not in src:
            fails.append(f"kit marker '{marker}' missing: copy the template's style and runtime blocks whole")
    # inline <code> may name the demo, so a page about eli15 itself can say `café`
    demo = None if allow_demo else DEMO.search(re.sub(r"<code>.*?</code>", "", src, flags=re.S))
    if demo:
        fails.append(f"template demo text left in the page ('{demo.group(0)}'): replace every demo figure")
    if re.search(r"\$\$|\\frac|\\\(", src):
        fails.append("LaTeX in the page: write formulas in MathML")
    counts = {
        "live sliders": len(re.findall(r'type="range"', body)),
        "steppers": len(re.findall(r'class="[^"]*\bstepper\b', body)),
        "toggles": len(re.findall(r"\bdata-toggle\b", body)),
        "predict boxes": len(re.findall(r'class="predict\b', body)),
        "linked terms": len(re.findall(r'class="ref\b', body)),
        "details": len(re.findall(r"<details\b", body)),
        "concept colours": len(set(re.findall(r"--c-[a-z0-9-]+(?=\s*:)", src))),
        "sections": len(re.findall(r"<section\b(?![^>]*\bsources\b)", body)),
        "figures": n_fig,
    }
    if counts["live sliders"] + counts["steppers"] + counts["toggles"] == 0:
        fails.append("no interactive figure: add a live model, a stepper or a before/after toggle")
    if counts["live sliders"] and "aria-live" not in body:
        fails.append("a slider but no aria-live readout")
    if counts["predict boxes"] == 0:
        warns.append("no predict-then-reveal box")
    if counts["concept colours"] < 2:
        warns.append("fewer than two --c-* concept colours")
    if counts["figures"] < counts["sections"] - 2:
        warns.append(f"{counts['figures']} figures for {counts['sections']} sections")
    if re.search(r"\d(\.\d+)?d?vh\b", src):
        warns.append("vh units: they break the tall-window screenshots and jump on phones")
    if re.search(r"font-family:[^;]*\bInter\b", src):
        warns.append("Inter: use the kit fonts")
    if re.search(r"background-clip:\s*text|-webkit-background-clip:\s*text", src):
        warns.append("gradient text")
    if re.search(r"(linear|radial|conic)-gradient\(", src):
        warns.append("a gradient: flat fills read better in figures")
    if re.search(r"border-left:\s*[3-9]px", src):
        warns.append("a thick left border (accent bar on a card)")
    if "backdrop-filter" in src:
        warns.append("backdrop-filter (glass)")
    for h in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", src, re.S):
        if EMOJI.search(h):
            warns.append(f"emoji in a heading: {re.sub('<[^>]+>', '', h)[:60]}")
    return fails, warns, counts


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("check.py: Chrome not found; set CHROME=/path/to/chrome")


class Chrome:
    def __init__(self, exe: str, out: Path):
        self.exe, self.prof = exe, out / "_profile"

    def run(self, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
        cmd = [self.exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--run-all-compositor-stages-before-draw",
               f"--user-data-dir={self.prof}", *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def audit(chrome: Chrome, url: str, width: int) -> dict:
    res = chrome.run("--dump-dom", "--virtual-time-budget=9000", f"--window-size={max(width, 500)},900", url)
    m = re.search(r'<script type="application/json" id="eli15-audit">(.*?)</script>', res.stdout, re.S)
    if not m:
        return {"errors": [f"audit did not finish at {width}px: {res.stderr.strip()[-300:]}"],
                "overlaps": [], "outside": [], "fonts": [], "overflow": [], "height": 6000,
                "scrollWidth": width, "width": width, "firstFigureTop": None}
    return json.loads(m.group(1))


def trim_and_tile(png: Path, max_h: int) -> list[Path]:
    im = Image.open(png).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((im.width - 3, im.height - 3)))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        im = im.crop((0, 0, im.width, min(im.height, box[3] + 40)))
    im.save(png)
    tiles = []
    for i, top in enumerate(range(0, im.height, max_h), 1):
        t = png.with_name(f"{png.stem}-{i}.png")
        im.crop((0, top, im.width, min(top + max_h, im.height))).save(t)
        tiles.append(t)
    return tiles


def render(page: Path, out: Path, a_desk: dict, a_phone: dict, has_alt: bool) -> list[str]:
    chrome = Chrome(find_chrome(), out)
    uri = page.as_uri()
    # headless Chrome has no working switch to turn JS off, so the no-JS view is a copy without scripts
    src = page.read_text(encoding="utf-8").replace("<head>", f'<head><base href="{page.parent.as_uri()}/">', 1)
    nojs = out / "_nojs.html"
    nojs.write_text(re.sub(r"<script\b.*?</script>", "", src, flags=re.S | re.I), encoding="utf-8")
    alt = out / "_alt.html"
    alt.write_text(src.replace("</body>", FLIP_JS + "</body>", 1), encoding="utf-8")
    h_desk, h_phone = a_desk.get("height", 6000) + 200, a_phone.get("height", 9000) + 200
    shots = [
        ("desktop-light", 1280, h_desk, uri + "?theme=light&motion=off"),
        ("desktop-dark", 1280, h_desk, uri + "?theme=dark&motion=off"),
        ("nojs", 1280, h_desk, nojs.as_uri()),
    ]
    if has_alt:
        shots.append(("alt-states", 1280, h_desk, alt.as_uri() + "?theme=light&motion=off&step=1"))
    lines = []
    wrap = out / "_phone.html"
    wrap.write_text(PHONE_WRAP.format(src=uri + "?theme=light&motion=off", h=h_phone), encoding="utf-8")
    png = out / "phone.png"
    chrome.run("--virtual-time-budget=7000", f"--window-size=500,{min(h_phone, 16000)}", f"--screenshot={png}",
               wrap.as_uri())
    if png.exists():
        Image.open(png).crop((0, 0, 390, min(h_phone, 16000))).save(png)
        lines.append("  phone: " + " ".join(t.name for t in trim_and_tile(png, 1600)))
    else:
        lines.append("  phone: screenshot failed")
    for name, w, h, url in shots:
        png = out / f"{name}.png"
        chrome.run("--virtual-time-budget=7000", f"--window-size={w},{min(h, 16000)}", f"--screenshot={png}", url)
        if not png.exists():
            lines.append(f"  {name}: screenshot failed")
            continue
        tiles = trim_and_tile(png, 1400)
        lines.append(f"  {name}: " + " ".join(t.name for t in tiles))
    desk, phone = out / "desktop-light.png", out / "phone.png"
    if desk.exists() and phone.exists():
        a, b = Image.open(desk), Image.open(phone)
        sheet = Image.new("RGB", (1280 + 32 + 390, 900), "white")
        sheet.paste(a.crop((0, 0, 1280, min(900, a.height))), (0, 0))
        sheet.paste(b.crop((0, 0, 390, min(844, b.height))), (1312, 0))
        sheet.save(out / "first-screen.png")
        lines.insert(0, "  first screen (desktop | phone): first-screen.png")
    pdf = out / "print.pdf"
    chrome.run("--no-pdf-header-footer", "--virtual-time-budget=4000", f"--print-to-pdf={pdf}", uri)
    if pdf.exists():
        pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))
        line = f"  print: print.pdf ({pages} pages)"
        if shutil.which("sips"):
            p1 = out / "print-page1.png"
            subprocess.run(["sips", "-s", "format", "png", str(pdf), "--out", str(p1)], capture_output=True)
            if p1.exists():
                line += ", page 1: print-page1.png"
        lines.append(line)
    else:
        lines.append("  print: PDF export failed")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", type=Path)
    ap.add_argument("--allow-demo", action="store_true", help="the template itself: allow its demo text")
    ap.add_argument("--no-render", action="store_true", help="static rules only")
    ap.add_argument("--out", type=Path, help="where renders go (default $TMPDIR/eli15-check/<page>)")
    args = ap.parse_args()
    page = args.page.resolve()
    src = page.read_text(encoding="utf-8")
    fails, warns, counts = static_checks(src, args.allow_demo)

    print(f"eli15 check: {page}")
    print("  " + ", ".join(f"{v} {k}" for k, v in counts.items()))
    shot_lines: list[str] = []
    out = Path()
    if not args.no_render:
        out = (args.out or Path(tempfile.gettempdir()) / "eli15-check" / page.stem).resolve()
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob("*.png"):
            old.unlink()
        probe = out / "_audit.html"
        probe.write_text(src.replace("<head>", "<head>" + ERR_HOOK, 1).replace("</body>", AUDIT_JS + "</body>", 1),
                         encoding="utf-8")
        chrome = Chrome(find_chrome(), out)
        wrap = out / "_phone-audit.html"
        wrap.write_text(PHONE_WRAP.format(src=probe.as_uri() + "?theme=light", h=900), encoding="utf-8")
        a_desk = audit(chrome, probe.as_uri() + "?theme=light", 1280)
        a_phone = audit(chrome, wrap.as_uri(), 390)
        for label, a in (("desktop", a_desk), ("phone", a_phone)):
            fails += [f"{label}: JS error: {e}" for e in a["errors"]]
            fails += [f"{label}: {o}" for o in a["overlaps"]]
            fails += [f"{label}: {o}" for o in a["outside"]]
            if a["scrollWidth"] > a["width"] + 1:
                fails.append(f"{label}: page scrolls sideways ({a['scrollWidth']}px > {a['width']}px): "
                             + "; ".join(a["overflow"]))
        top = a_desk.get("firstFigureTop")
        if top is None or top > 1000:
            fails.append(f"no figure starts in the first screen (first figure at {top}px): lead with the picture")
        for name, px in a_phone["fonts"]:
            if px < 10:
                warns.append(f"phone: smallest label in {name} renders at {px}px; give its .frame a --min-phone width")
        shot_lines = render(page, out, a_desk, a_phone, counts["steppers"] + counts["toggles"] > 0)

    for f in fails:
        print(f"FAIL  {f}")
    for w in warns:
        print(f"WARN  {w}")
    if shot_lines:
        print(f"Look at these before shipping (Read the tiles in {out}/):")
        print("\n".join(shot_lines))
    print("RESULT:", "FAIL" if fails else "PASS", f"({len(fails)} fail, {len(warns)} warn)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
