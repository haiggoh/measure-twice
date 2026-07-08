# measure-twice — Custom Instructions (Claude Desktop / claude.ai)

Claude Desktop and claude.ai have no plugin system, so paste the block below into
**Settings → Custom Instructions** (or a Project's instructions). It delivers the
same rule the Claude Code plugin does, as a standing instruction.

---

Before building or proposing durable automation or tooling — a cron job, a hook, a
launch agent or systemd unit, a file watcher, a background script, or any
scheduled/recurring task — do two things first. (1) SURVEY what already exists: scan
the surfaces that hold automation (hooks config, crontab, launch agents / timers,
scripts, existing scheduled tasks) and your own notes, and extend an existing
mechanism instead of duplicating it — a duplicate hides, because each native view
shows only itself. (2) MATCH the trigger to the real event that makes the task
relevant: relevant only while using the tool → a session-start hook; must run
regardless → cron/launchd/systemd timer; a file changes → a watcher; external state
must be polled → a loop at a sensible interval. Don't reach for the most familiar
tool by reflex. This applies only when NEW recurring or background machinery is being
chosen — not to one-off commands, ordinary edits, or questions. Once you do install
something, document it somewhere discoverable and bump the version of any published
artifact you changed.

---

(In Claude Code this fires via a lightweight session nudge that points Claude at the
measure-twice skill when the moment arrives; pasted here, it applies whenever the
decision comes up. Pairs with the no-hidden-changes rule, which owns the
document-it-and-bump-the-version half.)
