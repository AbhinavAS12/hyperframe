#!/usr/bin/env python3
"""Allegiance Brazil campaign, new private-bank style (brief + moodboard, Nov 2026).

  python3 caio/build_lux.py long    -> caio/v1-long   (Video 1 Long, ~60 s)
  python3 caio/build_lux.py short   -> caio/v1-short  (Video 1 Short, ~30 s)

Source footage is pre-processed (shared/caio-*-13x.mp4): wall logo blurred,
light film grain, sped up 1.3x with pitch kept. Span times below are in the
ORIGINAL (1.0x) clock and divided by SPEED when placed.
"""
import json, os, shutil, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.join(HERE, "shared")
W, H = 1080, 1920
SPEED = 1.3
LEAD, TAIL = 0.06, 0.10
HOLD = 1.5           # end-card hold after the last word
OUTRO_LEN = 5.15

C = dict(emerald="#0B2B22", night="#07150F", gold="#C9A86A", champ="#E5D3A6", ivory="#F5F0E6", grey="#5A6670", red="#C8473D", slate="#0E1418")
SRC_IMF = "Fonte: FMI, World Economic Outlook, out. 2026"

ICON = {
    "dollar": '<circle cx="24" cy="24" r="19"/><path d="M30 16.5c-1.4-1.8-3.6-2.6-6-2.6-3.4 0-6 1.8-6 4.6 0 6.6 12.4 3.6 12.4 10.4 0 2.9-2.8 4.8-6.4 4.8-2.7 0-5-1-6.4-2.9M24 10v4M24 34v4"/>',
}

# ------------------------------------------------------------------ videos ----
# span: (a, b, mode, opts)   mode: hook | chart | full | punch | split | broll | sf06 | creds | end
LONG = dict(
    out="v1-long", src="caio-full-13x-clean.mp4", music_start=0.0,
    file="ALLEGIANCE_BR_V1_LONG_9x16_v01.mp4",
    spans=[
        (0.633, 4.666, "brazil", dict(cap=["O Brasil deve crescer apenas 1,9% em 2027."], beats=dict(b19=2.55))),
        (6.000, 12.266, "chart", dict(cap=["Os Emirados Árabes Unidos devem crescer 7,7%, contra 3,2% da média mundial."],
                                      beats=dict(e77=8.75, m32=9.95))),
        (16.666, 23.200, "full", dict(l3=True, cap=["Eu me chamo Caio Rezende, eu sou advogado e tenho mais de dez anos",
                                                     "de experiência em consultoria imobiliária em São Paulo."])),
        (24.300, 29.066, "punch", dict(cap=["E hoje eu assessoro investidores brasileiros a investir aqui nos Emirados Árabes Unidos."])),
        (29.566, 30.966, "broll", dict(clip="b12", cap=["E por que investir aqui?"])),
        (31.300, 36.833, "full", dict(chip="Moeda atrelada ao dólar", cap=["A moeda é atrelada ao dólar desde 1997,", "então seu patrimônio fica dolarizado e protegido."])),
        (36.966, 40.100, "split", dict(clip="b03", head="Aluguel acima da média", sub="das grandes capitais do mundo",
                                       cap=["O retorno com aluguel é acima da média das grandes capitais do mundo."])),
        (40.366, 44.533, "sf06", dict(clip="b09", idx="03 / 08", big="0%", line="de imposto local sobre a renda e o lucro na venda",
                                      cap=["Não tem imposto local sobre a renda", "e nem sobre o lucro na venda da propriedade."])),
        (45.233, 49.266, "split", dict(clip="b05", head="População em crescimento recorde", sub="e a demanda por imóveis cresce junto",
                                       cap=["A população tá crescendo em ritmo recorde, e a demanda por imóveis cresce junto."])),
        (49.566, 54.866, "full", dict(chip="Segurança e regras estáveis", cap=["Um dos países mais seguros do mundo,", "com regras estáveis e feitas pro investidor estrangeiro."])),
        (55.266, 64.233, "split", dict(clip="b08", head="Propriedade plena", sub="Registro oficial e escrow fiscalizado pelo governo",
                                       cap=["A propriedade é plena, o registro é oficial num órgão local,",
                                            "e o dinheiro da compra na planta fica protegido numa conta garantida, fiscalizada pelo governo."])),
        (64.733, 67.466, "punch", dict(chip="Liquidez", cap=["Mercado líquido pra entrar e sair quando você quiser."])),
        (67.833, 73.133, "full", dict(chip="Visto de 10 anos*", foot="*A partir de valor mínimo de investimento",
                                      cap=["E, a partir de um valor específico de investimento,", "um visto de dez anos pra você e pra sua família."])),
        (76.166, 79.066, "creds", dict(step="intro", cap=["Nós somos uma consultoria global de investimentos,"])),
        (82.333, 83.766, "creds", dict(step="offices", cap=["com sete escritórios no mundo,"])),
        (84.100, 87.133, "creds", dict(step="seals", cap=["registro no órgão regulador imobiliário de Dubai"])),
        (87.333, 90.766, "creds", dict(step="aed", cap=["e mais de 20 bilhões de dirhams em transações imobiliárias."])),
        (94.133, 98.200, "punch", dict(cap=["Agende uma consulta inicial comigo, como cortesia da Allegiance,"])),
        (98.233, 101.033, "end", dict(cap=[])),
    ])

SHORT = dict(
    out="v1-short", src="caio-v2-13x-clean.mp4", music_start=25.0,
    file="ALLEGIANCE_BR_V1_SHORT_9x16_v01.mp4",
    spans=[
        (0.36, 4.34, "brazil", dict(cap=["O Brasil deve crescer apenas 1,9%."], beats=dict(b19=3.0))),
        (7.82, 14.86, "chart", dict(cap=["7,7% é quanto os Emirados Árabes Unidos devem crescer em 2027,", "contra 3,2% do restante do mundo."],
                                    beats=dict(e77=8.10, m32=12.95))),
        (15.50, 22.78, "full", dict(l3=True, cap=["Eu me chamo Caio Rezende, eu sou advogado e consultor imobiliário,",
                                                  "eu assessoro investidores brasileiros a investir aqui nos Emirados."])),
        (23.56, 24.64, "full", dict(chip="Moeda atrelada ao dólar", cap=["Moeda atrelada ao dólar,"])),
        (24.98, 26.72, "split", dict(clip="b03", head="Aluguel acima da média", sub="mundial", cap=["aluguel acima da média mundial,"])),
        (26.94, 29.64, "sf06", dict(clip="b09", idx="03 / 05", big="0%", line="de imposto local sobre aluguel e renda",
                                    cap=["sem imposto local sobre o aluguel e a renda,"])),
        (30.32, 32.28, "split", dict(clip="b05", head="Segurança", sub="um dos países mais seguros do mundo", cap=["um dos países mais seguros do mundo"])),
        (32.66, 34.18, "full", dict(chip="Visto de 10 anos*", cap=["e um visto de dez anos"])),
        (35.58, 37.22, "punch", dict(chip="Visto de 10 anos*", foot="*A partir de valor mínimo de investimento",
                                     cap=["a partir de um valor de investimento."])),
        (37.80, 39.02, "creds", dict(step="intro", cap=["Tudo isso com a Allegiance."])),
        (39.30, 41.68, "creds", dict(step="offices", cap=["Nós temos sete escritórios pelo mundo"])),
        (42.16, 44.90, "creds", dict(step="seals", cap=["e registro no órgão regulador de Dubai, o RERA."])),
        (45.36, 47.62, "punch", dict(cap=["Agende uma consulta inicial comigo"])),
        (48.88, 51.78, "end", dict(cap=[])),
    ])


