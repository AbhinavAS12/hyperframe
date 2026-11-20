#!/usr/bin/env python3
"""Option C: Option A's kinetic look on the full, uncropped original footage,
with Higgsfield b-roll replacing most of the text animations.

  python3 caio/build_c.py      -> writes caio/option-c

Needs:
  shared/caio-full.mp4      the clean original (no burned subtitles), 1080x1920
  shared/broll/bNN.mp4      the 13 Higgsfield clips, numbered as in BROLL below
"""
import json, os, shutil
import build as B

HERE = B.HERE
SHARED = B.SHARED
W, H, DUR = B.W, B.H, B.DUR
S = dict(B.STYLE["a"], name="Option C - Kinetic + B-roll")
OPT = "a"  # reuse Option A styling everywhere
B.EMPH.update({"sete", "escritórios"})

# (clip file, start, end, label icon, label text)
BROLL = [
    ("b00", 12.55, 16.45, "chart", "Quem investe antes, <b>valoriza mais</b>"),
    ("b01", 24.30, 28.35, "globe", "Brasil <b>→</b> Emirados"),
    ("b02", 31.30, 35.00, "dollar", "Moeda atrelada ao <b>dólar</b> desde 1997"),
    ("b03", 36.95, 40.30, "house", "Aluguel <b>acima da média</b>"),
    ("b04", 40.35, 45.20, "percent", "<b>0% imposto</b> sobre renda e lucro"),
    ("b05", 45.20, 48.45, "people", "População em <b>ritmo recorde</b>"),
    ("b06", 49.55, 53.05, "shield", "Um dos países <b>mais seguros</b>"),
    ("b07", 55.25, 58.90, "key", "Propriedade <b>plena</b> e registro oficial"),
    ("b08", 59.10, 62.95, "lock", "Conta garantia <b>fiscalizada</b>"),
    ("b09", 64.70, 67.55, "swap", "Mercado <b>líquido</b>"),
    ("b10", 70.10, 73.75, "family", "Visto de <b>10 anos</b> para a família"),
    ("b11", 76.15, 79.40, "globe", "Consultoria <b>global</b> de investimentos"),
    ("b12", 87.30, 91.05, "chart", "Mais de <b>AED 20 bilhões</b> em transações"),
]
RATE = {"b04": ' data-playback-rate="1.04"'}
# image backgrounds behind the text-only cards
BG = {"g-question": ("bg-question.jpg", 1.85), "g-brand": ("bg-brand.jpg", 2.35)}
CUTS = [("g-chart", 6.0, 12.45), ("g-question", 29.45, 31.3), ("g-brand", 73.8, 76.15)]
OVERS = [("o-name", 16.55, 24.25), ("o-stats", 79.45, 87.25), ("o-cta", 93.9, DUR)]
# punch-ins on the talking-head stretches only
PUNCH = [(0, 1.0), (3.77, 1.12), (16.45, 1.0), (21.8, 1.1), (28.35, 1.0), (35.0, 1.1),
         (48.45, 1.1), (53.05, 1.0), (62.95, 1.1), (67.55, 1.0),
         (79.4, 1.08), (82.33, 1.0), (84.1, 1.1), (91.05, 1.0), (94.13, 1.1), (98.23, 1.0)]


def with_bg(cid, html_):
    img, dur = BG[cid]
    layer = (f'<img id="{cid}-bgimg" src="assets/{img}" alt="" style="position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover;">'
             f'<div id="{cid}-bgdim" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,8,14,.55) 0%,rgba(4,8,14,.35) 45%,rgba(4,8,14,.75) 100%);"></div>')
    i = html_.index('data-height="1920">', html_.index('<div id="root"')) + len('data-height="1920">')
    html_ = html_[:i] + "\n        " + layer + html_[i:]
    anim = f'tl.fromTo("#{cid}-bgimg",{{scale:1.1}},{{scale:1.0,duration:{dur},ease:"power1.out"}},0);\n          window.__timelines'
    return html_.replace("window.__timelines", anim, 1)


