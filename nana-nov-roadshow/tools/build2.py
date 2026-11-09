"""Generate the Nana Nov Roadshow v2 composition from the edited video.

Usage: python3 -I build2.py <fontsource_pkg_dir> <project_dir> <overlay|clean>

  overlay  subtitles sit on a translucent dark pill (as in v1)
  clean    subtitles have no pill, only an outline and soft shadow
"""
import html, os, re, shutil, sys

FONT_PKG, P, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
assert MODE in ("overlay", "clean")
FPS = 30
CUT_FRAMES = [0, 295, 698, 1042, 1229, 1490]   # shot boundaries in the edit
CUTS = [f / FPS for f in CUT_FRAMES]
HANDLE = 0.2                                   # frozen frames each side of a cut
XF = 0.4                                       # crossfade length
SPEECH_END = CUTS[-1]                          # 49.667
END_START = 49.35
END_DUR = 3.9
TOTAL = round(END_START + END_DUR, 3)

# Speech islands (seconds in the edit) and the phrases spoken in each.
ISLANDS = [
    (0.44, 2.30, ["ドバイ不動産アリージェンスと"]),
    (2.52, 5.35, ["中東民間最大デベロッパー", "ダマックが"]),
    (5.56, 6.75, ["今月[[11月]]も"]),
    (6.88, 9.75, ["再び東京で", "特別イベントを開催いたします"]),
    (10.11, 11.28, ["[[2026年]]"]),
    (11.39, 13.55, ["ドバイ不動産投資で注目したいのは"]),
    (13.76, 14.48, ["海沿いの"]),
    (14.59, 16.40, ["高級コンドミニアムだけでなく"]),
    (16.67, 18.10, ["商業用オフィスや"]),
    (18.30, 20.85, ["ヴィラ・タウンハウスなど", "土地付きの戸建てなど"]),
    (21.05, 23.20, ["さまざまな投資の選択肢があります"]),
    (23.45, 24.60, ["今回のイベントでは"]),
    (24.73, 27.75, ["このような最新プロジェクトの", "ご紹介に加えて"]),
    (27.96, 29.40, ["イベント参加者限定の"]),
    (29.47, 31.45, ["ドバイ旅行[[無料ご招待]]や"]),
    (31.74, 34.70, ["大幅なディスカウント交渉の", "機会も設けております"]),
    (35.00, 35.75, ["開催日は"]),
    (35.84, 38.45, ["[[11月28日と29日]]"]),
    (38.81, 40.93, ["会場は", "[[銀座ブルガリタワー]]です"]),
    (41.24, 43.95, ["今年最後の東京開催と", "なりますので"]),
    (44.28, 45.30, ["ドバイ不動産や"]),
    (45.37, 47.25, ["海外投資にご興味をお持ちの方は"]),
    (47.42, 49.40, ["ぜひお気軽にご参加ください"]),
]

VENUE_IN, VENUE_OUT = 39.2, 41.6          # full-frame hotel photo
DATE_IN, DATE_DUR = 35.55, 3.15

def plain(s):
    return s.replace("[[", "").replace("]]", "")

groups = []
for a, b, phrases in ISLANDS:
    lens = [len(plain(p)) for p in phrases]
    tot, acc = sum(lens), 0
    for p, n in zip(phrases, lens):
        s0 = a + (b - a) * acc / tot
        acc += n
        groups.append([s0, a + (b - a) * acc / tot, p])

# Keep every caption clear of the transitions; the venue cut hides under the photo.
guard = [c for c in CUTS[1:-1] if not (VENUE_IN < c < VENUE_OUT)]
cap = []
for i, (s0, s1, p) in enumerate(groups):
    st = max(0.12, s0 - 0.06)
    nxt = groups[i + 1][0] - 0.06 if i + 1 < len(groups) else s1 + 0.3
    en = min(max(s1 + 0.15, st + 0.5), nxt)
    for c in guard:
        if st < c + HANDLE and en > c - HANDLE:
            if s0 >= c - 0.05:
                st = max(st, c + HANDLE)
            else:
                en = min(en, c - HANDLE)
    en = min(en, SPEECH_END)
    cap.append((round(st, 2), round(en - st, 2), p))

