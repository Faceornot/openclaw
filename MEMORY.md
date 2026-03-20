# MEMORY.md

## User preferences

- The user wants the assistant to remember important conversation content across sessions as much as possible by writing durable notes to local memory files and reloading them in future sessions.
- The user values continuity and expects the assistant to check saved memory before answering questions about prior context.
- The user wants the assistant to keep remembering ongoing requirements and step-by-step context continuously until the user explicitly says it is no longer needed.
- All project roots must maintain a `CHANGELOG.md` version-iteration document.
- Every changelog version entry must include version number, date, and change summary.
- The difference for each version must be described with a table including: changed item, old behavior, new behavior, and reason for change.
- Every new git-committed version must update `CHANGELOG.md` at the same time.
- Every outgoing message should begin with a timestamp, using `[HH:MM]` or `[YYYY-MM-DD HH:MM]`.
- Before restarting the OpenClaw gateway, the assistant must explicitly notify 姚浩然 that the gateway is about to be restarted; silent restarts are forbidden.
- During task execution, every small step should be reported, including what was done, the result, and the next step.
- When receiving a message from 姚浩然 in a Feishu group, the first action should be adding an emoji reaction before handling the request.
- Every completed change/function/fix must be followed immediately by `git commit` and `git push`; commit-only is insufficient.
- Commit messages should be written in Chinese.
- If a remote repository does not exist yet, create a private Gitee repository before pushing.
- Files must never be deleted. When removal is needed, move them to `~/Delete/` or a project-local `delete/` directory while preserving relative paths.
- New tasks should be tracked immediately in a todo system: create on receipt, mark `in_progress` when started, `done` when completed, and `skipped` if abandoned.
- Todo items should be grouped by project, and pending todos should be checked at the start of each workday.

## Ongoing tasks and project context

- The user previously asked for help completing a Kaggle Titanic survivor prediction assignment: optimize the video-demonstrated analysis workflow and baseline models, generate and submit predictions on Kaggle, obtain a leaderboard ranking screenshot, and write a research report covering data-analysis optimization, model improvement, result analysis, and ranking screenshot.
- Prior discussed deliverables included optimized Titanic code, a report draft, and a Word-compatible document; however, actual Kaggle submission and real leaderboard screenshot still require either the user's manual login/submission or a later authenticated workflow.
- For the user's Isaac Lab / Unitree Go2 training exploration on host `10.168.1.102` (`yhr`), the current remembered conclusion is: environment is healthy, single-GPU training is confirmed successful, 4-GPU training is confirmed successful, and 7-GPU distributed training is unstable and may trigger host disconnect/reboot. Current safe recommendation is to use 4 GPUs and probe 5-6 GPUs before attempting 7 again.
