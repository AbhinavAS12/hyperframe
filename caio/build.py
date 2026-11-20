#!/usr/bin/env python3
"""Generates the two HyperFrames edit options for the Caio Rezende reel.

  python3 caio/build.py            -> writes caio/option-a and caio/option-b

Option A "Kinetic"  : reference-style word-pop captions (white + cyan keyword),
                      dark full-screen cutaways, hard punch-ins.
Option B "Prestige" : navy/gold, karaoke subtitle pills, Three.js gold particle
                      cutaways with a circular PiP of Caio, smooth push-ins.
Both share the word timings in shared/words.json (from the client SRT, PT-BR).
"""
import json, os, re, shutil, html

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.join(HERE, "shared")
DUR = 101.1
W, H = 1080, 1920

data = json.load(open(os.path.join(SHARED, "words.json"), encoding="utf-8"))
WORDS, SEGS = data["words"], data["segments"]

# ---------------------------------------------------------------- styles ----
STYLE = {
    "a": dict(
        name="Option A - Kinetic",
        bg="#07090d", ink="#ffffff", accent="#2fd3f5", accent2="#7cf0ff",
        muted="rgba(255,255,255,.62)", card="rgba(12,16,24,.82)",
        line="rgba(47,211,245,.35)", head="Montserrat", body="Montserrat",
        globe="globe-a.png", sfx_vol=0.45,
    ),
    "b": dict(
        name="Option B - Prestige",
        bg="#081024", ink="#f7f3ea", accent="#d4af6a", accent2="#f3d9a4",
        muted="rgba(247,243,234,.66)", card="rgba(10,20,44,.80)",
        line="rgba(212,175,106,.45)", head="Playfair Display", body="Inter",
        globe="globe-b.png", sfx_vol=0.38,
    ),
}

# ------------------------------------------------------------- timeline ----
# Full-screen cutaways (speaker audio keeps playing underneath)
CUTS = [
    ("g-chart", 6.0, 12.45),
    ("g-globe", 24.3, 29.45),
    ("g-question", 29.45, 31.3),
    ("g-list1", 31.3, 44.75),
    ("g-list2", 55.2, 64.5),
    ("g-brand", 73.8, 76.15),
]
# Overlays on the talking head
OVERS = [
    ("o-name", 16.55, 24.25),
    ("o-chips1", 45.0, 55.15),
    ("o-chips2", 64.55, 73.75),
    ("o-stats", 76.15, 91.3),
    ("o-cta", 93.9, DUR),
]
# Talking-head framing: (time, scale)
PUNCH = [(0, 1.0), (3.77, 1.13), (12.45, 1.0), (16.67, 1.1), (21.8, 1.0),
         (29.45, 1.0), (44.75, 1.12), (49.57, 1.0), (64.5, 1.1), (70.13, 1.0),
         (76.15, 1.08), (82.33, 1.0), (87.33, 1.12), (91.37, 1.0), (94.13, 1.1),
         (98.23, 1.0)]

# ------------------------------------------------------------------ icons ----
ICON = {
    "dollar": '<circle cx="24" cy="24" r="19"/><path d="M30 16.5c-1.4-1.8-3.6-2.6-6-2.6-3.4 0-6 1.8-6 4.6 0 6.6 12.4 3.6 12.4 10.4 0 2.9-2.8 4.8-6.4 4.8-2.7 0-5-1-6.4-2.9M24 10v4M24 34v4"/>',
    "house": '<path d="M7 22 24 8l17 14"/><path d="M12 19v20h24V19"/><path d="M20 39V28h8v11"/>',
    "percent": '<path d="M12 36 36 12"/><circle cx="14" cy="14" r="5"/><circle cx="34" cy="34" r="5"/>',
    "people": '<circle cx="17" cy="16" r="6"/><circle cx="33" cy="18" r="5"/><path d="M5 38c1-7 6-11 12-11s11 4 12 11"/><path d="M29 28c5 0 13 3 14 10"/>',
    "shield": '<path d="M24 6 39 12v11c0 10-6.5 16-15 19C15.5 39 9 33 9 23V12z"/><path d="m17 24 5 5 9-10"/>',
    "key": '<circle cx="16" cy="30" r="8"/><path d="M22 24 39 7M33 13l5 5M28 18l4 4"/>',
    "doc": '<path d="M12 6h17l9 9v27H12z"/><path d="M29 6v9h9M18 24h14M18 31h14"/>',
    "lock": '<rect x="10" y="21" width="28" height="20" rx="3"/><path d="M16 21v-6a8 8 0 0 1 16 0v6M24 29v5"/>',
    "swap": '<path d="M8 17h30l-7-7M40 31H10l7 7"/>',
    "passport": '<rect x="11" y="6" width="26" height="36" rx="3"/><circle cx="24" cy="21" r="6"/><path d="M17 33h14"/>',
    "globe": '<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6c6 6 6 30 0 36M24 6c-6 6-6 30 0 36"/>',
    "news": '<rect x="6" y="9" width="30" height="30" rx="2"/><path d="M36 17h6v18a4 4 0 0 1-8 0M12 16h18M12 23h18M12 30h11"/>',
    "pin": '<path d="M24 43s14-13 14-24a14 14 0 0 0-28 0c0 11 14 24 14 24z"/><circle cx="24" cy="19" r="5"/>',
    "badge": '<circle cx="24" cy="19" r="12"/><path d="m17 29-4 13 11-5 11 5-4-13"/><path d="m19 19 4 4 7-8"/>',
    "chart": '<path d="M7 40h34"/><path d="m9 32 9-9 7 6 14-15"/><path d="M33 14h6v6"/>',
    "cal": '<rect x="7" y="10" width="34" height="31" rx="3"/><path d="M7 19h34M16 6v8M32 6v8M15 27h5M22 27h5M29 27h5M15 34h5"/>',
    "scale": '<path d="M24 7v34M14 41h20M8 13h32"/><path d="m8 13-5 13a6 6 0 0 0 10 0zM40 13l-5 13a6 6 0 0 0 10 0z"/>',
    "family": '<circle cx="15" cy="12" r="5"/><circle cx="33" cy="12" r="5"/><circle cx="24" cy="25" r="4"/><path d="M6 40c0-9 4-14 9-14s9 5 9 14M24 40c0-9 4-14 9-14s9 5 9 14"/>',
}


