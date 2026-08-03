# AI Investor Intelligence Platform — Backend

REST JSON backend for financial-document intelligence: ingest 10-K PDFs, chunk/embed
them into Astra DB, extract structured KPIs via Claude, persist KPIs in Postgres, and
serve it all under `/api/*` for a separately-hosted frontend. Built on Anthropic Claude,
Voyage AI, and Astra DB. Full rationale in `docs/memory/decisions.md`.

## Get oriented here, in this order

1. **`docs/memory/status.md`** — current state: stack, module layout, what's done, what's
   missing (credentials, tests, etc). Read this first, every time — it's a live snapshot,
   not history.
2. **`docs/memory/decisions.md`** — why the project is built this way. Read before making
   a change that seems to contradict existing structure; the reason is probably logged
   there.
3. **`docs/memory/changelog.md`** — dated log of what changed and, where relevant, bugs
   caught along the way and how they were found.
4. **`docs/project_journey.md`** — phase-by-phase build narrative.

## Keeping `docs/memory/` healthy

This directory is the project's persistent memory across sessions and agents. It is only
useful if it stays accurate and small enough to read in full. Maintain it as follows:

- **After any change that isn't purely cosmetic** (new module, dependency swap,
  architecture change, a bug that wasn't obvious, a decision between real alternatives):
  add an entry. Use `changelog.md` for "what happened," `decisions.md` for "why, when
  there was a real fork in the road." Most changes only need a changelog entry — reserve
  `decisions.md` for choices a future agent might otherwise second-guess or accidentally
  reverse.
- **Update `status.md` in place** whenever it goes stale — new modules, resolved gaps,
  newly configured credentials, new known issues. It describes *now*, so overwrite rather
  than append. If unsure whether something changed enough to warrant an update, check it
  against the file rather than skipping the check.
- **`changelog.md` and `decisions.md` are append-only.** Don't rewrite history — if a
  past decision is reversed, add a new dated entry that says so and references the old
  one (`See DEC-006`).
- **Keep entries short.** A few sentences, not a report. Link to code/files rather than
  re-explaining what's readable from the source. If an entry is mostly restating what
  `git log` or the diff already shows, it doesn't need to exist — write down what isn't
  obvious from the code: *why*, and any non-obvious verification or bug caught along the
  way.
- **Prune when a file grows unwieldy.** If `changelog.md` accumulates many entries for
  the same settled area, it's fine to consolidate old ones into a single summary entry
  and move the detail into `decisions.md` if it's still load-bearing, or drop it if it's
  not. Don't let memory grow unbounded just because it's append-only by convention —
  append-only means don't silently rewrite what happened, not never consolidate.
- **Don't duplicate what code already documents.** No file paths, function signatures, or
  step-by-step "how it works" here beyond what `status.md`'s module-layout section
  already gives — that's what reading the source is for. Memory is for things reading the
  source won't tell you: why, what was tried and rejected, what broke and how it was
  caught.

## Quick facts

- Run the API: `uv run uvicorn src.app:app --reload`
- Run standalone ingestion: `uv run ai-investor-intelligence-platform-server`
- `src/` is itself the installable package — use relative imports for everything inside
  it (`DEC-006` in `docs/memory/decisions.md` explains why).
- Env vars: see `.env_example`. No live credentials are committed; `.env` is gitignored.
