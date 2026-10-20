# Vexora sample-ad kit (used by the "Vexora form requests" scheduled task)

1. Gmail `get_message` (messageFormat RAW) on the FormSubmit email. If the result is inline, save it to a
   file with Python from the tool text; if Claude Code saved it to a tool-results file, use that path.
2. `python3 kit/samples/parse_request.py <raw-file> work/<slug>` → request.json + photos/
3. Look at the photos (Read), research the business (WebSearch/WebFetch on their site), write
   work/<slug>/spec.json in the shape of spec-example.json.
4. `python3 kit/samples/build_samples.py work/<slug>/spec.json s/<token>` → mockups, page, email.
5. Read s/<token>/preview.jpg to check it, then commit + push `s/<token>/` (GitHub Pages serves it at
   https://stormie014.github.io/vexora-media/s/<token>/ within ~1 minute).
Needs Pillow + playwright (Chromium). Fonts are in kit/fonts.
