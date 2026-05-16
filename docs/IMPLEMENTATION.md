# Step-by-Step Implementation Plan

1. **Bootstrap infrastructure** with Docker Compose for FastAPI, Redis, PostgreSQL, Neo4j, OpenSearch, Ollama, and the React frontend.
2. **Persist investigations** in PostgreSQL tables and mirror entity relationships into Neo4j using idempotent merge semantics.
3. **Submit root entities** through `POST /api/investigations`, normalize them, and enqueue worker jobs.
4. **Run async investigators** with `asyncio.gather`, keeping each investigator independent and side-effect free.
5. **Extract pivots** from findings, normalize them, score confidence, store provenance, and enqueue only unseen entities that pass confidence and depth policies.
6. **Index findings** in OpenSearch to support keyword search, timeline review, and report generation.
7. **Apply local AI** through Ollama for summarization, duplicate review, relationship analysis, and analyst-facing report prose.
8. **Render graph intelligence** in Cytoscape.js and poll live status from FastAPI.
9. **Generate reports** as JSON in-process and PDF through a worker task for production deployments.
10. **Scale safely** by adding connector rate limits, audit logging, tenant isolation, and per-source legal policy controls.
