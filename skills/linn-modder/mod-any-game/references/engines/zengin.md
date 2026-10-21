# ZenGin: distinguish scripts, volumes and engine plugins

Use for Gothic 1/2. The scan correlates a `system/` game executable or VDFS runtime with
`Data/*.vdf`; that identifies a likely family, not the exact supported executable build.

Choose the smallest layer that reaches the feature:

- Dialogue, quests and data: investigate the matching Daedalus scripts and mod development
  kit before native hooks. Preserve stable instance names and save references.
- Assets: inspect the VDF/MOD volume and resource versions. [GothicKit/ZenKit](https://github.com/GothicKit/ZenKit)
  documents ZenGin formats; check each format's read/write support rather than assuming a
  reader can compile scripts or produce a loadable replacement.
- Engine behavior: verify the exact game's build against the chosen Union/plugin SDK and
  its maintainers' current compatibility documentation. A matching executable filename does
  not authorize replacing the executable or establish ABI compatibility.

Stage one changed resource, verify an [archive round trip](../../../reverse-engineering/references/archive-roundtrip.md),
then test loading and the requested behavior when game execution is in scope. Preserve
the existing mod loader and user configuration. Toolkit detection uses synthetic fixtures;
no Gothic runtime or archive writer is bundled.

Detection reference: [upstream c1dff21](https://github.com/rehan-remade/universal-modder/blob/c1dff21/um/scan.py).