# ---------------------------------------------------------- Video 2 (Brazil) ----
SRC_BC = "Fonte: Banco Central do Brasil"
COLD = dict(cold=True)
V3 = dict(
    out="v3-long", src="caio-v3-13x-clean.mp4", src_cold="caio-v3-13x-cold.mp4", words="v3_words.json",
    dark="music-dark-v3.mp3", dark_ms=4.0, dark_vol=0.16, file="ALLEGIANCE_BR_V2_LONG_9x16_v01.mp4",
    spans=[
        (0.58, 3.72, "full", dict(COLD, num=dict(n="R$ 1 = US$ 1", label="Em 1994", src=SRC_BC, red=False, size=130, at=0.3))),
        (3.92, 5.26, "brl", dict(COLD)),
        (6.14, 9.34, "brl", dict(COLD)),
        (9.96, 15.06, "full", dict(COLD, num=dict(n="13,75%", label="Selic: juros entre os mais altos do planeta, e a projeção para 2027 subiu",
                                                 src="Fonte: Banco Central do Brasil, Copom e Boletim Focus", at=0.9))),
        (15.58, 17.08, "broll", dict(COLD, clip="c20", num=dict(n="82,9% do PIB", label="Dívida bruta do Brasil", src=SRC_BC + ", ago. 2026", size=130))),
        (17.44, 22.02, "broll", dict(COLD, clip="c21", num=dict(n="10%", label="sobre dividendos · regras mudando até 2033", src="Fonte: Lei 15.270/2025"))),
        (22.56, 25.88, "broll", dict(COLD, clip="c22", num=dict(n="Até 22,5%", label="de imposto na venda de imóvel com lucro", src="Fonte: Receita Federal", size=150, at=1.0))),
        (26.40, 30.76, "full", dict(COLD, num=dict(n="~1.200", label="milionários deixaram o Brasil em um ano", src="Fonte: Henley & Partners, 2025"))),
        (31.04, 36.04, "broll", dict(COLD, clip="c23")),
        (36.46, 41.20, "full", dict(COLD)),
        (None, 0.8, "gap", dict()),
        (41.64, 44.70, "broll", dict(clip="b24", chip="Economia em crescimento")),
        (45.02, 45.84, "full", dict(chip="Moeda atrelada ao dólar")),
        (46.14, 48.28, "sf06", dict(clip="b12", idx="EMIRADOS ÁRABES UNIDOS", big="0%", line="de imposto local sobre aluguel e ganho de capital")),
        (48.64, 54.08, "split", dict(clip="b05", head="Segurança", sub="um ambiente feito para o investidor estrangeiro")),
        (54.52, 58.46, "punch", dict(chip="Proteja o que você construiu")),
        (59.12, 63.90, "full", dict(l3=True)),
        (64.36, 68.94, "full", dict()),
        (68.98, 70.50, "creds", dict(step="intro")),
        (70.52, 71.92, "creds", dict(step="offices")),
        (72.22, 73.92, "creds", dict(step="press")),
        (74.22, 77.00, "creds", dict(step="seals")),
        (77.60, 79.86, "full", dict()),
        (80.12, 82.88, "punch", dict()),
        (83.26, 85.46, "end", dict(cap=[])),
    ])

V4 = dict(
    out="v4-short", src="caio-v3-13x-clean.mp4", src_cold="caio-v3-13x-cold.mp4", words="v3_words.json",
    dark="music-dark-v3.mp3", dark_ms=10.0, dark_vol=0.16, file="ALLEGIANCE_BR_V2_SHORT_9x16_v01.mp4",
    spans=[
        (0.58, 3.72, "full", dict(COLD, num=dict(n="R$ 1 = US$ 1", label="Em 1994", src=SRC_BC, red=False, size=130, at=0.3))),
        (3.92, 5.26, "brl", dict(COLD)),
        (6.14, 9.34, "brl", dict(COLD)),
        (9.96, 12.36, "full", dict(COLD, num=dict(n="13,75%", label="Selic: juros entre os mais altos do planeta", src="Fonte: Banco Central do Brasil, Copom", at=0.3))),
        (15.58, 17.08, "broll", dict(COLD, clip="c20", num=dict(n="82,9% do PIB", label="Dívida bruta do Brasil", src=SRC_BC + ", ago. 2026", size=130))),
        (17.44, 19.10, "broll", dict(COLD, clip="c21", num=dict(n="10%", label="sobre dividendos", src="Fonte: Lei 15.270/2025"))),
        (22.56, 25.88, "broll", dict(COLD, clip="c22", num=dict(n="Até 22,5%", label="de imposto na venda de imóvel com lucro", src="Fonte: Receita Federal", size=150, at=1.0))),
        (26.40, 27.62, "full", dict(COLD, num=dict(n="~1.200", label="milionários deixaram o Brasil em um ano", src="Fonte: Henley & Partners, 2025"))),
        (31.04, 34.56, "broll", dict(COLD, clip="c23")),
        (38.90, 41.20, "full", dict(COLD)),
        (None, 0.6, "gap", dict()),
        (41.64, 44.70, "broll", dict(clip="b24", chip="Economia em crescimento")),
        (45.02, 45.84, "full", dict(chip="Moeda atrelada ao dólar")),
        (46.14, 48.28, "sf06", dict(clip="b12", idx="EMIRADOS ÁRABES UNIDOS", big="0%", line="de imposto local sobre aluguel e ganho de capital")),
        (48.64, 50.58, "split", dict(clip="b05", head="Segurança", sub="entre as maiores do planeta")),
        (59.12, 61.32, "full", dict(l3=True)),
        (68.98, 71.30, "creds", dict(step="intro")),
        (74.22, 77.00, "creds", dict(step="seals")),
        (80.12, 82.88, "end", dict(cap=[])),
    ])


def esc(s):
    return html.escape(s, quote=False)


