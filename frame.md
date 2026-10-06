# Design Spec — Dubai South & Al Maktoum International Airport

## Concept angle
A nation-scale infrastructure bet rendered as a living, gold-lit map — the airport's blueprint becomes the investor's own dashboard.

## Palette (dark/premium — tech/finance/cinematic)
- `--bg`: #0D1321 (deep navy-black, constant across every scene)
- `--bg-panel`: #1D2D44 (card/panel fill)
- `--line`: #3E5C76 (muted steel-blue — inactive map lines, dividers)
- `--muted`: #748CAB (secondary text, timeline strip, captions)
- `--fg`: #F0EBD8 (warm cream — primary text)
- `--accent`: #D4AF6A (single gold accent hue — active boundary lines, data highlights, badges, counters)
- `--danger`: #C0453F (DXB capacity-overflow bar only — the one semantic exception to "one accent")

## Typography (sans + mono, crosses the serif/sans boundary via mono instead — no embedded non-banned serif exists)
- Display / headlines / on-screen titles: **League Gothic**, 400 only (already a heavy condensed display face — never request 700/900 on it)
- Data / narration captions / counters / timeline strip / badges: **Space Mono**, 400 & 700
- Tension: institutional, editorial authority (condensed display) vs. precise, auditable data (mono) — mirrors the film's own argument (a nation's story, backed by numbers an investor can check)
- Sizes (full-screen 1920x1080 viewing): headlines 96–160px / data labels 28–40px / captions 24–28px. Weight contrast: League Gothic 400 reads heavy by construction; pair against Space Mono 400 (light) vs 700 (bold) for data emphasis.

## Focal element
The animated map/boundary itself, always center-frame: coastline trace → DXB pin → DWC site boundary → Dubai South masterplan boundary → orbital network. One continuous visual thread acts as the spine of the whole film.

## Edge anchors
- Top-left (from Act II on): persistent small kicker — "ALLEGIANCE REAL ESTATE · DUBAI SOUTH" — Space Mono 400, `--muted`, 11% opacity tracking wide.
- Bottom-right: current act label in League Gothic caps, `--accent`, low opacity (e.g. "THE MEGA-PROJECT").

## Supporting detail / background treatment
- Constant `--bg` across all scenes (continuity).
- 2–4 ambient decoratives per scene, all with slow GSAP breathing/drift (never static): thin gold hairline latitude/longitude rings at 4–6% opacity; large ghost coordinate numerals (e.g. "25.2048° N") at 3–5% opacity drifting slowly; a soft radial gold glow breathing behind the focal map element.

## Motion identity
- Camera moves between scenes read as one continuous zoom (world → region → site → district → dashboard → orbital pull-back) even across sub-composition cuts — each scene's entry motion continues the previous scene's implied camera direction (zooming in Acts I–IV, pulling back in Act V).
- Data callouts hold 2–3s longer than the narration needs them, per the brief.
- Boundary/runway lines draw themselves on (svg-path-draw), never fade in as a solid shape.

## Audio identity
- Narration: confident, measured documentary-investor register (local Kokoro TTS, American English voice).
- Music: epic/inspiring cinematic-corporate instrumental, swells at the Act V pull-back, resolves warmly under the logo card (sourced opportunistically; silence is an acceptable fallback if no provider is available — never a placeholder beep or synth pad standing in for a real score).
