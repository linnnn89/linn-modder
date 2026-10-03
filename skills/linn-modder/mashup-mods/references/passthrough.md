# Two-process passthrough

Read when sharing state, frames or collision between a host and guest. Follow the user's requested scope and validation level.

## Pattern 2: passthrough (two games at once)
chasm's description of Minecraft-in-Skyrim: *"minecraft and skyrim run at the same time and you make a mod
for both that lets them communicate. Then you passthrough the things you want into the renderer in the
right place and feed stuff like collision data back to minecraft."* No code was published. The design below
is the standard way to build it.
1. **Guest process** (e.g. Minecraft with a Fabric mod, or a headless reimplementation): runs the simulation
   and publishes state every tick. That's entities/blocks near the player, or a rendered layer.
2. **Transport**, all on `127.0.0.1`:
   - state: a shared-memory ring buffer (`CreateFileMapping`) or UDP/named pipes;
   - control: JSON lines or HTTP;
   - GPU frames: DXGI shared handles (`CreateSharedHandle` / `OpenSharedResource1` + keyed mutex), Vulkan
     external memory, or Spout2.
3. **Host injection:** a host-side plugin (SKSE/xNVSE/UE4SS/REFramework/ReShade addon) draws the guest's
   geometry **inside the host's pass**. It uses the host's view-projection matrices (find them with
   RenderDoc) and depth buffer, or spawns host-native objects so host lighting and shadows apply. The
   Skyrim clip gave Steve Skyrim's lighting, which points to scene integration, not a flat overlay.
4. **Back-channel:** the host's collision near the player (raycasts, or exported nearby mesh) goes to the
   guest as solid blocks or colliders. Input routes to one process at a time.
5. **Sync:** timestamps on every message, tolerance for the two frame rates, and a watchdog when one side
   dies.
6. **Start small:** a cube from process A drawn in B at the right spot. Then positions every frame, then
   collision, and only then real content.

Bridge-plugin template in public: chasm-bridge-fnv (thin xNVSE plugin, file-drop/HTTP transport,
data-driven actions). The Terraria agent bridge in `examples/terraria-tmodloader/reference/` is the same
idea.

### Worked example: real Minecraft inside GTA V
Code: `examples/minecraft-gta5-passthrough`. Every lesson: `knowledge/games/gta-v/minecraft-passthrough.md`.
- **Minecraft (Fabric mod):** it takes camera, ground and input from the host over a WebSocket on
  `127.0.0.1`. Each frame it writes world colour + depth and a separate hand/HUD overlay into named shared
  memory.
- **GTA (ScriptHookV ASI + ReShade add-on):**
  - it sends GTA's camera and the ground under the player (as barrier blocks);
  - it composites Minecraft's colour against GTA's reversed-Z depth in a shader;
  - it turns Minecraft explosions, arrows and firework hits into GTA explosions and bullets.
- **Mapping:** 1 metre = 1 block. GTA (x, y, z) → MC (x, z + offset, −y); yaw = 180 − heading;
  pitch = −pitch.
- **Latency:** Minecraft's frame is re-projected onto GTA's camera, rotation then full 6-DoF with depth.
  Measure the pose lag with a scene where one side draws something the other doesn't (a gold wall vs the
  skyline).
- **Built without the game:** most of it was built before the host game was even installed, against a
  fake host (known geometry) and a fake D3D11 "GTA" that runs the real compositor.
- **What didn't work:** putting host-game guns in Steve's hands (the aim cam and animations don't fit).
  Guest weapons with host effects did.
