# Deployment Guide

## Local Docker Compose

1. Copy `.env.example` to `.env`.
2. Keep `QUEUE_MODE=inline` for local single-process development, or set `QUEUE_MODE=celery` when using durable worker execution.
3. Use `REPOSITORY_BACKEND=postgres` whenever API and workers run in separate processes so queued work can share investigation state.
4. Run `docker compose up --build`.
5. Pull an Ollama model if local summarization is required: `docker compose exec ollama ollama pull llama3.1`.

## Kubernetes

The `k8s/` directory contains starter manifests for API, worker, and frontend deployments. Use managed PostgreSQL, Redis, Neo4j, and OpenSearch for production.

## Security and compliance

- Require authentication and per-investigation authorization before public deployment.
- Store source provenance and legal basis for auditability.
- Keep `ENABLE_DARK_WEB=false` unless your organization has approved indexes and legal review.
- Rate-limit all external connectors and honor robots.txt and provider terms.

## Local intelligence indexes

Mount legally obtained JSONL metadata indexes and set `BREACH_INDEX_PATH` or `DARK_WEB_INDEX_PATH`. Each line should contain an `entity` field, optional `related` pivots, provenance fields, and confidence. The bundled sample data is synthetic.
