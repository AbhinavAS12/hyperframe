#!/usr/bin/env python3
"""Build the reel from edit.json: stabilized shot clips, the HyperFrames scene files and index.html.

usage: python3 tools/build_reel.py [--footage DIR] [--no-stab] [--force-stab] [--only-html]

The edit lives in edit.json, timed in BEATS so it can be re-cut to a new music track by changing
`bpm`, `beat0_s` and the music clips. Beat k lands at beat0_s + k * 60 / bpm, rounded to a frame.

Every shot is stabilized from its 4K original (tools/stabilize.sh) into assets/clips/<scene>-<id>.mp4,
with handles, so trims in Studio have room. Each shot is three nested wrappers around its <video>:
  .tr  transitions (zoom punch between shots, whip pans, flash settle)
  .pu  punch-ins on a beat (instant scale steps)
  .mo  the shot's own move (slow push, drift)
so the three kinds of motion never fight over one transform.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920

ZOOM_OUT_DUR = 0.16    # outgoing shot accelerates into the cut
ZOOM_IN_DUR = 0.36     # incoming shot lands and settles
WHIP_DUR = 0.30        # one strip, power3.inOut, centered on the cut
FLASH_SETTLE = 0.42
HANDLE = 0.4           # seconds of extra source kept on each side of a shot


def load_edit():
    with open(os.path.join(ROOT, "edit.json")) as f:
        return json.load(f)


class Clock:
    def __init__(self, edit):
        self.fps = edit.get("fps", 30)
        self.beat = 60.0 / edit["bpm"]
        self.beat0 = edit.get("beat0_s", 0.0)

    def t(self, beat):
        """Film time of a beat index, rounded to a frame (computed from the index, never accumulated)."""
        return round((self.beat0 + beat * self.beat) * self.fps) / self.fps

    def r(self, seconds):
        return round(seconds * self.fps) / self.fps


def fmt(x):
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def source_advance(dur, rate=1.0, ramp=None):
    """Seconds of source consumed by a clip of `dur` seconds at a constant rate or along a rate lane."""
    if not ramp:
        return dur * rate
    pts = sorted(ramp, key=lambda p: p[0])
    n = 400
    total = 0.0
    for i in range(n):
        t = (i + 0.5) * dur / n
        if t <= pts[0][0]:
            v = pts[0][1]
        elif t >= pts[-1][0]:
            v = pts[-1][1]
        else:
            for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
                if t0 <= t <= t1:
                    v = v0 + (v1 - v0) * (t - t0) / (t1 - t0)
                    break
        total += v * dur / n
    return total


def plan(edit):
    """Resolve every shot to film/scene times and the source window it needs."""
    clk = Clock(edit)
    scenes = []
    for sc in edit["scenes"]:
        s0 = clk.t(sc["start_beat"])
        shots = []
        b = sc["start_beat"]
        for sh in sc["shots"]:
            start, end = clk.t(b), clk.t(b + sh["beats"])
            shots.append({**sh, "beat": b, "abs_start": start, "abs_end": end,
                          "start": start - s0, "end": end - s0})
            b += sh["beats"]
        if abs(b - sc["end_beat"]) > 1e-6:
            sys.exit(f"scene {sc['id']}: shots cover {b - sc['start_beat']} beats, scene spans "
                     f"{sc['end_beat'] - sc['start_beat']}")
        # transitions widen the visible window of the shots on either side of a cut
        for i, sh in enumerate(shots):
            sh["pre"], sh["post"] = 0.0, 0.0
        for i, sh in enumerate(shots):
            enter = (sh.get("enter") or "cut")
            if enter.startswith("whip") and i > 0:
                sh["pre"] = WHIP_DUR / 2
                shots[i - 1]["post"] = WHIP_DUR / 2
        for sh in shots:
            vis = (sh["end"] + sh["post"]) - (sh["start"] - sh["pre"])
            rate = sh.get("rate", 1.0)
            ramp = sh.get("ramp")
            sh["vis_start"] = clk.r(sh["start"] - sh["pre"])
            sh["vis_dur"] = clk.r(vis)
            pre_src = source_advance(sh["pre"], rate, None) if not ramp else sh["pre"] * ramp[0][1]
            sh["src_a"] = sh["in_s"] - pre_src
            sh["src_b"] = sh["src_a"] + source_advance(sh["vis_dur"], rate, ramp)
        scenes.append({**sc, "t0": s0, "t1": clk.t(sc["end_beat"]), "shots_resolved": shots})
    return clk, scenes


def stabilize(edit, scenes, footage, force=False, skip=False):
    os.makedirs(os.path.join(ROOT, "assets", "clips"), exist_ok=True)
    for sc in scenes:
        for sh in sc["shots_resolved"]:
            name = f"{sc['id']}-{sh['id']}"
            out = os.path.join(ROOT, "assets", "clips", f"{name}.mp4")
            src = os.path.join(footage, f"{sh['clip']}.MP4")
            a = max(0.0, sh["src_a"] - HANDLE)
            dur = (sh["src_b"] + HANDLE) - a
            st = sh.get("stab", {})
            fps = 50 if (sh.get("rate", 1.0) < 1.0 or sh.get("ramp")) else edit.get("fps", 30)
            args = [src, f"{a:.3f}", f"{dur:.3f}", out, str(fps), str(st.get("smooth", 15)),
                    str(st.get("margin", 1.10)), str(st.get("maxshift", 40)), str(st.get("maxangle", 0.012))]
            key = hashlib.sha1(json.dumps(args[:3] + args[4:]).encode()).hexdigest()[:12]
            sh["asset"] = f"assets/clips/{name}.mp4"
            sh["media_start"] = round(sh["src_a"] - a, 3)
            stamp = out + ".key"
            if skip or (not force and os.path.exists(out) and os.path.exists(stamp)
                        and open(stamp).read().strip() == key):
                continue
            if not os.path.exists(src):
                sys.exit(f"missing footage {src} (shot {name}); pass --footage DIR")
            print(f"stabilize {name}: {sh['clip']} {a:.2f}s +{dur:.2f}s @{fps}fps", flush=True)
            subprocess.run([os.path.join(ROOT, "tools", "stabilize.sh")] + args, check=True)
            with open(stamp, "w") as f:
                f.write(key + "\n")


def automation_attr(ramp):
    lane = {"version": 1, "lanes": [{"target": "rate",
                                     "points": [{"t": round(t, 3), "v": v} for t, v in ramp]}]}
    return escape(json.dumps(lane, separators=(",", ":")), quote=True)


def scene_html(edit, clk, sc):
    sid = sc["id"]
    shots = sc["shots_resolved"]
    dur = sc["t1"] - sc["t0"]
    lines = []
    lines.append("<template>")
    lines.append("  <style>")
    lines.append("    #root { position: absolute; inset: 0; overflow: hidden; background: #000; }")
    lines.append("    #root .tr, #root .pu, #root .mo { position: absolute; inset: 0; }")
    lines.append("    #root video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }")
    lines.append("  </style>")
    lines.append(f'  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">')
    for i, sh in enumerate(shots):
        name = f"{sid}-{sh['id']}"
        origin = sh.get("origin", "50% 50%")
        attrs = [f'id="{name}"', 'class="clip"', f'src="{sh["asset"]}"',
                 f'data-start="{fmt(sh["vis_start"])}"', f'data-duration="{fmt(sh["vis_dur"])}"',
                 f'data-media-start="{fmt(sh["media_start"])}"', f'data-track-index="{i % 2}"']
        if sh.get("ramp"):
            attrs.append(f'data-automation="{automation_attr(sh["ramp"])}"')
        elif sh.get("rate", 1.0) != 1.0:
            attrs.append(f'data-playback-rate="{fmt(sh["rate"])}"')
        attrs += ["muted", "playsinline"]
        note = sh.get("note", "")
        lines.append(f"    <!-- {name}: {sh['clip']} @{fmt(sh['in_s'])}s, {fmt(sh['beats'])} beats"
                     f"{' - ' + escape(note) if note else ''} -->")
        lines.append(f'    <div id="{name}-tr" class="tr" style="z-index: {i + 1}; transform-origin: {origin}">')
        lines.append(f'      <div id="{name}-pu" class="pu" style="transform-origin: {origin}">')
        lines.append(f'        <div id="{name}-mo" class="mo" style="transform-origin: {origin}">')
        lines.append(f"          <video {' '.join(attrs)}></video>")
        lines.append("        </div>")
        lines.append("      </div>")
        lines.append("    </div>")
    lines.append("  </div>")
    lines.append("  <script>")
    lines.append("    const tl = gsap.timeline({ paused: true });")
    for i, sh in enumerate(shots):
        name = f"#{sid}-{sh['id']}"
        s, e = sh["start"], sh["end"]
        vs, ve = sh["vis_start"], sh["vis_start"] + sh["vis_dur"]
        lines.append(f"    // {sid}-{sh['id']}")
        # the shot's own move, across its whole visible window
        mv = sh.get("move")
        if mv:
            frm = {"scale": mv.get("from", 1.0), "x": mv.get("x0", 0), "y": mv.get("y0", 0)}
            to = {"scale": mv.get("to", 1.0), "x": mv.get("x1", 0), "y": mv.get("y1", 0)}
            ease = mv.get("ease", "none")
            lines.append(f'    tl.fromTo("{name}-mo", {{ scale: {frm["scale"]}, x: {frm["x"]}, y: {frm["y"]} }}, '
                         f'{{ scale: {to["scale"]}, x: {to["x"]}, y: {to["y"]}, duration: {fmt(ve - vs)}, '
                         f'ease: "{ease}" }}, {fmt(vs)});')
        # punch-ins: instant steps on a beat (a hit is a 0 ms set; easing a hit kills it)
        punches = sh.get("punch", [])
        if punches:
            lines.append(f'    tl.set("{name}-pu", {{ scale: 1 }}, {fmt(vs)});')
            scale = 1.0
            for p in punches:
                pb = p["at"] if isinstance(p, dict) else p
                scale = p.get("scale", round(scale + 0.14, 3)) if isinstance(p, dict) else round(scale + 0.14, 3)
                lines.append(f'    tl.set("{name}-pu", {{ scale: {scale} }}, {fmt(clk.t(sh["beat"] + pb) - sc["t0"])});')
        # how this shot enters
        enter = sh.get("enter") or "cut"
        prev = f"#{sid}-{shots[i - 1]['id']}" if i > 0 else None
        if enter == "zoom":
            if prev:
                lines.append(f'    tl.fromTo("{prev}-tr", {{ scale: 1 }}, {{ scale: 1.32, duration: {ZOOM_OUT_DUR}, '
                             f'ease: "power3.in" }}, {fmt(s - ZOOM_OUT_DUR)});')
            lines.append(f'    tl.fromTo("{name}-tr", {{ scale: 1.24 }}, {{ scale: 1, duration: {ZOOM_IN_DUR}, '
                         f'ease: "expo.out" }}, {fmt(s)});')
        elif enter.startswith("whip"):
            sign = -1 if enter == "whip-left" else 1
            t0 = s - WHIP_DUR / 2
            if prev:
                lines.append(f'    tl.fromTo("{prev}-tr", {{ x: 0 }}, {{ x: {sign * W}, duration: {WHIP_DUR}, '
                             f'ease: "power3.inOut" }}, {fmt(t0)});')
            lines.append(f'    tl.fromTo("{name}-tr", {{ x: {-sign * W} }}, {{ x: 0, duration: {WHIP_DUR}, '
                         f'ease: "power3.inOut" }}, {fmt(t0)});')
        elif enter == "flash":
            # recipe: outgoing leans in just before the hit, incoming lands slightly large and settles
            if prev:
                lines.append(f'    tl.fromTo("{prev}-tr", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.12, '
                             f'ease: "power3.in" }}, {fmt(s - 0.16)});')
            lines.append(f'    tl.fromTo("{name}-tr", {{ scale: 1.1 }}, {{ scale: 1, duration: {FLASH_SETTLE}, '
                         f'ease: "power3.out" }}, {fmt(s)});')
        # a scene's last shot may lean into a flash that opens the next scene
        if i == len(shots) - 1 and sc.get("exit") == "flash":
            lines.append(f'    tl.fromTo("{name}-tr", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.12, '
                         f'ease: "power3.in" }}, {fmt(e - 0.16)});')
    lines.append(f"    tl.set({{}}, {{}}, {fmt(dur)});")
    lines.append(f'    window.__timelines["{sid}"] = tl;')
    lines.append("  </script>")
    lines.append("</template>")
    return "\n".join(lines) + "\n"


def title_html(edit, clk):
    t = edit["title"]
    t_in = clk.t(t["in_beat"]) - clk.t(t["start_beat"])
    t_date = clk.t(t["date_beat"]) - clk.t(t["start_beat"])
    t_out = clk.t(t["out_beat"]) - clk.t(t["start_beat"])
    dur = clk.t(t["end_beat"]) - clk.t(t["start_beat"])
    variables = [
        {"id": "kicker", "type": "string", "label": "Kicker", "default": t["kicker"]},
        {"id": "line1", "type": "string", "label": "Title line 1", "default": t["line1"]},
        {"id": "line2", "type": "string", "label": "Title line 2", "default": t["line2"]},
        {"id": "italic", "type": "string", "label": "Italic line", "default": t["italic"]},
        {"id": "date", "type": "string", "label": "Date line", "default": t["date"]},
    ]
    var_attr = escape(json.dumps(variables), quote=True)
    return f"""<template>
  <style>
    @font-face {{
      font-family: "Source Serif 4";
      src: url("assets/fonts/SourceSerif4-Variable.ttf") format("truetype");
      font-style: normal;
      font-weight: 200 900;
    }}
    @font-face {{
      font-family: "Source Serif 4";
      src: url("assets/fonts/SourceSerif4-Italic-Variable.ttf") format("truetype");
      font-style: italic;
      font-weight: 200 900;
    }}
    #root {{
      position: absolute;
      inset: 0;
      overflow: hidden;
      --ink: #f2ede3;
    }}
    /* legibility scrim for bright footage: dark at the bottom, gone by the middle of the frame */
    #title-scrim {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 1180px;
      background: linear-gradient(to top, rgba(8, 10, 12, 0.72) 0%, rgba(8, 10, 12, 0.5) 38%, rgba(8, 10, 12, 0) 100%);
    }}
    #title-block {{
      position: absolute;
      left: 84px;
      right: 84px;
      bottom: 596px;
      color: var(--ink);
      text-shadow: 0 2px 18px rgba(0, 0, 0, 0.45);
    }}
    #title-kicker,
    #title-date {{
      font-family: "IBM Plex Mono", monospace;
      font-weight: 400;
      font-size: 30px;
      letter-spacing: 0.32em;
      text-transform: uppercase;
    }}
    #title-kicker {{
      margin-bottom: 30px;
    }}
    #title-date {{
      margin-top: 34px;
    }}
    #title-lines {{
      font-family: "Source Serif 4", serif;
      font-optical-sizing: none;
      font-variation-settings: "opsz" 20;
      font-weight: 420;
      font-size: 112px;
      line-height: 1.04;
      letter-spacing: -0.005em;
    }}
    #title-lines .it {{
      font-style: italic;
    }}
  </style>
  <div id="root" data-composition-id="title" data-width="{W}" data-height="{H}" data-composition-variables="{var_attr}">
    <div id="title-scrim" data-layout-ignore></div>
    <div id="title-block">
      <div id="title-kicker" data-var-text="kicker">{escape(t["kicker"])}</div>
      <div id="title-lines">
        <div id="title-line1" data-var-text="line1">{escape(t["line1"])}</div>
        <div id="title-line2" data-var-text="line2">{escape(t["line2"])}</div>
        <div id="title-italic" class="it" data-var-text="italic">{escape(t["italic"])}</div>
      </div>
      <div id="title-date" data-var-text="date">{escape(t["date"])}</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // in: the scrim breathes in, the kicker and the lines blur in one after another (the reference's entrance)
    tl.fromTo("#title-scrim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, {fmt(max(0, t_in - 0.2))});
    tl.fromTo("#title-kicker", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, {fmt(t_in)});
    tl.fromTo(["#title-line1", "#title-line2", "#title-italic"], {{ opacity: 0, filter: "blur(10px)" }},
      {{ opacity: 1, filter: "blur(0px)", duration: 0.42, ease: "power3.out", stagger: 0.09 }}, {fmt(t_in + 0.08)});
    tl.fromTo("#title-date", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, {fmt(t_date)});
    // out: one blur-out of the whole block, then the scrim
    tl.fromTo("#title-block", {{ opacity: 1, filter: "blur(0px)" }}, {{ opacity: 0, filter: "blur(8px)", duration: 0.24, ease: "power2.in" }}, {fmt(t_out)});
    tl.fromTo("#title-scrim", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {fmt(t_out + 0.05)});
    tl.set({{}}, {{}}, {fmt(dur)});
    window.__timelines["title"] = tl;
  </script>
</template>
"""


def index_html(edit, clk, scenes):
    dur = edit["duration_s"]
    out = []
    out.append("<!doctype html>")
    out.append('<html lang="en" data-resolution="portrait">')
    out.append("  <head>")
    out.append('    <meta charset="UTF-8" />')
    out.append(f'    <meta name="viewport" content="width={W}, height={H}" />')
    out.append(f"    <title>{escape(edit.get('name', 'Reel'))}</title>")
    out.append('    <script src="vendor/gsap.min.js"></script>')
    out.append("    <style>")
    out.append("      * { margin: 0; padding: 0; box-sizing: border-box; }")
    out.append(f"      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}")
    out.append("      #root { position: relative; width: 100%; height: 100%; overflow: hidden; }")
    out.append("      #outro { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }")
    out.append("    </style>")
    out.append("  </head>")
    out.append("  <body>")
    out.append(f'    <div id="root" data-composition-id="main" data-start="0" data-duration="{fmt(dur)}" '
               f'data-width="{W}" data-height="{H}" data-fps="{edit.get("fps", 30)}" data-motion-blur="on">')
    track = 0
    z = 1
    for sc in scenes:
        out.append(f'      <div id="{sc["id"]}" data-composition-id="{sc["id"]}" '
                   f'data-composition-src="compositions/{sc["id"]}.html" data-start="{fmt(sc["t0"])}" '
                   f'data-duration="{fmt(sc["t1"] - sc["t0"])}" data-track-index="{track}" data-track-kind="graphics" '
                   f'data-width="{W}" data-height="{H}" style="z-index: {z}"></div>')
        track = 1 - track
        z += 1
    o = edit["outro"]
    o_start = clk.t(o["start_beat"])
    out.append(f'      <video id="outro" class="clip" src="{o["src"]}" data-start="{fmt(o_start)}" '
               f'data-duration="{fmt(dur - o_start)}" data-media-start="{fmt(o.get("media_start_s", 0))}" '
               f'data-track-index="2" style="z-index: {z}" muted playsinline></video>')
    z += 1
    t = edit["title"]
    out.append(f'      <div id="title" data-composition-id="title" data-composition-src="compositions/title.html" '
               f'data-start="{fmt(clk.t(t["start_beat"]))}" '
               f'data-duration="{fmt(clk.t(t["end_beat"]) - clk.t(t["start_beat"]))}" data-track-index="4" '
               f'data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: {z + 2}"></div>')
    for k, fl in enumerate(edit.get("flashes", [])):
        d = fl.get("dur_s", 0.6)
        hit = max(0.12, d * 0.58)   # the block's own hit point
        st = clk.t(fl["at_beat"]) - hit
        out.append(f'      <div id="flash-{k + 1}" data-composition-id="editorial-flash-overlay" '
                   f'data-composition-src="compositions/editorial-flash-overlay.html" data-start="{fmt(clk.r(st))}" '
                   f'data-duration="{fmt(d)}" data-track-index="{5 + k}" data-track-kind="graphics" '
                   f'data-width="{W}" data-height="{H}" style="z-index: {z + 3}"></div>')
    for m in edit["music"]:
        m_start = clk.t(m["start_beat"])
        m_end = clk.t(m["end_beat"]) if "end_beat" in m else m["end_s"]
        attrs = [f'id="{m["id"]}"', f'src="{m["src"]}"', f'data-start="{fmt(m_start)}"',
                 f'data-duration="{fmt(m_end - m_start)}"', f'data-media-start="{fmt(m["media_start_s"])}"',
                 f'data-volume="{fmt(m.get("volume", 1))}"', f'data-track-index="{m.get("track", 8)}"']
        if m.get("fade_in_s"):
            attrs.append(f'data-fade-in="{fmt(m["fade_in_s"])}"')
        if m.get("fade_out_s"):
            attrs.append(f'data-fade-out="{fmt(m["fade_out_s"])}"')
        out.append(f"      <audio {' '.join(attrs)}></audio>")
    out.append("    </div>")
    out.append("    <script>")
    out.append("      window.__timelines = window.__timelines || {};")
    out.append(f'      window.__timelines["main"] = gsap.timeline({{ paused: true }}).set({{}}, {{}}, {fmt(dur)});')
    out.append("    </script>")
    out.append("  </body>")
    out.append("</html>")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--footage", default=os.environ.get("FOOTAGE_DIR", os.path.join(ROOT, "footage")))
    ap.add_argument("--no-stab", action="store_true", help="skip stabilization (clips must exist)")
    ap.add_argument("--force-stab", action="store_true")
    args = ap.parse_args()
    edit = load_edit()
    clk, scenes = plan(edit)
    stabilize(edit, scenes, args.footage, force=args.force_stab, skip=args.no_stab)
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for sc in scenes:
        with open(os.path.join(ROOT, "compositions", f"{sc['id']}.html"), "w") as f:
            f.write(scene_html(edit, clk, sc))
    with open(os.path.join(ROOT, "compositions", "title.html"), "w") as f:
        f.write(title_html(edit, clk))
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(index_html(edit, clk, scenes))
    # a readable cut list for the person and the next turn
    rows = ["| film time | scene | shot | clip @ in | beats | enter | move / punch | note |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for sc in scenes:
        for sh in sc["shots_resolved"]:
            mv = "push" if sh.get("move") else ""
            if sh.get("punch"):
                mv += (" + " if mv else "") + f"punch x{len(sh['punch'])}"
            if sh.get("ramp"):
                mv += (" + " if mv else "") + "speed ramp"
            rows.append(f"| {sh['abs_start']:.2f}-{sh['abs_end']:.2f} | {sc['id']} | {sh['id']} | "
                        f"{sh['clip']} @ {sh['in_s']:.2f}s | {fmt(sh['beats'])} | {sh.get('enter') or 'cut'} | "
                        f"{mv} | {sh.get('note', '')} |")
    with open(os.path.join(ROOT, "CUTLIST.md"), "w") as f:
        f.write("# Cut list\n\nGenerated by `tools/build_reel.py` from `edit.json`.\n\n" + "\n".join(rows) + "\n")
    print(f"built {sum(len(s['shots_resolved']) for s in scenes)} shots in {len(scenes)} scenes, "
          f"{edit['duration_s']}s")


if __name__ == "__main__":
    main()