def icon(name, size, color):
    return (f'<svg viewBox="0 0 48 48" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="3" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


FONTS = """
        @font-face { font-family:"Cormorant Garamond"; font-weight:600; src:url("assets/fonts/cormorant-garamond-latin-600-normal.woff2") format("woff2"); }
        @font-face { font-family:"Cormorant Garamond"; font-weight:500; src:url("assets/fonts/cormorant-garamond-latin-500-normal.woff2") format("woff2"); }
"""
SERIF = '"Cormorant Garamond", serif'
SANS = '"Montserrat", sans-serif'


def scene(cid, inner, css, js):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head><meta charset="UTF-8"></head>
  <body>
    <template>
      <style>
{FONTS}
        #root {{ position:absolute; inset:0; overflow:hidden; color:{C['ivory']}; font-family:{SANS}; font-weight:500; }}
{css}
      </style>
      <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{inner}
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


REVEAL = '{opacity:0,y:12},{opacity:1,y:0,duration:0.27,ease:"power2.out"}'


def reveal(sel, t):
    return f'tl.fromTo("{sel}",{REVEAL},{t:.3f});'


def hide(sel, t, d=0.2):
    return f'tl.to("{sel}",{{opacity:0,duration:{d},ease:"power1.in"}},{t:.3f});'


# ------------------------------------------------------------- timeline ----
def layout(cfg):
    """Place spans back to back; returns list of dicts with out times."""
    t = 0.0
    out = []
    for a, b, mode, o in cfg["spans"]:
        if mode == "gap":
            t1 = round((t + b) * 30) / 30
            out.append(dict(a=None, b=None, a0=None, mode=mode, o=o, t0=t, t1=t1, ms=None))
            t = t1
            continue
        a0, b0 = a - LEAD, b + TAIL
        d = (b0 - a0) / SPEED
        t1 = round((t + d) * 30) / 30
        out.append(dict(a=a, b=b, a0=a0, mode=mode, o=o, t0=t, t1=t1, ms=a0 / SPEED))
        t = t1
    return out, t


def tmap(sp, src_t):
    """Original-clock time inside a span -> output time."""
    return sp["t0"] + (src_t - sp["a0"]) / SPEED


# ------------------------------------------------------------- overlays ----
def ov_open(spans):
    br = next(s for s in spans if s["mode"] == "brazil")
    chart = next(s for s in spans if s["mode"] == "chart")
    t19 = tmap(br, br["o"]["beats"]["b19"])
    t77 = tmap(chart, chart["o"]["beats"]["e77"])
    t32 = tmap(chart, chart["o"]["beats"]["m32"])
    c0, end = chart["t0"], chart["t1"]
    bars = [("Brasil", 1.9, C["grey"], f"{C['ivory']}99", c0 + 0.25), ("Mundo", 3.2, "#DCD3C6", C["ivory"], max(t32, c0 + 0.8)),
            ("Emirados", 7.7, C["gold"], C["gold"], max(t77, c0 + 0.5))]
    hmax = 470
    cols, js = [], []
    for i, (lab, v, col, tcol, t) in enumerate(bars):
        hgt = round(hmax * v / 7.7)
        cols.append(f'<div class="col"><div class="val" id="cv{i}" style="color:{tcol}">0,0%</div>'
                    f'<div class="bar" id="cb{i}" style="height:{hgt}px;background:{col}"></div>'
                    f'<div class="lab" style="color:{C["gold"] if lab == "Emirados" else C["ivory"]}">{lab}</div></div>')
        js.append(f'tl.fromTo("#cb{i}",{{scaleY:0}},{{scaleY:1,duration:1.0,ease:"power3.out"}},{t:.3f});')
        js.append(reveal(f"#cv{i}", t))
        js.append(f'(function(){{const o={{v:0}},e=document.getElementById("cv{i}");tl.fromTo(o,{{v:0}},{{v:{v},duration:1.0,ease:"power3.out",'
                  f'onUpdate:()=>{{e.textContent=o.v.toFixed(1).replace(".",",")+"%";}}}},{t:.3f});}})();')
    inner = f"""
        <div id="bz" class="clip" data-start="{t19 - 0.1:.3f}" data-duration="{br['t1'] - t19 + 0.1:.3f}" data-track-index="0">
          <div class="bzn"><div id="bz-n" class="n">1,9%</div><div id="bz-r" class="rule"></div>
          <div id="bz-l" class="l">Crescimento projetado do Brasil em 2027</div></div>
        </div>
        <div id="ch" class="clip" data-start="{c0:.3f}" data-duration="{end - c0:.3f}" data-track-index="1">
          <div id="ch-in" class="chin">
            <div id="ch-k" class="kick">PROJEÇÃO DE CRESCIMENTO 2027</div>
            <div id="ch-h" class="chh">Os Emirados devem crescer 4× mais que o Brasil</div>
            <div class="bars" data-layout-allow-overflow>{''.join(cols)}</div>
            <div class="src chs">{SRC_IMF}</div>
          </div>
        </div>"""
    css = f"""
        #root .clip {{ position:absolute; inset:0; }}
        #root .bzn {{ position:absolute; left:110px; right:110px; top:1010px; }}
        #root .bzn .n {{ font:600 170px/0.9 {SERIF}; color:{C['ivory']}; text-shadow:0 4px 30px rgba(7,21,15,.6); }}
        #root .bzn .rule {{ width:220px; height:3px; margin-top:12px; background:{C['ivory']}; opacity:.7; transform-origin:0 50%; }}
        #root .bzn .l {{ margin-top:14px; font:500 28px {SANS}; color:{C['ivory']}; text-shadow:0 2px 12px rgba(7,21,15,.8); }}
        #root .src {{ position:absolute; left:110px; font:500 20px {SANS}; color:{C['ivory']}; opacity:.6; }}
        #root .chin {{ position:absolute; inset:0; background:{C['emerald']}; }}
        #root .kick {{ position:absolute; left:110px; top:330px; font:500 24px {SANS}; letter-spacing:5px; color:{C['gold']}; }}
        #root .chh {{ position:absolute; left:110px; right:110px; top:380px; font:600 78px/1.1 {SERIF}; color:{C['ivory']}; }}
        #root .bars {{ position:absolute; left:130px; right:130px; top:640px; height:620px; display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid {C['gold']}55; }}
        #root .col {{ width:220px; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; position:relative; }}
        #root .bar {{ width:170px; transform-origin:50% 100%; }}
        #root .val {{ font:600 72px/1 {SERIF}; margin-bottom:14px; }}
        #root .lab {{ position:absolute; bottom:-52px; font:500 28px {SANS}; }}
        #root .chs {{ top:1330px; }}
    """
    js = [reveal("#bz-n", t19 - 0.1), f'tl.fromTo("#bz-r",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{t19 + 0.1:.3f});',
          reveal("#bz-l", t19 + 0.2), hide("#bz .bzn", br["t1"] - 0.2),
          f'tl.fromTo("#ch-in",{{opacity:0}},{{opacity:1,duration:0.2,ease:"none"}},{c0:.3f});',
          reveal("#ch-k", c0 + 0.1), reveal("#ch-h", c0 + 0.2)] + js
    return scene("ov-open", inner, css, "\n".join("          " + j for j in js)), (0, end)


BRL = [(1994, 1.0), (1996, 1.01), (1998, 1.16), (1999, 1.81), (2001, 2.35), (2002, 2.92), (2003, 3.08), (2005, 2.43),
       (2007, 1.95), (2008, 1.83), (2010, 1.76), (2011, 1.67), (2013, 2.16), (2015, 3.33), (2016, 3.49), (2018, 3.65),
       (2019, 3.94), (2020, 5.16), (2021, 5.40), (2022, 5.16), (2023, 4.99), (2024, 5.39), (2025, 5.45), (2026, 5.65)]


def ov_brl(spans):
    bs = [s for s in spans if s["mode"] == "brl"]
    t0, t1 = bs[0]["t0"], bs[-1]["t1"]
    t_red = bs[-1]["t0"] if len(bs) > 1 else t0 + 1.4
    x0, x1, y0, y1 = 120, 960, 1180, 740          # plot box (px)
    X = lambda yr: x0 + (yr - 1994) / (2026 - 1994) * (x1 - x0)
    Y = lambda v: y0 - (v - 0.8) / (6.0 - 0.8) * (y0 - y1)
    pts = [(X(a), Y(b)) for a, b in BRL]
    main = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1])
    red = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts[-2:])
    ticks = "".join(f'<text x="{X(yr):.0f}" y="{y0 + 44}" text-anchor="middle">{yr}</text>' for yr in (1994, 2002, 2010, 2018, 2026))
    ex, ey = pts[-1]
    inner = f"""        <div id="br" class="clip" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="0">
          <div id="br-in" class="brin">
            <div id="br-k" class="kick">QUANTOS REAIS VALE UM DÓLAR</div>
            <div id="br-h" class="hh">Em 1994, um real<br>valia um dólar.</div>
            <svg class="plot" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
              <line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{C['ivory']}" stroke-opacity=".25" stroke-width="2"/>
              <g class="tk">{ticks}</g>
              <polyline id="br-l" points="{main}" fill="none" stroke="{C['ivory']}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
              <polyline id="br-r" points="{red}" fill="none" stroke="{C['red']}" stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
              <circle id="br-s" cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="9" fill="{C['ivory']}"/>
              <circle id="br-e" cx="{ex:.1f}" cy="{ey:.1f}" r="11" fill="{C['red']}"/>
              <text id="br-st" x="{pts[0][0] + 6:.0f}" y="{pts[0][1] - 26:.0f}" class="lbl">R$ 1,00 (1994)</text>
            </svg>
            <div id="br-v" class="endv" style="top:{ey - 175:.0f}px">R$ 5,65</div>
            <div id="br-vl" class="endl" style="top:{ey - 58:.0f}px">hoje · alta desde a eleição</div>
            <div id="br-note" class="note">Moeda que mais perdeu valor no mundo nas últimas semanas</div>
            <div class="src">Fonte: Banco Central do Brasil (PTAX), curva ilustrativa · Austin Rating</div>
          </div>
        </div>"""
    css = f"""
        #root .clip {{ position:absolute; inset:0; }}
        #root .brin {{ position:absolute; inset:0; background:radial-gradient(110% 70% at 50% 40%, #151d22 0%, {C['slate']} 60%, #080b0d 100%); }}
        #root .kick {{ position:absolute; left:110px; top:300px; font:500 24px {SANS}; letter-spacing:5px; color:{C['ivory']}; opacity:.7; }}
        #root .hh {{ position:absolute; left:110px; right:110px; top:350px; font:600 84px/1.05 {SERIF}; color:{C['ivory']}; }}
        #root .plot {{ position:absolute; left:0; top:0; }}
        #root .tk text {{ font:500 24px {SANS}; fill:{C['ivory']}; fill-opacity:.6; }}
        #root .lbl {{ font:500 26px {SANS}; fill:{C['ivory']}; }}
        #root .endv {{ position:absolute; right:110px; font:600 92px/1 {SERIF}; color:{C['ivory']}; text-align:right; }}
        #root .endl {{ position:absolute; right:110px; font:500 24px {SANS}; color:{C['red']}; text-align:right; }}
        #root .note {{ position:absolute; left:110px; right:110px; top:1240px; font:500 32px/1.3 {SANS}; color:{C['ivory']}; }}
        #root .src {{ position:absolute; left:110px; top:1330px; font:500 20px {SANS}; color:{C['ivory']}; opacity:.6; }}
    """
    js = [f'tl.fromTo("#br-in",{{opacity:0}},{{opacity:1,duration:0.2,ease:"none"}},{t0:.3f});',
          reveal("#br-k", t0 + 0.05), reveal("#br-h", t0 + 0.1),
          f'tl.fromTo("#br-s",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,duration:0.3}},{t0 + 0.1:.3f});',
          reveal("#br-st", t0 + 0.15),
          f'tl.fromTo("#br-l",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:1.3,ease:"power1.inOut"}},{t0 + 0.2:.3f});',
          f'tl.fromTo("#br-r",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.5,ease:"power2.out"}},{t_red:.3f});',
          f'tl.fromTo("#br-e",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,duration:0.3}},{t_red + 0.4:.3f});',
          reveal("#br-v", t_red + 0.4), reveal("#br-vl", t_red + 0.55), reveal("#br-note", t_red + 0.7),
          f'tl.fromTo("#br .src",{{opacity:0}},{{opacity:0.6,duration:0.3}},{t0 + 0.5:.3f});',
          f'tl.to("#br-in",{{opacity:0,duration:0.2}},{t1 - 0.2:.3f});']
    return scene("ov-brl", inner, css, "\n".join("          " + j for j in js))


