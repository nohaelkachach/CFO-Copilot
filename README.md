# CFO Copilot
 
> AI-powered financial intelligence platform for SMEs — upload any financial document, get instant insights.
 
![CI](https://github.com/nohaelkachach/CFO-Copilot/actions/workflows/ci.yml/badge.svg)
 
## Overview
 
CFO Copilot is a full-stack web application that helps small and medium businesses make sense of their financial documents. Upload invoices, P&L statements, balance sheets, bank statements, or tax declarations — the AI classifies them, extracts key financial data, detects anomalies, and answers natural language questions about your finances.
 
Built as a portfolio project demonstrating full-stack AI engineering with production-grade practices.
 
## Features
 
- **AI Document Classification** — Automatically identifies document type (invoice, P&L, balance sheet, bank statement, VAT declaration) and extracts key fields
- **Financial Dashboard** — Real-time KPI cards, P&L bar chart, balance sheet breakdown, and cash flow trend
- **Anomaly Detection** — AI flags unusual transactions, inconsistencies, and audit risks across all uploaded documents
- **Natural Language Q&A** — Ask anything about your finances in plain English, grounded strictly in your documents
- **Multi-document Analysis** — Cross-references multiple documents to detect patterns and inconsistencies
- **Professional Onboarding** — Two-step company setup with sector selection
## Tech Stack
 
**Backend**
- FastAPI — REST API with async background task processing
- SQLAlchemy + PostgreSQL 18 — ORM with relational schema (companies, documents, invoices, financial statements, tax documents, bank statements, anomalies)
- LangChain + Groq (Llama 3.3 70B) — AI classification, anomaly detection, and Q&A chains
- pdfplumber — PDF text extraction
- Pydantic V2 — structured AI output validation
- pytest — unit and integration tests with mocking
**Frontend**
- React 19 + TypeScript + Vite — component-based UI
- Tailwind CSS — utility-first styling
- Recharts — financial charts (bar chart, area chart)
- React Router — client-side navigation
- Axios — API communication
**Infrastructure**
- GitHub Actions — CI pipeline (tests + frontend build on every push)
- Docker + Docker Compose — containerized deployment (backend, frontend, PostgreSQL, each as a separate service on a shared network)
- uv — fast Python package management
## Architecture
 
```
CFO-Copilot/
├── backend/
│   ├── core/           # Config, LLM client, Pydantic AI models, prompts
│   ├── db/             # SQLAlchemy engine and session management
│   ├── models/         # Database ORM models
│   ├── schemas/        # Pydantic API schemas
│   ├── routers/        # FastAPI route handlers
│   ├── services/       # Business logic (document processing, AI service)
│   ├── tests/          # pytest test suite
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ # Reusable UI components (layout, dashboard, anomalies, chat)
│   │   ├── pages/      # Page-level components (Dashboard, Upload, Documents, Anomalies, Chat)
│   │   └── services/   # Axios API client
│   └── Dockerfile
└── docker-compose.yml
```
 
**Document Processing Pipeline:**
```
PDF Upload → Text Extraction (pdfplumber)
          → AI Classification (LangChain + Groq)
          → Save to Child Table (invoice/financial_statement/tax/bank_statement)
          → Cross-document Anomaly Detection
          → Update Status → Frontend Polling → UI Update
```
 
## Getting Started
 
### Prerequisites
- Docker Desktop
- Groq API key (free at [console.groq.com](https://console.groq.com))
### Environment Setup
 
Create a `.env` file in the project root (used by Docker Compose to configure all services):
 
```dotenv
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=cfo_copilot
DATABASE_URL=postgresql://your_db_user:your_db_password@db:5432/cfo_copilot
GROQ_API_KEY=your_groq_api_key
```
 
> Note: `DATABASE_URL` uses `db` as the host (the Postgres service name in `docker-compose.yml`), not `localhost` — this is how containers reach each other on the same Docker network. The username, password, and database name inside `DATABASE_URL` must exactly match `DB_USER`, `DB_PASSWORD`, and `DB_NAME` above.
 
### Run with Docker
 
```bash
docker-compose up --build
```
 
- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8080/docs`
- PostgreSQL: exposed on `localhost:5432`
To stop:
```bash
docker-compose down
```
 
To stop and wipe the database volume (fresh start):
```bash
docker-compose down -v
```
 
### Local Development (without Docker)
 
**Backend**
```bash
cd backend
 
# Install dependencies
uv sync --all-groups
 
# Add a .env file here with DATABASE_URL and GROQ_API_KEY
# (point DATABASE_URL at localhost instead of db if Postgres isn't containerized)
 
# Start the server
uv run uvicorn main:app --reload --port 8080
```
 
API docs available at `http://localhost:8080/docs`
 
**Frontend**
```bash
cd frontend
 
# Install dependencies
npm install
 
# Start dev server
npm run dev
```
 
App available at `http://localhost:5173`
 
### Run Tests
 
```bash
cd backend
uv run pytest tests/ -v
```
 
## Notes on PostgreSQL 18
 
This project uses the `postgres:18` Docker image, which changed its expected data directory structure compared to earlier Postgres versions. The Compose volume mount is set to `pgdata:/var/lib/postgresql` (not `/var/lib/postgresql/data`) to match this. If you previously ran an older Postgres version against this project's volume, run `docker-compose down -v` before starting fresh with `postgres:18` to avoid a data directory conflict.
 
## Document Types Supported
 
| Category | Types |
|---|---|
| Financial Statements | P&L / Income Statement, Balance Sheet, Cash Flow, Budget |
| Tax Documents | VAT (TVA), Corporate Tax (IS), CNSS, Income Tax (IR) |
| Audit Documents | Invoices, Bank Statements, Contracts, Payslips, Receipts |
 
## API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| POST | `/companies/` | Create company and session |
| GET | `/companies/me` | Get current company |
| POST | `/documents/upload` | Upload and process document |
| GET | `/documents/{id}/status` | Poll processing status |
| GET | `/financial/pnl` | P&L data for charts |
| GET | `/financial/balance-sheet/latest` | Latest balance sheet |
| GET | `/anomalies/` | List anomalies with filter |
| PATCH | `/anomalies/{id}/resolve` | Mark anomaly resolved |
| POST | `/chat/` | Ask natural language question |
| GET | `/bank-statements/cash-flow` | Cash flow over time |
 
## Key Engineering Decisions
 
**Background task DB session isolation** — FastAPI closes the request DB session before background tasks run. A dedicated `SessionLocal()` is created inside `run_process_document` to avoid "session already closed" errors — a common FastAPI pattern.
 
**StrOutputParser over JsonOutputParser** — LangChain's `JsonOutputParser` injects format instructions that confuse the LLM. Using `StrOutputParser` with manual JSON parsing gives more reliable, predictable classification results.
 
**Pydantic V2 output validation** — All AI responses are validated through Pydantic models (`DocumentClassification`, `AnomalyItem`) before touching the database, ensuring type safety and graceful fallbacks.
 
**Cross-document anomaly detection** — When a new document is processed, anomaly detection receives the combined extracted text of all previously processed documents, enabling detection of cross-document inconsistencies.
 
**PostgreSQL over SQLite for production** — Migrated from SQLite (used during initial prototyping) to PostgreSQL for proper concurrent-write support and production-readiness. Environment variables are scoped per-service in `docker-compose.yml` so each container only receives what it needs — e.g. the backend receives `DATABASE_URL` and `GROQ_API_KEY`, not the raw Postgres provisioning credentials (`DB_USER`/`DB_PASSWORD`/`DB_NAME`), which are only needed by the `db` service itself.
 
**Containerized multi-service architecture** — Backend, frontend, and PostgreSQL each run as isolated Docker containers on a shared Compose network, communicating via service names rather than `localhost`, mirroring how the app would be deployed in a real cloud environment.
 
## Author
 
**Noha El Kachach** — CS graduate (AI specialization)
