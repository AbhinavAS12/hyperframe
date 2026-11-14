#!/usr/bin/env python3
"""Build compositions/captions.html for the Pak roadshow caption versions.

Usage: python3 build_captions.py a ../pak-roadshow-a
       python3 build_captions.py b ../pak-roadshow-b

Tiers (Montserrat):
  r = Regular 400, white      (plain connecting words)
  m = Medium 500, white       (secondary emphasis)
  b = Bold 700, yellow        (key words: names, company, offers)
  h = Bold 700, yellow, hero  (place, date, Golden Visa, headline offers)
"""
import json
import os
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(HERE, "words.json")))

# Each group: list of lines; each line: (tier, [(display text, word index), ...]).
# Word indices refer to words.json; spoken words not shown (e.g. "of") are simply skipped.
GROUPS = [
    [("h", [("Lahore,", 0)])],
    [("b", [("Dubai", 1)]), ("r", [("is", 2), ("coming", 3), ("to", 4), ("you", 5)])],
    [("m", [("and", 6), ("so", 7), ("am", 8), ("I.", 9)])],
    [("r", [("I", 10), ("am", 11)]), ("m", [("Zainul", 12), ("Abideen", 13)])],
    [("r", [("from", 14)]), ("b", [("Allegiance", 15)]), ("b", [("Real", 16), ("Estate.", 17)])],
    [("r", [("Join", 18), ("me", 19), ("for", 20), ("our", 21)])],
    [("b", [("Dubai", 22), ("Property", 23)]), ("b", [("Roadshow", 24)])],
    [("r", [("at", 25)]), ("h", [("Nishat", 26), ("Hotel,", 27)]), ("b", [("Johar", 28), ("Town", 29)])],
    [("r", [("on", 30)]), ("h", [("21st", 31), ("&", 32), ("22nd", 33)]), ("h", [("November", 35)])],
    [("r", [("Come", 36), ("compare", 37)]), ("m", [("properties", 38)])],
    [("r", [("that", 39), ("fit", 40), ("your", 41)]), ("b", [("budget", 42)])],
    [("r", [("and", 43), ("explore", 44)]), ("b", [("flexible", 45)]), ("b", [("payment", 46), ("plans,", 47)])],
    [("h", [("Year-end", 48)]), ("h", [("offers", 49)])],
    [("r", [("and", 50)]), ("b", [("extra", 51), ("discounts", 52)])],
    [("m", [("only", 53), ("available", 54)]), ("r", [("at", 55), ("the", 56), ("event.", 57)])],
    [("r", [("We", 58), ("will", 59), ("walk", 60), ("you", 61)]), ("r", [("through", 62), ("buying", 63), ("in", 64)]), ("b", [("Dubai", 65)])],
    [("r", [("and", 66), ("explain", 67), ("how", 68)]), ("m", [("eligible", 69), ("investors", 70)])],
    [("r", [("can", 71), ("apply", 72), ("for", 73)]), ("h", [("10-Year", 74)]), ("h", [("Golden", 76), ("Visa.", 77)])],
    [("r", [("So", 78)]), ("b", [("register", 79), ("now", 80)])],
    [("r", [("to", 81)]), ("b", [("book", 82), ("your", 83)]), ("b", [("appointment.", 84)])],
    [("m", [("See", 85), ("you", 86), ("there!", 87)])],
]

TOTAL = 31.6
# Word 74 "ten" is displayed as "10-Year" and also covers 75 "years".

STYLES = {
    # base font sizes per tier, vertical anchor (centre of group), italic highlights
    "a": dict(sizes=dict(r=56, m=62, b=104, h=132), anchor=1010, upper=False),
    "b": dict(sizes=dict(r=56, m=62, b=78, h=124), anchor=1215, upper=True),
}
WEIGHT = dict(r=400, m=500, b=700, h=700)