def ov_items(spans):
    els, js = [], []
    for i, s in enumerate(spans):
        o, t0, t1 = s["o"], s["t0"], s["t1"]
        d = t1 - t0
        if o.get("chip"):
            els.append(f'<div id="cp{i}" class="clip chip" data-start="{t0 + 0.15:.3f}" data-duration="{d - 0.15:.3f}" data-track-index="0">'
                       f'<div class="ci"><span class="dot"></span>{esc(o["chip"])}</div></div>')
            js += [reveal(f"#cp{i} .ci", t0 + 0.15), hide(f"#cp{i} .ci", t1 - 0.22)]
        if o.get("foot"):
            els.append(f'<div id="ft{i}" class="clip foot" data-start="{t0 + 0.4:.3f}" data-duration="{d - 0.4:.3f}" data-track-index="1"><div class="fi">{esc(o["foot"])}</div></div>')
            js += [f'tl.fromTo("#ft{i} .fi",{{opacity:0}},{{opacity:0.7,duration:0.3}},{t0 + 0.4:.3f});', hide(f"#ft{i} .fi", t1 - 0.22)]
        if o.get("num"):
            nm = o["num"]
            tn = t0 + nm.get("at", 0.15)
            dim = '<div class="ndim"></div>' if s["mode"] == "broll" else ""
            red = f'<div class="nrule" style="background:{C["red"] if nm.get("red", True) else C["gold"]}"></div>'
            els.append(f'<div id="nm{i}" class="clip num" data-start="{t0:.3f}" data-duration="{d:.3f}" data-track-index="3">{dim}'
                       f'<div class="nb"><div class="nn" style="font-size:{nm.get("size", 170)}px">{esc(nm["n"])}</div>{red}'
                       f'<div class="nl">{esc(nm["label"])}</div><div class="ns">{esc(nm.get("src", ""))}</div></div></div>')
            js += [reveal(f"#nm{i} .nn", tn), f'tl.fromTo("#nm{i} .nrule",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{tn + 0.15:.3f});',
                   reveal(f"#nm{i} .nl", tn + 0.25), f'tl.fromTo("#nm{i} .ns",{{opacity:0}},{{opacity:0.6,duration:0.3}},{tn + 0.35:.3f});',
                   hide(f"#nm{i} .nb", t1 - 0.22)]
        if s["mode"] == "split":
            els.append(f'<div id="sl{i}" class="clip split" data-start="{t0:.3f}" data-duration="{d:.3f}" data-track-index="2">'
                       f'<div class="rule"></div><div class="shade"></div>'
                       f'<div class="sh"><div class="h1">{esc(o["head"])}</div><div class="h2">{esc(o["sub"])}</div></div></div>')
            js += [f'tl.fromTo("#sl{i} .rule",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{t0:.3f});',
                   reveal(f"#sl{i} .h1", t0 + 0.15), reveal(f"#sl{i} .h2", t0 + 0.3), hide(f"#sl{i} .sh", t1 - 0.22)]
        if s["mode"] == "sf06":
            els.append(f'<div id="sx{i}" class="clip sf06" data-start="{t0:.3f}" data-duration="{d:.3f}" data-track-index="2">'
                       f'<div class="dim"></div><div class="si"><div class="idx" data-layout-allow-overlap>{esc(o["idx"])}</div><div class="big" data-layout-allow-overlap>{esc(o["big"])}</div>'
                       f'<div class="ln">{esc(o["line"])}</div></div></div>')
            js += [reveal(f"#sx{i} .idx", t0 + 0.1), reveal(f"#sx{i} .big", t0 + 0.2), reveal(f"#sx{i} .ln", t0 + 0.4), hide(f"#sx{i} .si", t1 - 0.22)]
    css = f"""
        #root .clip {{ position:absolute; inset:0; }}
        #root .chip {{ display:flex; justify-content:center; }}
        #root .ci {{ position:absolute; top:1235px; display:flex; align-items:center; gap:14px; padding:14px 30px; border-radius:60px;
                    background:rgba(11,43,34,.72); border:1.5px solid {C['gold']}; font:500 30px {SANS}; color:{C['ivory']}; }}
        #root .dot {{ width:11px; height:11px; border-radius:50%; background:{C['gold']}; }}
        #root .num .ndim {{ position:absolute; inset:0; background:linear-gradient(180deg,rgba(7,12,16,.35) 0%,rgba(7,12,16,.25) 40%,rgba(7,12,16,.85) 100%); }}
        #root .nb {{ position:absolute; left:110px; right:110px; top:960px; }}
        #root .nn {{ font-family:{SERIF}; font-weight:600; line-height:0.95; color:{C['ivory']}; text-shadow:0 4px 30px rgba(7,12,16,.6); white-space:nowrap; }}
        #root .nrule {{ width:220px; height:3px; margin-top:12px; transform-origin:0 50%; }}
        #root .nl {{ margin-top:14px; font:500 30px/1.3 {SANS}; color:{C['ivory']}; text-shadow:0 2px 12px rgba(7,12,16,.85); }}
        #root .ns {{ margin-top:10px; font:500 20px {SANS}; color:{C['ivory']}; opacity:.6; }}
        #root .fi {{ position:absolute; left:0; right:0; text-align:center; top:1330px; font:500 21px {SANS}; color:{C['ivory']}; }}
        #root .rule {{ position:absolute; left:0; right:0; top:959px; height:2px; background:{C['gold']}; }}
        #root .shade {{ position:absolute; left:0; right:0; top:961px; bottom:0; background:linear-gradient(180deg,{C['night']}cc 0%,{C['night']}33 35%,{C['night']}00 55%,{C['night']}cc 100%); }}
        #root .sh {{ position:absolute; left:110px; right:110px; top:1000px; }}
        #root .h1 {{ font:600 72px/1.05 {SERIF}; color:{C['ivory']}; }}
        #root .h2 {{ margin-top:10px; font:500 26px/1.3 {SANS}; color:{C['ivory']}; opacity:.8; }}
        #root .sf06 .dim {{ position:absolute; inset:0; background:linear-gradient(180deg,{C['night']}80 0%,{C['night']}40 30%,{C['night']}cc 60%,{C['night']}f0 100%); }}
        #root .si {{ position:absolute; left:110px; right:110px; top:880px; }}
        #root .idx {{ font:500 24px {SANS}; letter-spacing:5px; color:{C['gold']}; }}
        #root .big {{ font:600 230px/0.9 {SERIF}; color:{C['gold']}; margin-top:28px; }}
        #root .ln {{ font:500 58px/1.12 {SERIF}; color:{C['ivory']}; margin-top:6px; }}
    """
    return scene("ov-items", "\n".join("        " + e for e in els), css, "\n".join("          " + j for j in js))


