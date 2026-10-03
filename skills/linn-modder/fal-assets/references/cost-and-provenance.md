# Generation cost and provenance

Read when budgeting a batch or preparing asset credits. Follow the user's requested scope and validation level.

## Cost and etiquette
- **Price the expensive stuff:** before batching 3D, video or long music, check the price
  (`um fal price <endpoint>` / MCP `get_pricing`). For more than about 20 generations or anything
  video-sized, tell the user the rough cost first.
- **Iterate cheap:** use low quality or resolution while exploring (`--quality low`, `--res 0.5K`), then
  re-run the winners at full quality with the same prompt (and seed where supported).
- **Reproducibility:** keep `fal_manifest.jsonl` with the assets; it records prompts, seeds and request ids.
- **Credits:** in the mod's README, credit that assets were generated with fal and name the models. Check a
  model's license page for commercial use.
