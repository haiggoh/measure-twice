#!/usr/bin/env bash
# measure-twice — SessionStart hook.
#
# Stateless: emits ONE JSON object carrying a one-line, MODEL-ONLY nudge
# (hookSpecificOutput.additionalContext). No markers, no reconciliation, no
# user-visible banner — this rule is purely REACTIVE, meant to fire the skill at
# the moment the user asks to build automation or tooling. Unlike no-hidden-changes,
# there is no first-run pass to run, so there is nothing to track between sessions.
#
# Pure bash (3.2-compatible); no jq/python dependency at runtime.

set -uo pipefail

# --- pure-bash JSON string escaper (bash 3.2 verified) ---
json_escape() {
  local s=$1
  s=${s//\\/\\\\}    # backslash -> \\  (MUST run first)
  s=${s//\"/\\\"}    # "         -> \"
  s=${s//$'\n'/\\n}  # newline   -> \n
  s=${s//$'\t'/\\t}  # tab       -> \t
  s=${s//$'\r'/\\r}  # CR        -> \r
  printf '%s' "$s"
}

NUDGE="measure-twice: before building or proposing durable automation or tooling (a cron job, hook, launch agent, watcher, background script, or scheduled/recurring task) — STOP and consult the measure-twice skill. Two checks first: (1) SURVEY existing mechanisms — hooks config, crontab, launch agents, ~/.claude/scripts, scheduled tasks, and your own notes/memory — so you EXTEND what's there instead of duplicating it; (2) MATCH the trigger to the real event that makes the task relevant (relevant only while using Claude -> SessionStart hook; must run regardless of Claude -> cron/launchd; a file changes -> a watcher; external state must be polled -> a loop/monitor). Then hand off to no-hidden-changes: document what you install and bump any published artifact's version."

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
  "$(json_escape "$NUDGE")"
