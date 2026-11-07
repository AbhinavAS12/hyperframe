"""Generate the Nana Nov Roadshow HyperFrames project files.

Usage: python3 -I build.py <scratchpad> <project_dir>
"""
import html, os, re, shutil, sys

S, P = sys.argv[1], sys.argv[2]
FONT_PKG = os.path.join(S, "npm", "package")

# ---------------------------------------------------------------- timeline
CLIPS = [  # id, file duration (s)
    ("c1", 10.6), ("c2", 14.4), ("c3", 12.3), ("c4", 7.3), ("c5", 9.7),
]
starts, t = {}, 0.0
for cid, d in CLIPS:
    starts[cid] = round(t, 3)
    t += d
SPEECH_END = round(t, 3)          # 54.3
END_CARD = 3.6
TOTAL = round(SPEECH_END + END_CARD, 3)

# Speech islands (clip-local seconds) and the phrases spoken in each.
# Phrases inside an island are timed by character share.
# Wrap a highlighted span in [[ ]].
ISLANDS = {
    "c1": [
        (0.22, 2.10, ["ドバイ不動産アリージェンスと"]),
        (2.27, 5.30, ["中東民間最大デベロッパー", "ダマックが"]),
        (5.34, 10.30, ["今月[[11月]]も再び東京で", "特別イベントを開催いたします"]),
    ],
    "c2": [
        (0.28, 1.48, ["[[2026年]]"]),
        (1.53, 3.80, ["ドバイ不動産投資で注目したいのは"]),
        (3.93, 4.68, ["海沿いの"]),
        (4.73, 6.70, ["高級コンドミニアムだけでなく"]),
        (6.81, 14.20, ["商業用オフィスや", "ヴィラ・タウンハウスなど", "土地付きの戸建てなど", "さまざまな投資の選択肢があります"]),
    ],
    "c3": [
        (0.28, 1.48, ["今回のイベントでは"]),
        (1.53, 4.65, ["このような最新プロジェクトの", "ご紹介に加えて"]),
        (4.76, 8.55, ["イベント参加者限定の", "ドバイ旅行[[無料ご招待]]や"]),
        (8.57, 12.20, ["大幅なディスカウント交渉の", "機会も設けております"]),
    ],
    "c4": [
        (0.32, 3.95, ["開催日は", "[[11月28日と29日]]"]),
        (4.09, 4.80, ["会場は"]),
        (4.83, 7.20, ["[[銀座ブルガリタワー]]です"]),
    ],
    "c5": [
        (0.28, 4.40, ["今年最後の東京開催と", "なりますので", "ドバイ不動産や"]),
        (4.40, 9.55, ["海外投資にご興味をお持ちの方は", "ぜひお気軽にご参加ください"]),
    ],
}

def plain(s):
    return s.replace("[[", "").replace("]]", "")

groups = []
for cid, islands in ISLANDS.items():
    base = starts[cid]
    for a, b, phrases in islands:
        lens = [len(plain(p)) for p in phrases]
        tot, acc = sum(lens), 0
        for p, n in zip(phrases, lens):
            s0 = a + (b - a) * acc / tot
            acc += n
            s1 = a + (b - a) * acc / tot
            groups.append((round(base + s0, 2), round(base + s1, 2), p))

# Make each group open a hair early and close right before the next opens.
cap = []
for i, (s0, s1, p) in enumerate(groups):
    st = max(0.12, s0 - 0.06)
    nxt = groups[i + 1][0] - 0.06 if i + 1 < len(groups) else s1 + 0.4
    en = min(max(s1, st + 0.5), nxt) if nxt > st + 0.3 else s1
    cap.append((round(st, 2), round(en - st, 2), p))

# ---------------------------------------------------------------- fonts
EXTRA_TEXT = (
    "開催日会場銀座ブルガリタワー東京特別イベント土日・アリージェンス×ダマック"
    "ドバイ不動産月年ご参加お待ちしております今年最後の"
)
used = set("".join(plain(p) for _, _, p in cap) + EXTRA_TEXT)
used = {ord(c) for c in used if ord(c) > 0x7F}

