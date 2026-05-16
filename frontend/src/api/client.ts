import type { EntityType, GraphResponse, Investigation, InvestigationSummary } from '../types/investigation';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function createInvestigation(type: EntityType, value: string): Promise<Investigation> {
  const response = await fetch(`${API_BASE_URL}/api/investigations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, value, max_depth: 3, min_confidence: 0.35, legal_basis: 'authorized OSINT investigation' })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function getInvestigation(id: string): Promise<InvestigationSummary> {
  const response = await fetch(`${API_BASE_URL}/api/investigations/${id}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function getGraph(id: string): Promise<GraphResponse> {
  const response = await fetch(`${API_BASE_URL}/api/investigations/${id}/graph`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
