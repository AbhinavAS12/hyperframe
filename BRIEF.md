---
workflow: general-video
flow: automation
storyboard: no
message: "Dubai South, built around the world's largest new airport, is a freehold, Golden-Visa-eligible investment opportunity priced at its earliest, most accessible point."
destination: investor-presentation
aspect: 1920x1080
language: en
audience: prospective real estate investors
length: 120s
angle: airport-driven-growth-story
---

## Intent

An investor-facing map/data-animation film for Allegiance Real Estate on Dubai South
and Al Maktoum International Airport (DWC). Premium, elegant, confident and
cinematic — never playful or cartoonish. The story: Dubai International is nearly
full, so Dubai committed to a five-times-larger airport (DWC), and an entire
freehold city (Dubai South) is rising around it at today's early, accessible
prices. Five acts: Hook, The Mega-Project, Dubai South, The Investment Case,
The Conclusion — ending on an Allegiance Real Estate brand card and CTA.

## Assets

None supplied by the user. Source cinematic aerial Dubai / Dubai South / airport
b-roll and an epic-inspiring-corporate instrumental score via `/media-use`
(Envato Elements references already shortlisted — see Notes). Generate narration
via TTS through `/media-use`'s shared audio engine (no ElevenLabs access in this
session — see Notes).

## Customizations

- Animated map/data visuals: UAE night map with igniting pins; DXB capacity bar
  overflow; DWC site boundary with runway/gate draw-in; Dubai South 145 sq km
  boundary with six districts lighting up; data dashboard with count-up price
  figures and badges (Freehold / 100% Foreign Ownership / Golden Visa / 60-40
  Payment Plans); orbital pull-back with flight-path network; Allegiance Real
  Estate logo card close.
- On-screen data callouts exactly as scripted (see STORYBOARD / script below),
  held 2-3s longer than the VO needs so investors can read them.
- Small on-screen timeline strip in Act II: 2013 -> 2024 -> ~2030 -> 2032.

## Notes

- This session has no live link to the user's computer, so it cannot drive a
  Chrome browser for Google Earth capture or operate ElevenLabs directly, and no
  Google Earth key file was actually attached. Map visuals are therefore built as
  generative HyperFrames graphics (SVG/CSS/GSAP) rather than literal Google Earth
  tiles, and narration comes from the local TTS pipeline in `/media-use`, not
  ElevenLabs.
- A parallel hosted HeyGen HyperFrames MCP project was already composed from the
  same script (projectId 9e691869-2697-4baf-86a2-9a3117ec4425) as a cloud-rendered
  version; this local project is the Node.js/HTML version the user asked for
  specifically, so they have an editable, committable source file.
- Facts used (verified Oct 2026): DWC — $35B investment, 70 sq km (5x DXB), 5
  runways, 400 gates, up to 260M passengers/year at full build-out, DXB full
  handover 2032. Dubai South — 145 sq km, six districts, Expo City 35K residents
  + 40K professionals. Entry prices (Q1 2026): studio AED 340K, 1BR AED 673K, 2BR
  AED 1.05M, 3BR townhouse AED 2.075M, ~AED 800/sqft average, freehold, Golden
  Visa eligible, 60/40 and post-handover payment plans.
- Run shape: treated as "just build it" given the user's repeated urgency signals
  across the conversation — flow locked to automation, storyboard skipped (one
  shot from this confirmed brief) rather than pausing for a review pass.
- Full scene-by-scene script (visuals, on-screen text, narration, timecodes) is
  carried over verbatim from the companion script document the user already
  reviewed; see STORYBOARD.md once written.
