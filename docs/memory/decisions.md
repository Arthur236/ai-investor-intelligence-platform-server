# Decisions

> Append-only log of real forks in the road: a choice was made among genuine
> alternatives, for a reason that isn't obvious from reading the code. One entry per
> decision. Never edit or delete a past entry to reflect a later reversal — if a
> decision is later reversed, add a new entry that says so and links back (`See DEC-004`).
> Don't log routine implementation choices that follow obviously from an already-logged
> decision.

## DEC-001: Anthropic + Voyage AI + Astra DB as the stack

Date: 2026-08-03 (backdated — reconstructed from session history)

The developer has Anthropic API credits and prior hands-on experience with Pinecone and
Astra DB.

Decision: use Anthropic Claude (chat + KPI extraction), Voyage AI (embeddings —
Claude has no first-party embeddings API), and Astra DB (vector store, chosen over
Pinecone on developer familiarity).

## DEC-002: langchain-anthropic's `with_structured_output()` over raw Anthropic SDK tool-use

Date: 2026-08-03 (backdated)

For structured KPI extraction (`FinancialMetrics` schema), two approaches were viable:
raw Anthropic SDK tool-use, or `langchain-anthropic`'s `.with_structured_output()`.

Decision: use `langchain-anthropic`. It was already a pyproject dependency, and the
ingestion pipeline already uses LangChain `Document` objects via
`langchain_experimental.SemanticChunker` — staying in the LangChain object model avoids
mixing two client styles in one codebase.

## DEC-003: claude-sonnet-5 as the single default model

Date: 2026-08-03 (backdated)

One `ANTHROPIC_MODEL` env var (`src/config.py`) drives both chat and KPI-extraction
calls, defaulting to `claude-sonnet-5`. No per-task model tiering was introduced —
revisit only if cost/latency profiling on real usage justifies splitting them.

## DEC-004: Pure REST JSON backend, no server-rendered dashboard

Date: 2026-08-03 (backdated)

The alternative was a Jinja2-rendered dashboard served directly from the backend. This
project splits backend and frontend: the backend (this repo) exposes JSON-only endpoints under
`/api/*` with CORS enabled (`ALLOWED_ORIGINS` in `src/config.py`); a separate frontend
app (not yet built, out of scope here) will consume them.

Why it matters: don't add template rendering, static file mounting for a dashboard, or
`jinja2` back into this backend. If a frontend is added, it belongs in its own
app/repo/directory, not inside `src/`.

## DEC-005: Astra DB retrieval uses real vector similarity search, not keyword search

Date: 2026-08-03 (backdated)

Plain keyword/full-text search over a store that also holds embeddings is an easy trap:
it looks like vector retrieval but never uses the vectors.

Decision: do real similarity search. Astra requires the vector field to be named `$vector` to
be ANN-indexed (`src/vectorstore/astra_vectorstore.py::upload_chunks`); `Retriever.invoke()`
embeds the query and does a real `collection.find(filter, vector=..., include_similarity=True)`
call with company/year metadata filtering, not a text match.

## DEC-006: `src/` is the installable package itself, with relative imports

Date: 2026-08-03 (backdated)

Original layout nested the package one level deeper: `src/ai_investor_intelligence_platform/`.
Developer asked to flatten everything directly under `src/`. This exposed a real fork:

- **Flat, unpackaged imports** (`from config import ...`) — simplest to read, but breaks
  once the project is installed/run as a package (`uv run python -c "import config"`
  fails with `ModuleNotFoundError`; confirmed empirically).
- **`src` as the package name + relative imports** (`from .config import ...`,
  `from ..llm.anthropic_client import ...`) — keeps `uv run uvicorn src.app:app` and the
  `ai-investor-intelligence-platform-server` console script working exactly as before.

Decision: the second option. Required `[tool.uv.build-backend]` in `pyproject.toml`
(`module-name = "src"`, `module-root = ""`) since `uv_build` otherwise expects
`src/<normalized-project-name>/__init__.py`, not `src/__init__.py` directly.

Why it matters: any new module added under `src/` must use relative imports
(`.` for same-package, `..` for parent package), not absolute imports rooted at
`src.something` or bare module names. `src/config.py`'s `REPO_ROOT` is
`Path(__file__).resolve().parents[1]` — if `config.py` ever moves to a different depth,
this must be recalculated (a `parents[2]` vs `parents[1]` bug here previously caused
silent 0-PDFs-converted failures; see `changelog.md`).
