# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

Project Root:
/home/danox/.openclaw/workspace-shared/

Tool contract:
- For every shell command, call `exec` with `workdir` set to the Project Root above.
- For every file operation, use absolute paths under the Project Root.
- Do not use workspace-relative paths for project files.
- Do not treat /home/danox/.openclaw/workspace-shared as the app directory.
- First, verify the directory with an exec call that prints pwd and lists the top-level files.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
