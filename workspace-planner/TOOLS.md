# TOOLS.md - Planner Local Notes

Skills define _how_ tools work. This file is for _this agent's local setup_ — paths, filenames, schema notes, task patterns, and workflow-specific reminders.

For role boundaries and planning standards, use `SOUL.md`.
For session, memory, and tool-result discipline, use `AGENTS.md`.

## Workspace

- Agent workspace: `workspace-planner`
- Use this workspace for local planning notes, memory files, and scratch outputs.
- Do not assume the project root. Use the task-provided project path when available.
- Do not modify downstream agent workspaces unless explicitly instructed.

## Shared Workspace

- The shared project workspace is "/home/danox/.openclaw/workspace-shared"
- If you can't find a file you're looking for in your workspace, look for it in the shared workspace before claiming it doesn't exit.

## Common Local Files

Useful files in this workspace:

- `SOUL.md` — planner role, scope, and task-list output expectations
- `AGENTS.md` — workspace, session, memory, and tool behavior
- `IDENTITY.md` — lightweight identity metadata
- `USER.md` — minimal operator context
- `MEMORY.md` — curated long-term notes
- `memory/YYYY-MM-DD.md` — daily raw notes
- `HEARTBEAT.md` — small heartbeat checklist, if used

## Planning Note Files

When saving planning notes, prefer clear filenames:

- `production-plan-notes.md`
- `asset-task-list.md`
- `deliverable-map.md`
- `dependency-notes.md`
- `schema-notes.md`
- `role-assignment-notes.md`
- `acceptance-criteria-notes.md`

Use dated filenames only when multiple versions matter:

- `asset-task-list-YYYY-MM-DD.md`

## Source Priority

When creating task lists, prefer:

1. Task-provided schema and required output envelope
2. Approved strategy data
3. Researcher and Strategist outputs
4. Client-provided context
5. Existing campaign/content/landing page/email/form data
6. Clearly labeled assumptions when required context is missing

Do not use `USER.md` as project or client context.

## Common Operation Pattern

Typical planned production tasks may use:

```text
operationId: asset-creation
assignedAgentRole: Content Creator
intent: Create the following marketing asset: [Asset name]. [Specific requirements.]