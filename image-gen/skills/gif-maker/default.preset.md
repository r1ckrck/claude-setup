# gif-maker preset — Default

The single default preset for gif-maker. No per-domain variants — all GIF defaults live here. Empty fields (`—`) are intentional — Claude infers them from the user's request at prompt time. Edit any field to lock a value.

---

- **description:** Default GIF settings — 10fps, 480px wide, 64 colors, bayer dither.
- **default fps:** 10
- **default width:** 480
- **default max colors:** 64
- **default dither:** bayer (bayer_scale=5)
- **default loop:** infinite
- **default trim:** use full source
- **default source model:** fal-ai/kling-video/v2.5-turbo/pro/text-to-video (or `.../image-to-video` when a source still is provided)
- **default source duration:** model minimum (5s on Kling 2.5 Turbo Pro)
- **default source resolution:** smallest tier the chosen model exposes
- **default source audio:** off
- **default aspect ratio:** —
- **forbidden treatments:** watermarks · visible text artifacts (unless requested) · Instagram-filter aesthetic · stock-photo cliché poses · heavy HDR
- **forbidden subjects:** real public figures (named celebrities, political figures, athletes) · identifiable third-party trademarks/logos (unless requested) · copyrighted characters · minors in suggestive contexts
- **color-budget intent map:** loader → 16-32 · micro-animation → 16-32 · hero → 64 · decorative → 32-64 · photographic → 128
- **dither intent map:** loader / micro-animation / hero / decorative → bayer · photographic → floyd_steinberg
- **fps override range:** 8–15 (lower = fewer frames, smaller file; higher = smoother motion, larger file)
- **width override examples:** 320 (tiny micro-animations) · 480 (default) · 640 / 720 (hero GIFs)
- **notes for AI:** Color budget is intent-driven aesthetic guidance, not a literal prompt instruction. Reflect through aesthetic choices ("limited palette", "high-contrast silhouettes"), not "use exactly N colors."
