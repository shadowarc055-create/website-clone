# Scaling Strategy

- Scale Celery workers horizontally by queue type (`investigations`, `screenshots`, `reports`).
- Partition OpenSearch indexes by month or tenant.
- Keep Neo4j write paths idempotent with `MERGE` and batch updates for high-volume investigations.
- Add connector-specific circuit breakers, budgets, and rate limits.
- Use Redis streams or Kafka when queue fan-out exceeds Celery visibility needs.
- Cache DNS/WHOIS responses with TTLs to reduce repeated lookups.
