# Code and runtime inspection

Read when selecting a decompiler, debugger or graphics inspector. Follow the user's requested scope and validation level.

## Pick the tool by what the code is (`um scan` tells you)

**Managed .NET** (XNA/FNA, Unity Mono, most indie C#)
- `dotnet tool install -g ilspycmd`, then `ilspycmd -p -o ~/<game>-decomp <Game>.exe` (or
  `Assembly-CSharp.dll`). This gives a full C# project you can grep.
- dnSpyEx: step through with a debugger, set breakpoints, edit methods.
- MCP: ILSpy-MCP / dnspy-mcp let an agent query types and methods directly.

**Unity IL2CPP**
- Cpp2IL (or Il2CppDumper) on `GameAssembly.dll` + `global-metadata.dat` gives types, fields, method
  signatures and addresses, plus dummy DLLs for ILSpy.
- Method bodies are native: load `GameAssembly.dll` in Ghidra/IDA and apply the generated script to name
  functions.
- Live: UnityExplorer, or `il2cpp-frida-mcp`.

**Java** (Minecraft, Slay the Spire...)
Vineflower / CFR / Recaf. For Minecraft, use Loom `genSources` with Mojang mappings.

**Native C/C++** (custom engines, Unreal game code, console recomps)
- Ghidra (free) or IDA, driven through MCP so the agent can decompile, rename, retype and follow
  cross-references:
  - Ghidra: GhidraMCP (LaurieWired), pyghidra-mcp (headless, with a run-script tool; code-capable tools beat
    hundreds of tiny ones), ReVa.
  - IDA: the official Hex-Rays IDA MCP (IDA 9.4+ Pro/Home; "code mode" runs IDAPython), or ida-pro-mcp.
  - Binary Ninja and radare2 have MCP servers too.
- Workflow:
  1. Strings, then cross-references, then the function.
  2. Name and type everything you understand. Renames accumulate into a readable program.
  3. Confirm dynamically (below) before building on a guess. Agents can confidently misidentify things.
- Unreal: dump the reflection data first (UE4SS dumper or Dumper-7); it names most gameplay classes and
  properties for free.

**Dynamic / live**
- Cheat Engine: value scans → "find out what writes to this address" → struct → owner. CheatEngine MCP
  servers exist.
- x64dbg: breakpoints and tracing (x64dbg-mcp; bind it to 127.0.0.1, since some default to 0.0.0.0).
- Frida (frida-mcp, frida-game-hacking-mcp): hook functions from JavaScript, log arguments.
- ReClass.NET rebuilds structs from live memory.

**Graphics**
- RenderDoc (renderdoc-mcp) captures a frame and shows every draw, the render targets, the constant buffers
  (view/projection matrices) and the depth buffer.
- That's how you find where to inject geometry or effects (mashup-mods), and which texture holds a sprite
  atlas.