def ov_l3(spans):
    s = next(s for s in spans if s["o"].get("l3"))
    t0, t1 = s["t0"], s["t1"]
    inner = f"""        <div id="l3" class="clip" data-start="{t0 + 0.2:.3f}" data-duration="{t1 - t0 - 0.2:.3f}" data-track-index="0">
          <div class="l3bg"></div><div class="l3"><div class="rl"></div><div><div id="l3n" class="nm">Caio Rezende</div><div id="l3t" class="tt">Advogado e consultor imobiliário</div>
          <div id="l3x" class="tx">+10 anos em transações de alto valor · Allegiance</div></div></div></div>"""
    css = f"""
        #root .clip {{ position:absolute; inset:0; }}
        #root .l3bg {{ position:absolute; left:0; top:1040px; width:900px; height:260px; background:radial-gradient(60% 50% at 25% 50%, rgba(7,21,15,.7) 0%, rgba(7,21,15,.35) 60%, rgba(7,21,15,0) 100%); }}
        #root .l3 {{ position:absolute; left:110px; top:1100px; display:flex; gap:24px; }}
        #root .rl {{ width:2px; background:{C['gold']}; transform-origin:50% 0; }}
        #root .nm {{ font:600 66px/1 {SERIF}; color:{C['ivory']}; }}
        #root .tt {{ margin-top:10px; font:500 28px {SANS}; color:{C['gold']}; }}
        #root .tx {{ margin-top:8px; font:500 22px {SANS}; color:{C['ivory']}; opacity:.75; }}
    """
    js = [f'tl.fromTo("#l3 .rl",{{scaleY:0}},{{scaleY:1,duration:0.4,ease:"power2.out"}},{t0 + 0.2:.3f});',
          reveal("#l3n", t0 + 0.3), reveal("#l3t", t0 + 0.45), reveal("#l3x", t0 + 0.6), hide("#l3 .l3", t1 - 0.25), hide("#l3 .l3bg", t1 - 0.25), f'tl.fromTo("#l3 .l3bg",{{opacity:0}},{{opacity:1,duration:0.3}},{t0 + 0.2:.3f});']
    return scene("ov-l3", inner, css, "\n".join("          " + j for j in js))


