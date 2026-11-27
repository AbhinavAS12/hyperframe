"""Builds compositions/captions.html from the timed caption spec below.

Each group: (start, end, [(style, text, in_time), ...]).
Styles mirror the reference video's caption language:
  s  - small white Montserrat bold lead-in
  si - small white Montserrat italic lead-in
  b  - big white Montserrat ExtraBold
  ec - big cyan Playfair Display bold-italic emphasis
  ey - big yellow Playfair Display bold-italic emphasis
  gc - huge cyan Montserrat Black (venue / company names)
  gg - huge orange->yellow gradient Montserrat Black (places, dates, times)
"""
import html, pathlib

GROUPS = [
    (0.15, 0.95, [("ey", "Namaskara!", 0.15)]),
    (0.95, 2.05, [("s", "Nanu", 0.95), ("ec", "Hemant", 1.29)]),
    (2.10, 4.04, [("s", "I will be at the", 2.10), ("gc", "Ritz-Carlton", 2.61), ("gg", "BENGALURU", 3.46)], "mid"),
    (4.04, 6.40, [("s", "on", 4.04), ("gg", "12th & 13th", 4.08), ("ec", "December", 5.38)]),
    (6.40, 7.56, [("s", "from", 6.40), ("gg", "10 AM – 8 PM", 6.54)]),
    (7.56, 9.60, [("s", "and I would love to", 7.56), ("ec", "catch up", 8.95)]),
    (9.60, 11.94, [("s", "with you over a", 9.60), ("ey", "tea or coffee.", 10.71)]),
    (11.94, 13.09, [("s", "We can have a", 11.94), ("ec", "private,", 12.61)]),
    (13.09, 14.95, [("b", "no-pressure", 13.09), ("ey", "one-on-one discussion", 13.69)]),
    (14.99, 16.20, [("s", "about your", 14.99), ("gg", "UAE", 15.47), ("b", "portfolio", 15.65)]),
    (16.20, 18.25, [("s", "and", 16.20), ("b", "business setup", 16.38), ("ec", "opportunities", 17.34)], "mid"),
    (18.25, 19.20, [("s", "in", 18.25), ("gg", "DUBAI", 18.39)], "mid"),
    (19.20, 20.95, [("s", "and what to expect in", 19.20), ("gg", "2027", 20.03)]),
    (21.00, 22.95, [("s", "whether it makes sense", 21.00), ("b", "to exit", 22.24)]),
    (22.95, 24.46, [("si", "or", 23.06), ("ey", "double down.", 23.52)]),
    (24.46, 26.10, [("s", "Let me know", 24.46), ("ec", "what time suits you", 25.00)]),
    (26.10, 27.22, [("s", "and I'll", 26.10), ("ey", "reserve a slot", 26.69)]),
    (27.22, 29.40, [("s", "it would be great to", 27.22), ("ec", "catch up with you!", 28.06)]),
]

DURATION = 29.46

groups_html, lines_js = [], []
for gi, (start, end, lines, *opt) in enumerate(GROUPS):
    mid = " mid" if opt and opt[0] == "mid" else ""
    rows = []
    for li, (style, text, t) in enumerate(lines):
        lid = f"c{gi}-{li}"
        rows.append(f'        <div id="{lid}" class="ln {style}"><span>{html.escape(text)}</span></div>')
        lines_js.append(f'    ["{lid}", "{style}", {t - start:.2f}],')
    groups_html.append(
        f'      <div id="cg{gi}" class="cg clip" data-start="{start:.2f}" data-duration="{end - start:.2f}" data-track-index="0">\n'
        f'       <div id="cg{gi}-in" class="cg-in{mid}">\n' + "\n".join(rows) + "\n       </div>\n      </div>"
    )

group_js = ",\n".join(f'    ["cg{gi}", {s:.2f}, {e:.2f}]' for gi, (s, e, *_) in enumerate(GROUPS))

