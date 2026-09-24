# Cold-Chain Logistics FDE Agent

An end-to-end **Forward Deployed Engineer** build: an agentic AI system that sits on top of a "legacy" enterprise fleet database, enforces least-privilege data access, retrieves company SOPs, and gives dispatchers a chat console to reason about shipments, weather, and SOP compliance in real time.

The scenario simulates a real FDE engagement — a legacy MSSQL fleet-tracking system, locked-down views for an AI agent, retrieval-augmented SOP lookups, tool-using orchestration, full audit logging, and a production deployment.

## Architecture

```
CSV dataset ──▶ Legacy MSSQL (Docker/EC2, dbo.TBL_SC_FLEET_HIST_RAW)
                        │
                        ▼
        FDE_VIEWS schema (read-only views, RBAC via USR_FDE_RO)
                        │
                        ▼
        LangGraph agent + tools (SQL, weather, SOP retrieval)
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
     Pinecone SOP index    AgentAuditLog table
                        │
                        ▼
              Streamlit dispatcher console
                        │
                        ▼
              EC2 + systemd deployment
```

## Tech stack

- **Data / DB**: SQL Server 2022 (Docker), pyodbc, SQLAlchemy
- **Retrieval**: Pinecone (vector store for SOP docs)
- **Agent**: LangGraph, LangChain, OpenAI
- **UI**: Streamlit
- **Infra**: Docker, AWS EC2, systemd
- **Env/deps**: uv, Python 3.12.13

## Getting started

```bash
# install the pinned Python version and create the venv
uv python install 3.12.13
uv venv --python 3.12.13

# install dependencies
uv pip install -r requirements.txt
source .venv/bin/activate
```

Spin up the legacy database:

```bash
docker run -v mssql_data:/var/opt/mssql \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
  -p 1433:1433 \
  --name legacy-mssql \
  -d mcr.microsoft.com/mssql/server:2022-latest
```

## Progress

### Phase 0 — Legacy data ingestion
- [x] Source dataset (`data/raw/dynamic_supply_chain_logistics_dataset.csv`)
- [x] `legacy-mssql` Docker container running (SQL Server 2022, port 1433)
- [x] Python env pinned and reproducible via `uv` (Python 3.12.13, `requirements.txt`)
- [x] `scripts/ingest_legacy_data.py` — load CSV into `dbo.TBL_SC_FLEET_HIST_RAW`
- [x] Verify row counts (32,065 rows loaded)
- [ ] Production DB on EC2 (`c7i-flex.large`, 30GB, Ubuntu)

### Phase 1 — SOP ingestion (RAG)
- [ ] Pinecone index + API key
- [ ] `scripts/ingest_sop_pinecone.py`

### Phase 2 — Data security
- [ ] `FDE_VIEWS` schema + read-only views over raw tables
- [ ] `USR_FDE_RO` least-privilege SQL login for the agent
- [ ] Verify: agent can read views, denied on raw tables

### Phase 3 — Agent orchestration
- [ ] `src/agent_tools.py` (SQL, weather, SOP retrieval tools)
- [ ] `src/orchestrator.py` (LangGraph agent)
- [ ] Validate tool-routing and no-tool-routing behavior

### Phase 4 — Audit logging
- [ ] `FDE_VIEWS.AgentAuditLog` table
- [ ] Agent writes session/tool/content to audit log on every run

### Phase 5 — Dispatcher UI
- [ ] `src/ui.py` (Streamlit console)

### Phase 6 — Deployment
- [ ] EC2 provisioning + dependencies (ODBC driver, venv)
- [ ] `systemd` service for the Streamlit console

## Repo structure

```
data/
  raw/            # source dataset
  source/         # data provenance notes
scripts/          # ingestion / one-off data scripts
src/
  ai_fde/         # package
  agent_tools.py  # (Phase 3)
  orchestrator.py # (Phase 3)
  ui.py           # (Phase 5)
```
