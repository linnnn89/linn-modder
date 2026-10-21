# Choose a container tool by capability, not extension

Read for an unfamiliar game archive, or when extraction succeeds but editing/repacking
does not. First record game/build, container magic/version, compression and companion
index/payload files from a small representative sample in the workspace.

## Select the implementation

Prefer an official tool, then a maintained implementation for that exact game/container.
Inspect its README, source and supported versions; similarly named `.pak`, `.bin` and `.arc`
files are not interchangeable. Record separate capabilities: list, extract, replace,
add entries and rebuild. Keep unresolved filename hashes visible.

[Ekey's repositories](https://github.com/Ekey) are useful format-specific references, not
one universal adapter. For example, [REE.PAK.Tool](https://github.com/Ekey/REE.PAK.Tool)
has RE Engine extraction/repacking support. That does not establish support for unrelated
PAK containers or every new RE Engine build. Some tools need title-specific filename lists,
an older .NET runtime or a library from the user's own installation. Check those requirements
before choosing the tool; do not install dependencies or redistribute game libraries implicitly.

After selection, follow the existing [archive round-trip workflow](archive-roundtrip.md).
Verify unchanged entries and any paired index against the affected source archive; then
change one resource. A rebuilt archive that only our reader accepts is still unverified
in the game. A missing writer is a capability gap, not permission to improvise an encoder.

## UE3 packages that yield only a header or zero exports

Do not conclude that the package contains no objects. Check the game build, package and
licensee versions, and compression before changing offsets or export tables.

Start with [Gildor's UE Viewer tools and compatibility list](https://www.gildor.org/en/projects/umodel)
and the [PackageUnpack implementation](https://github.com/gildor2/UEViewer/tree/master/Tools/PackageUnpack).
Viewer/export support and package decompression are distinct from writing a game-ready package.

Upstream's [UE3 LZO fallback reference](https://github.com/rehan-remade/universal-modder/tree/c1dff21/skills/reverse-engineering/references/ue3-packages)
reports a Dishonored 801/30 case where a reader stops before exporting objects. Its script
handles LZO only, uses a C extension, and prepares a package for UELib inspection. It is
not bundled here as a general unpacker or repacker. Do not copy the example's compression
flag offset to another build or use the analysis output as an installed replacement.

Sources checked 2026-10-21. The upstream
[tool catalogue](https://github.com/rehan-remade/universal-modder/blob/c1dff21/knowledge/techniques/ekey-tool-family-per-engine-archive-unpackers-and-packers.md)
is a discovery aid; refresh individual tools' compatibility before use. No game archive
was unpacked or round-tripped as part of this toolkit integration.
