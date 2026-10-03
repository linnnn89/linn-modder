# Skill documentation design

## One entry, topic folders, selected references

The repository distributes one skill: `skills/linn-modder/SKILL.md`.
Its task table directs the agent into a topic subfolder. Each topic uses an ordinary
`GUIDE.md` and focused `references/`; the only discovery metadata belongs to the entry.

| Level | Location | Read when |
|---|---|---|
| Fixed context | `AGENTS.md` | Harness loads repository rules |
| Skill discovery and routing | `skills/linn-modder/SKILL.md` | Task concerns game modding |
| Topic workflow | `skills/linn-modder/<topic>/GUIDE.md` | Entry selects this task |
| Step details | Topic `references/*.md`; shared `skills/linn-modder/references/` | Current step needs the detail |
| Findings | Indexed `knowledge/` | A relevant prior observation is useful |
| Current sources | URLs in the research topic | Version, tool or format needs online verification |

For example, a UI task follows `SKILL.md` → `linn-modder/ui-mod/GUIDE.md` →
`linn-modder/ui-mod/references/layout-and-state.md`. The other topic documents remain unloaded.
Cross-topic links are normal document navigation; the harness discovers one skill.

## Writing and routing

1. Describe when to invoke the skill using concrete user requests, including requests that omit
   the word MOD (finding Workshop files, swapping portraits, changing menus/fonts or save values,
   and repairing mods after updates). Keep useful English/Chinese/Japanese task terms tied to games.
   Put these selection cues in frontmatter; body-only cues are unavailable before invocation.
2. Add or update a topic's row in the entry when its purpose changes.
3. Give each guide a short workflow, required inputs, expected output and conditional links.
4. Use `GUIDE.md` for topics. Put substantial commands, formats and examples in references.
5. Keep shared interface facts in `skills/linn-modder/references/tools.md`.
6. Use actual operation/parameter names and preserve the user's requested scope.
7. Keep paths relative and portable. Resolve installation roots from configuration or target metadata.

Topic documents have no skill frontmatter or `agents/openai.yaml`.
The unified entry owns `name: linn-modder` and its optional Codex UI metadata.
Portable instructions remain Markdown and use available client tools for web research.

## Reading, distribution and compatibility

`um://guide` and `um://workflow` return the unified entry. `skills/README.md` links to it.
For `manual_read`, resolve links relative to the current document and pass the resulting
path relative to the collection. Example:

```json
{"collection":"skills","path":"linn-modder/ui-mod/GUIDE.md"}
```

Read the next reference at `linn-modder/ui-mod/references/layout-and-state.md`.
Knowledge notes use the `knowledge` collection. Checkout-only development documents
and examples are read with the client's file tools.

Wheels and `manuals_export` include the same single-entry directory tree. Existing
`manual_read` paths such as `ui-mod/SKILL.md` and `ui-mod/references/...` resolve to
new topic documents through a compatibility mapping; no duplicate files are exported.
Plugin identifiers and MCP/CLI operation names stay stable. Installation details live
in [setup](setup.md), and implementation rules in [development](development.md).

## Structural checks

`scripts/check_docs.py` validates exactly one discoverable `SKILL.md`, topic coverage
in its routing table, local links, packaged boundaries and entry metadata.
It rejects nested skill entries and topic UI discovery metadata.
The unified entry stays within 400 words and 3,000 characters, its description within
512 characters, and `AGENTS.md` within 2,000 characters. These are project budgets;
the description budget leaves room for concrete multilingual selection cues while staying
below the Agent Skills specification's 1,024-character maximum.
The same checks run against installed-wheel manuals. MCP integration exercises entry,
topic and reference reads; export checks verify one physical entry and usable guides.

## Reusable experience and sources

Use the research topic for unfamiliar tools, formats, errors and version changes.
Free English/Chinese/Japanese sources are split into engine/files and art/UI drawers.
Reusable design principles and game findings stay in indexed knowledge notes.
Public guidance uses neutral examples, stable IDs, resource responsibilities and
portable deployment rules. Machine inventories and diagnostic paths belong to local evidence.

Design basis: [Agent Skills specification](https://agentskills.io/specification) and
[Codex skill loading](https://learn.chatgpt.com/docs/build-skills), read on 2026-10-03.
The single-entry organization follows this project's chosen interface.
