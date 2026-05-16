CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS investigations (
  id UUID PRIMARY KEY,
  status TEXT NOT NULL,
  root_entity_key TEXT NOT NULL,
  root_entity JSONB NOT NULL,
  max_depth INTEGER NOT NULL CHECK (max_depth >= 0),
  min_confidence DOUBLE PRECISION NOT NULL CHECK (min_confidence >= 0 AND min_confidence <= 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entities (
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  type TEXT NOT NULL,
  value TEXT NOT NULL,
  normalized TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  source TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  payload JSONB NOT NULL,
  PRIMARY KEY (investigation_id, key)
);

CREATE TABLE IF NOT EXISTS relationships (
  id BIGSERIAL PRIMARY KEY,
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  edge_key TEXT NOT NULL,
  source_key TEXT NOT NULL,
  target_key TEXT NOT NULL,
  type TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  provenance TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_relationship_edge UNIQUE (investigation_id, edge_key)
);

CREATE TABLE IF NOT EXISTS findings (
  id BIGSERIAL PRIMARY KEY,
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  investigator TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  source_url TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_entities_type_normalized ON entities(type, normalized);
CREATE INDEX IF NOT EXISTS idx_relationships_edge ON relationships(investigation_id, edge_key);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(investigation_id, source_key);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(investigation_id, target_key);
CREATE INDEX IF NOT EXISTS idx_findings_investigator ON findings(investigation_id, investigator);