# ---------------------------------------------------------------- fonts
EXTRA = ("開催日会場銀座ブルガリタワー東京特別イベント土日・アリージェンス×ダマック"
         "ドバイ不動産月年ご参加お待ちしております今年最後の()")
used = {ord(c) for c in "".join(plain(p) for _, _, p in cap) + EXTRA if ord(c) > 0x7F}

def parse_ranges(rng):
    out = []
    for part in rng.split(","):
        part = part.strip().replace("U+", "")
        lo, _, hi = part.partition("-")
        out.append((int(lo, 16), int(hi or lo, 16)))
    return out

font_dir = os.path.join(P, "assets", "fonts")
shutil.rmtree(font_dir, ignore_errors=True)
os.makedirs(font_dir)
faces = []
for w in (700, 900):
    css = open(os.path.join(FONT_PKG, f"{w}.css"), encoding="utf-8").read()
    for blk in re.findall(r"@font-face\s*{(.*?)}", css, re.S):
        fn = re.search(r"url\(\./files/([^)]+\.woff2)\)", blk).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", blk).group(1)
        if any(lo <= cp <= hi for cp in used for lo, hi in parse_ranges(rng)):
            shutil.copy(os.path.join(FONT_PKG, "files", fn), font_dir)
            faces.append("@font-face{font-family:'NotoJP';font-style:normal;font-weight:%d;"
                         "font-display:block;src:url('assets/fonts/%s') format('woff2');unicode-range:%s;}"
                         % (w, fn, rng))
FONT_CSS = "\n".join(faces)

TOKENS = """      --navy: #0d1524;
      --gold: #d9b56a;
      --gold-hi: #f3d58e;
      --ink: #ffffff;
"""

def esc(s):
    return html.escape(s, quote=True)

def rich(p):
    out = []
    for part in re.split(r"(\[\[.*?\]\])", p):
        if part.startswith("[["):
            out.append('<span class="hl">%s</span>' % esc(part[2:-2]))
        elif part:
            out.append(esc(part))
    return "".join(out)

def comp(cid, css, body, js):
    return f"""<template>
  <style>
{FONT_CSS}
    #root {{
      position: absolute;
      inset: 0;
{TOKENS}    }}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""

def write(name, text):
    open(os.path.join(P, "compositions", name), "w", encoding="utf-8").write(text)

os.makedirs(os.path.join(P, "compositions"), exist_ok=True)
for f in os.listdir(os.path.join(P, "compositions")):
    os.remove(os.path.join(P, "compositions", f))

# ---------------------------------------------------------------- captions
if MODE == "overlay":
    txt_style = """      padding: 10px 26px 14px;
      border-radius: 18px;
      background: rgba(10, 14, 24, 0.42);
      text-shadow: 0 3px 10px rgba(0, 0, 0, 0.55);"""
else:
    o = "rgba(8,10,16,0.92)"
    ring = ", ".join(f"{x}px {y}px 0 {o}" for x, y in
                     [(-3, -3), (0, -4), (3, -3), (4, 0), (3, 3), (0, 4), (-3, 3), (-4, 0)])
    txt_style = f"""      padding: 10px 26px 14px;
      text-shadow: {ring}, 0 6px 16px rgba(0, 0, 0, 0.6);"""

cap_css = f"""
    .cap {{
      position: absolute;
      left: 0;
      right: 0;
      top: 1180px;
      height: 150px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: visible;
    }}
    .cap-txt {{
      display: inline-block;
      font-family: 'NotoJP', sans-serif;
      font-weight: 900;
      color: var(--ink);
      line-height: 1.25;
      white-space: nowrap;
      letter-spacing: 0.01em;
{txt_style}
    }}
    .hl {{
      color: #1a1408;
      text-shadow: none;
      padding: 0 10px;
      margin: 0 4px;
      border-radius: 10px;
      background-image: linear-gradient(90deg, var(--gold-hi), var(--gold));
      background-repeat: no-repeat;
      background-position: left center;
      background-size: 100% 100%;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
    }}