def group_times():
    out = []
    for gi, g in enumerate(GROUPS):
        idx = [i for _, toks in g for _, i in toks]
        first, last = min(idx), max(idx)
        start = max(0.2, WORDS[first][1] - 0.1)
        out.append([start, WORDS[last][2]])
    for gi in range(len(out)):
        nxt = out[gi + 1][0] if gi + 1 < len(out) else TOTAL
        out[gi][1] = round(min(out[gi][1] + 0.55, nxt), 3)
        out[gi][0] = round(out[gi][0], 3)
    return out


def build(variant):
    st = STYLES[variant]
    times = group_times()
    markup = []
    tl_groups = []
    for gi, g in enumerate(GROUPS):
        start, end = times[gi]
        lines_html = []
        lines_meta = []
        for li, (tier, toks) in enumerate(g):
            words_html = []
            wmeta = []
            for wi, (txt, idx) in enumerate(toks):
                wid = f"cw-{gi}-{li}-{wi}"
                words_html.append(f'<span class="w" id="{wid}">{escape(txt)}</span>')
                wmeta.append([wid, round(WORDS[idx][1], 3)])
            text = " ".join(t for t, _ in toks)
            if st["upper"] and tier in "bh":
                text = text.upper()
            lid = f"cl-{gi}-{li}"
            inner = " ".join(words_html)
            if variant == "b" and tier == "b":
                inner = f'<span class="pill" id="cp-{gi}-{li}">{inner}</span>'
            lines_html.append(f'<div class="ln t-{tier}" id="{lid}">{inner}</div>')
            lines_meta.append(dict(id=lid, tier=tier, text=text, words=wmeta))
        dur = round(end - start, 3)
        markup.append(
            f'<div id="cg-{gi}" class="clip cg" data-start="{start}" data-duration="{dur}" '
            f'data-track-index="{gi % 2}">\n        ' + "\n        ".join(lines_html) + "\n      </div>"
        )
        tl_groups.append(dict(id=f"cg-{gi}", start=start, end=end, lines=lines_meta))
    return markup, tl_groups


CSS_COMMON = """
    #root { position: absolute; inset: 0; overflow: visible; }
    .cg {
      position: absolute; left: 0; width: 100%; top: __ANCHOR__px;
      transform: translateY(-50%);
      text-align: center; overflow: visible; pointer-events: none;
    }
    .ln { display: block; width: 100%; font-family: "Montserrat", sans-serif; line-height: 1.04; white-space: nowrap; }
    .w { display: inline-block; will-change: transform, opacity; }
    .t-r { font-weight: 400; color: #ffffff; }
    .t-m { font-weight: 500; color: #ffffff; }
    .t-b, .t-h { font-weight: 700; color: #F5EE1F; }
"""

CSS_A = """
    .ln {
      text-shadow: 0 2px 3px rgba(0,0,0,0.7), 0 0 14px rgba(0,0,0,0.45), 0 6px 24px rgba(0,0,0,0.45);
      letter-spacing: -0.01em;
    }
    .t-b, .t-h { font-style: italic; letter-spacing: -0.025em; line-height: 1.0; }
    .t-r, .t-m { line-height: 1.25; }
    .ln + .ln { margin-top: 6px; }
"""

CSS_B = """
    .ln { text-shadow: 0 2px 4px rgba(0,0,0,0.7), 0 0 14px rgba(0,0,0,0.45), 0 8px 26px rgba(0,0,0,0.5); line-height: 1.2; }
    .ln + .ln { margin-top: 4px; }
    .t-b, .t-h { text-transform: uppercase; letter-spacing: 0.01em; }
    .t-b { text-shadow: none; margin: 10px 0 8px; }
    .t-h { letter-spacing: -0.01em; }
    .pill {
      display: inline-block; background: #F5EE1F; color: #111111;
      padding: 0.08em 0.32em 0.04em; border-radius: 0.12em;
      box-shadow: 0 10px 28px rgba(0,0,0,0.35);
    }
"""

