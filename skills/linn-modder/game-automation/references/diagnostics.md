# Crashes and cleanup

Read when diagnosing a crash or cleaning up known processes. Follow the user's requested scope and validation level.

## Crashes and cleanup
- **Crash reporters** (BugSplat `BsSndRpt64.exe`, `CrashReportClient.exe`, `UnityCrashHandler64.exe`) can
  linger and make Steam say "already running". `um win ps` to spot them, `um win kill <pid>` to clear
  them.
- Never `pkill -f` or wildcard `taskkill /IM`. The pattern can match your own shell or other apps.
- After a crash, read the loader or game log first (the mod-any-game topic guide lists them), then the Windows
  Event Viewer (Application log) for native crashes.
