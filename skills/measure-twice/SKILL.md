---
name: measure-twice
description: Use BEFORE building or proposing durable automation or tooling — a cron job, a SessionStart or other hook, a launch agent / systemd unit, a file watcher, a background script, or any scheduled/recurring task — and whenever a request sounds like "notify me when…", "every N minutes / daily / hourly", "keep running", "watch for…", "poll…", or "set up a job". It enforces two checks before you create anything: (1) survey the surfaces that already hold automation so you extend an existing mechanism instead of duplicating it, and (2) match the mechanism's trigger to the real-world event that makes the task relevant, rather than reaching for the most familiar tool. Don't trigger for one-off commands, ordinary code edits, or questions — only when NEW recurring/background machinery is being chosen or designed.
---

# Measure Twice

## The core principle

Two decisions come *before* any durable automation, and both are cheap to get right now and expensive to unwind later:

1. **Whether to build it** — does a mechanism already exist that does this job?
2. **What to build** — which trigger fires on the event that actually makes the task relevant?

Skipping the first gives you a **duplicate** (two mechanisms doing one job, each invisible to the other's native view). Skipping the second gives you a **mismatch** (a job firing on the wrong clock — e.g. a daily cron for something that only matters when you open the tool). Measure twice, cut once.

## 1. Survey before you build

Before creating a cron, hook, agent, or script, scan the surfaces that already hold automation — and extend what you find instead of adding a rival:

- **Claude Code hooks** — `~/.claude/settings.json` and `settings.local.json` (and any project `.claude/settings.json`).
- **User schedulers** — `crontab -l`; on macOS `~/Library/LaunchAgents` + `launchctl list`; on Linux `systemctl --user list-timers`.
- **Ad-hoc scripts** — `~/.claude/scripts/` and anything the hooks above already call.
- **Session/tooling schedules** — existing scheduled tasks, watchers, or loops.
- **Your own records** — memory / notes / `CLAUDE.md`, which may already describe (or forbid) the thing you're about to build.

If something already does the job, extend or reconfigure it. A duplicate is not just wasteful — it hides, because each native surface shows only itself.

## 2. Match the trigger to the real event

Ask: *"What real-world event makes this task relevant?"* Then pick the mechanism whose trigger fires on **that** event — not the tool you reach for by habit.

| The task is relevant when… | Use | Avoid |
|---|---|---|
| a Claude session starts / only while you use Claude | **SessionStart hook** | a cron (fires on days you never open the tool) |
| a wall-clock time arrives, regardless of Claude | **cron / launchd / systemd timer** | a session hook (won't fire when the app is closed) |
| a specific file or directory changes | **a watcher** (fswatch, inotify, launchd `WatchPaths`) | a tight polling loop |
| external state must be checked repeatedly | **a loop / monitor** at a sensible interval | a one-shot command |
| a git push / PR / tag happens | **CI or a repo hook** | a local cron guessing at timing |

A visible-but-mis-triggered job is honest, just wasteful; getting the trigger right is the difference between machinery that earns its keep and machinery that fires into the void.

## Hand off to no-hidden-changes

Measure-twice covers *before you build* (survey) and *what to build* (trigger). The moment you actually install something, its sibling rule takes over:

- **Document what you install** — record the mechanism, its trigger, and where it lives, somewhere discoverable.
- **Bump the version** of any published/versioned artifact you changed.

(That's the `no-hidden-changes` skill's job — install it too if you haven't.)

## When NOT to apply

Stay quiet for one-off commands, ordinary code edits, refactors, and questions. This skill is about *choosing and shaping new recurring/background machinery* — not a tax on every shell command.
