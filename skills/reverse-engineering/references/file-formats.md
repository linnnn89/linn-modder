# File-format investigation

Read when reading an unknown archive or proving an encoder round trip. Follow the user's requested scope and validation level.

## Data files and asset formats
Use the community tool first:
- Unity: UABEA, AssetRipper
- Unreal: FModel, UAssetGUI
- Bethesda: xEdit, BSArch
- GameMaker: UndertaleModTool
- Genie: genieutils
- Source: VRF, Crowbar
- FromSoft: WitchyBND, Smithbox
- Godot: GDRE Tools

For an **undocumented format**:
1. Collect several stock files. Compare sizes, and hex-dump the headers (`xxd | head`). Look for magic
   numbers, counts, offsets and tables of fixed-size records.
2. Form a hypothesis for the header, then the frame/record layout, then the compression. Check it by
   parsing every stock file without errors.
3. Write a reader that decodes to something viewable (PNGs, JSON) and **look at it**.
4. Write the writer, and **prove it with a round trip**: decode → encode → decode, compared against the
   original. The AoE2 SLD sprite writer was accepted only when it round-tripped the stock knight at
   0.9/255 mean error (`examples/aoe2-de-civ/sld.py`).
5. Only then write new files. When runtime tests are in scope, test one asset in game before expanding. Otherwise keep results staged and label runtime as untested.
