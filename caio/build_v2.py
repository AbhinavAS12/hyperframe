#!/usr/bin/env python3
"""Caio Video 2 in the Option C format (kinetic captions, Higgsfield b-roll with
label chips, image-backed cards, funky music bed, Allegiance outro).

  python3 caio/build_v2.py    -> writes caio/video2

Captions come from shared/v2_words.json (ElevenLabs Scribe word timings, with
"Legions" -> Allegiance and "Hera" -> RERA corrected).
"""
import json, os, shutil
import build as B

HERE, SHARED = B.HERE, B.SHARED
W, H = B.W, B.H
TALK = 52.1                     # spoken video length
OUTRO_AT, OUTRO_LEN = 51.95, 5.15
TOTAL = round(OUTRO_AT + OUTRO_LEN, 2)
S = dict(B.STYLE["a"], name="Video 2 - Kinetic + B-roll")
OPT = "a"

data = json.load(open(os.path.join(SHARED, "v2_words.json"), encoding="utf-8"))
B.WORDS[:] = data["words"]
B.SEGS[:] = data["segments"]
B.DUR = TALK
B.EMPH.discard("dez"); B.EMPH.discard("10"); B.EMPH.update({"imobiliário", "compromisso", "rera", "mundo", "allegiance", "sete", "escritórios"})

# (clip, start, end, media_start, icon, label)
BROLL = [
    ("b01", 19.65, 22.95, 0.6, "globe", "Brasil <b>→</b> Emirados"),
    ("b02", 23.45, 24.90, 0.8, "dollar", "Moeda atrelada ao <b>dólar</b>"),
    ("b03", 24.92, 26.88, 0.5, "house", "Aluguel <b>acima da média</b>"),
    ("b04", 26.90, 30.20, 1.7, "percent", "<b>Sem imposto</b> sobre aluguel e renda"),
    ("b06", 30.22, 32.55, 0.4, "shield", "Um dos países <b>mais seguros</b>"),
    ("b10", 32.58, 36.10, 0.5, "family", "Visto de <b>10 anos</b> para a família"),
    ("b11", 39.25, 41.90, 0.5, "pin", "<b>Sete escritórios</b> pelo mundo"),
]
CUTS = [("g-chart", 7.6, 15.15), ("g-brand", 37.65, 39.25)]
BG = {"g-chart": ("bg-chart.jpg", 7.55), "g-brand": ("bg-brand.jpg", 1.6)}
PUNCH = [(0, 1.0), (2.85, 1.12), (5.5, 1.0), (15.15, 1.0), (17.6, 1.1), (36.1, 1.0),
         (41.9, 1.1), (44.4, 1.0), (45.3, 1.08), (48.85, 1.0)]


def with_bg(cid, html_):
    img, dur = BG[cid]
    layer = (f'<img id="{cid}-bgimg" src="assets/{img}" alt="" style="position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover;">'
             f'<div id="{cid}-bgdim" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,8,14,.55) 0%,rgba(4,8,14,.35) 45%,rgba(4,8,14,.75) 100%);"></div>')
    i = html_.index('data-height="1920">', html_.index('<div id="root"')) + len('data-height="1920">')
    html_ = html_[:i] + "\n        " + layer + html_[i:]
    anim = f'tl.fromTo("#{cid}-bgimg",{{scale:1.1}},{{scale:1.0,duration:{dur},ease:"power1.out"}},0);\n          window.__timelines'
    return html_.replace("window.__timelines", anim, 1)