def parse_ranges(rng):
    out = []
    for part in rng.split(","):
        part = part.strip().replace("U+", "")
        if "-" in part:
            lo, hi = part.split("-")
            out.append((int(lo, 16), int(hi, 16)))
        else:
            out.append((int(part, 16), int(part, 16)))
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
        rs = parse_ranges(rng)
        if any(lo <= cp <= hi for cp in used for lo, hi in rs):
            shutil.copy(os.path.join(FONT_PKG, "files", fn), font_dir)
            faces.append(
                "@font-face{font-family:'NotoJP';font-style:normal;font-weight:%d;"
                "font-display:block;src:url('assets/fonts/%s') format('woff2');unicode-range:%s;}"
                % (w, fn, rng)
            )
FONT_CSS = "\n".join(faces)

# ---------------------------------------------------------------- shared style
TOKENS = """
      --navy: #0d1524;
      --gold: #d9b56a;
      --gold-hi: #f3d58e;
      --ink: #ffffff;
"""

def esc(s):
    return html.escape(s, quote=True)

def rich(p):
    out, parts = [], re.split(r"(\[\[.*?\]\])", p)
    for part in parts:
        if part.startswith("[["):
            out.append('<span class="hl">%s</span>' % esc(part[2:-2]))
        elif part:
            out.append(esc(part))
    return "".join(out)

def comp(cid, body_css, body_html, body_js, w=1080, h=1920):
    return f"""<template>
  <style>
{FONT_CSS}
    #root {{
      position: absolute;
      inset: 0;
{TOKENS}    }}
{body_css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{w}" data-height="{h}">
{body_html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{body_js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""

os.makedirs(os.path.join(P, "compositions"), exist_ok=True)

# ---------------------------------------------------------------- captions
cap_html, cap_js = [], []
for i, (st, du, p) in enumerate(cap):
    n = len(plain(p))
    fs = int(min(80, max(50, 900 / max(n, 1))))
    gid = f"cap-{i:02d}"
    cap_html.append(
        f'    <div id="{gid}" class="clip cap" data-start="{st}" data-duration="{du}">'
        f'<span class="cap-txt" style="font-size:{fs}px">{rich(p)}</span></div>'
    )
    cap_js.append(
        f'    tl.fromTo("#{gid} .cap-txt", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power2.out" }}, {st});'
    )
    if "[[" in p:
        cap_js.append(
            f'    tl.fromTo("#{gid} .hl", {{ backgroundSize: "0% 100%" }}, {{ backgroundSize: "100% 100%", duration: 0.35, ease: "power2.out" }}, {st + 0.12});'
        )
    cap_js.append(
        f'    tl.to("#{gid} .cap-txt", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {round(st + du - 0.1, 2)});'
    )

cap_css = """
    .cap {
      position: absolute;
      left: 0;
      right: 0;
      top: 1180px;
      height: 150px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: visible;
    }
    .cap-txt {
      display: inline-block;
      font-family: 'NotoJP', 'Noto Sans JP', sans-serif;
      font-weight: 900;
      color: var(--ink);
      line-height: 1.25;
      white-space: nowrap;
      padding: 10px 26px 14px;
      border-radius: 18px;
      background: rgba(10, 14, 24, 0.42);
      text-shadow: 0 3px 10px rgba(0, 0, 0, 0.55);
      letter-spacing: 0.01em;
    }
    .hl {
      color: #1a1408;
      text-shadow: none;
      padding: 0 10px;
      margin: 0 4px;
      border-radius: 10px;
      background-image: linear-gradient(90deg, var(--gold-hi), var(--gold));
      background-repeat: no-repeat;
      background-position: left center;
      background-size: 100% 100%;
    }
