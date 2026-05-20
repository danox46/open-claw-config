# TOOLS.md - Writer Local Notes

Skills define _how_ tools work. This file is for _this agent's local setup_ and small workflow reminders.

For role boundaries and writing standards, use `SOUL.md`.
For session, memory, and tool-result discipline, use `AGENTS.md`.

## Workspace

- Agent workspace: `workspace-writer`
- Use this workspace for local writing notes, memory files, and scratch outputs.
- Do not assume the project root. Use the task-provided project path when available.
- Do not modify other agent workspaces unless explicitly instructed.

## Shared Workspace

- The shared project workspace is "/home/danox/.openclaw/workspace-shared"
- If you can't find a file you're looking for in your workspace, look for it in the shared workspace before claiming it doesn't exit.

## Common Local Files

- `SOUL.md` — writer role, scope, and writing expectations
- `AGENTS.md` — workspace, session, memory, and tool behavior
- `IDENTITY.md` — lightweight identity metadata
- `USER.md` — minimal operator context
- `MEMORY.md` — curated long-term notes
- `memory/YYYY-MM-DD.md` — daily raw notes

## Writing Notes

When saving drafts or notes, prefer simple filenames:

- `copy-draft.md`
- `landing-page-copy.md`
- `blog-post-draft.md`
- `email-sequence-draft.md`
- `claims-to-verify.md`

Use dated filenames only when multiple versions matter.

## Source Priority

When writing, prefer:

1. Task-provided schema and required output format
2. Asset requirements
3. Approved strategy data
4. Planner task context
5. Research or client-provided proof
6. Clearly labeled placeholders when information is missing

Do not use `USER.md` as client, product, audience, or campaign context.