"""
cap_html, cap_js = [], []
for i, (st, du, p) in enumerate(cap):
    fs = int(min(80, max(50, 900 / max(len(plain(p)), 1))))
    gid = f"cap-{i:02d}"
    # Full-body shots (first and last): lift the line up to hand height.
    top = 885 if st < CUTS[1] else (815 if st >= CUTS[4] else None)
    pos = f' style="top:{top}px"' if top else ""
    cap_html.append(f'    <div id="{gid}" class="clip cap" data-start="{st}" data-duration="{du}"{pos}>'
                    f'<span class="cap-txt" style="font-size:{fs}px">{rich(p)}</span></div>')
    cap_js.append(f'    tl.fromTo("#{gid} .cap-txt", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power2.out" }}, {st});')
    if "[[" in p:
        cap_js.append(f'    tl.fromTo("#{gid} .hl", {{ backgroundSize: "0% 100%" }}, {{ backgroundSize: "100% 100%", duration: 0.35, ease: "power2.out" }}, {round(st + 0.12, 2)});')
    cap_js.append(f'    tl.to("#{gid} .cap-txt", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {round(st + du - 0.1, 2)});')
write("captions.html", comp("captions", cap_css, "\n".join(cap_html), "\n".join(cap_js)))

# ---------------------------------------------------------------- intro tag
write("intro.html", comp("intro", """
    #intro-tag { position: absolute; left: 0; right: 0; top: 745px; display: flex; justify-content: center; }
    #intro-pill {
      display: flex; flex-direction: column; align-items: center; gap: 6px;
      padding: 20px 44px 22px; border-radius: 26px;
      background: rgba(13, 21, 36, 0.72); border: 2px solid rgba(217, 181, 106, 0.75);
    }
    #intro-brand { font-family: Montserrat, sans-serif; font-weight: 700; font-size: 34px; letter-spacing: 0.22em; color: var(--gold-hi); }
    #intro-sub { font-family: 'NotoJP', sans-serif; font-weight: 700; font-size: 40px; color: var(--ink); letter-spacing: 0.06em; }
""", """    <div id="intro-tag" class="clip" data-start="0" data-duration="5">
      <div id="intro-pill">
        <div id="intro-brand" data-var-text="introBrand">ALLEGIANCE × DAMAC</div>
        <div id="intro-sub" data-var-text="introSub">東京特別イベント 2026.11</div>
      </div>
    </div>""", """    tl.fromTo("#intro-pill", { opacity: 0, y: -30, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }, 0.25);
    tl.to("#intro-pill", { opacity: 0, y: -20, duration: 0.4, ease: "power2.in" }, 4.5);"""))

# ---------------------------------------------------------------- date card (2/3 of v1)
write("date-card.html", comp("date-card", """
    #date-wrap { position: absolute; left: 0; right: 0; top: 860px; display: flex; justify-content: center; }
    #date-card {
      padding: 22px 40px 26px; border-radius: 26px; text-align: center;
      background: rgba(13, 21, 36, 0.82); border: 2px solid rgba(217, 181, 106, 0.8);
      box-shadow: 0 20px 56px rgba(0, 0, 0, 0.4);
    }
    #date-label { font-family: 'NotoJP', sans-serif; font-weight: 700; font-size: 26px; letter-spacing: 0.3em; color: var(--gold); }
    #date-row { margin-top: 4px; display: flex; align-items: baseline; justify-content: center; gap: 14px; color: var(--ink); }
    .date-num { font-family: Montserrat, sans-serif; font-weight: 700; font-size: 88px; letter-spacing: -0.02em; line-height: 1; }
    .date-dow { font-family: 'NotoJP', sans-serif; font-weight: 700; font-size: 30px; color: var(--gold-hi); }
    #date-amp { font-family: Montserrat, sans-serif; font-weight: 700; font-size: 48px; color: var(--gold); }
    #date-rule { margin: 16px auto 0; height: 4px; width: 70%; border-radius: 2px; background: linear-gradient(90deg, var(--gold), var(--gold-hi)); transform-origin: left center; }
