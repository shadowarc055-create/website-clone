# Deployment Guide

## Local Docker Compose

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Pull an Ollama model if local summarization is required: `docker compose exec ollama ollama pull llama3.1`.

## Kubernetes

The `k8s/` directory contains starter manifests for API, worker, and frontend deployments. Use managed PostgreSQL, Redis, Neo4j, and OpenSearch for production.

## Security and compliance

- Require authentication and per-investigation authorization before public deployment.
- Store source provenance and legal basis for auditability.
- Keep `ENABLE_DARK_WEB=false` unless your organization has approved indexes and legal review.
- Rate-limit all external connectors and honor robots.txt and provider terms.