def labels_scene():
    els, js = [], []
    for i, (f, a, b, _m, ic, txt) in enumerate(BROLL):
        el = f"lb{i}"
        els.append(f'        <div id="{el}" class="clip lab" data-start="{a + 0.12:.2f}" data-duration="{b - a - 0.17:.2f}" data-track-index="{i % 2}"><div class="li">{B.icon(ic, 46)}<span>{txt}</span></div></div>')
        js.append(f'tl.fromTo("#{el} .li",{{opacity:0,y:-30,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.35,ease:"back.out(1.7)"}},{a + 0.12:.2f});')
        js.append(f'tl.to("#{el} .li",{{opacity:0,y:-14,duration:0.16,ease:"power2.in"}},{b - 0.2:.2f});')
    css = """
        #root .lab { position:absolute; left:0; right:0; top:300px; display:flex; justify-content:center; }
        #root .li { display:flex; align-items:center; gap:14px; padding:18px 30px; border-radius:60px; background:#fff; color:#0b0f16;
                    font:700 40px/1.15 "Montserrat", sans-serif; box-shadow:0 14px 40px rgba(0,0,0,.35); max-width:900px; }
        #root .li svg { flex:none; stroke:#0aa5c6; }
        #root .li b { color:#0aa5c6; font-weight:900; }
    """
    return B.scene("o-labels", "\n".join(els), css, "\n".join("          " + j for j in js), False, S)


def o_name():
    base, end = 15.4, 19.6
    els = f"""        <div id="nm-card" class="clip nm" data-start="0.05" data-duration="{end - base - 0.05:.2f}" data-track-index="0">
          <div id="nm-in" class="nmi">
            <div class="bar"></div>
            <div>
              <div class="n">Caio Rezende</div>
              <div id="nm-r1" class="r">Advogado · Consultor imobiliário</div>
              <div class="chips"><span id="nm-c1">{B.icon('people', 34)} Assessoria a investidores brasileiros</span></div>
            </div>
          </div>
        </div>"""
    js = f"""
          tl.fromTo("#nm-in", {{ opacity:0, x:-60 }}, {{ opacity:1, x:0, duration:0.5, ease:"expo.out" }}, 0.05);
          tl.fromTo("#nm-in .bar", {{ scaleY:0 }}, {{ scaleY:1, duration:0.5, ease:"expo.out" }}, 0.1);
          tl.fromTo("#nm-r1", {{ opacity:0, y:10 }}, {{ opacity:1, y:0, duration:0.35 }}, {16.94 - base:.2f});
          tl.fromTo("#nm-c1", {{ opacity:0, scale:0.7 }}, {{ opacity:1, scale:1, duration:0.4, ease:"back.out(2)" }}, {18.98 - base:.2f});
          tl.to("#nm-in", {{ opacity:0, x:-40, duration:0.22, ease:"power2.in" }}, {end - base - 0.26:.2f});
    """
    css = f"""
        #root .nm {{ position:absolute; left:70px; right:70px; top:{B.OVER_TOP}px; }}
        #root .nmi {{ display:flex; gap:22px; padding:24px 30px; border-radius:24px; background:{S['card']}; border:1.5px solid {S['line']};
                     box-shadow:0 14px 40px rgba(0,0,0,.35); }}
        #root .bar {{ width:8px; border-radius:4px; background:{S['accent']}; transform-origin:50% 0; }}
        #root .n {{ font:800 58px/1.05 "{S['head']}", serif; color:{S['ink']}; }}
        #root .r {{ font:600 34px "{S['body']}"; color:{S['accent']}; margin-top:6px; }}
        #root .chips {{ display:flex; gap:14px; margin-top:14px; flex-wrap:wrap; }}
        #root .chips span {{ display:inline-flex; align-items:center; gap:8px; padding:8px 18px; border-radius:40px; background:rgba(255,255,255,.08);
                            border:1px solid {S['line']}; font:600 28px "{S['body']}"; color:{S['ink']}; }}
        #root .chips svg {{ stroke:{S['accent']}; }}
    """
    return B.scene("o-name", els, css, js, False, S)


def o_stats():
    return B.overlay_cards("o-stats", S, OPT, 42.1, [
        (42.1, 45.2, "badge", "Registrada na <b>RERA</b><small>Órgão regulador imobiliário de Dubai</small>"),
    ])