""", f"""    <div id="date-wrap" class="clip" data-start="0" data-duration="{DATE_DUR}">
      <div id="date-card">
        <div id="date-label">開催日</div>
        <div id="date-row">
          <div class="date-num" id="date-a">11.28</div><div class="date-dow">(土)</div>
          <div id="date-amp">&amp;</div>
          <div class="date-num" id="date-b">29</div><div class="date-dow">(日)</div>
        </div>
        <div id="date-rule"></div>
      </div>
    </div>""", f"""    tl.fromTo("#date-card", {{ opacity: 0, y: 30, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }}, 0);
    tl.fromTo("#date-a", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.15);
    tl.fromTo("#date-b", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.7);
    tl.fromTo("#date-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power2.out" }}, 0.4);
    tl.to("#date-card", {{ opacity: 0, y: -18, duration: 0.3, ease: "power2.in" }}, {round(DATE_DUR - 0.32, 2)});"""))

# ---------------------------------------------------------------- venue cutaway (full-frame photo)
VDUR = round(VENUE_OUT - VENUE_IN, 2)
write("venue.html", comp("venue", """
    #venue-frame { position: absolute; inset: 0; overflow: hidden; background: #0d1524; }
    #venue-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 40%; }
    #venue-shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,12,20,0.55) 0%, rgba(8,12,20,0) 26%, rgba(8,12,20,0) 55%, rgba(8,12,20,0.5) 100%); }
    #venue-label { position: absolute; left: 0; right: 0; top: 210px; text-align: center; }
    #venue-k { font-family: 'NotoJP', sans-serif; font-weight: 700; font-size: 34px; letter-spacing: 0.32em; color: var(--gold-hi); }
    #venue-en { margin-top: 8px; font-family: Montserrat, sans-serif; font-weight: 700; font-size: 34px; letter-spacing: 0.26em; color: #fff; text-shadow: 0 3px 12px rgba(0,0,0,0.6); }
    #venue-rule { margin: 16px auto 0; width: 160px; height: 4px; border-radius: 2px; background: linear-gradient(90deg, var(--gold), var(--gold-hi)); }
""", f"""    <div id="venue-frame" class="clip" data-start="0" data-duration="{VDUR}">
      <img id="venue-photo" src="assets/images/venue.jpg" data-var-src="venuePhoto" alt="銀座ブルガリタワー" />
      <div id="venue-shade"></div>
      <div id="venue-label">
        <div id="venue-k">会場</div>
        <div id="venue-en">BVLGARI GINZA TOWER</div>
        <div id="venue-rule"></div>
      </div>
    </div>""", f"""    tl.fromTo("#venue-frame", {{ opacity: 0 }}, {{ opacity: 1, duration: {XF}, ease: "power2.inOut" }}, 0);
    tl.fromTo("#venue-photo", {{ scale: 1.12 }}, {{ scale: 1.0, duration: {VDUR}, ease: "power1.out" }}, 0);
    tl.fromTo("#venue-label", {{ opacity: 0, y: -16 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.25);
    tl.fromTo("#venue-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power2.out" }}, 0.4);
    tl.to("#venue-frame", {{ opacity: 0, duration: {XF}, ease: "power2.inOut" }}, {round(VDUR - XF, 2)});"""))

# ---------------------------------------------------------------- end card
write("end-card.html", comp("end-card", """
    #end-bg { position: absolute; inset: 0; background: radial-gradient(110% 70% at 50% 35%, #1b2740 0%, #0d1524 55%, #070b14 100%); }
    #end-wrap { position: absolute; left: 80px; right: 80px; top: 470px; text-align: center; color: var(--ink); }
    #end-brand { font-family: Montserrat, sans-serif; font-weight: 700; font-size: 40px; letter-spacing: 0.24em; color: var(--gold-hi); }
    #end-title { margin-top: 26px; font-family: 'NotoJP', sans-serif; font-weight: 900; font-size: 96px; line-height: 1.2; }
    #end-rule { margin: 40px auto; width: 260px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, var(--gold), var(--gold-hi)); }
    .end-line { white-space: nowrap; font-family: 'NotoJP', sans-serif; font-weight: 700; font-size: 46px; line-height: 1.5; }
    .end-line .k { color: var(--gold); margin-right: 18px; }
    #end-cta { margin-top: 60px; display: inline-block; padding: 22px 54px 26px; border-radius: 60px; background: linear-gradient(90deg, var(--gold), var(--gold-hi)); color: #1a1408; font-family: 'NotoJP', sans-serif; font-weight: 900; font-size: 52px; }