def labels_scene():
    cid = "o-labels"
    els, js = [], []
    for i, (f, a, b, ic, txt) in enumerate(BROLL):
        el = f"lb{i}"
        els.append(f'        <div id="{el}" class="clip lab" data-start="{a + 0.15:.2f}" data-duration="{b - a - 0.2:.2f}" data-track-index="{i % 2}"><div class="li">{B.icon(ic, 46)}<span>{txt}</span></div></div>')
        js.append(f'tl.fromTo("#{el} .li",{{opacity:0,y:-30,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.4,ease:"back.out(1.7)"}},{a + 0.15:.2f});')
        js.append(f'tl.to("#{el} .li",{{opacity:0,y:-14,duration:0.18,ease:"power2.in"}},{b - 0.24:.2f});')
    css = f"""
        #root .lab {{ position:absolute; left:0; right:0; top:300px; display:flex; justify-content:center; }}
        #root .li {{ display:flex; align-items:center; gap:14px; padding:18px 30px; border-radius:60px; background:#fff; color:#0b0f16;
                    font:700 40px/1.15 "Montserrat", sans-serif; box-shadow:0 14px 40px rgba(0,0,0,.35); max-width:900px; }}
        #root .li svg {{ flex:none; stroke:#0aa5c6; }}
        #root .li b {{ color:#0aa5c6; font-weight:900; }}
    """
    return B.scene(cid, "\n".join(els), css, "\n".join("          " + j for j in js), False, S)


def o_stats_c():
    cards = [
        (79.45, 82.28, "news", "Reconhecida pela <b>imprensa internacional</b>"),
        (82.33, 84.05, "pin", "<b>Sete escritórios</b> no mundo"),
        (84.1, 87.2, "badge", "Registrada no <b>regulador imobiliário</b> de Dubai"),
    ]
    return B.overlay_cards("o-stats", S, OPT, 79.45, cards)


def sfx():
    s = [("whoosh-short", a - 0.1, 0.57, 0.7) for _, a, *_ in BROLL]
    s += [("whoosh", a - 0.12, 0.57, 1.0) for _, a, _ in CUTS]
    s += [("impact-bass-1", 8.7, 2.1, 0.7), ("pop", 6.1, 0.72, 0.6), ("pop", 9.6, 0.72, 0.6),
          ("click-soft", 16.6, 0.37, 1.0), ("click-soft", 79.45, 0.37, 1.0), ("click-soft", 82.33, 0.37, 1.0),
          ("click-soft", 84.1, 0.37, 1.0), ("sparkle", 74.2, 1.8, 0.7), ("click", 96.3, 0.3, 1.0),
          ("chime", 96.35, 2.5, 0.6)]
    return sorted(s, key=lambda x: x[1])


