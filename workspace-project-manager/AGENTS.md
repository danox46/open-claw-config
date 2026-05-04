## Path discipline

Workspace root is only the agent home, not the app root.

For project work:
- Always treat the assigned Project Root as the real app directory.
- Every `exec` tool call must include `workdir` set to the exact Project Root.
- Never run shell commands from the workspace root unless the task explicitly requires it.
- For file tools (`read`, `write`, `edit`, `apply_patch`), always use absolute paths under Project Root.
- Never use relative paths like `src/...`, `package.json`, or `README.md` for project files.
- Before making changes, verify the target with an `exec` call using the project root as `workdir`.

Project Root:
/home/danox/.openclaw/workspace-shared/

Tool contract:
- For every shell command, call `exec` with `workdir` set to the Project Root above.
- For every file operation, use absolute paths under the Project Root.
- Do not use workspace-relative paths for project files.
- Do not treat /home/danox/.openclaw/workspace-shared as the app directory.
- First, verify the directory with an exec call that prints pwd and lists the top-level files.