def ov_creds(spans, sfx):
    cs = [s for s in spans if s["mode"] == "creds"]
    t0, t1 = cs[0]["t0"], cs[-1]["t1"]
    step = {s["o"]["step"]: s["t0"] for s in cs}
    t_off = step.get("offices", t0 + 1.0)
    t_seal = step.get("seals", t_off + 1.5)
    t_aed = step.get("aed", t0 + 0.9)
    t_press = step.get("press", step.get("aed", t_seal) + 1.0)
    cities = "".join(f'<span class="cty{" hq" if c == "DUBAI" else ""}">{"<i></i>" if c == "DUBAI" else ""}{c}</span>'
                     for c in ["DUBAI", "BEIRUT", "PARIS", "RIYADH", "SYDNEY", "TOKYO", "LJUBLJANA"])
    inner = f"""        <div id="cr" class="clip" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="0">
          <div id="cr-in" class="crin">
            <img id="cr-logo" class="logo" src="assets/allegiance-logo-gold.png" alt="Allegiance Real Estate">
            <div id="cr-tag" class="tag">CONSULTORIA GLOBAL DE INVESTIMENTOS</div>
            <div class="stats">
              <div id="st0" class="st"><b>AED 20B+</b><span>em transações</span></div>
              <div id="st1" class="st"><b>5.000+</b><span>clientes</span></div>
              <div id="st2" class="st"><b>7</b><span>escritórios</span></div>
            </div>
            <div id="cr-cty" class="cities">{cities}</div>
            <div class="seals"><div id="sl0" class="seal"><b>RERA</b><span>Real Estate Regulatory Agency</span></div>
              <div id="sl1" class="seal"><b>DLD</b><span>Dubai Land Department</span></div></div>
            <div id="cr-pr" class="press"><div class="k">COMO VISTO EM</div><div class="pl">Forbes · Business Insider · Gulf News · CEO Weekly</div>
              <div class="gr">Google Reviews 4,9/5</div></div>
            <div class="src crs">Fonte: Allegiance, perfil institucional</div>
          </div>
        </div>"""
    css = f"""
        #root .clip {{ position:absolute; inset:0; }}
        #root .crin {{ position:absolute; inset:0; background:radial-gradient(90% 60% at 50% 35%, #0f3a2d 0%, {C['emerald']} 55%, {C['night']} 100%); }}
        #root .logo {{ position:absolute; left:50%; margin-left:-300px; top:300px; width:600px; }}
        #root .tag {{ position:absolute; left:0; right:0; top:460px; text-align:center; font:500 22px {SANS}; letter-spacing:6px; color:{C['champ']}; }}
        #root .stats {{ position:absolute; left:90px; right:90px; top:560px; display:flex; justify-content:space-between; text-align:center; }}
        #root .st {{ width:300px; white-space:nowrap; }}
        #root .st b {{ display:block; font:600 66px/1 {SERIF}; color:{C['gold']}; }}
        #root .st span {{ display:block; margin-top:8px; font:500 24px {SANS}; color:{C['ivory']}; }}
        #root .cities {{ position:absolute; left:120px; right:120px; top:760px; text-align:center; font:500 25px/1.9 {SANS}; letter-spacing:3px; }}
        #root .cty {{ display:inline-block; margin:0 14px; color:{C['ivory']}; }}
        #root .cty.hq {{ color:{C['gold']}; }}
        #root .cty i {{ display:inline-block; width:12px; height:12px; border-radius:50%; background:{C['gold']}; margin-right:10px; vertical-align:2px; }}
        #root .seals {{ position:absolute; left:0; right:0; top:900px; display:flex; justify-content:center; gap:30px; }}
        #root .seal {{ width:330px; height:120px; border:1.5px solid {C['gold']}; border-radius:14px; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
        #root .seal b {{ font:600 46px/1 {SERIF}; color:{C['ivory']}; letter-spacing:4px; }}
        #root .seal span {{ margin-top:8px; font:500 18px {SANS}; color:{C['champ']}; }}
        #root .press {{ position:absolute; left:0; right:0; top:1080px; text-align:center; }}
        #root .press .k {{ font:500 22px {SANS}; letter-spacing:6px; color:{C['gold']}; }}
        #root .press .pl {{ margin-top:14px; font:500 30px {SANS}; color:{C['ivory']}; opacity:.75; }}
        #root .press .gr {{ margin-top:12px; font:500 22px {SANS}; color:{C['ivory']}; opacity:.75; }}
        #root .src {{ position:absolute; left:110px; font:500 20px {SANS}; color:{C['ivory']}; opacity:.6; }}
        #root .crs {{ top:1290px; }}
    """
    js = [f'tl.fromTo("#cr-in",{{opacity:0}},{{opacity:1,duration:0.2,ease:"none"}},{t0:.3f});',
          reveal("#cr-logo", t0 + 0.1), reveal("#cr-tag", t0 + 0.3), reveal("#st1", t0 + 0.6),
          reveal("#st2", t_off), reveal("#cr-cty", t_off + 0.2),
          f'tl.fromTo("#cr-cty i",{{scale:1}},{{scale:1.6,duration:0.6,ease:"sine.inOut",yoyo:true,repeat:3}},{t_off + 0.5:.3f});',
          reveal("#sl0", t_seal), reveal("#sl1", t_seal + 0.4), reveal("#st0", t_aed), reveal("#cr-pr", t_press),
          f'tl.fromTo("#cr .src",{{opacity:0}},{{opacity:0.6,duration:0.3}},{t0 + 0.5:.3f});',
          f'tl.to("#cr-in",{{opacity:0,duration:0.2}},{t1 - 0.2:.3f});']
    sfx += [("impact-bass-1", t_seal, 2.1, 0.12), ("impact-bass-1", t_seal + 0.4, 2.1, 0.10)]
    return scene("ov-creds", inner, css, "\n".join("          " + j for j in js))


