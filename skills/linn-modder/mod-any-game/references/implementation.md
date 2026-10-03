# Internals and the first working slice

Read when reading game behavior or implementing one feature. Follow the user's requested scope and validation level.

### Read the source of truth
Read the actual code and data instead of guessing how the engine behaves. The **reverse-engineering** topic guide
covers the tools:
- decompile: ILSpy/`ilspycmd`, Cpp2IL, Vineflower, Ghidra/IDA over MCP;
- dump data: genieutils, xEdit, UndertaleModTool, FModel;
- inspect live: UnityExplorer, the UE4SS live viewer, REFramework, Cheat Engine.

Record exact names and IDs in MODLOG.md. Check what the executable enforces as well as what the data says.
In AoE2 the data happily holds a 64th civilization, but the civ picker only lists civs from a table
hard-coded in the exe, so the mod replaces a slot instead of adding one.

### Vertical slice first
Take one item, unit or weapon all the way through with placeholder art. Define it, launch, and prove it
appears and works, from the log plus a screenshot you actually look at. Only then widen. Commit each working
step in the mod's own git repo.
