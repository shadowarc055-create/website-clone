# API Documentation

## `POST /api/investigations`

Creates an investigation from a root entity and starts recursive processing.

Request:

```json
{
  "type": "email",
  "value": "analyst@example.com",
  "max_depth": 3,
  "min_confidence": 0.35,
  "legal_basis": "authorized OSINT investigation"
}
```

## `GET /api/investigations/{id}`

Returns investigation status, counts, and post-stabilization AI summary.

## `GET /api/investigations/{id}/graph`

Returns Cytoscape-ready nodes and edges.

## `GET /api/investigations/{id}/timeline`

Returns chronological findings for analyst review.

## `POST /api/investigations/{id}/reports`

Generates JSON reports in-process. PDF report generation is intended for worker deployment.