def root():
    hosts = []
    for cid, a, b in CUTS:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="3" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:5"></div>')
    for cid, a, b in OVERS + [("o-labels", 0, DUR)]:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="4" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:6"></div>')
    hosts.append(f'      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="5" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:9"></div>')
    brolls, bjs = [], []
    for i, (f, a, b, *_r) in enumerate(BROLL):
        d = b - a
        brolls.append(f'      <div id="bw{i}" class="bw"><video id="br{i}" class="clip" src="assets/broll/{f}.mp4" muted playsinline data-start="{a:.2f}" data-duration="{d:.2f}" data-media-start="0"{RATE.get(f, '')} data-track-index="2"></video></div>')
        bjs.append(f'      tl.fromTo("#bw{i}", {{ scale:1.12 }}, {{ scale:1.0, duration:{d:.2f}, ease:"power1.out" }}, {a:.2f});')
    aud = [f'      <audio id="sfx{i}" src="assets/sfx/{f}.mp3" data-start="{t:.2f}" data-duration="{d}" data-track-index="{11 + (i % 2)}" data-volume="{v * S["sfx_vol"]:.2f}"></audio>'
           for i, (f, t, d, v) in enumerate(sfx())]
    cam = "\n".join(f'      tl.set("#cam", {{ scale:{s} }}, {t});' for t, s in PUNCH)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8">
    <title>Caio Rezende - {S['name']}</title>
    <script src="assets/gsap.min.js"></script>
    <script src="assets/three.min.js"></script>
    <script src="assets/fx.js"></script>
    <style>
      body {{ margin:0; background:#000; }}
      #root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#000; }}
      #root > div[data-composition-src] {{ position:absolute; inset:0; }}
      #cam {{ position:absolute; inset:0; transform-origin:50% 26%; z-index:1; }}
      #talk {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; }}
      .bw {{ position:absolute; inset:0; z-index:3; overflow:hidden; transform-origin:50% 50%; }}
      .bw video {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="root" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="cam">
        <video id="talk" class="clip" src="assets/caio-full.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></video>
      </div>
      <div id="grade" style="position:absolute;inset:0;z-index:4;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,0) 20%,rgba(0,0,0,0) 50%,rgba(0,0,0,.45) 100%);"></div>
{chr(10).join(brolls)}
{chr(10).join(hosts)}
      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="0.16" data-fade-in="0.5" data-fade-out="2.5"></audio>
{chr(10).join(aud)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{cam}
{chr(10).join(bjs)}
      window.__timelines["root"] = tl;
    </script>
  </body>
</html>
"""


def main():
    out = os.path.join(HERE, "option-c")
    comp, assets = os.path.join(out, "compositions"), os.path.join(out, "assets")
    for d in (comp, os.path.join(assets, "sfx"), os.path.join(assets, "broll")):
        os.makedirs(d, exist_ok=True)
    src_full = os.path.join(SHARED, "caio-full.mp4")
    dst_full = os.path.join(assets, "caio-full.mp4")
    if os.path.exists(src_full) and (not os.path.exists(dst_full) or os.path.getsize(dst_full) != os.path.getsize(src_full)):
        shutil.copy(src_full, dst_full)
    bdir = os.path.join(SHARED, "broll")
    if os.path.isdir(bdir):
        for f in os.listdir(bdir):
            shutil.copy(os.path.join(bdir, f), os.path.join(assets, "broll", f))
    shutil.copy(os.path.join(SHARED, "three.min.js"), assets)
    shutil.copy(os.path.join(SHARED, "music-c.mp3"), os.path.join(assets, "music.mp3"))
    for img in ("bg-question.jpg", "bg-brand.jpg"):
        shutil.copy(os.path.join(SHARED, img), os.path.join(assets, img))
    shutil.copy(os.path.join(HERE, "..", "vendor", "gsap.min.js"), os.path.join(assets, "gsap.min.js"))
    for f in os.listdir(SHARED):
        if f.endswith(".mp3") and not f.startswith("music"):
            shutil.copy(os.path.join(SHARED, f), os.path.join(assets, "sfx", f))
    open(os.path.join(assets, "fx.js"), "w").write(B.FX_JS)
    files = {
        "captions.html": B.build_captions(S, OPT),
        "g-chart.html": B.g_chart(S, OPT, 6.45),
        "g-question.html": with_bg("g-question", B.g_question(S, OPT, 1.85)),
        "g-brand.html": with_bg("g-brand", B.g_brand(S, OPT, 2.35)),
        "o-name.html": B.o_name(S, OPT, 16.55, 24.25),
        "o-stats.html": o_stats_c(),
        "o-cta.html": B.o_cta(S, OPT, 93.9, DUR),
        "o-labels.html": labels_scene(),
    }
    for k, v in files.items():
        open(os.path.join(comp, k), "w", encoding="utf-8").write(v)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(root())
    json.dump({"id": "caio-option-c", "name": S["name"]}, open(os.path.join(out, "meta.json"), "w"), indent=2)
    shutil.copy(os.path.join(HERE, "..", "hyperframes.json"), os.path.join(out, "hyperframes.json"))
    json.dump({"name": "caio-option-c", "private": True, "type": "module", "scripts": {
        "dev": "npx --yes hyperframes@0.8.137 preview", "check": "npx --yes hyperframes@0.8.137 check",
        "render": "npx --yes hyperframes@0.8.137 render"}}, open(os.path.join(out, "package.json"), "w"), indent=2)
    print("wrote", out)


if __name__ == "__main__":
    main()