JS = r"""
    (function () {
      var VARIANT = "__VARIANT__";
      var GROUPS = __GROUPS__;
      var SIZES = __SIZES__;
      var WEIGHT = { r: 400, m: 500, b: 700, h: 700 };
      var tl = gsap.timeline({ paused: true });
      var hf = window.__hyperframes;

      GROUPS.forEach(function (g) {
        g.lines.forEach(function (ln) {
          var el = document.getElementById(ln.id);
          var base = SIZES[ln.tier];
          var size = base;
          // leave headroom for pop scale and pill padding
          var maxW = ln.tier === "h" ? 900 : (ln.tier === "b" ? (VARIANT === "b" ? 820 : 900) : 920);
          if (hf && hf.fitTextFontSize) {
            size = hf.fitTextFontSize(ln.text, {
              fontFamily: "Montserrat", fontWeight: WEIGHT[ln.tier],
              maxWidth: maxW, baseFontSize: base, minFontSize: 36, step: 2,
            }).fontSize;
          }
          el.style.fontSize = size + "px";
        });
      });

      GROUPS.forEach(function (g) {
        var all = [];
        g.lines.forEach(function (ln) {
          var big = ln.tier === "b" || ln.tier === "h";
          ln.words.forEach(function (w) {
            var el = document.getElementById(w[0]);
            var t = Math.max(g.start, w[1] - 0.05);
            all.push(el);
            if (VARIANT === "a") {
              if (big) {
                tl.fromTo(el, { opacity: 0, scale: ln.tier === "h" ? 1.45 : 1.3, y: 10 },
                  { opacity: 1, scale: 1, y: 0, duration: 0.26, ease: "back.out(2.2)" }, t);
              } else {
                tl.fromTo(el, { opacity: 0, y: 16 },
                  { opacity: 1, y: 0, duration: 0.2, ease: "power3.out" }, t);
              }
            } else {
              if (ln.tier === "h") {
                tl.fromTo(el, { opacity: 0, scale: 1.7, y: -20 },
                  { opacity: 1, scale: 1, y: 0, duration: 0.3, ease: "power4.out" }, t);
              } else if (ln.tier === "b") {
                tl.fromTo(el, { opacity: 0, y: 24 },
                  { opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }, t);
              } else {
                // karaoke: whole line pre-shown dim, each word lights up as spoken
                tl.fromTo(el, { opacity: 0 }, { opacity: 0.38, duration: 0.14, ease: "none" }, g.start);
                tl.to(el, { opacity: 1, duration: 0.08, ease: "none" }, t);
              }
            }
          });
          if (VARIANT === "b" && ln.tier === "b") {
            var pill = document.getElementById(ln.id).querySelector(".pill");
            var t0 = Math.max(g.start, ln.words[0][1] - 0.08);
            tl.fromTo(pill, { clipPath: "inset(0% 100% 0% 0%)" },
              { clipPath: "inset(0% 0% 0% 0%)", duration: 0.3, ease: "power3.inOut" }, t0);
          }
        });
        var grp = document.getElementById(g.id);
        tl.to(all, { opacity: 0, duration: 0.12, ease: "power2.in" }, g.end - 0.12);
        tl.set(grp, { opacity: 0, visibility: "hidden" }, g.end);
      });

      window.__timelines["captions"] = tl;
    })();
"""


def main():
    variant, outdir = sys.argv[1], sys.argv[2]
    st = STYLES[variant]
    markup, tl_groups = build(variant)
    css = CSS_COMMON.replace("__ANCHOR__", str(st["anchor"])) + (CSS_A if variant == "a" else CSS_B)
    js = (JS.replace("__VARIANT__", variant)
            .replace("__GROUPS__", json.dumps(tl_groups))
            .replace("__SIZES__", json.dumps(st["sizes"])))
    html = f"""<template>
  <style>{css}  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920" data-layout-allow-overflow>
      {chr(10).join('      ' + m for m in markup).lstrip()}
  </div>
  <script>{js}  </script>
</template>
"""
    os.makedirs(os.path.join(outdir, "compositions"), exist_ok=True)
    with open(os.path.join(outdir, "compositions", "captions.html"), "w") as f:
        f.write(html)
    print("wrote", len(tl_groups), "groups to", outdir)


if __name__ == "__main__":
    main()
