import { useEffect, useState } from 'react';
import { createInvestigation, getGraph, getInvestigation } from '../api/client';
import type { EntityType, GraphResponse, InvestigationSummary } from '../types/investigation';
import { GraphView } from './GraphView';
import { InvestigationForm } from './InvestigationForm';

export function Dashboard() {
  const [activeId, setActiveId] = useState<string>();
  const [summary, setSummary] = useState<InvestigationSummary>();
  const [graph, setGraph] = useState<GraphResponse>();

  async function start(type: EntityType, value: string) {
    const investigation = await createInvestigation(type, value);
    setActiveId(investigation.id);
  }

  useEffect(() => {
    if (!activeId) return;
    const timer = window.setInterval(async () => {
      setSummary(await getInvestigation(activeId));
      setGraph(await getGraph(activeId));
    }, 1500);
    return () => window.clearInterval(timer);
  }, [activeId]);

  return <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
    <section className="mx-auto max-w-7xl space-y-6">
      <header>
        <p className="text-sm uppercase tracking-[0.35em] text-cyan-300">Autonomous OSINT</p>
        <h1 className="text-4xl font-bold">Recursive Entity Intelligence Dashboard</h1>
        <p className="mt-2 max-w-3xl text-slate-300">Authorized investigations only. Every discovered entity can become a new queue item with depth limits, visited tracking, and confidence scoring.</p>
      </header>
      <InvestigationForm onSubmit={start} />
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <GraphView graph={graph} />
        <aside className="rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
          <h2 className="text-xl font-semibold">Live status</h2>
          {summary ? <dl className="mt-4 space-y-3 text-sm">
            <div><dt className="text-slate-400">Status</dt><dd className="font-mono text-cyan-300">{summary.investigation.status}</dd></div>
            <div><dt className="text-slate-400">Entities</dt><dd>{summary.entity_count}</dd></div>
            <div><dt className="text-slate-400">Relationships</dt><dd>{summary.relationship_count}</dd></div>
            <div><dt className="text-slate-400">Findings</dt><dd>{summary.finding_count}</dd></div>
            <div><dt className="text-slate-400">AI Summary</dt><dd className="text-slate-300">{summary.summary ?? 'Waiting for stabilization…'}</dd></div>
          </dl> : <p className="mt-4 text-slate-400">Start an investigation to stream graph intelligence.</p>}
        </aside>
      </div>
    </section>
  </main>;
}
