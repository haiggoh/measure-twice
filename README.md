# measure-twice

A tiny Claude behavior rule: **before building automation, measure twice.** When a
task calls for durable machinery — a cron job, a hook, a launch agent, a watcher, a
background script — this steers Claude to do two things *before* creating anything:

1. **Survey** the surfaces that already hold automation (hooks config, `crontab`,
   launch agents, `~/.claude/scripts`, scheduled tasks, notes/memory) and **extend**
   what's there instead of duplicating it.
2. **Match the trigger to the real event** that makes the task relevant — a
   SessionStart hook for something relevant only while you use Claude, cron/launchd
   for something that must run regardless, a watcher for file changes, a loop for
   polling — rather than reaching for the most familiar tool by reflex.

## Why

The rule came from a real moment: asked to "notify me when X changes," Claude reached
straight for a new cron job — when an existing SessionStart hook already did the job,
and a cron was the *wrong* trigger anyway (it would fire on days the tool was never
opened). Two mistakes in one: it didn't survey, and it didn't match the trigger to the
event. Generalized, that's this plugin.

## Install — Claude Code (one-click)

```
/plugin marketplace add haiggoh/get-haiggoh
/plugin install measure-twice@haiggoh
```

> The `haiggoh` marketplace catalog is hosted in the
> [`get-haiggoh`](https://github.com/haiggoh/get-haiggoh) repo
> (it lists several `haiggoh` plugins). Add the marketplace once from there, then install
> `measure-twice` by name. This repo ships the plugin itself, not a marketplace catalog.

You get:
- a `measure-twice` **skill** (visible in `/skills`, zero token cost until invoked)
  carrying the survey checklist and the trigger-matching decision table, and
- a one-line, stateless **SessionStart hook** that reminds Claude the skill exists so
  it fires when a build-automation request comes up. No markers, no first-run pass —
  it's purely reactive.

## Install — Claude Desktop / claude.ai (copy-paste)

These apps have no plugin marketplace. Open
[`templates/custom-instructions.md`](templates/custom-instructions.md) and paste the
rule block into **Settings → Custom Instructions** (or a Project's instructions).

## Pairs with no-hidden-changes

`measure-twice` owns the decisions *before* you build (survey) and *what* to build
(trigger). Its sibling [`no-hidden-changes`](https://github.com/haiggoh/no-hidden-changes)
owns *after* you build: document what you installed, and bump the version of any
published artifact you changed. Install both for the full loop; neither depends on the
other to work.

## License

MIT © Heiko Brantsch
