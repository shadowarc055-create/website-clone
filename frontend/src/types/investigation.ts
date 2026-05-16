export type EntityType = 'email' | 'phone' | 'username' | 'domain' | 'ip_address' | 'crypto_wallet' | 'social_profile' | 'full_name' | 'url' | 'unknown';

export interface Investigation {
  id: string;
  status: 'queued' | 'running' | 'stabilized' | 'failed';
  root_entity: { type: EntityType; value: string; normalized: string; confidence: number };
  max_depth: number;
  min_confidence: number;
}

export interface InvestigationSummary {
  investigation: Investigation;
  entity_count: number;
  relationship_count: number;
  finding_count: number;
  summary?: string;
}

export interface GraphResponse {
  nodes: Array<{ id: string; label: string; type: EntityType; confidence: number }>;
  edges: Array<{ id: string; source: string; target: string; label: string; confidence: number }>;
}
