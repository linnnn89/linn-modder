# Bannerlord: use the module boundary

Read when the scan finds both `bin/<platform>/TaleWorlds.MountAndBlade.dll` and
`Modules/Native/SubModule.xml`, or the user explicitly names Bannerlord. A launcher alone
is insufficient. Optional `Version.xml` is a hint; match the actual installed assemblies
and game edition before choosing a target framework or dependency version.

Start from the [official module and asset documentation](https://moddocs.bannerlord.com/)
and [API reference](https://apidoc.bannerlord.com/). These describe supported entry points;
they do not prove compatibility with the user's build.

- Data changes belong in a separate module with `SubModule.xml` and `ModuleData` XML.
  Prefer the documented merge/XSLT facilities to overwriting Native data.
- Code belongs in an `MBSubModuleBase` implementation referencing the installed game's
  assemblies. Declare module dependencies and validate load order; use hooks only when
  the official callback cannot express the requested behavior.
- Models, textures and scenes use the version-matched official tools and resource pipeline.
  A prepared PNG or compiled DLL is not proof that the game registered the resource.
- Stage the module outside the install. When runtime validation is authorized, check its
  loading log and one requested behavior in a disposable profile; campaign save compatibility
  needs its own evidence.

For upgrades, use [faithful migration](../mod-migration.md). Linn Modder provides detection
and guidance here, not a Bannerlord builder or installer. Detection patterns were adapted
from [upstream c1dff21](https://github.com/rehan-remade/universal-modder/blob/c1dff21/um/scan.py).