def icon(name, size=56, stroke=None, cls="ic"):
    st = f' style="stroke:{stroke}"' if stroke else ""
    return (f'<svg class="{cls}" viewBox="0 0 48 48" width="{size}" height="{size}"{st} '
            f'fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


def esc(s):
    return html.escape(s, quote=False)


# ----------------------------------------------------------- scene shell ----
def scene(cid, inner_html, css, js, opaque, S, extra_root=""):
    bg = f"background:{S['bg']};" if opaque else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head><meta charset="UTF-8"></head>
  <body>
    <template>
      <style>
        #root {{ position:absolute; inset:0; overflow:hidden; {bg} font-family:"{S['body']}", sans-serif; color:{S['ink']}; }}
{css}
      </style>
      <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}"{extra_root}>
{inner_html}
      </div>
      <script>
        (function () {{
          const tl = gsap.timeline({{ paused: true }});
{js}
          window.__timelines["{cid}"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""


def cut_frame(cid, dur, S, opt):
    """Shared wrapper markup/css/js for a full-screen cutaway."""
    p = cid
    css = f"""
        #{p}-stage {{ position:absolute; inset:0; }}
        #{p}-bg3d {{ position:absolute; inset:0; width:{W}px; height:{H}px; }}
        #{p}-vig {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 50% 38%, rgba(0,0,0,0) 40%, rgba(0,0,0,.55) 100%); }}
        #{p}-ring {{ position:absolute; left:{PIP['x']-8}px; top:{PIP['y']-8}px; width:{PIP['s']+16}px; height:{PIP['s']+16}px;
                    border-radius:50%; border:3px solid {S['accent']}; box-shadow:0 0 40px rgba(212,175,106,.35); }}
    """
    bg = ""
    js = ""
    if opt == "a":
        bg = f'<div id="{p}-glow" style="position:absolute;inset:0;background:radial-gradient(70% 45% at 50% 40%, rgba(47,211,245,.10), rgba(0,0,0,0) 70%);"></div>'
        js += f"""
          tl.fromTo("#{p}-stage", {{ scale:1.18, filter:"blur(14px)", opacity:0 }}, {{ scale:1, filter:"blur(0px)", opacity:1, duration:0.32, ease:"expo.out" }}, 0);
          tl.to("#{p}-stage", {{ scale:0.94, filter:"blur(10px)", opacity:0, duration:0.18, ease:"power3.in" }}, {dur - 0.2:.3f});
        """
    else:
        bg = (f'<canvas id="{p}-bg3d" width="{W}" height="{H}"></canvas><div id="{p}-vig"></div>'
              f'<div id="{p}-ring"></div>')
        js += f"""
          tl.fromTo("#{p}-stage", {{ clipPath:"circle(0% at 540px {PIP['y']+PIP['s']//2}px)" }}, {{ clipPath:"circle(150% at 540px {PIP['y']+PIP['s']//2}px)", duration:0.55, ease:"power3.inOut" }}, 0);
          tl.to("#{p}-stage", {{ opacity:0, duration:0.22, ease:"power2.in" }}, {dur - 0.24:.3f});
          const bg = window.CaioFX.goldField(document.getElementById("{p}-bg3d"), {sum(map(ord, cid))});
          const st = {{ t:0 }};
          tl.fromTo(st, {{ t:0 }}, {{ t:{dur:.3f}, duration:{dur:.3f}, ease:"none", onUpdate:() => bg(st.t) }}, 0);
          bg(0);
        """
    return bg, css, js


PIP = dict(x=410, y=150, s=260)

# --------------------------------------------------------------- captions ----
EMPH = set("""1,9% 2027 fmi 7,7% 3,2% mundial crescimento valorização caio rezende advogado 10
experiência imobiliária paulo brasileiros emirados aqui? dólar 1997 dolarizado protegido aluguel média
imposto renda lucro população recorde imóveis junto seguros estrangeiro plena oficial conta garantida
governo líquido quiser investimento família allegiance? global internacional 7 dubai 20 bilhões dirhams
segurança? consulta allegiance unidos""".split())


def norm(t):
    return t.lower().strip(".,!")


def caption_groups(maxw):
    groups = []
    for s in SEGS:
        idx = s["words"]
        n = len(idx)
        k = max(1, -(-n // maxw))
        size = -(-n // k)
        for i in range(0, n, size):
            groups.append(idx[i:i + size])
    out = []
    for gi, g in enumerate(groups):
        st = max(0.1, WORDS[g[0]]["start"] - 0.06)
        en = WORDS[g[-1]]["end"] + 0.35
        out.append([g, st, en])
    for i in range(len(out) - 1):
        out[i][2] = min(out[i][2], out[i + 1][1])
    out[-1][2] = min(out[-1][2], DUR)
    return out


def build_captions(S, opt):
    cid = "captions"
    groups = caption_groups(4 if opt == "a" else 6)
    items, js = [], []
    for gi, (g, st, en) in enumerate(groups):
        gid = f"cg{gi}"
        key = None
        if opt == "a":
            for wi in g:
                if norm(WORDS[wi]["text"]) in EMPH:
                    key = wi
                    if re.search(r"\d", WORDS[wi]["text"]):
                        break
        spans_small, spans_key = [], ""
        for wi in g:
            t = esc(WORDS[wi]["text"])
            if wi == key:
                L = len(WORDS[wi]["text"])
                fs = int(min(124, 860 / (0.70 * max(L, 3))))
                spans_key = f'<span id="{gid}w{wi}" class="w key" style="font-size:{fs}px">{t}</span>'
            else:
                spans_small.append(f'<span id="{gid}w{wi}" class="w">{t}</span>')
        if opt == "a":
            inner = ""
            if spans_small:
                inner += f'<div class="sm">{" ".join(spans_small)}</div>'
            if spans_key:
                inner += f'<div class="bg">{spans_key}</div>'
        else:
            inner = f'<div class="pill">{" ".join(spans_small)}</div>'
        items.append(
            f'        <div id="{gid}" class="clip cg" data-start="{st:.3f}" data-duration="{en - st:.3f}" data-track-index="0">'
            f'<div id="{gid}i" class="cgi">{inner}</div></div>')
        for wi in g:
            w = WORDS[wi]
            sel = f"#{gid}w{wi}"
            t0 = max(st, w["start"] - 0.04)
            if opt == "a":
                if wi == key:
                    js.append(f'tl.fromTo("{sel}",{{opacity:0,scale:1.35,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.22,ease:"expo.out"}},{t0:.3f});')
                else:
                    js.append(f'tl.fromTo("{sel}",{{opacity:0,y:12,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.14,ease:"power3.out"}},{t0:.3f});')
            else:
                js.append(f'tl.fromTo("{sel}",{{opacity:0.45,color:"{S["ink"]}",backgroundColor:"rgba(212,175,106,0)"}},{{opacity:1,color:"#0b1630",backgroundColor:"rgba(212,175,106,1)",duration:0.08,ease:"none"}},{t0:.3f});')
                js.append(f'tl.to("{sel}",{{color:"{S["ink"]}",backgroundColor:"rgba(212,175,106,0)",duration:0.1,ease:"none"}},{max(t0 + 0.09, w["end"] - 0.02):.3f});')
        if opt == "b":
            js.append(f'tl.fromTo("#{gid}i",{{opacity:0,y:18}},{{opacity:1,y:0,duration:0.2,ease:"power3.out"}},{st:.3f});')
        js.append(f'tl.to("#{gid}i",{{opacity:0,duration:0.12,ease:"power2.in"}},{en - 0.12:.3f});')
        js.append(f'tl.set("#{gid}i",{{opacity:0}},{en:.3f});')

    if opt == "a":
        css = f"""
        #root .cg {{ position:absolute; left:0; right:0; top:1090px; height:230px; overflow:visible; }}
        #root .cgi {{ position:absolute; left:0; right:0; bottom:0; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; text-align:center; }}
        #root .sm {{ font:700 54px/1.15 "Montserrat", sans-serif; color:#fff; padding:0 110px; letter-spacing:-0.5px;
                    text-shadow:0 3px 14px rgba(0,0,0,.75), 0 0 3px rgba(0,0,0,.9); }}
        #root .bg {{ line-height:1.0; margin-top:-4px; }}
        #root .w {{ display:inline-block; }}
        #root .key {{ font-family:"Montserrat", sans-serif; font-weight:900; letter-spacing:-2px; color:{S['accent']};
                     text-shadow:0 4px 22px rgba(0,0,0,.55), 0 0 3px rgba(0,30,40,.9); }}
        """
    else:
        css = f"""
        #root .cg {{ position:absolute; left:0; right:0; top:1100px; height:220px; overflow:visible; }}
        #root .cgi {{ position:absolute; left:0; right:0; bottom:0; display:flex; justify-content:center; text-align:center; }}
        #root .pill {{ max-width:860px; padding:16px 26px; border-radius:22px; background:rgba(8,16,36,.72);
                      border:1.5px solid rgba(212,175,106,.45); font:600 50px/1.32 "Inter", sans-serif; color:{S['ink']}; }}
        #root .w {{ display:inline-block; padding:0 8px; border-radius:10px; }}
        """
    return scene(cid, "\n".join(items), css, "\n".join("          " + j for j in js), False, S)


# ------------------------------------------------------------- cutaways ----
def g_chart(S, opt, dur):
    cid = "g-chart"
    bg, fcss, fjs = cut_frame(cid, dur, S, opt)
    top = 440 if opt == "b" else 250
    bars = [("Brasil", 1.9, "rgba(255,255,255,.35)", 0.05), ("Mundo", 3.2, "rgba(255,255,255,.6)", 3.75), ("Emirados", 7.7, S["accent"], 2.7)]
    hmax = 340 if opt == "a" else 250
    cols = []
    js = [fjs]
    for i, (lab, v, col, t) in enumerate(bars):
        h = round(hmax * v / 7.7)
        cols.append(f"""
          <div class="col">
            <div class="val" id="chv{i}">0,0%</div>
            <div class="bar" id="chb{i}" style="height:{h}px;background:{col}"></div>
            <div class="lab">{lab}</div>
          </div>""")
        js.append(f'tl.fromTo("#chb{i}",{{scaleY:0}},{{scaleY:1,duration:0.7,ease:"expo.out"}},{t});')
        js.append(f'tl.fromTo("#chv{i}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,ease:"power3.out"}},{t});')
        js.append(f'(function(){{const o={{v:0}};const el=document.getElementById("chv{i}");'
                  f'tl.fromTo(o,{{v:0}},{{v:{v},duration:0.7,ease:"expo.out",onUpdate:()=>{{el.textContent=o.v.toFixed(1).replace(".",",")+"%";}}}},{t});}})();')
    js.append(f'tl.fromTo("#ch-title",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:"expo.out"}},0.1);')
    js.append(f'tl.fromTo("#ch-sub",{{opacity:0}},{{opacity:1,duration:0.4}},0.35);')
    js.append(f'tl.fromTo("#ch-badge",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.45,ease:"back.out(1.6)"}},4.4);')
    html_ = f"""        {bg}
        <div id="{cid}-stage">
          {bg if False else ''}
          <div id="ch-title" class="ttl">Crescimento do PIB<br><span>em 2027</span></div>
          <div id="ch-sub" class="sub">{icon('chart', 40, S['accent'])} Projeção do FMI</div>
          <div class="chart">{''.join(cols)}
          </div>
          <div id="ch-badge" class="badge">4× a média do Brasil</div>
        </div>"""
    css = fcss + f"""
        #root .ttl {{ position:absolute; top:{top}px; left:0; right:0; text-align:center; font:800 84px/1.02 "{S['head']}", serif; letter-spacing:-1px; }}
        #root .ttl span {{ color:{S['accent']}; }}
        #root .sub {{ position:absolute; top:{top + 190}px; left:0; right:0; display:flex; gap:12px; justify-content:center; align-items:center; font:600 36px "{S['body']}"; color:{S['muted']}; }}
        #root .chart {{ position:absolute; left:150px; right:150px; top:{top + 330}px; height:{hmax + 140}px; display:flex; align-items:flex-end; justify-content:space-between; }}
        #root .col {{ width:200px; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; }}
        #root .bar {{ width:150px; border-radius:18px 18px 4px 4px; transform-origin:50% 100%; }}
        #root .val {{ font:900 54px "{S['body']}"; margin-bottom:12px; }}
        #root .lab {{ font:600 34px "{S['body']}"; margin-top:16px; color:{S['muted']}; }}
        #root .badge {{ position:absolute; left:50%; margin-left:-260px; width:520px; top:{top + 250}px; padding:12px 0; text-align:center; border-radius:60px;
                       background:{S['accent']}; color:#06121a; font:800 36px "{S['body']}"; }}
    """
    return scene(cid, html_, css, "\n".join("          " + j for j in js), True, S)


def g_globe(S, opt, dur):
    cid = "g-globe"
    bg, fcss, fjs = cut_frame(cid, dur, S, opt)
    top = 440 if opt == "b" else 250
    gy = 880 if opt == "a" else 960
    js = fjs + f"""
          const R = window.CaioFX.globe(document.getElementById("gl-canvas"), "assets/{S['globe']}", "{S['accent']}", {gy});
          const g = {{ p:0, a:0 }};
          tl.fromTo(g, {{ p:0 }}, {{ p:1, duration:{dur - 0.4:.2f}, ease:"power2.inOut", onUpdate:() => R(g.p, g.a) }}, 0);
          tl.fromTo(g, {{ a:0 }}, {{ a:1, duration:2.2, ease:"power2.inOut", onUpdate:() => R(g.p, g.a) }}, 1.0);
          R(0, 0);
          tl.fromTo("#gl-from", {{ opacity:0, x:-30 }}, {{ opacity:1, x:0, duration:0.4, ease:"expo.out" }}, 0.25);
          tl.fromTo("#gl-to", {{ opacity:0, x:30 }}, {{ opacity:1, x:0, duration:0.4, ease:"expo.out" }}, 2.9);
          tl.fromTo("#gl-ttl", {{ opacity:0, y:24 }}, {{ opacity:1, y:0, duration:0.5, ease:"expo.out" }}, 0.1);
    """
    html_ = f"""        {bg}
        <div id="{cid}-stage">
          <canvas id="gl-canvas" width="{W}" height="{H}" style="position:absolute;inset:0"></canvas>
          <div id="gl-ttl" class="ttl">Investidores <span>brasileiros</span><br>nos Emirados</div>
          <div class="route">
            <div id="gl-from" class="pt">{icon('pin', 40, S['muted'])} São Paulo</div>
            <div class="arrow">→</div>
            <div id="gl-to" class="pt hi">{icon('pin', 40, S['accent'])} Dubai</div>
          </div>
        </div>"""
    css = fcss + f"""
        #root .ttl {{ position:absolute; top:{top}px; left:0; right:0; text-align:center; font:800 74px/1.05 "{S['head']}", serif; }}
        #root .ttl span {{ color:{S['accent']}; }}
        #root .route {{ position:absolute; top:{top + 190}px; left:0; right:0; display:flex; justify-content:center; align-items:center; gap:22px; font:700 42px "{S['body']}"; }}
        #root .pt {{ display:flex; align-items:center; gap:8px; padding:12px 26px; border-radius:50px; background:{S['card']}; border:1.5px solid {S['line']}; }}
        #root .pt.hi {{ color:{S['accent']}; }}
        #root .arrow {{ color:{S['muted']}; }}
    """
    return scene(cid, html_, css, js, True, S)


def g_question(S, opt, dur):
    cid = "g-question"
    bg, fcss, fjs = cut_frame(cid, dur, S, opt)
    qcol = "#ff3b4f" if opt == "a" else S["accent"]
    js = fjs + f"""
          tl.fromTo("#q-mark", {{ scale:0.2, rotation:-25, opacity:0 }}, {{ scale:1, rotation:-8, opacity:1, duration:0.55, ease:"back.out(1.8)" }}, 0.05);
          tl.fromTo("#q-l1", {{ opacity:0, filter:"blur(8px)" }}, {{ opacity:1, filter:"blur(0px)", duration:0.2 }}, 0.2);
          tl.fromTo("#q-l2", {{ opacity:0, scale:1.3, filter:"blur(10px)" }}, {{ opacity:1, scale:1, filter:"blur(0px)", duration:0.3, ease:"expo.out" }}, 0.75);
    """
    top = 600 if opt == "b" else 420
    html_ = f"""        {bg}
        <div id="{cid}-stage">
          <div class="qwrap">
            <div id="q-mark" class="qm">?</div>
            <div class="qt"><div id="q-l1" class="l1">Por que investir</div><div id="q-l2" class="l2">aqui?</div></div>
          </div>
        </div>"""
    css = fcss + f"""
        #root .qwrap {{ position:absolute; top:{top}px; left:0; right:0; display:flex; justify-content:center; align-items:center; gap:24px; }}
        #root .qm {{ font:900 400px/1 "{S['head'] if opt == 'b' else 'Montserrat'}", serif; color:{qcol};
                    text-shadow: 6px 10px 0 rgba(0,0,0,.45), 0 0 60px {qcol}55; }}
        #root .l1 {{ font:700 56px "{S['body']}"; color:{S['ink']}; }}
        #root .l2 {{ font:900 130px/1 "{S['head'] if opt == 'b' else 'Montserrat'}"; color:{S['accent']}; font-style:{'italic' if opt == 'b' else 'normal'}; }}
    """
    return scene(cid, html_, css, js, True, S)


def g_list(cid, S, opt, dur, start_num, items, title):
    bg, fcss, fjs = cut_frame(cid, dur, S, opt)
    top = 440 if opt == "b" else 280
    rows, js = [], [fjs]
    js.append(f'tl.fromTo("#{cid}-ttl",{{opacity:0,y:24}},{{opacity:1,y:0,duration:0.45,ease:"expo.out"}},0.08);')
    for i, (t, ic, head, sub) in enumerate(items):
        n = start_num + i
        rid = f"{cid}-r{i}"
        rows.append(f"""
            <div id="{rid}" class="row">
              <div class="num">{n}</div>
              <div class="txt"><div class="hd">{icon(ic, 46, S['accent'])}<span>{head}</span></div><div class="sb">{sub}</div></div>
            </div>""")
        js.append(f'tl.fromTo("#{rid} .num",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.4,ease:"back.out(2)"}},{t:.2f});')
        js.append(f'tl.fromTo("#{rid} .hd",{{opacity:0,x:-30,filter:"blur(8px)"}},{{opacity:1,x:0,filter:"blur(0px)",duration:0.35,ease:"expo.out"}},{t + 0.08:.2f});')
        js.append(f'tl.fromTo("#{rid} .sb",{{opacity:0}},{{opacity:1,duration:0.35}},{t + 0.3:.2f});')
        if i > 0:
            js.append(f'tl.to("#{cid}-r{i-1}",{{opacity:0.45,duration:0.3}},{t:.2f});')
    html_ = f"""        {bg}
        <div id="{cid}-stage">
          <div id="{cid}-ttl" class="ttl">{title}</div>
          <div class="list">{''.join(rows)}
          </div>
        </div>"""
    css = fcss + f"""
        #root .ttl {{ position:absolute; top:{top}px; left:0; right:0; text-align:center; font:800 64px "{S['head']}", serif; color:{S['ink']}; }}
        #root .list {{ position:absolute; top:{top + (150 if opt == 'a' else 120)}px; left:110px; right:110px; display:flex; flex-direction:column; gap:{40 if opt == 'a' else 18}px; }}
        #root .row {{ display:flex; gap:28px; align-items:flex-start; padding:{'0' if opt == 'a' else '18px 24px'}; border-radius:24px;
                     {'' if opt == 'a' else f"background:{S['card']}; border:1.5px solid {S['line']};"} }}
        #root .num {{ flex:none; width:76px; height:76px; border-radius:50%; background:{S['accent']}; color:#06121a; display:grid; place-items:center; font:900 40px "{S['body']}"; }}
        #root .hd {{ display:flex; align-items:center; gap:14px; font:800 46px/1.15 "{S['body']}"; }}
        #root .hd svg {{ flex:none; }}
        #root .sb {{ margin-top:6px; font:500 {34 if opt == 'a' else 30}px/1.3 "{S['body']}"; color:{S['muted']}; }}
    """
    return scene(cid, html_, css, "\n".join("          " + j for j in js), True, S)


def g_brand(S, opt, dur):
    cid = "g-brand"
    bg, fcss, fjs = cut_frame(cid, dur, S, opt)
    letters = "".join(f'<span class="lt">{c}</span>' for c in "ALLEGIANCE")
    js = fjs + """
          tl.fromTo("#br-q", { opacity:0, y:20 }, { opacity:1, y:0, duration:0.35, ease:"expo.out" }, 0.05);
          tl.fromTo("#br-word .lt", { opacity:0.0, y:40, filter:"blur(8px)" }, { opacity:1, y:0, filter:"blur(0px)", duration:0.4, ease:"expo.out", stagger:0.05 }, 0.45);
          tl.fromTo("#br-line", { scaleX:0 }, { scaleX:1, duration:0.6, ease:"power3.inOut" }, 0.9);
          tl.fromTo("#br-tag", { opacity:0 }, { opacity:1, duration:0.4 }, 1.2);
    """
    top = 700 if opt == "b" else 560
    html_ = f"""        {bg}
        <div id="{cid}-stage">
          <div class="brand">
            <div id="br-q" class="q">Por que escolher a</div>
            <div id="br-word" class="word">{letters}</div>
            <div id="br-line" class="line"></div>
            <div id="br-tag" class="tag">Consultoria global de investimentos</div>
          </div>
        </div>"""
    css = fcss + f"""
        #root .brand {{ position:absolute; top:{top}px; left:0; right:0; text-align:center; }}
        #root .q {{ font:600 48px "{S['body']}"; color:{S['muted']}; }}
        #root .word {{ margin-top:18px; font:{'900' if opt == 'a' else '700'} 112px/1 "{S['head'] if opt == 'b' else 'Montserrat'}"; letter-spacing:10px; color:{S['accent']}; }}
        #root .lt {{ display:inline-block; }}
        #root .line {{ width:520px; height:4px; margin:34px auto 0; background:{S['accent']}; transform-origin:50% 50%; }}
        #root .tag {{ margin-top:26px; font:600 40px "{S['body']}"; }}
    """
    return scene(cid, html_, css, js, True, S)


# --------------------------------------------------------------- overlays ----
OVER_TOP = 1335


def card_css(S, opt):
    return f"""
        #root .card {{ position:absolute; left:0; right:0; top:{OVER_TOP}px; display:flex; justify-content:center; overflow:visible; }}
        #root .ci {{ display:flex; align-items:center; gap:18px; padding:20px 34px; border-radius:{'60px' if opt == 'a' else '22px'};
                    background:{'#ffffff' if opt == 'a' else S['card']}; color:{'#0b0f16' if opt == 'a' else S['ink']};
                    border:{'0' if opt == 'a' else '1.5px solid ' + S['line']}; box-shadow:0 14px 40px rgba(0,0,0,.35);
                    font:700 40px/1.2 "{S['body']}"; max-width:880px; }}
        #root .ci svg {{ flex:none; stroke:{'#0aa5c6' if opt == 'a' else S['accent']}; }}
        #root .ci b {{ color:{'#0aa5c6' if opt == 'a' else S['accent']}; font-weight:900; }}
        #root .ci small {{ display:block; font:500 30px "{S['body']}"; opacity:.7; margin-top:4px; }}
    """


def card_js(cid_el, st, en):
    return [f'tl.fromTo("#{cid_el} .ci",{{opacity:0,y:40,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.45,ease:"back.out(1.7)"}},{st:.2f});',
            f'tl.to("#{cid_el} .ci",{{opacity:0,y:-20,duration:0.22,ease:"power2.in"}},{en - 0.24:.2f});']


def overlay_cards(cid, S, opt, base, cards):
    """cards: (abs_start, abs_end, icon, html)"""
    els, js = [], []
    for i, (a, b, ic, txt) in enumerate(cards):
        el = f"{cid}-c{i}"
        st, en = a - base, b - base
        els.append(f'        <div id="{el}" class="clip card" data-start="{st:.2f}" data-duration="{en - st:.2f}" data-track-index="{i % 2}"><div class="ci">{icon(ic, 52)}<div>{txt}</div></div></div>')
        js += card_js(el, st, en)
    return scene(cid, "\n".join(els), card_css(S, opt), "\n".join("          " + j for j in js), False, S)


def o_name(S, opt, base, end):
    cid = "o-name"
    els = f"""        <div id="nm-card" class="clip nm" data-start="0.05" data-duration="{end - base - 0.05:.2f}" data-track-index="0">
          <div id="nm-in" class="nmi">
            <div class="bar"></div>
            <div>
              <div id="nm-n" class="n">Caio Rezende</div>
              <div id="nm-r1" class="r">Advogado · Consultor imobiliário</div>
              <div id="nm-r2" class="chips"><span id="nm-c1">{icon('badge', 34)} +10 anos de experiência</span><span id="nm-c2">{icon('pin', 34)} São Paulo, Brasil</span></div>
            </div>
          </div>
        </div>"""
    js = f"""
          tl.fromTo("#nm-in", {{ opacity:0, x:-60 }}, {{ opacity:1, x:0, duration:0.5, ease:"expo.out" }}, 0.05);
          tl.fromTo("#nm-in .bar", {{ scaleY:0 }}, {{ scaleY:1, duration:0.5, ease:"expo.out" }}, 0.1);
          tl.fromTo("#nm-r1", {{ opacity:0, y:10 }}, {{ opacity:1, y:0, duration:0.35 }}, {18.17 - base:.2f});
          tl.fromTo("#nm-c1", {{ opacity:0, scale:0.7 }}, {{ opacity:1, scale:1, duration:0.4, ease:"back.out(2)" }}, {19.4 - base:.2f});
          tl.fromTo("#nm-c2", {{ opacity:0, scale:0.7 }}, {{ opacity:1, scale:1, duration:0.4, ease:"back.out(2)" }}, {22.67 - base:.2f});
          tl.to("#nm-in", {{ opacity:0, x:-40, duration:0.25, ease:"power2.in" }}, {end - base - 0.3:.2f});
    """
    css = f"""
        #root .nm {{ position:absolute; left:70px; right:70px; top:{OVER_TOP}px; }}
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
    return scene(cid, els, css, js, False, S)


def o_stats(S, opt, base, end):
    cid = "o-stats"
    cards = [
        (76.17, 79.38, "globe", "Consultoria <b>global</b> de investimentos"),
        (79.43, 82.28, "news", "Reconhecida pela <b>imprensa internacional</b>"),
        (82.33, 84.05, "pin", '<b id="st-n7">7</b> escritórios pelo mundo'),
        (84.1, 87.28, "badge", "Registrada no <b>regulador imobiliário</b> de Dubai"),
        (87.33, 91.25, "chart", 'Mais de <b>AED <span id="st-n20">20</span> bilhões</b><small>em transações imobiliárias</small>'),
    ]
    els, js = [], []
    for i, (a, b, ic, txt) in enumerate(cards):
        el = f"{cid}-c{i}"
        st, en = a - base, b - base
        els.append(f'        <div id="{el}" class="clip card" data-start="{st:.2f}" data-duration="{en - st:.2f}" data-track-index="{i % 2}"><div class="ci">{icon(ic, 52)}<div>{txt}</div></div></div>')
        js += card_js(el, st, en)
    s7, s20 = 82.33 - base, 87.33 - base
    js.append(f'(function(){{const o={{v:0}};const e=document.getElementById("st-n7");tl.fromTo(o,{{v:0}},{{v:7,duration:0.8,ease:"power2.out",onUpdate:()=>{{e.textContent=Math.round(o.v);}}}},{s7:.2f});}})();')
    js.append(f'(function(){{const o={{v:0}};const e=document.getElementById("st-n20");tl.fromTo(o,{{v:0}},{{v:20,duration:1.2,ease:"power2.out",onUpdate:()=>{{e.textContent=Math.round(o.v);}}}},{s20 + 0.2:.2f});}})();')
    return scene(cid, "\n".join(els), card_css(S, opt), "\n".join("          " + j for j in js), False, S)


def o_cta(S, opt, base, end):
    cid = "o-cta"
    d = end - base
    els = f"""        <div id="cta-card" class="clip cta" data-start="0.2" data-duration="{d - 0.2:.2f}" data-track-index="0">
          <div id="cta-in" class="ctai">
            <div class="ttl">{icon('cal', 48, S['accent'])} Consulta inicial <b>gratuita</b></div>
            <div id="cta-btn" class="btn">Agende com o Caio</div>
            <div id="cta-sub" class="sub">Cortesia da <b>Allegiance</b> · Invista nos Emirados com segurança</div>
          </div>
        </div>"""
    t_tap = 96.3 - base
    js = f"""
          tl.fromTo("#cta-in", {{ opacity:0, y:60, scale:0.9 }}, {{ opacity:1, y:0, scale:1, duration:0.55, ease:"expo.out" }}, 0.2);
          tl.fromTo("#cta-btn", {{ scale:1 }}, {{ scale:0.92, duration:0.1, ease:"power2.in" }}, {t_tap:.2f});
          tl.to("#cta-btn", {{ scale:1, duration:0.35, ease:"back.out(3)" }}, {t_tap + 0.1:.2f});
          tl.fromTo("#cta-sub", {{ opacity:0 }}, {{ opacity:1, duration:0.4 }}, {t_tap:.2f});
    """
    css = f"""
        #root .cta {{ position:absolute; left:80px; right:80px; top:{OVER_TOP}px; }}
        #root .ctai {{ padding:28px 32px; border-radius:28px; background:{S['card']}; border:1.5px solid {S['line']}; text-align:center; box-shadow:0 14px 40px rgba(0,0,0,.4); }}
        #root .ttl {{ display:flex; gap:14px; align-items:center; justify-content:center; font:700 44px "{S['body']}"; }}
        #root .ttl b {{ color:{S['accent']}; }}
        #root .btn {{ margin:20px auto 0; width:600px; padding:22px 0; border-radius:60px; background:{S['accent']}; color:#06121a; font:900 44px "{S['body']}"; }}
        #root .sub {{ margin-top:18px; font:500 30px "{S['body']}"; color:{S['muted']}; }}
        #root .sub b {{ color:{S['ink']}; }}
    """
    return scene(cid, els, css, js, False, S)


# ------------------------------------------------------------------- root ----
SFX = []  # (id, file, start, dur, vol)


def build_sfx(opt):
    s = []
    for cid, a, b in CUTS:
        s.append(("whoosh", a - 0.12, 0.57, 1.0))
    s += [("impact-bass-1", 8.7, 2.1, 0.7), ("pop", 6.1, 0.72, 0.6), ("pop", 9.6, 0.72, 0.6),
          ("pop", 31.35, 0.72, 0.8), ("pop", 36.97, 0.72, 0.8), ("pop", 40.37, 0.72, 0.8),
          ("pop", 55.3, 0.72, 0.8), ("pop", 56.67, 0.72, 0.8), ("pop", 59.1, 0.72, 0.8),
          ("click-soft", 16.6, 0.37, 1.0), ("click-soft", 45.0, 0.37, 1.0), ("click-soft", 49.57, 0.37, 1.0),
          ("click-soft", 64.6, 0.37, 1.0), ("click-soft", 70.13, 0.37, 1.0),
          ("click-soft", 76.17, 0.37, 1.0), ("click-soft", 79.43, 0.37, 1.0), ("click-soft", 82.33, 0.37, 1.0),
          ("click-soft", 84.1, 0.37, 1.0), ("impact-bass-1", 87.4, 2.1, 0.55),
          ("sparkle", 74.2, 1.8, 0.7), ("click", 96.3, 0.3, 1.0), ("chime", 96.35, 2.5, 0.6)]
    return sorted(s, key=lambda x: x[1])


def build_root(S, opt):
    hosts = []
    for cid, a, b in CUTS:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="2" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:5"></div>')
    for cid, a, b in OVERS:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="3" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:6"></div>')
    hosts.append(f'      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="4" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:9"></div>')
    pips = []
    if opt == "b":
        for i, (cid, a, b) in enumerate(CUTS):
            pips.append(f'      <video id="pip{i}" class="clip pip" src="assets/caio-crop.mp4" muted playsinline data-start="{a + 0.2:.2f}" data-duration="{b - a - 0.45:.2f}" data-media-start="{a + 0.2:.2f}" data-track-index="5" style="z-index:7"></video>')
    sfx = []
    for i, (f, t, d, v) in enumerate(build_sfx(opt)):
        sfx.append(f'      <audio id="sfx{i}" src="assets/sfx/{f}.mp3" data-start="{t:.2f}" data-duration="{d}" data-track-index="{11 + (i % 2)}" data-volume="{v * S["sfx_vol"]:.2f}"></audio>')

    if opt == "a":
        cam_js = "\n".join(f'      tl.set("#cam", {{ scale:{s} }}, {t});' for t, s in PUNCH)
    else:
        cam_js = "\n".join(
            f'      tl.to("#cam", {{ scale:{1.0 + (s - 1.0) * 0.9 + 0.02:.3f}, duration:0.7, ease:"power2.inOut" }}, {t});' for t, s in PUNCH[1:])
        cam_js = '      tl.set("#cam", { scale:1.02 }, 0);\n' + cam_js
        cam_js += '\n      tl.fromTo("#grade", { opacity:0 }, { opacity:1, duration:1 }, 0);'
    grade = ""
    if opt == "b":
        grade = '<div id="grade" style="position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(180deg,rgba(8,16,36,.35) 0%,rgba(8,16,36,0) 22%,rgba(8,16,36,0) 55%,rgba(8,16,36,.55) 100%);"></div>'
    else:
        grade = '<div id="grade" style="position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,0) 50%,rgba(0,0,0,.45) 100%);"></div>'

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
      #cam {{ position:absolute; inset:0; transform-origin:50% 34%; z-index:1; }}
      #talk {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; }}
      .pip {{ position:absolute; left:{PIP['x']}px; top:{PIP['y']}px; width:{PIP['s']}px; height:{PIP['s']}px; border-radius:50%; object-fit:cover; object-position:50% 30%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="root" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="cam">
        <video id="talk" class="clip" src="assets/caio-crop.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></video>
      </div>
      {grade}
{chr(10).join(hosts)}
{chr(10).join(pips)}
{chr(10).join(sfx)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{cam_js}
      window.__timelines["root"] = tl;
    </script>
  </body>
</html>
"""


FX_JS = r"""
// Shared Three.js helpers. Every frame is a pure function of the time passed in.
(function () {
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  function renderer(canvas) {
    const r = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
    r.setPixelRatio(1); r.setSize(canvas.width, canvas.height, false);
    return r;
  }

  // Gold particle field + slow wireframe rings (Option B cutaway backgrounds)
  function goldField(canvas, seed) {
    const r = renderer(canvas);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x081024);
    const cam = new THREE.PerspectiveCamera(50, canvas.width / canvas.height, 0.1, 100);
    cam.position.set(0, 0, 14);
    const rnd = mulberry32(seed + 7);
    const N = 900, pos = new Float32Array(N * 3), base = [];
    for (let i = 0; i < N; i++) { base.push([(rnd() - .5) * 18, (rnd() - .5) * 32, (rnd() - .5) * 14, rnd() * 6.28, 0.2 + rnd() * 0.6]); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xd4af6a, size: 0.09, transparent: true, opacity: 0.85 }));
    scene.add(pts);
    const ring1 = new THREE.Mesh(new THREE.TorusGeometry(5.2, 0.025, 8, 160), new THREE.MeshBasicMaterial({ color: 0xd4af6a, transparent: true, opacity: 0.35 }));
    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(6.4, 0.018, 8, 160), new THREE.MeshBasicMaterial({ color: 0xf3d9a4, transparent: true, opacity: 0.22 }));
    const ico = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(3.2, 1)), new THREE.LineBasicMaterial({ color: 0xd4af6a, transparent: true, opacity: 0.18 }));
    [ring1, ring2, ico].forEach(m => { m.position.set(0, -1.5, -4); scene.add(m); });
    return function (t) {
      for (let i = 0; i < N; i++) { const b = base[i];
        pos[i * 3] = b[0] + Math.sin(t * 0.4 + b[3]) * 0.3; pos[i * 3 + 1] = ((b[1] + t * b[4] + 16) % 32) - 16; pos[i * 3 + 2] = b[2]; }
      geo.attributes.position.needsUpdate = true;
      ring1.rotation.set(1.1 + t * 0.12, t * 0.18, 0); ring2.rotation.set(0.6 - t * 0.1, -t * 0.14, 0.3);
      ico.rotation.set(t * 0.08, t * 0.15, 0);
      cam.position.x = Math.sin(t * 0.15) * 0.8;
      cam.lookAt(0, 0, 0);
      r.render(scene, cam);
    };
  }

  // Dotted globe turning from Brazil to the UAE with an arc between them.
  function globe(canvas, texUrl, accentHex, centerY) {
    const r = renderer(canvas);
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(30, canvas.width / canvas.height, 0.1, 100);
    // shift the globe vertically so it sits at centerY px
    const ndcY = 1 - 2 * (centerY / canvas.height);
    cam.position.set(0, 0, 20.5);
    cam.setViewOffset(canvas.width, canvas.height, 0, ndcY * canvas.height / 2, canvas.width, canvas.height);
    const accent = new THREE.Color(accentHex);
    const tex = new THREE.TextureLoader().load(texUrl, () => { ready = true; });
    let ready = false;
    tex.colorSpace = THREE.SRGBColorSpace;
    const g = new THREE.Group(); scene.add(g);
    const sphere = new THREE.Mesh(new THREE.SphereGeometry(2, 96, 96), new THREE.MeshBasicMaterial({ map: tex }));
    g.add(sphere);
    const halo = new THREE.Mesh(new THREE.SphereGeometry(2.08, 64, 64), new THREE.MeshBasicMaterial({ color: accent, transparent: true, opacity: 0.08, side: THREE.BackSide }));
    scene.add(halo);
    function ll(lat, lon, rad) { const phi = (90 - lat) * Math.PI / 180, th = (lon + 180) * Math.PI / 180;
      return new THREE.Vector3(-rad * Math.sin(phi) * Math.cos(th), rad * Math.cos(phi), rad * Math.sin(phi) * Math.sin(th)); }
    const A = ll(-23.55, -46.63, 2.01), B = ll(25.2, 55.27, 2.01);
    const mid = A.clone().add(B).multiplyScalar(0.5).normalize().multiplyScalar(3.1);
    const curve = new THREE.QuadraticBezierCurve3(A, mid, B);
    const P = curve.getPoints(160);
    const arcGeo = new THREE.BufferGeometry().setFromPoints(P);
    const arc = new THREE.Line(arcGeo, new THREE.LineBasicMaterial({ color: accent, linewidth: 2 }));
    g.add(arc);
    const dotA = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    const dotB = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), new THREE.MeshBasicMaterial({ color: accent }));
    dotA.position.copy(A); dotB.position.copy(B); g.add(dotA); g.add(dotB);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), new THREE.MeshBasicMaterial({ color: accent }));
    g.add(head);
    // rotation so Brazil faces camera (+z), then the UAE
    const yawFor = lon => -((lon + 90) * Math.PI / 180);
    const y0 = yawFor(-46.6), y1 = yawFor(6);
    return function (p, a) {
      g.rotation.y = y0 + (y1 - y0) * p;
      g.rotation.x = 0.18 - 0.25 * p;
      const n = Math.max(2, Math.floor(a * P.length));
      arcGeo.setDrawRange(0, n);
      head.position.copy(P[Math.min(P.length - 1, n - 1)]);
      head.visible = a > 0.01 && a < 0.99;
      dotB.scale.setScalar(a > 0.98 ? 1.6 : 1);
      r.render(scene, cam);
    };
  }
  window.CaioFX = { goldField, globe };
})();
"""


def main():
    for opt in ("a", "b"):
        S = STYLE[opt]
        out = os.path.join(HERE, f"option-{opt}")
        comp = os.path.join(out, "compositions")
        assets = os.path.join(out, "assets")
        os.makedirs(comp, exist_ok=True)
        os.makedirs(os.path.join(assets, "sfx"), exist_ok=True)
        for f in ("caio-crop.mp4", "three.min.js", S["globe"]):
            dst = os.path.join(assets, f)
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(os.path.join(SHARED, f)):
                shutil.copy(os.path.join(SHARED, f), dst)
        shutil.copy(os.path.join(HERE, "..", "vendor", "gsap.min.js"), os.path.join(assets, "gsap.min.js"))
        for f in os.listdir(SHARED):
            if f.endswith(".mp3") and not f.startswith("music"):
                shutil.copy(os.path.join(SHARED, f), os.path.join(assets, "sfx", f))
        open(os.path.join(assets, "fx.js"), "w").write(FX_JS)
        files = {
            "captions.html": build_captions(S, opt),
            "g-chart.html": g_chart(S, opt, 6.45),
            "g-globe.html": g_globe(S, opt, 5.15),
            "g-question.html": g_question(S, opt, 1.85),
            "g-list1.html": g_list("g-list1", S, opt, 13.45, 1, [
                (0.15, "dollar", "Moeda atrelada ao dólar", "Desde 1997 · patrimônio dolarizado"),
                (5.67, "house", "Aluguel acima da média", "Acima das grandes capitais do mundo"),
                (9.07, "percent", "0% de imposto", "Sobre a renda e o lucro na venda"),
            ], "Por que investir nos <span style='color:%s'>Emirados</span>" % S["accent"]),
            "g-list2.html": g_list("g-list2", S, opt, 9.3, 4, [
                (0.1, "key", "Propriedade plena", "Freehold: o imóvel é 100% seu"),
                (1.47, "doc", "Registro oficial", "Em órgão público local"),
                (3.9, "lock", "Conta garantia", "Compra na planta protegida e fiscalizada pelo governo"),
            ], "Segurança <span style='color:%s'>jurídica</span>" % S["accent"]),
            "g-brand.html": g_brand(S, opt, 2.35),
            "o-name.html": o_name(S, opt, 16.55, 24.25),
            "o-chips1.html": overlay_cards("o-chips1", S, opt, 45.0, [
                (45.2, 49.45, "people", "População crescendo em <b>ritmo recorde</b>"),
                (49.57, 55.1, "shield", "Um dos países <b>mais seguros</b> do mundo<small>Regras estáveis para o investidor estrangeiro</small>"),
            ]),
            "o-chips2.html": overlay_cards("o-chips2", S, opt, 64.55, [
                (64.7, 69.9, "swap", "<b>Mercado líquido</b><small>Entre e saia quando quiser</small>"),
                (70.1, 73.7, "family", "Visto de <b>10 anos</b><small>Para você e sua família</small>"),
            ]),
            "o-stats.html": o_stats(S, opt, 76.15, 91.3),
            "o-cta.html": o_cta(S, opt, 93.9, DUR),
        }
        for k, v in files.items():
            open(os.path.join(comp, k), "w", encoding="utf-8").write(v)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(build_root(S, opt))
        json.dump({"id": f"caio-option-{opt}", "name": S["name"]}, open(os.path.join(out, "meta.json"), "w"), indent=2)
        shutil.copy(os.path.join(HERE, "..", "hyperframes.json"), os.path.join(out, "hyperframes.json"))
        json.dump({"name": f"caio-option-{opt}", "private": True, "type": "module", "scripts": {
            "dev": "npx --yes hyperframes@0.8.137 preview", "check": "npx --yes hyperframes@0.8.137 check",
            "render": "npx --yes hyperframes@0.8.137 render"}}, open(os.path.join(out, "package.json"), "w"), indent=2)
        print("wrote", out)


if __name__ == "__main__":
    main()