def o_cta():
    base = 45.3
    d = TALK - base
    els = f"""        <div id="cta-card" class="clip cta" data-start="0.15" data-duration="{d - 0.15:.2f}" data-track-index="0">
          <div id="cta-in" class="ctai">
            <div class="ttl">{B.icon('cal', 48, S['accent'])} Consulta inicial <b>sem compromisso</b></div>
            <div id="cta-btn" class="btn">Agende com o Caio</div>
            <div id="cta-sub" class="sub">Invista nos Emirados com a <b>Allegiance</b></div>
          </div>
        </div>"""
    t_tap = 47.1 - base
    js = f"""
          tl.fromTo("#cta-in", {{ opacity:0, y:60, scale:0.9 }}, {{ opacity:1, y:0, scale:1, duration:0.55, ease:"expo.out" }}, 0.15);
          tl.fromTo("#cta-btn", {{ scale:1 }}, {{ scale:0.92, duration:0.1, ease:"power2.in" }}, {t_tap:.2f});
          tl.to("#cta-btn", {{ scale:1, duration:0.35, ease:"back.out(3)" }}, {t_tap + 0.1:.2f});
          tl.fromTo("#cta-sub", {{ opacity:0 }}, {{ opacity:1, duration:0.4 }}, {48.9 - base:.2f});
    """
    css = f"""
        #root .cta {{ position:absolute; left:80px; right:80px; top:{B.OVER_TOP}px; }}
        #root .ctai {{ padding:28px 32px; border-radius:28px; background:{S['card']}; border:1.5px solid {S['line']}; text-align:center; box-shadow:0 14px 40px rgba(0,0,0,.4); }}
        #root .ttl {{ display:flex; gap:14px; align-items:center; justify-content:center; font:700 42px "{S['body']}"; }}
        #root .ttl b {{ color:{S['accent']}; }}
        #root .btn {{ margin:20px auto 0; width:600px; padding:22px 0; border-radius:60px; background:{S['accent']}; color:#06121a; font:900 44px "{S['body']}"; }}
        #root .sub {{ margin-top:18px; font:500 32px "{S['body']}"; color:{S['muted']}; }}
        #root .sub b {{ color:{S['ink']}; }}
    """
    return B.scene("o-cta", els, css, js, False, S)


OVERS = [("o-name", 15.4, 19.6), ("o-stats", 42.1, 45.2), ("o-cta", 45.3, TALK)]


def sfx():
    s = [("whoosh-short", a - 0.1, 0.57, 0.7) for _, a, *_ in BROLL]
    s += [("whoosh", a - 0.12, 0.57, 1.0) for _, a, _ in CUTS]
    s += [("pop", 7.7, 0.72, 0.6), ("impact-bass-1", 7.85, 2.1, 0.7), ("pop", 12.75, 0.72, 0.6),
          ("click-soft", 15.45, 0.37, 1.0), ("click-soft", 42.15, 0.37, 1.0), ("sparkle", 37.9, 1.8, 0.7),
          ("click", 47.1, 0.3, 1.0), ("chime", 47.15, 2.5, 0.6), ("sparkle", OUTRO_AT + 0.05, 1.8, 0.8)]
    return sorted(s, key=lambda x: x[1])


