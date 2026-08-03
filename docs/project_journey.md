# AI-Powered Investor Intelligence Platform

> End-to-end Financial Document Intelligence backend using Anthropic Claude, Voyage AI, Astra DB, Postgres, and FastAPI. A pure REST JSON API — no server-rendered frontend; a separate frontend app consumes it.

---

## Project Goal

Build a REST API capable of:

* Processing financial reports (10-K filings)
* Extracting key financial insights (KPIs) via RAG
* Serving structured metrics for a separately-hosted dashboard frontend
* Supporting RAG-based financial research (chat)

Built on Anthropic Claude, Voyage AI embeddings, and Astra DB. Retrieval does real vector
similarity search against Astra DB rather than keyword matching.

---

## Phase 1: Project Planning

Status: Completed

Activities:

* Selected Financial Statement Analysis as the use case.
* Chose annual reports (10-Ks) as the primary data source.
* Selected Tesla, Apple, Microsoft, Amazon, Google, and Meta annual reports.
* Defined RAG + REST API architecture (no server-rendered dashboard — frontend is a separate app).
* Chose Anthropic Claude, Voyage AI, and Astra DB as the stack.

---

## Phase 2: Dataset Preparation

Status: Completed

Activities:

* Downloaded annual reports (6 companies).
* Stored PDF files under `data/pdfs/`.

---

## Phase 3: PDF to Markdown Conversion

Status: Completed

Module: `src/ingestion/pdf_to_markdown.py`

Objective: Convert annual report PDFs into markdown format suitable for downstream LLM processing.

Library: PyMuPDF4LLM

Output: `data/markdown/`

---

## Phase 4: Semantic Chunking

Status: Completed

Module: `src/ingestion/semantic_chunker.py`

Objective: Generate semantically meaningful chunks from markdown documents.

Library: LangChain `SemanticChunker`

Embedding Model: Voyage AI (`voyage-3`, 1024 dimensions)

Output: Document Chunks

---

## Phase 5: Anthropic + Voyage AI Integration

Status: Completed

Modules:

* `src/llm/anthropic_client.py`
* `src/embeddings/voyage_embeddings.py`

Objective: Centralize LLM and embeddings client configuration.

Deliverables:

* Voyage AI embeddings client (`get_embeddings()`)
* Anthropic chat client (`get_client()`, `get_chat_completion()`)
* Structured KPI extraction via `langchain-anthropic`'s `with_structured_output()`
  (`get_structured_completion()`)

---

## Phase 6: Astra DB Vector Store Integration

Status: Completed

Modules:

* `src/vectorstore/create_index.py`
* `src/vectorstore/astra_vectorstore.py`

Objective: Store document chunks and embeddings for retrieval, with real vector similarity search.

Deliverables:

* Idempotent collection creation (`ensure_collection()`)
* Chunk upload with embeddings (`upload_chunks()`)
* Vector similarity search with company/year metadata filtering (`Retriever`)

---

## Phase 7: KPI Extraction

Status: Completed

Module: `src/rag/kpi_extractor_rag.py`

Objective: Extract financial KPIs using Retrieval-Augmented Generation (RAG).

KPIs:

* Revenue
* Net Income
* Operating Income
* Cash Flow from Operating Activities
* Total Assets
* Total Liabilities
* Top Risk Factors
* Top Growth Drivers

Output: Structured Financial Metrics (`FinancialMetrics` pydantic model)

---

## Phase 8: Postgres Integration

Status: Completed

Modules: `src/database/*.py`

Objective: Store extracted KPI data for API consumption.

Deliverables:

* `create_database()` / `create_tables()` — `financial_metrics` table
* `save_metrics()` — persist extracted KPIs per company/year, with source file traceability
* `get_metrics()` — latest metrics row per company/year (window function)

Output: Financial Metrics Database

---

## Phase 9: Ingestion Orchestration

Status: Completed

Module: `src/ingestion/ingest_documents.py`

Objective: Chain PDF → Markdown → Chunk → Embed → Upload → Extract → Save into one pipeline.

Deliverables:

* `parse_company_year()` — derive company/year from filename
* `ingest_document()` — single-document pipeline
* `ingest_directory()` — batch pipeline over `data/pdfs/`

---

## Phase 10: FastAPI REST Backend

Status: Completed

Module: `src/app.py` + `src/routes/*.py`

Objective: Expose a pure JSON REST API — no server-rendered templates — for a separately-hosted
frontend to consume. CORS enabled for local frontend dev servers.

Endpoints:

* `GET /api/health` — service health check
* `GET /api/metrics` — financial metrics, optional `company`/`year` filters
* `GET /api/companies` — distinct companies with ingested data
* `POST /api/chat` — RAG-grounded financial research chat
* `POST /api/upload` — upload a new 10-K PDF and run the full ingestion pipeline

---

## Phase 11: RAG Research Pipeline

Status: Completed

Implemented as part of Phase 10's `/api/chat` endpoint plus the retrieval logic in
`vectorstore/astra_vectorstore.py::Retriever`.

Components:

* Retriever (real vector similarity search + metadata filtering)
* System prompt / context builder
* Claude response generator

Example Questions:

* Why did revenue increase?
* What are the major risks?
* What acquisitions were discussed?
* Compare AI investments across companies.

---

## Phase 12: Frontend (separate app, future)

Status: Pending / Out of scope for this repo

Objective: Build a separately-hosted frontend (framework TBD) that consumes the `/api/*` REST
endpoints above. Not part of this backend's build — tracked here only for
completeness.

---

## Phase 13: Containerization & Deployment (future)

Status: Pending / Out of scope for this repo

Objective: Package the backend (and eventual frontend) for deployment. Deferred — this project
currently targets local development only.

---

## Final Deliverable (current scope)

AI-Powered Investor Intelligence Platform — REST Backend

Capabilities:

* Financial Report Processing
* Real Vector Semantic Search (Astra DB)
* KPI Extraction (Claude structured output)
* REST API for Metrics, Companies, Chat, and Upload
* RAG-Based Financial Research
