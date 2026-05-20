# TOOLS.md - Researcher Local Notes

Skills define _how_ tools work. This file is for _this agent's local setup_ — paths, filenames, search patterns, source notes, and workflow-specific reminders.

For role boundaries and evidence standards, use `SOUL.md`.
For session, memory, and tool-result discipline, use `AGENTS.md`.

## Workspace

- Agent workspace: `workspace-researcher`
- Use this workspace for local research notes, memory files, and scratch outputs.
- Do not assume the project root. Use the task-provided project path when available.
- Do not modify downstream agent workspaces unless explicitly instructed.

## Shared Workspace

- The shared project workspace is "/home/danox/.openclaw/workspace-shared"
- If you can't find a file you're looking for in your workspace, look for it in the shared workspace before claiming it doesn't exit.

## Common Local Files

Useful files in this workspace:

- `SOUL.md` — researcher role, scope, and research output expectations
- `AGENTS.md` — workspace, session, memory, and tool behavior
- `IDENTITY.md` — lightweight identity metadata
- `USER.md` — minimal operator context
- `MEMORY.md` — curated long-term notes
- `memory/YYYY-MM-DD.md` — daily raw notes
- `HEARTBEAT.md` — small heartbeat checklist, if used

## Research Note Files

When saving research notes, prefer clear filenames:

- `research-summary.md`
- `audience-research.md`
- `market-research.md`
- `competitor-notes.md`
- `channel-research.md`
- `content-research.md`
- `conversion-research.md`
- `sales-handoff-research.md`

Use dated filenames only when multiple versions matter:

- `research-summary-YYYY-MM-DD.md`

## Source Priority

When the task allows source selection, prefer:

1. Client-provided context
2. Current source/web research when facts may have changed
3. Official documentation or primary sources
4. Credible industry reports and reputable publications
5. Clearly labeled inference from general knowledge

## Search Patterns

Useful query shapes:

```text
[industry] buyer pain points [audience]
[product category] trends [year]
[competitor/product] positioning
[category] landing page examples
[category] lead generation benchmarks
[buyer persona] objections [product category]
[region] [industry] compliance marketing considerations