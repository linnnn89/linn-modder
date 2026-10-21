# Wwise replacement: preserve the bank contract

Use for `.bnk`/`.wem` voice, music or effects. A WEM that plays in a media tool does not
prove that the game's event can find it or that its loop and timing are correct.

1. Inspect a workspace copy: game/build, `BKHD` bank version, platform/codec, language,
   and whether media is embedded (`DIDX`/`DATA`) or externally streamed. Follow event/object
   references in `HIRC` where the selected parser supports that bank version.
2. Select a reader and writer explicitly compatible with the bank version. For authoring,
   match the game's Wwise generation rather than automatically using the newest editor.
   Do not infer a version mapping from a different game or undocumented example.
3. Preserve media/object IDs and event references unless a deliberate new-event integration
   is in scope. Check channel count, sample rate, duration, loop points and streaming flags.
   Do not rewrite unrelated banks or languages to replace one voice line.
4. Prove a no-change rebuild with the chosen writer, then replace one media item and
   re-read the output. Retain the original bank and an affected-file recovery manifest.
5. If runtime work is authorized, trigger the actual event and inspect sound, loop/stop
   behavior, subtitle timing and logs. Playback in a converter is only format evidence.

Public source starting point: [WolvenKit/wwise-audio-tools](https://github.com/WolvenKit/wwise-audio-tools).
Inspect its supported operations and format versions before adoption. Authoring downloads
and documentation come from [Audiokinetic](https://www.audiokinetic.com/en/download/).

The upstream [version/toolchain note](https://github.com/rehan-remade/universal-modder/blob/c1dff21/knowledge/techniques/wwise-soundbank-versions-and-open-toolchain.md)
includes a Watch Dogs: Legion example and an author's **unpublished** merged toolchain.
Those are reported observations, not code available in Linn Modder or a verified version
matrix for other games. We retain the capability-selection method without importing that
private tool's paths or promising BNK writing. Sources checked 2026-10-21; no audio writer
or new dependency is installed by this guidance.
