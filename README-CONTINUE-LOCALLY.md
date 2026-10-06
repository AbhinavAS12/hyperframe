# Continuing this project in Claude Code (your machine)

This is the full HyperFrames project for the **Dubai South & Al Maktoum
International Airport** investor video, built for Allegiance Real Estate.
It was authored in a cloud sandbox, which is why two things are still
missing: real Google Earth/Maps imagery and licensed Envato b-roll. Both
were blocked by the sandbox's network policy and lack of your logged-in
browser session — neither limitation applies on your own machine.

## What's in here

- `BRIEF.md`, `frame.md`, `STORYBOARD.md` — the intent, design spec, and
  scene-by-scene plan (narration text + timing + cited animation blueprints).
- `compositions/act1-hook.html` … `act5-conclusion.html` — the five scene
  compositions (GSAP timelines, HTML/CSS/SVG).
- `index.html` — the root composition that assembles all five scenes plus
  narration audio.
- `assets/voice/narration.wav` — the full narration track (Kokoro TTS,
  132.6s).
- `narration.txt` — the narration script as plain text.
- `vendor/gsap.min.js` — GSAP vendored locally (avoids a CDN dependency).
- `renders/` — the already-rendered MP4 from the cloud build (no music,
  generative maps, no stock footage).
- `snapshots/` — reference PNG stills of each scene for a quick visual check.

`node_modules/` was intentionally left out to keep this small — it isn't
needed (GSAP is already vendored), but `npm install` will recreate it if
any tool expects it.

## Setup

1. Install Node.js 18+ if you don't already have it.
2. From this folder, run:
   ```bash
   npx hyperframes doctor
   ```
   to confirm Chrome, ffmpeg, and the local TTS/audio tooling are available
   on your machine (Claude Code can install anything missing).
3. Preview the current build:
   ```bash
   npm run dev
   ```
4. Re-render after any change:
   ```bash
   npm run check   # lint + runtime + layout + motion + contrast gate
   npm run render  # renders to renders/
   ```

## Finishing the two deferred pieces

**Google Earth / Maps imagery** — your API key works fine from your own
network (it was only the cloud sandbox's egress policy blocking
`maps.googleapis.com`, not the key). Treat the key as a secret: keep it out
of anything you commit or share, and scope/restrict it in the Google Cloud
console to the Maps Static API and your own IP/referrer if you haven't
already. A natural approach: fetch satellite stills for the DXB/DWC and
Dubai South masterplan views via the Static Maps API, then overlay the
existing animated SVG boundary lines on top (the boundary coordinates in
`compositions/act2-megaproject.html` and `act3-dubaisouth.html` are already
geometrically close to the real masterplan shapes — swap the drawn `<path>`
backgrounds for the real satellite images and keep the draw-on animation).

**Envato b-roll** — with Envato Elements open and logged in in your own
Chrome, download the clips you want (candidates were shared in chat:
Dubai skyline aerials, DXB/DWC runway and construction footage, business
district and residential interiors, investor handshake shots). Drop the
downloaded MP4s into a new `assets/video/` folder, and swap the relevant
generative scene backgrounds for `<video muted>` elements referencing
them with `data-start`/`data-duration` matching the scene timing — see
`/hyperframes-core` → `references/creator-editing-recipes.md` (installed
under `.claude/skills/` or `.agents/skills/` once you run
`npx hyperframes skills update`) for the exact clip-placement contract.

## Everything else

Narration timing, the design palette (League Gothic + Space Mono, dark
premium finance palette), and all five scenes' structure are already
locked in `BRIEF.md` / `frame.md` / `STORYBOARD.md` — Claude Code can read
those directly and keep working from the same plan without re-asking you
the brief questions.
