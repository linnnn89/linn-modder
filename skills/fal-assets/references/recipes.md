# fal asset recipes

Read when selecting a generation command or model endpoint. Follow the user's requested scope and validation level.

## Recipes (`um fal <recipe> --help` for options; `--model` overrides the endpoint; `--set k=v` passes extra inputs)

| Asset | Command | Default endpoint |
|---|---|---|
| Sprite / icon, transparent background | `um fal sprite "<subject, view, style>" --name x` | `openai/gpt-image-2` (`background=transparent`) |
| Concept art, key art, backgrounds | `um fal image "<prompt>" --aspect 16:9` | `fal-ai/nano-banana-2` |
| Consistent variants, extra frames, recolors, same character new pose | `um fal edit "<change>" --ref base.png` | `fal-ai/nano-banana-2/edit` |
| Background removal | `um fal rmbg in.png` | `fal-ai/birefnet/v2` |
| Clean pixel art from any image | `um fal pixelate in.png --colors 24` | `fal-ai/image2pixel` |
| Upscale | `um fal upscale in.png --factor 2` | `fal-ai/seedvr/upscale/image` |
| Seamless tiling texture | `um fal texture "mossy cobblestone"` | `fal-ai/z-image/turbo/tiling` |
| PBR maps (basecolor, normal, roughness, metalness, height) | `um fal pbr "rusted sheet metal"` | `fal-ai/patina/material` |
| Image → textured 3D model (GLB) | `um fal model3d concept.png [--engine trellis2\|hunyuan\|tripo\|meshy]` | `fal-ai/trellis-2` |
| Auto-rig a humanoid, optional animations | `um fal rig character.glb --animate` | `fal-ai/meshy/rigging` |
| Sound effect | `um fal sfx "plasma rifle shot, punchy" --seconds 1.2` | `fal-ai/elevenlabs/sound-effects/v2` |
| Music | `um fal music "tense boss battle, chiptune, 150 bpm" --seconds 90` | `elevenlabs/music/v2.5` |
| Voice line | `um fal voice "You dare challenge me?" --voice-id Adam` | `fal-ai/elevenlabs/tts/eleven-v3` |
| Trailer / cutscene clip | `um fal video still.png "camera orbits the boss"` | `bytedance/seedance-2.5/image-to-video` |
| Anything else | `um fal run <endpoint> key=value key:=json image_url=@local.png` | any |

Other useful endpoints:
- 3D: `tripo3d/tripo/remesh` and `fal-ai/meshy/v5/remesh` (low-poly, game-ready), `fal-ai/trellis-2/retexture`.
- Motion: `fal-ai/hunyuan-motion` (text → motion).
- Icons: `fal-ai/recraft/v4.1/text-to-vector` (SVG icons).
- Video cutouts: `pixelcut/video-background-removal`.
- Music: `google/lyria-3.5`.
- Voice: `fal-ai/minimax/speech-2.8-hd`.