"""
open(os.path.join(P, "compositions", "captions.html"), "w", encoding="utf-8").write(
    comp("captions", cap_css, "\n".join(cap_html), "\n".join(cap_js))
)

# ---------------------------------------------------------------- intro tag
intro_css = """
    #intro-tag {
      position: absolute;
      left: 0;
      right: 0;
      top: 196px;
      display: flex;
      justify-content: center;
    }
    #intro-pill {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      padding: 20px 44px 22px;
      border-radius: 26px;
      background: rgba(13, 21, 36, 0.72);
      border: 2px solid rgba(217, 181, 106, 0.75);
    }
    #intro-brand {
      font-family: Montserrat, sans-serif;
      font-weight: 700;
      font-size: 34px;
      letter-spacing: 0.22em;
      color: var(--gold-hi);
    }
    #intro-sub {
      font-family: 'NotoJP', sans-serif;
      font-weight: 700;
      font-size: 40px;
      color: var(--ink);
      letter-spacing: 0.06em;
    }
"""
intro_html = """    <div id="intro-tag" class="clip" data-start="0" data-duration="5">
      <div id="intro-pill">
        <div id="intro-brand" data-var-text="introBrand">ALLEGIANCE × DAMAC</div>
        <div id="intro-sub" data-var-text="introSub">東京特別イベント 2026.11</div>
      </div>
    </div>"""
intro_js = """    tl.fromTo("#intro-pill", { opacity: 0, y: -30, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }, 0.25);
    tl.to("#intro-pill", { opacity: 0, y: -20, duration: 0.4, ease: "power2.in" }, 4.5);"""
open(os.path.join(P, "compositions", "intro.html"), "w", encoding="utf-8").write(
    comp("intro", intro_css, intro_html, intro_js)
)

# ---------------------------------------------------------------- date card
DATE_DUR = 2.9
date_css = """
    #date-card {
      position: absolute;
      left: 90px;
      right: 90px;
      top: 790px;
      padding: 34px 40px 40px;
      border-radius: 34px;
      background: rgba(13, 21, 36, 0.82);
      border: 2px solid rgba(217, 181, 106, 0.8);
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
      text-align: center;
    }
    #date-label {
      font-family: 'NotoJP', sans-serif;
      font-weight: 700;
      font-size: 38px;
      letter-spacing: 0.3em;
      color: var(--gold);
    }
    #date-row {
      margin-top: 8px;
      display: flex;
      align-items: baseline;
      justify-content: center;
      gap: 22px;
      color: var(--ink);
    }
    .date-num {
      font-family: Montserrat, sans-serif;
      font-weight: 700;
      font-size: 132px;
      letter-spacing: -0.02em;
      line-height: 1;
    }
    .date-dow {
      font-family: 'NotoJP', sans-serif;
      font-weight: 700;
      font-size: 44px;
      color: var(--gold-hi);
    }
    #date-amp {
      font-family: Montserrat, sans-serif;
      font-weight: 700;
      font-size: 70px;
      color: var(--gold);
    }
    #date-rule {
      margin: 24px auto 0;
      height: 6px;
      width: 70%;
      border-radius: 3px;
      background: linear-gradient(90deg, var(--gold), var(--gold-hi));
      transform-origin: left center;
    }
