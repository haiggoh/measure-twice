# Changelog

All notable changes to the `measure-twice` plugin are documented here.

## [0.2.4] — 2026-11-12

### Fixed
- SKILL.md frontmatter: the `description:` value is now a double-quoted YAML scalar. It previously
  contained unquoted `: ` sequences ("…before you create anything: (1) survey…"), which strict YAML
  parsers reject outright (PyYAML `ScannerError`; the same class claude.ai upload validation
  enforces). Claude Code's lenient loader masked it. The rendered description is byte-identical
  (verified, 810 chars) — packaging changed, content did not.

### Added
- `tests/test_skill_yaml.sh`: strictly parses every `skills/*/SKILL.md` frontmatter (PyYAML;
  falls back to the pipx pytest venv python when system python3 lacks pyyaml; exit 2, same
  convention as the jq requirement) and asserts non-empty `name`/`description`; chained into the
  rtc-ship gate after `test_hook.sh`.

## [0.2.3] — 2026-11-09

### Added
- Transient-watcher exemption (nudge + skill): a bounded, one-event, `$TMPDIR`-only,
  `run_in_background` watcher (prefer free-agents' `bin/watch-until`) is NOT durable
  automation — no survey needed; anything that outlives the session or re-arms itself still is.

## [0.2.2] — 2026-10-31

### Changed
- The plugin description (plugin.json, and the marketplace listing it feeds) is rewritten to describe
  the plugin's full current capabilities.

## [0.2.1] — 2026-10-31 — ⚖️: the credit-moment mark on the plugin's surfaces

- The repo's GitHub About emoji (⚖️) now leads what the user and model read at the plugin's credit
  moments (plan 2026-10-28, §Wave 3 Task 8): the SessionStart nudge's first token, a ≤3-line
  Branding section in the SKILL.md, the plugin.json description, and the README h1.
- tests/test_hook.sh: the nudge label pin strengthened from substring to the exact branded prefix.

## [0.2.0] — 2026-09-23

### Added — a third check: do not assume your hook runs in the order you wrote it

The skill covered *survey before you build* and *match the trigger to the real event*. It said nothing
about the case where more than one hook can fire on the same event — and there, ordering is not yours
to decide.

- **New skill section "3. Do not assume your hook runs in the order you wrote it."** SessionStart hooks
  contributed by different plugins run in **parallel with no ordering guarantee**; neither `hooks.json`
  nor `plugin.json` has any priority, weight, or order field, and observed order matches neither
  install order, plugin name, nor the sequence in settings. So a hook that reads state another hook
  writes, or a banner that must appear above someone else's, rests on an assumption the platform never
  made.
- **Two designs given, in order of preference:** win on prominence rather than position when the output
  only needs to be noticed; and when a predecessor genuinely must finish first, use a **one-way,
  best-effort, session-scoped done-flag** — producer writes it atomically in a `finally` whether or not
  it emitted anything and never waits on anything itself; consumer detects the producer from **config**
  (never by importing its code), polls with a **bounded** wait, and **always proceeds regardless**.
  Ordering without a dependency: no import either direction, both hooks still work standalone, and the
  worst case is the race you already had.
- **Verification guidance:** a timing- or TTY-gated path needs a live three-case smoke test (producer
  not installed / installed but flag absent / flag present) before the automated tests, because that is
  the only thing that proves the bounded wait actually bounds.
- The SessionStart nudge now carries the check as item (3), so it fires without the skill being read.

### Testing

`tests/test_hook.sh` 9 → **12** checks. Each of the three new assertions was **mutation-tested** — the
nudge wording was broken deliberately (`PARALLEL`→`SEQUENTIAL`, `fail-open`→`fail-closed`,
`no priority field`→`a priority field`) and each was confirmed to fail, then restored. A doc assertion
that cannot fail is decoration.

## [0.1.0]

Initial release: the survey-before-you-build and match-the-trigger checks, the SessionStart nudge, the
skill, and the Claude Desktop instruction template.