""", f"""    <div id="end-bg" class="clip" data-start="0" data-duration="{END_DUR}"></div>
    <div id="end-wrap" class="clip" data-start="0" data-duration="{END_DUR}">
      <div id="end-brand">ALLEGIANCE × DAMAC</div>
      <div id="end-title">東京特別イベント</div>
      <div id="end-rule"></div>
      <div class="end-line" id="end-date"><span class="k">開催日</span>2026年11月28日(土)・29日(日)</div>
      <div class="end-line" id="end-venue"><span class="k">会場</span>銀座ブルガリタワー</div>
      <div id="end-cta">ご参加お待ちしております</div>
    </div>""", """    tl.fromTo("#end-bg", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, 0);
    tl.fromTo("#end-brand", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 0.35);
    tl.fromTo("#end-title", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, 0.5);
    tl.fromTo("#end-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.75);
    tl.fromTo("#end-date", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 0.9);
    tl.fromTo("#end-venue", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 1.1);
    tl.fromTo("#end-cta", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)" }, 1.35);"""))

# ---------------------------------------------------------------- root
shots, js = [], []
for i in range(5):
    pre = 0 if i == 0 else HANDLE
    post = 0 if i == 4 else HANDLE
    st = round(CUTS[i] - pre, 4)
    du = round(CUTS[i + 1] - CUTS[i] + pre + post, 4)
    shots.append(
        f'      <div id="shot{i+1}" class="shot" style="z-index:{i+1}">\n'
        f'        <video id="v{i+1}" class="clip" src="assets/shots/s{i+1}.mp4" data-start="{st}" '
        f'data-duration="{du}" data-track-index="0" muted playsinline></video>\n      </div>')
    js.insert(0, f'      gsap.set("#shot{i+1}", {{ opacity: {0 if i else 1}, scale: {1.045 if i else 1} }});')
    if i > 0:
        c = CUTS[i]
        js.append(f'      tl.to("#shot{i+1}", {{ opacity: 1, duration: {XF}, ease: "power1.inOut" }}, {round(c - HANDLE, 3)});')
        js.append(f'      tl.to("#shot{i+1}", {{ scale: 1, duration: 0.8, ease: "power2.out" }}, {round(c - HANDLE, 3)});')
        js.append(f'      tl.to("#shot{i}", {{ scale: 1.025, duration: {XF}, ease: "power1.in" }}, {round(c - HANDLE, 3)});')

sfx_times = [CUTS[1], CUTS[2], CUTS[3], VENUE_IN + 0.2, VENUE_OUT - 0.2]
sfx = []
for k, t in enumerate(sfx_times):
    vol = 0.32 if k < 4 else 0.22
    sfx.append(f'      <audio id="sfx{k+1}" src="assets/audio/whoosh.wav" data-start="{round(t - 0.42, 3)}" '
               f'data-duration="0.75" data-track-index="7" data-volume="{vol}"></audio>')

def host(hid, start, dur, track, kind="graphics", z=20):
    return (f'      <div id="{hid}" data-composition-id="{hid}" data-composition-src="compositions/{hid}.html" '
            f'data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="{kind}" '
            f'data-width="1080" data-height="1920" style="z-index:{z}"></div>')

