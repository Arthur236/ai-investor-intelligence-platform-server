# Project Status

> Snapshot of "where things stand right now." This file describes current state only —
> history and rationale belong in `decisions.md` and `changelog.md`. Overwrite sections
> in place as state changes; don't append dated entries here.

Last updated: 2026-08-03

## What this project is

A REST JSON backend for financial-document intelligence: ingest 10-K PDFs, chunk and
embed them, store vectors in Astra DB, extract structured KPIs via Claude, persist KPIs
in Postgres, and serve everything (metrics, companies, chat) over `/api/*` for a
separately-hosted frontend to consume. See `decisions.md` for why it is built this way.

## Stack (current)

| Concern | Provider | Package |
|---|---|---|
| Chat + structured KPI extraction | Anthropic Claude (`claude-sonnet-5`) | `langchain-anthropic`, `anthropic` |
| Embeddings | Voyage AI (`voyage-3`, 1024-dim) | `langchain-voyageai` |
| Vector store | Astra DB | `astrapy` |
| KPI storage | Postgres | `psycopg2-binary`, `sqlalchemy` |
| API | FastAPI, pure JSON REST, CORS-enabled | `fastapi`, `uvicorn` |

## Package layout

`src/` is itself the installable package (not `src/ai_investor_intelligence_platform/` —
that nesting was flattened away; see `decisions.md`). Internal imports are relative.

```
src/app.py            FastAPI entrypoint, lifespan, CORS, routers under /api
src/config.py         all env var reads, DATA_DIR/PDFS_DIR/MARKDOWN_DIR path math
src/llm/               anthropic_client.py
src/embeddings/        voyage_embeddings.py
src/vectorstore/       create_index.py, astra_vectorstore.py (upload_chunks, Retriever)
src/database/          postgres_sql.py, create_table.py, save_metrics.py, metrics.py
src/rag/               kpi_extractor_rag.py (FinancialMetrics + extract_financial_metrics)
src/ingestion/         pdf_to_markdown.py, semantic_chunker.py, ingest_documents.py
src/routes/            health.py, metrics.py, chat.py, ingestion.py
```

Run: `uv run uvicorn src.app:app --reload` (API) or `uv run ai-investor-intelligence-platform-server`
(CLI ingestion over `data/pdfs/`).

## Build progress

All 13 phases in `docs/project_journey.md` are implemented (backend scope). Phases 12–13
(separate frontend app, containerization/deployment) are explicitly out of scope for this
repo and only tracked there for completeness.

## Known gaps / not yet done

- `VOYAGE_API_KEY` and `ASTRA_DB_API_ENDPOINT` / `ASTRA_DB_APPLICATION_TOKEN` are now
  configured and live ingestion has been exercised end-to-end (see `changelog.md`
  2026-08-03 "First live ingestion run"). Postgres connection details still need
  confirming — not yet verified against a live ingestion run through to `save_metrics`.
- No automated test suite (pytest) — verification so far has been manual/live smoke
  testing per module, described in `changelog.md`.
- No git commits yet for the backend build or the `src/` flattening — working tree has
  the full implementation but history is still just the initial "Project setup" commit.
- No frontend app exists yet (by design — separate repo/app, out of scope here).

## Where to look for more

- `docs/memory/decisions.md` — why things are built this way, one entry per real fork.
- `docs/memory/changelog.md` — dated log of what changed, session by session.
- `docs/project_journey.md` — phase-by-phase build narrative.
- `/Users/arthur/.claude/plans/twinkly-cooking-honey.md` — the original build plan (local
  to the machine, not in this repo).
