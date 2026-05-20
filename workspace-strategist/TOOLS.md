# TOOLS.md - Strategist Local Notes

Skills define _how_ tools work. This file is for _this agent's local setup_ — paths, filenames, search patterns, source notes, and workflow-specific reminders.

For role boundaries and strategy standards, use `SOUL.md`.
For session, memory, and tool-result discipline, use `AGENTS.md`.

## Workspace

- Agent workspace: `workspace-strategist`
- Use this workspace for local strategy notes, memory files, and scratch outputs.
- Do not assume the project root. Use the task-provided project path when available.
- Do not modify downstream agent workspaces unless explicitly instructed.

## Shared Workspace

- The shared project workspace is "/home/danox/.openclaw/workspace-shared"
- If you can't find a file you're looking for in your workspace, look for it in the shared workspace before claiming it doesn't exit.

## Common Local Files

Useful files in this workspace:

- `SOUL.md` — strategist role, scope, and strategy output expectations
- `AGENTS.md` — workspace, session, memory, and tool behavior
- `IDENTITY.md` — lightweight identity metadata
- `USER.md` — minimal operator context
- `MEMORY.md` — curated long-term notes
- `memory/YYYY-MM-DD.md` — daily raw notes
- `HEARTBEAT.md` — small heartbeat checklist, if used

## Strategy Note Files

When saving strategy notes, prefer clear filenames:

- `strategy-summary.md`
- `positioning-strategy.md`
- `messaging-strategy.md`
- `funnel-strategy.md`
- `channel-strategy.md`
- `content-strategy.md`
- `landing-page-strategy.md`
- `sales-handoff-strategy.md`

Use dated filenames only when multiple versions matter:

- `strategy-summary-YYYY-MM-DD.md`

## Source Priority

When forming strategy, prefer:

1. Client-provided context
2. Researcher output and cited research
3. Task-provided business goals and constraints
4. Current source/web research when strategy depends on changing facts
5. Clearly labeled inference from general marketing knowledge

## Strategy Patterns

Useful strategy framing patterns:

```text
Goal → audience → pain point → positioning → message → channel → conversion path
Audience segment → motivation → objection → proof point → CTA
Business constraint → strategic tradeoff → recommended direction → risk
Research finding → strategic implication → downstream guidance