# Skill documentation design

The documentation has four loading levels. Fixed harness context should route a task;
implementation details should be loaded only for the current step.

| Level | Location | Load when | Contents |
|---|---|---|---|
| Fixed project context | `AGENTS.md`; `CLAUDE.md` imports it; Gemini points to it | Harness loads project instructions | Scope, non-negotiable boundaries and a few routing paths |
| Discovery | Each skill's frontmatter; compact plugin descriptions | Harness discovers skills | Name and specific task trigger, no workflow or command catalog |
| Task entry | `skills/<name>/SKILL.md` | Task matches that skill | Minimum steps, constraints, expected output and a reference table |
| Detail | `skills/<name>/references/*.md` | Current step requires it | Commands, templates, version-specific facts and examples |

[README](../README.md) is the human starting point.
[Skill router](../skills/README.md) is the fallback when the task is unclear; it is not
required before every specialist. [Setup](setup.md) and [development](development.md)
serve installation/toolkit work without loading the general mod workflow.

## Writing rules

1. Use a short, specific description. Explain when the skill applies; do not list every tool
   or advertise completion guarantees. Keep skill names stable for installed harnesses.
2. Begin the body with the minimum useful workflow. Name required inputs, the concrete output
   and the distinction between assumptions and evidence.
3. Give each reference a task condition. Avoid instructions to read every reference, every
   engine playbook or all examples. Link directly to the file needed at the next decision.
4. Keep reusable interface facts in `skills/references/tools.md`; preserve engine playbooks
   at existing paths. Avoid copies of the same setup/permission text in every workflow.
5. Use literal operation/parameter/profile names. Separate implemented service tools,
   legacy CLI commands and future adapters so an LLM cannot mistake a plan for an available tool.
6. Preserve requested scope. Runtime tests, paid generation, videos and public releases
   are conditional tasks, not automatic steps in every code change.
7. Reuse existing user authorization. Keep important boundaries in fixed context; detailed
   rationale lives in the safety reference and is read only when relevant.

## Paths and packaged manuals

Markdown links are relative to the current file. For `manual_read`, resolve that link and
pass the resulting path relative to the chosen collection. `skills/README.md` is available
as `um://guide`; `um://workflow` remains the compact general skill for compatibility.
All linked skill files remain inside the `skills` collection so a wheel-only MCP session
can traverse the workflow without fetching checkout-only documentation.

References can mention `examples/`, `docs/` or `knowledge/` as checkout paths. These do not
imply that `manual_read(collection="skills")` can access another collection or a checkout.
Use the knowledge collection for notes; use a file-capable checkout for code examples.

## Size and validation

`scripts/check_docs.py` checks local Markdown link targets, skill frontmatter/name matching,
packaged skill-link boundaries and entry budgets: `AGENTS.md` ≤ 2,000 characters,
`CLAUDE.md` is the single import, descriptions ≤ 240 characters, task entries ≤ 400 words,
and plugin/extension discovery descriptions ≤ 160 characters. These are regression guards,
not estimates of a model's exact token count.

The checker also runs against skill resources in an installed wheel. CI validates the
MCP guide and selective reference reading. A PATH-only session hook must not print manuals.
Actual skill discovery and caching depend on the harness; the toolkit supplies compact
metadata and stable paths but does not claim to control every client's context assembly.