def ov_end(spans, t_end):
    s = next(s for s in spans if s["mode"] == "end")
    t0 = s["t0"]
    inner = f"""        <div id="ec" class="clip" data-start="{t0:.3f}" data-duration="{t_end - t0:.3f}" data-track-index="0">
          <div id="ec-g" class="grad"></div>
          <div id="ec-cover" class="cover"></div>
          <div class="blk">
            <div id="ec-k" class="k">CORTESIA ALLEGIANCE</div>
            <div id="ec-h" class="h">Consulta inicial<br>com Caio Rezende</div>
            <div id="ec-s" class="s">Entenda como proteger seu patrimônio<br>e investir nos Emirados Árabes Unidos.</div>
            <div id="ec-b" class="btn">Agende sua consulta</div>
            <img id="ec-l" class="lg" src="assets/allegiance-logo-gold.png" alt="Allegiance Real Estate">
            <div id="ec-r" class="r">Caio Rezende · RERA BRN 100501</div>
          </div>
        </div>"""
    css = f"""
        #root .clip {{ position:absolute; inset:0; }}
        #root .grad {{ position:absolute; inset:0; background:linear-gradient(180deg, {C['emerald']}00 0%, {C['emerald']}00 28%, {C['emerald']}e6 44%, {C['emerald']} 52%); }}
        #root .cover {{ position:absolute; inset:0; background:{C['emerald']}; }}
        #root .blk {{ position:absolute; left:80px; right:80px; top:880px; text-align:center; }}
        #root .k {{ font:500 24px {SANS}; letter-spacing:6px; color:{C['gold']}; }}
        #root .h {{ margin-top:22px; font:600 88px/1.02 {SERIF}; color:{C['ivory']}; }}
        #root .s {{ margin-top:22px; font:500 28px/1.4 {SANS}; color:{C['ivory']}; opacity:.85; }}
        #root .btn {{ margin:30px auto 0; width:520px; padding:24px 0; border-radius:60px; background:{C['gold']}; color:{C['emerald']}; font:600 34px {SANS}; }}
        #root .lg {{ display:block; margin:34px auto 0; width:300px; }}
        #root .r {{ margin-top:12px; font:500 20px {SANS}; color:{C['ivory']}; opacity:.6; }}
    """
    js = [f'tl.fromTo("#ec-g",{{opacity:0}},{{opacity:1,duration:0.5,ease:"power1.out"}},{t0:.3f});',
          f'tl.fromTo("#ec-cover",{{opacity:0}},{{opacity:1,duration:1.0,ease:"power1.inOut"}},{s["t1"] - 0.2:.3f});',
          reveal("#ec-k", t0 + 0.2), reveal("#ec-h", t0 + 0.35), reveal("#ec-s", t0 + 0.6), reveal("#ec-b", t0 + 0.85),
          reveal("#ec-l", t0 + 1.05), reveal("#ec-r", t0 + 1.2)]
    return scene("ov-end", inner, css, "\n".join("          " + j for j in js))


WORDS = []
WEAK = set("a o e os as do da de dos das no na nos nas em um uma que com pra por para ao à é sobre entre mais".split())
MAXC = 54  # ~2 lines of 42px Montserrat in an 880px box


def fit2(text):
    """Split a sentence into chunks that each fit on two lines, preferring commas."""
    if len(text) <= MAXC:
        return [text]
    words = text.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) > MAXC:
            break
        last = words[i - 1].lower().strip(",.:;")
        weak = last in WEAK
        score = abs(len(a) - len(b)) - (40 if a[-1] in ",.:;" else 0) + (60 if weak else 0)
        if best is None or score < best[0]:
            best = (score, a, b)
    a, b = best[1], best[2]
    return [a] + fit2(b)


def captions(spans):
    els, js = [], []
    n = 0
    for s in spans:
        caps = s["o"].get("cap")
        if caps is None and WORDS and s["a"] is not None:
            ws = [w for w in WORDS if w["start"] >= s["a"] - 0.05 and w["end"] <= s["b"] + 0.05]
            chunks = fit2(" ".join(w["text"] for w in ws))
            k = 0
            for ci, c in enumerate(chunks):
                nw = len(c.split())
                st = s["t0"] if ci == 0 else tmap(s, ws[k]["start"]) - 0.05
                en = s["t1"] if ci == len(chunks) - 1 else tmap(s, ws[k + nw]["start"]) - 0.06
                els.append(f'<div id="cap{n}" class="clip cap" data-start="{st + 0.02:.3f}" data-duration="{en - st - 0.05:.3f}" data-track-index="0"><div class="ct">{esc(c)}</div></div>')
                js += [reveal(f"#cap{n} .ct", st + 0.02), hide(f"#cap{n} .ct", en - 0.18, 0.15)]
                n += 1
                k += nw
            continue
        caps = [c2 for c in (caps or []) for c2 in fit2(c)]
        if not caps:
            continue
        t0, t1 = s["t0"], s["t1"]
        tot = sum(len(c) for c in caps)
        t = t0
        for c in caps:
            d = (t1 - t0) * len(c) / tot
            st, en = t + 0.02, t + d - 0.03
            els.append(f'<div id="cap{n}" class="clip cap" data-start="{st:.3f}" data-duration="{en - st:.3f}" data-track-index="0"><div class="ct">{esc(c)}</div></div>')
            js += [reveal(f"#cap{n} .ct", st), hide(f"#cap{n} .ct", en - 0.15, 0.15)]
            n += 1
            t += d
    css = f"""
        #root .cap {{ position:absolute; left:0; right:0; top:1320px; height:200px; }}
        #root .ct {{ position:absolute; left:100px; right:100px; bottom:0; text-align:center; font:500 42px/1.3 {SANS}; color:{C['ivory']};
                    text-shadow:0 2px 14px rgba(7,21,15,.75), 0 0 2px rgba(7,21,15,.9); }}
    """
    return scene("captions", "\n".join("        " + e for e in els), css, "\n".join("          " + j for j in js))