"""
date_html = f"""    <div id="date-card" class="clip" data-start="0" data-duration="{DATE_DUR}">
      <div id="date-label">開催日</div>
      <div id="date-row">
        <div class="date-num" id="date-a">11.28</div><div class="date-dow">(土)</div>
        <div id="date-amp">&amp;</div>
        <div class="date-num" id="date-b">29</div><div class="date-dow">(日)</div>
      </div>
      <div id="date-rule"></div>
    </div>"""
date_js = f"""    tl.fromTo("#date-card", {{ opacity: 0, y: 40, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }}, 0);
    tl.fromTo("#date-a", {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.15);
    tl.fromTo("#date-b", {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.75);
    tl.fromTo("#date-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power2.out" }}, 0.4);
    tl.to("#date-card", {{ opacity: 0, y: -24, duration: 0.3, ease: "power2.in" }}, {DATE_DUR - 0.32});"""
open(os.path.join(P, "compositions", "date-card.html"), "w", encoding="utf-8").write(
    comp("date-card", date_css, date_html, date_js)
)

# ---------------------------------------------------------------- venue card
VENUE_DUR = round(starts["c5"] + 0.9 - (starts["c4"] + 4.0), 2)
venue_css = """
    #venue-card {
      position: absolute;
      left: 90px;
      right: 90px;
      top: 470px;
      border-radius: 34px;
      overflow: hidden;
      background: rgba(13, 21, 36, 0.86);
      border: 2px solid rgba(217, 181, 106, 0.8);
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
    }
    #venue-photo-wrap {
      position: relative;
      height: 520px;
      overflow: hidden;
      background: radial-gradient(120% 90% at 50% 0%, #2a3550 0%, #121a2b 60%, #0b111d 100%);
    }
    #venue-photo {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    #venue-text {
      padding: 26px 40px 34px;
      text-align: center;
    }
    #venue-label {
      font-family: 'NotoJP', sans-serif;
      font-weight: 700;
      font-size: 36px;
      letter-spacing: 0.3em;
      color: var(--gold);
    }
    #venue-name {
      margin-top: 4px;
      font-family: 'NotoJP', sans-serif;
      font-weight: 900;
      font-size: 76px;
      color: var(--ink);
      letter-spacing: 0.02em;
      line-height: 1.2;
    }
    #venue-en {
      margin-top: 6px;
      font-family: Montserrat, sans-serif;
      font-weight: 700;
      font-size: 28px;
      letter-spacing: 0.26em;
      color: rgba(255, 255, 255, 0.7);
    }
"""
HAS_PHOTO = os.path.exists(os.path.join(P, "assets", "images", "venue.jpg"))
photo_block = """
      <div id="venue-photo-wrap">
        <img id="venue-photo" src="assets/images/venue.jpg" data-var-src="venuePhoto" alt="銀座ブルガリタワー" />
      </div>""" if HAS_PHOTO else ""
if not HAS_PHOTO:
    venue_css = venue_css.replace("top: 470px;", "top: 780px;")
venue_html = f"""    <div id="venue-card" class="clip" data-start="0" data-duration="{VENUE_DUR}">{photo_block}
      <div id="venue-text">
        <div id="venue-label">会場</div>
        <div id="venue-name" data-var-text="venueName">銀座ブルガリタワー</div>
        <div id="venue-en">BVLGARI GINZA TOWER · TOKYO</div>
      </div>
    </div>"""
venue_js = f"""    tl.fromTo("#venue-card", {{ opacity: 0, y: 50, scale: 0.95 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.4)" }}, 0);
""" + (f"""    tl.fromTo("#venue-photo", {{ scale: 1.14 }}, {{ scale: 1.0, duration: {VENUE_DUR}, ease: "none" }}, 0);
""" if HAS_PHOTO else "") + f"""    tl.fromTo("#venue-name", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, 0.25);
    tl.fromTo("#venue-en", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 0.45);
    tl.to("#venue-card", {{ opacity: 0, y: -24, duration: 0.35, ease: "power2.in" }}, {round(VENUE_DUR - 0.37, 2)});"""
open(os.path.join(P, "compositions", "venue-card.html"), "w", encoding="utf-8").write(
    comp("venue-card", venue_css, venue_html, venue_js)
)

# ---------------------------------------------------------------- end card
end_css = """
    #end-bg {
      position: absolute;
      inset: 0;
      background: radial-gradient(110% 70% at 50% 35%, #1b2740 0%, #0d1524 55%, #070b14 100%);
    }
    #end-wrap {
      position: absolute;
      left: 80px;
      right: 80px;
      top: 470px;
      text-align: center;
      color: var(--ink);
    }
    #end-brand {
      font-family: Montserrat, sans-serif;
      font-weight: 700;
      font-size: 40px;
      letter-spacing: 0.24em;
      color: var(--gold-hi);
    }
    #end-title {
      margin-top: 26px;
      font-family: 'NotoJP', sans-serif;
      font-weight: 900;
      font-size: 96px;
      line-height: 1.2;
    }
    #end-rule {
      margin: 40px auto;
      width: 260px;
      height: 6px;
      border-radius: 3px;
      background: linear-gradient(90deg, var(--gold), var(--gold-hi));
    }
    .end-line {
      white-space: nowrap;
      font-family: 'NotoJP', sans-serif;
      font-weight: 700;
      font-size: 46px;
      line-height: 1.5;
    }
    .end-line .k {
      color: var(--gold);
      margin-right: 18px;
    }
    #end-cta {
      margin-top: 60px;
      display: inline-block;
      padding: 22px 54px 26px;
      border-radius: 60px;
      background: linear-gradient(90deg, var(--gold), var(--gold-hi));
      color: #1a1408;
      font-family: 'NotoJP', sans-serif;
      font-weight: 900;
      font-size: 52px;
    }
