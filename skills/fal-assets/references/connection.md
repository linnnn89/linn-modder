# fal connection and interface choice

Read when configuring fal or choosing MCP versus CLI. Follow the user's requested scope and validation level.

## Setup (check once per session)
- **Key.** `FAL_KEY` must be set (create one at https://fal.ai/dashboard/keys). `um fal` also reads it from
  a `.env` file (`FAL_KEY=...`) in the working folder. Never write the key into mod files; `um publish check`
  flags leaked keys.
- **MCP.** fal's hosted MCP server is `https://mcp.fal.ai/mcp` with header `Authorization: Bearer $FAL_KEY`.
  The repo pre-configures it for each agent:
  - Claude Code: `.mcp.json`
  - Codex: `.codex/config.toml`
  - Cursor: `.cursor/mcp.json`
  - VS Code/Copilot: `.vscode/mcp.json`
  - Gemini CLI: `gemini-extension.json`

  To add it by hand:
  - Claude Code: `claude mcp add --transport http fal https://mcp.fal.ai/mcp --header "Authorization: Bearer $FAL_KEY"`
  - Codex (`~/.codex/config.toml`): `[mcp_servers.fal]` with `url = "https://mcp.fal.ai/mcp"` and
    `bearer_token_env_var = "FAL_KEY"`
  - anything else: point its MCP config at the URL and header above.
  MCP tools: `search_models`, `recommend_model`, `get_model_schema`, `get_pricing`, `run_model`,
  `submit_job`/`check_job`/`get_job_result`, `upload_file`, `search_docs`.
- **CLI alternatives:** `pip install fal` gives `fal api <endpoint> key=value key:=json`; the genmedia CLI
  (`genmedia run ... --json --download`) is agent-friendly too.

## Which interface
- **Discovery** (what's the best model for X right now, its inputs, its price): fal MCP
  `recommend_model` / `search_models` / `get_model_schema` / `get_pricing`, or `um fal search`,
  `um fal schema <endpoint>`, `um fal price <endpoint>`. The catalog changes weekly. The defaults below were
  current in September 2026; check before a big batch.
- **Anything that must land on disk** (every game asset): `um fal <recipe>`. It uploads local inputs,
  queues, polls, downloads every output file, and appends the endpoint, inputs, seed and request id to
  `<out>/fal_manifest.jsonl`, so every asset can be traced and regenerated.
- **Quick look or one-off** where a URL is enough: MCP `run_model`.