# ----------------------------------------------------------------- root ----
def build(cfg):
    spans, talk = layout(cfg)
    end_at = talk + HOLD
    total = round(end_at + OUTRO_LEN, 2)
    sfx = []
    global WORDS
    WORDS = []
    if cfg.get("words"):
        WORDS = [w for w in json.load(open(os.path.join(SHARED, cfg["words"])))["words"] if w.get("type", "word") == "word"]
    gap = next((s for s in spans if s["mode"] == "gap"), None)
    if gap:
        dark_end, c_up = gap["t0"], gap["t1"]
    else:
        c_up = next(s for s in spans if s["mode"] == "chart")["t0"]
        dark_end = c_up + 0.8
    files = {"captions.html": captions(spans), "ov-items.html": ov_items(spans), "ov-l3.html": ov_l3(spans),
             "ov-creds.html": ov_creds(spans, sfx), "ov-end.html": ov_end(spans, end_at)}
    comps = [("ov-items", 6), ("ov-l3", 6), ("ov-creds", 6), ("ov-end", 7), ("captions", 9)]
    if any(s["mode"] == "brazil" for s in spans):
        files["ov-open.html"] = ov_open(spans)[0]
        comps.insert(0, ("ov-open", 5))
    if any(s["mode"] == "brl" for s in spans):
        files["ov-brl.html"] = ov_brl(spans)
        comps.insert(0, ("ov-brl", 5))

    vids, bvids, js = [], [], []
    for i, s in enumerate(spans):
        d = s["t1"] - s["t0"]
        if s["mode"] == "end":
            d += HOLD
        m = s["mode"]
        if m == "gap":
            continue
        clip = "inset(0 0 50% 0)" if m == "split" else "none"
        s0 = 1.15 if m == "punch" else 1.0
        org = "50% 30%"
        vids.append(f'      <div class="sp" style="clip-path:{clip}"><div id="mv{i}" class="mv" style="transform-origin:{org}">'
                    f'<video id="tk{i}" class="clip" src="assets/{'caio-cold' if s['o'].get('cold') else 'caio'}.mp4" playsinline data-has-audio="true" data-start="{s["t0"]:.3f}" '
                    f'data-duration="{d:.3f}" data-media-start="{s["ms"]:.3f}" data-track-index="{1 + 6 * (i % 2)}" data-volume="1"></video></div></div>')
        js.append(f'      tl.set("#mv{i}", {{ scale:{s0} }}, {s["t0"]:.3f});')
        clipname = s["o"].get("clip")
        if clipname:
            bt0, bt1 = s["t0"], s["t1"]
            bclip = "inset(50% 0 0 0)" if m == "split" else "none"
            bvids.append(f'      <div class="bw" style="clip-path:{bclip}"><div id="bm{i}" class="bm"><video id="bv{i}" class="clip" src="assets/broll/{clipname}.mp4" muted playsinline '
                         f'data-start="{bt0:.3f}" data-duration="{bt1 - bt0:.3f}" data-media-start="0.3" data-track-index="2"></video></div></div>')
            js.append(f'      tl.fromTo("#bm{i}", {{ scale:1.03 }}, {{ scale:1.0, duration:{bt1 - bt0:.3f}, ease:"none" }}, {bt0:.3f});')

    hosts = []
    for cid, z in comps:
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="0" '
                     f'data-duration="{end_at:.3f}" data-track-index="{3 if cid != "captions" else 4}" data-track-kind="{"captions" if cid == "captions" else "graphics"}" '
                     f'data-width="{W}" data-height="{H}" style="z-index:{z}"></div>')
    aud = [f'      <audio id="sfx{i}" src="assets/sfx/{f}.mp3" data-start="{t:.3f}" data-duration="{d}" data-track-index="{11 + (i % 2)}" data-volume="{v:.2f}"></audio>'
           for i, (f, t, d, v) in enumerate(sfx)]
    idx = f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8">
    <title>Allegiance - {cfg['out']}</title>
    <script src="assets/gsap.min.js"></script>
    <style>
{FONTS}
      body {{ margin:0; background:#000; }}
      #root {{ position:relative; width:100%; height:100%; overflow:hidden; background:{C['night']}; }}
      #root > div[data-composition-src] {{ position:absolute; inset:0; }}
      .sp {{ position:absolute; inset:0; z-index:1; overflow:hidden; }}
      .mv {{ position:absolute; inset:0; }}
      .mv video, .bm video {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; }}
      .bw {{ position:absolute; inset:0; z-index:3; overflow:hidden; }}
      .bm {{ position:absolute; inset:0; transform-origin:50% 50%; }}
      #vig {{ position:absolute; inset:0; z-index:4; pointer-events:none;
              background:radial-gradient(120% 75% at 50% 42%, rgba(7,21,15,0) 55%, rgba(7,21,15,.55) 100%),
                         linear-gradient(180deg, rgba(7,21,15,0) 58%, rgba(7,21,15,.6) 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="root" data-start="0" data-width="{W}" data-height="{H}" data-duration="{total}">
{chr(10).join(vids)}
{chr(10).join(bvids)}
      <div id="vig"></div>
{chr(10).join(hosts)}
      <div id="ow" class="bw" style="z-index:12"><div class="bm"><video id="outro" class="clip" src="assets/outro.mp4" muted playsinline data-start="{end_at:.3f}" data-duration="{OUTRO_LEN}" data-media-start="0" data-track-index="8"></video></div></div>
      <audio id="music-dark" src="assets/music-dark.mp3" data-start="0" data-duration="{dark_end:.3f}" data-media-start="{cfg.get('dark_ms', 0)}" data-track-index="9" data-volume="{cfg.get('dark_vol', 0.22)}" data-fade-in="0.3" data-fade-out="{0.25 if gap else 0.9}"></audio>
      <audio id="music" src="assets/music.mp3" data-start="{c_up:.3f}" data-duration="{total - c_up:.3f}" data-media-start="0" data-track-index="10" data-volume="0.12" data-fade-in="{0.05 if gap else 0.6}" data-fade-out="3"></audio>
{chr(10).join(aud)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      tl.fromTo("#ow", {{ opacity:0 }}, {{ opacity:1, duration:0.4, ease:"power1.inOut" }}, {end_at:.3f});
      window.__timelines["root"] = tl;
    </script>
  </body>
</html>
"""
    out = os.path.join(HERE, cfg["out"])
    comp, assets = os.path.join(out, "compositions"), os.path.join(out, "assets")
    for d in (comp, os.path.join(assets, "sfx"), os.path.join(assets, "broll"), os.path.join(assets, "fonts")):
        os.makedirs(d, exist_ok=True)

    def cp(src, dst):
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
            shutil.copy(src, dst)
    cp(os.path.join(SHARED, cfg["src"]), os.path.join(assets, "caio.mp4"))
    for b in sorted(f[:-4] for f in os.listdir(os.path.join(SHARED, "broll-lux"))):
        cp(os.path.join(SHARED, "broll-lux", b + ".mp4"), os.path.join(assets, "broll", b + ".mp4"))
    cp(os.path.join(SHARED, "outro-1080.mp4"), os.path.join(assets, "outro.mp4"))
    cp(os.path.join(SHARED, "music-lux.mp3"), os.path.join(assets, "music.mp3"))
    cp(os.path.join(SHARED, cfg.get("dark", "music-dark.mp3")), os.path.join(assets, "music-dark.mp3"))
    if cfg.get("src_cold"):
        cp(os.path.join(SHARED, cfg["src_cold"]), os.path.join(assets, "caio-cold.mp4"))
    cp(os.path.join(SHARED, "allegiance-logo-gold.png"), os.path.join(assets, "allegiance-logo-gold.png"))
    cp(os.path.join(SHARED, "impact-bass-1.mp3"), os.path.join(assets, "sfx", "impact-bass-1.mp3"))
    for f in os.listdir(os.path.join(SHARED, "fonts")):
        cp(os.path.join(SHARED, "fonts", f), os.path.join(assets, "fonts", f))
    shutil.copy(os.path.join(HERE, "..", "vendor", "gsap.min.js"), os.path.join(assets, "gsap.min.js"))
    for k, v in files.items():
        open(os.path.join(comp, k), "w", encoding="utf-8").write(v)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(idx)
    json.dump({"id": cfg["out"], "name": cfg["file"]}, open(os.path.join(out, "meta.json"), "w"), indent=2)
    shutil.copy(os.path.join(HERE, "..", "hyperframes.json"), os.path.join(out, "hyperframes.json"))
    json.dump({"name": cfg["out"], "private": True, "type": "module", "scripts": {
        "check": "npx --yes hyperframes@0.8.137 check", "render": "npx --yes hyperframes@0.8.137 render"}},
        open(os.path.join(out, "package.json"), "w"), indent=2)
    # Caio-on-screen share (full/punch/end count fully, split counts half)
    caio = sum((s["t1"] - s["t0"]) * (1 if s["mode"] in ("full", "punch", "end", "brazil") else 1 if s["mode"] == "split" else 0) for s in spans)
    print(f"wrote {out}: talk {talk:.1f}s, end card hold to {end_at:.1f}s, total {total}s, Caio on screen {caio / talk * 100:.0f}%")


if __name__ == "__main__":
    which = sys.argv[1:] or ["long", "short"]
    for w in which:
        build(dict(long=LONG, short=SHORT, v3=V3, v4=V4)[w])