hosts = [
    host("intro", 0, 5, 1, z=20),
    host("date-card", DATE_IN, DATE_DUR, 2, z=20),
    host("venue", VENUE_IN, VDUR, 3, z=15),
    host("captions", 0, SPEECH_END, 4, kind="captions", z=30),
    host("end-card", END_START, END_DUR, 5, z=40),
]
variables = ('[{"id":"venuePhoto","type":"string","label":"Venue photo","default":"assets/images/venue.jpg"},'
             '{"id":"introBrand","type":"string","label":"Intro brand line","default":"ALLEGIANCE × DAMAC"},'
             '{"id":"introSub","type":"string","label":"Intro sub line","default":"東京特別イベント 2026.11"}]')
music = ""
if os.path.exists(os.path.join(P, "assets", "audio", "music.mp3")):
    music = (f'      <audio id="music" src="assets/audio/music.mp3" data-start="0" data-duration="{TOTAL}" '
             f'data-track-index="6" data-volume="1"></audio>\n')

root = f"""<!doctype html>
<html lang="ja" data-composition-variables='{variables}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0d1524; }}
      #root {{ position: relative; width: 100%; height: 100%; background: #0d1524; }}
      .shot {{ position: absolute; inset: 0; overflow: hidden; }}
      .shot video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(shots)}
      <audio id="voice" src="assets/audio/voice.wav" data-start="0" data-duration="{round(SPEECH_END, 3)}" data-track-index="5"></audio>
{music}{chr(10).join(sfx)}
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(P, "index.html"), "w", encoding="utf-8").write(root)
print("mode", MODE, "total", TOTAL, "music", bool(music))
for st, du, p in cap:
    print(f"{st:6.2f} +{du:4.2f}  {p}")

# ---------------------------------------------------------------- square (1:1) variant
# Usage: add a 4th argument "square" to re-lay the same edit out at 1080x1080.
# The 9:16 footage is cropped 168 px from the top (object-position 50% 20%),
# and every overlay is moved by hand for the shorter frame.
if len(sys.argv) > 4 and sys.argv[4] == "square":
    Y0 = 168
    SQ_CROP = {1: 60, 2: 168, 3: 168, 4: 120, 5: 168}
    def patch(path, pairs):
        t = open(path, encoding="utf-8").read()
        for a, b in pairs:
            assert a in t, (path, a)
            t = t.replace(a, b)
        open(path, "w", encoding="utf-8").write(t)
    C = lambda n: os.path.join(P, "compositions", n)
    for n in os.listdir(os.path.join(P, "compositions")):
        patch(C(n), [('data-height="1920"', 'data-height="1080"')])
    patch(os.path.join(P, "index.html"), [
        ('content="width=1080, height=1920"', 'content="width=1080, height=1080"'),
        ("height: 1920px;", "height: 1080px;"),
        ('data-height="1920"', 'data-height="1080"'),
        ("object-fit: cover; }", f"object-fit: cover; object-position: 50% {Y0 / 840 * 100:.2f}%; }}"),
        # per-shot crop from the top (px of the 1920 frame): keep headroom on each shot
        ("    </style>", "".join(f"      #v{k} {{ object-position: 50% {y / 840 * 100:.2f}%; }}\n"
                                   for k, y in SQ_CROP.items()) + "    </style>"),
    ])
    patch(C("captions.html"), [
        ("top: 1180px;", "top: 860px;"),
        ('style="top:885px"', f'style="top:{885 - SQ_CROP[1]}px"'),
        ('style="top:815px"', f'style="top:{815 - Y0}px"'),
    ])
    patch(C("intro.html"), [("top: 745px;", f"top: {745 - SQ_CROP[1]}px;")])
    patch(C("date-card.html"), [("top: 860px;", "top: 640px;")])
    patch(C("venue.html"), [("top: 210px;", "top: 110px;")])
    patch(C("end-card.html"), [
        ("top: 470px;", "top: 150px;"),
        ("font-size: 96px;", "font-size: 84px;"),
        ("margin: 40px auto;", "margin: 28px auto;"),
        ("margin-top: 60px;", "margin-top: 40px;"),
    ])
    print("square layout applied")