def root():
    hosts = []
    for cid, a, b in CUTS:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="3" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:5"></div>')
    for cid, a, b in OVERS + [("o-labels", 0, TALK)]:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="4" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:6"></div>')
    hosts.append(f'      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TALK}" data-track-index="5" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:9"></div>')
    brolls, bjs = [], []
    for i, (f, a, b, m, *_r) in enumerate(BROLL):
        d = b - a
        brolls.append(f'      <div id="bw{i}" class="bw"><video id="br{i}" class="clip" src="assets/broll/{f}.mp4" muted playsinline data-start="{a:.2f}" data-duration="{d:.2f}" data-media-start="{m}" data-track-index="2"></video></div>')
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
    <div id="root" data-composition-id="root" data-start="0" data-width="{W}" data-height="{H}" data-duration="{TOTAL}">
      <div id="cam">
        <video id="talk" class="clip" src="assets/caio-v2.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{TALK}" data-track-index="1" data-volume="1"></video>
      </div>
      <div id="grade" style="position:absolute;inset:0;z-index:4;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,0) 20%,rgba(0,0,0,0) 50%,rgba(0,0,0,.45) 100%);"></div>
{chr(10).join(brolls)}
{chr(10).join(hosts)}
      <div id="ow" class="bw" style="z-index:12"><video id="outro" class="clip" src="assets/outro.mp4" muted playsinline data-start="{OUTRO_AT}" data-duration="{OUTRO_LEN}" data-media-start="0" data-track-index="6"></video></div>
      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="0.16" data-fade-in="0.5" data-fade-out="3"></audio>
{chr(10).join(aud)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{cam}
{chr(10).join(bjs)}
      tl.fromTo("#ow", {{ opacity:0, scale:1.06 }}, {{ opacity:1, scale:1, duration:0.4, ease:"power2.out" }}, {OUTRO_AT});
      window.__timelines["root"] = tl;
    </script>
  </body>
</html>
"""


def main():
    out = os.path.join(HERE, "video2")
    comp, assets = os.path.join(out, "compositions"), os.path.join(out, "assets")
    for d in (comp, os.path.join(assets, "sfx"), os.path.join(assets, "broll")):
        os.makedirs(d, exist_ok=True)

    def cp(src, dst):
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
            shutil.copy(src, dst)
    cp(os.path.join(SHARED, "caio-v2.mp4"), os.path.join(assets, "caio-v2.mp4"))
    for f, *_r in BROLL:
        cp(os.path.join(SHARED, "broll", f + ".mp4"), os.path.join(assets, "broll", f + ".mp4"))
    cp(os.path.join(SHARED, "outro-1080.mp4"), os.path.join(assets, "outro.mp4"))
    cp(os.path.join(SHARED, "music-c.mp3"), os.path.join(assets, "music.mp3"))
    for img in ("bg-chart.jpg", "bg-brand.jpg"):
        cp(os.path.join(SHARED, img), os.path.join(assets, img))
    shutil.copy(os.path.join(HERE, "..", "vendor", "gsap.min.js"), os.path.join(assets, "gsap.min.js"))
    for f in os.listdir(SHARED):
        if f.endswith(".mp3") and not f.startswith("music"):
            cp(os.path.join(SHARED, f), os.path.join(assets, "sfx", f))
    # chart: Brasil already on screen, Emirados lands on "7,7%", Mundo on "3,2%"
    chart = B.g_chart(S, OPT, 7.55, times=(0.05, 12.72 - 7.6, 7.82 - 7.6), badge_t=1.4)
    files = {
        "captions.html": B.build_captions(S, OPT),
        "g-chart.html": with_bg("g-chart", chart),
        "g-brand.html": with_bg("g-brand", B.g_brand(S, OPT, 1.6)),
        "o-name.html": o_name(),
        "o-stats.html": o_stats(),
        "o-cta.html": o_cta(),
        "o-labels.html": labels_scene(),
    }
    for k, v in files.items():
        open(os.path.join(comp, k), "w", encoding="utf-8").write(v)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(root())
    json.dump({"id": "caio-video-2", "name": S["name"]}, open(os.path.join(out, "meta.json"), "w"), indent=2)
    shutil.copy(os.path.join(HERE, "..", "hyperframes.json"), os.path.join(out, "hyperframes.json"))
    json.dump({"name": "caio-video-2", "private": True, "type": "module", "scripts": {
        "dev": "npx --yes hyperframes@0.8.137 preview", "check": "npx --yes hyperframes@0.8.137 check",
        "render": "npx --yes hyperframes@0.8.137 render"}}, open(os.path.join(out, "package.json"), "w"), indent=2)
    print("wrote", out)


if __name__ == "__main__":
    main()