doc = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: visible; }}
    .cg {{ position: absolute; left: 0; right: 0; top: 0; bottom: 0; overflow: visible; }}
    .cg-in {{
      position: absolute; left: 0; right: 0; bottom: 690px;
      display: flex; flex-direction: column; align-items: center;
      text-align: center; overflow: visible; padding-right: 36px;
      filter: drop-shadow(0 4px 14px rgba(0, 0, 0, 0.55)) drop-shadow(0 1px 2px rgba(0, 0, 0, 0.6));
    }}
    .cg-in.mid {{ top: 0; bottom: 0; justify-content: center; }}
    .ln {{ display: block; white-space: nowrap; line-height: 0.98; color: #ffffff; }}
    .ln span {{ display: inline-block; }}
    .s  {{ font-family: "Montserrat"; font-weight: 700; font-size: 50px; letter-spacing: -0.01em; margin-bottom: 4px; }}
    .si {{ font-family: "Montserrat"; font-weight: 600; font-style: italic; font-size: 50px; margin-bottom: 4px; }}
    .b  {{ font-family: "Montserrat"; font-weight: 800; font-size: 100px; letter-spacing: -0.02em; }}
    .ec, .ey {{ font-family: "Playfair Display"; font-weight: 800; font-style: italic; font-size: 112px; letter-spacing: -0.01em; line-height: 1.02; }}
    .ec, .ey {{ margin-top: 8px; }}
    .b, .gc, .gg {{ margin-top: 4px; }}
    .ec {{ color: #2ef3f0; }}
    .ey {{ color: #f0f53a; }}
    .gc {{ font-family: "Montserrat"; font-weight: 900; font-size: 128px; letter-spacing: -0.03em; color: #2ef3f0; }}
    .gg {{ font-family: "Montserrat"; font-weight: 900; font-size: 126px; letter-spacing: -0.03em; }}
    .gg span {{
      background: linear-gradient(90deg, #f7a42b 0%, #f4c928 45%, #e9f43a 100%);
      -webkit-background-clip: text; background-clip: text; color: transparent;
      padding: 0 0.04em;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(groups_html)}
  </div>
  <script>
    const GROUPS = [
{group_js}
    ];
    const LINES = [
{chr(10).join(lines_js)}
    ];
    const FONT = {{
      s: ["Montserrat", 700, 50], si: ["Montserrat", 600, 50], b: ["Montserrat", 800, 100],
      ec: ["Playfair Display", 800, 112], ey: ["Playfair Display", 800, 112],
      gc: ["Montserrat", 900, 128], gg: ["Montserrat", 900, 126],
    }};
    const hf = window.__hyperframes;
    LINES.forEach(([id, style]) => {{
      const el = document.getElementById(id);
      const [fontFamily, fontWeight, base] = FONT[style];
      if (hf && hf.fitTextFontSize) {{
        const r = hf.fitTextFontSize(el.textContent, {{ fontFamily, fontWeight, maxWidth: 780, baseFontSize: base, minFontSize: 40, step: 2 }});
        el.style.fontSize = Math.min(base, r.fontSize) + "px";
      }}
    }});

    const tl = gsap.timeline({{ paused: true }});
    const groupStart = Object.fromEntries(GROUPS.map(([id, s]) => [id, s]));
    LINES.forEach(([id, style, t]) => {{
      const gid = id.split("-")[0].replace("c", "cg");
      const at = groupStart[gid] + t;
      const big = style !== "s" && style !== "si";
      tl.fromTo("#" + id,
        {{ opacity: 0, y: big ? 46 : 22, scale: big ? 0.82 : 0.94 }},
        {{ opacity: 1, y: 0, scale: 1, duration: big ? 0.32 : 0.22, ease: big ? "back.out(1.7)" : "power3.out" }},
        at);
    }});
    GROUPS.forEach(([id, s, e]) => {{
      const inner = "#" + id + "-in";
      tl.fromTo(inner, {{ opacity: 1 }}, {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, e - 0.14);
      tl.set(inner, {{ opacity: 0, visibility: "hidden" }}, e);
    }});
    tl.set({{}}, {{}}, {DURATION});
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
out = pathlib.Path(__file__).resolve().parent.parent / "compositions" / "captions.html"
out.parent.mkdir(exist_ok=True)
out.write_text(doc)
print("wrote", out, len(GROUPS), "groups")