"""
end_html = f"""    <div id="end-bg" class="clip" data-start="0" data-duration="{END_CARD}"></div>
    <div id="end-wrap" class="clip" data-start="0" data-duration="{END_CARD}">
      <div id="end-brand">ALLEGIANCE × DAMAC</div>
      <div id="end-title">東京特別イベント</div>
      <div id="end-rule"></div>
      <div class="end-line" id="end-date"><span class="k">開催日</span>2026年11月28日(土)・29日(日)</div>
      <div class="end-line" id="end-venue"><span class="k">会場</span>銀座ブルガリタワー</div>
      <div id="end-cta">ご参加お待ちしております</div>
    </div>"""
end_js = """    tl.fromTo("#end-bg", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, 0);
    tl.fromTo("#end-brand", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 0.2);
    tl.fromTo("#end-title", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, 0.35);
    tl.fromTo("#end-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.6);
    tl.fromTo("#end-date", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 0.75);
    tl.fromTo("#end-venue", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 0.95);
    tl.fromTo("#end-cta", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)" }, 1.2);"""
open(os.path.join(P, "compositions", "end-card.html"), "w", encoding="utf-8").write(
    comp("end-card", end_css, end_html, end_js)
)

# ---------------------------------------------------------------- root
vids = []
for i, (cid, d) in enumerate(CLIPS):
    vids.append(
        f'      <video id="{cid}" class="clip" src="assets/clips/{cid}.mp4" data-start="{starts[cid]}" '
        f'data-duration="{d}" data-track-index="0" data-has-audio="true" playsinline></video>'
    )

def host(hid, start, dur, track, kind="graphics", z=2):
    return (
        f'      <div id="{hid}" data-composition-id="{hid}" data-composition-src="compositions/{hid}.html" '
        f'data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="{kind}" '
        f'data-width="1080" data-height="1920" style="z-index:{z}"></div>'
    )

date_start = round(starts["c4"] + 1.15, 2)
venue_start = round(starts["c4"] + 4.0, 2)
hosts = [
    host("intro", 0, 5, 1, z=3),
    host("date-card", date_start, DATE_DUR, 2, z=3),
    host("venue-card", venue_start, VENUE_DUR, 3, z=3),
    host("captions", 0, SPEECH_END, 4, kind="captions", z=4),
    host("end-card", SPEECH_END, END_CARD, 5, z=5),
]
variables = (
    '[{"id":"venuePhoto","type":"string","label":"Venue photo","default":"assets/images/venue.jpg"},'
    '{"id":"venueName","type":"string","label":"Venue name","default":"銀座ブルガリタワー"},'
    '{"id":"introBrand","type":"string","label":"Intro brand line","default":"ALLEGIANCE × DAMAC"},'
    '{"id":"introSub","type":"string","label":"Intro sub line","default":"東京特別イベント 2026.11"}]'
)
root = f"""<!doctype html>
<html lang="ja" data-composition-variables='{variables}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background: #0d1524;
      }}
      #root {{
        position: relative;
        width: 100%;
        height: 100%;
        background: #0d1524;
      }}
      video.clip {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 1;
      }}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="{TOTAL}"
      data-width="1080"
      data-height="1920"
    >
{chr(10).join(vids)}
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(P, "index.html"), "w", encoding="utf-8").write(root)

print("clips", starts, "speech_end", SPEECH_END, "total", TOTAL)
print("date", date_start, DATE_DUR, "venue", venue_start, VENUE_DUR)
print("fonts", len(os.listdir(font_dir)), "files")
for st, du, p in cap:
    print(f"{st:6.2f} +{du:4.2f}  {p}")
