# Changelog

> Append-only, most-recent-entry-last, dated. One entry per session/unit of work — a
> few sentences on what changed and, if a bug was caught, what it was and how it was
> found. Not a commit-by-commit log (git already has that); this is for things a future
> agent can't easily reconstruct from `git log` alone — e.g. verification that was done,
> bugs caught during that verification, and non-obvious context. Link to a decision
> (`See DEC-006`) instead of re-explaining it.

## 2026-08-03 — Initial backend build (Anthropic/Voyage/Astra)

Built the full backend from scratch per `DEC-001`–`DEC-005`: config module, Anthropic +
Voyage clients, Astra DB vector store with real similarity search, Postgres KPI storage,
RAG-based KPI extraction, ingestion orchestration, and a FastAPI REST layer under `/api`
(health, metrics, chat, upload). `.env_example` and `docs/project_journey.md` rewritten
to match. Verified module-by-module per the build plan; no automated test suite added.

## 2026-08-03 — Flattened `src/ai_investor_intelligence_platform/` to `src/`

Per `DEC-006`: moved every module up one directory level so `src/` is itself the
installable package, and converted all absolute imports across 18 files to relative
imports. Added `[tool.uv.build-backend]` to `pyproject.toml` to make `uv build` find
`src/__init__.py` under the new layout.

Bug caught during verification: `src/config.py`'s `REPO_ROOT` still used
`Path(__file__).resolve().parents[2]`, correct for the old (deeper) nesting but now one
level too high — `PDFS_DIR` silently resolved to a nonexistent path, and
`pdf_to_markdown.py`'s directory scan just returned 0 files with no error (`Path.glob()`
on a missing path doesn't raise). Fixed by changing to `parents[1]`. Found by directly
checking what each `parents[N]` index resolved to for the new file location, not by
guessing — worth doing the same check again if `config.py` ever moves.

Verified after the fix: `uv build` succeeds, all modules import cleanly, PDF→Markdown
regenerated all 6 filings, and a live `uvicorn` smoke test confirmed `/api/health` plus
all 4 other routes register correctly and Postgres/Astra connection failures at startup
are caught (not fatal) when no credentials are configured.

## 2026-08-03 — Added repo-level memory system

Created `docs/memory/` (`status.md`, `decisions.md`, `changelog.md`) plus a root
`CLAUDE.md` pointing to them, so any agent picking up this project has a fast way to
get oriented instead of re-deriving context from scratch. Backfilled `decisions.md` and
this changelog with the history above, reconstructed from the session that built the
project (no prior memory existed to draw from). See `CLAUDE.md` for the maintenance
convention going forward.

## 2026-08-03 — First live ingestion run: two credential/config bugs

First end-to-end `uv run ai-investor-intelligence-platform-server` against real
credentials surfaced two issues, both now fixed:

1. Voyage trial accounts without a payment method on file are capped at 3 RPM / 10K
   TPM, and `langchain_voyageai` constructs its internal `voyageai.Client` with
   `max_retries=0` — so a `SemanticChunker` embedding call that trips the cap raises
   `RateLimitError` immediately with no retry. No code fix applied (that's an account
   setting); resolved by the user adding a payment method in the Voyage dashboard.
2. `upload_chunks` (`src/vectorstore/astra_vectorstore.py`) hit
   `InsertManyException: Document size limitation violated` — Astra's Data API indexes
   every field by default, and indexed `String` values cap at 8000 bytes. Semantic
   chunks routinely exceed that (one was 33.8KB). Fixed by passing
   `indexing={"deny": ["content"]}` to `create_collection` in
   `src/vectorstore/create_index.py`, since `content` never needs exact-match
   filtering — only `company`/`year` do (used by `Retriever`'s metadata filter) and
   vector search (separate from field indexing).

   Non-obvious gotcha: Astra fixes a collection's indexing config at creation time —
   it can't be changed on an existing collection, only on a fresh one. Required
   dropping and recreating the `financial_documents` collection (confirmed with the
   user first, since that deletes any already-ingested data) for the fix to take
   effect.

3. `extract_financial_metrics` (`src/rag/kpi_extractor_rag.py`) hit
   `anthropic.BadRequestError: tools.0.custom.input_schema.properties: Property keys
   should match pattern '^[a-zA-Z0-9_.-]{1,64}$'`. `FinancialMetrics`'s fields used
   `Field(alias="Net Income")`-style aliases (spaces, title case) for LLM-readability;
   `with_structured_output` builds the Anthropic tool schema from those aliases, and
   Anthropic rejects property keys containing spaces. Fixed by switching from
   `alias=` to `description=` — keeps the same hint text for the model without it
   becoming a schema key. `model_dump()` now only emits snake_case keys;
   `save_metrics.py`'s `_field()` title-case fallback is consequently dead but
   harmless (kept as-is, not worth touching for this fix).

## 2026-08-04 — Hardcoded Postgres `sslmode="require"` broke local Postgres

`uv run uvicorn src.app:app` failed at startup: `psycopg2.OperationalError:
connection to server ... failed: server does not support SSL, but SSL was required`.
Both `src/database/create_table.py` and `src/database/postgres_sql.py` hardcoded
`sslmode="require"`, which assumes a managed/cloud Postgres — a local Postgres
(no SSL configured) can never satisfy that. Fixed by adding `POSTGRES_SSLMODE` to
`src/config.py` (default `"require"`, so cloud deployments are unaffected) and
using it in both files instead of the literal. Local `.env` set to
`POSTGRES_SSLMODE="disable"`; `.env_example` documents the new var. Verified with
a live `uvicorn` run — startup completes and the server binds successfully.

## 2026-08-04 — `SemanticChunker` producing empty chunks broke ingestion

`uv run ai-investor-intelligence-platform-server` crashed with
`voyageai.error.InvalidRequestError: ... Input cannot contain empty strings or
empty lists` inside `upload_chunks` (`src/vectorstore/astra_vectorstore.py`), on
the per-chunk `embeddings.embed_query(chunk.page_content)` call. Root cause:
`langchain_experimental`'s `SemanticChunker` (`chunk_markdown` in
`src/ingestion/semantic_chunker.py`) can emit chunks whose `page_content` is
empty or whitespace-only — Tesseract-OCR'd markdown routinely has blank
lines/pages that split out this way. Voyage's embed API rejects empty strings
outright, and nothing upstream validated chunk content before embedding. Fixed
by filtering `documents` for non-blank `page_content` at the end of
`chunk_markdown`, so no caller (ingestion or the module's own `__main__` smoke
test) can pass an empty chunk through to embedding.
