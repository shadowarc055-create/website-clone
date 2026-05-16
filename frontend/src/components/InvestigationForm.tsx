import { FormEvent, useState } from 'react';
import type { EntityType } from '../types/investigation';

const entityTypes: EntityType[] = ['email', 'phone', 'username', 'domain', 'ip_address', 'crypto_wallet', 'social_profile', 'full_name'];

export function InvestigationForm({ onSubmit }: { onSubmit: (type: EntityType, value: string) => Promise<void> }) {
  const [type, setType] = useState<EntityType>('email');
  const [value, setValue] = useState('analyst@example.com');
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try { await onSubmit(type, value); } finally { setBusy(false); }
  }

  return <form onSubmit={submit} className="rounded-xl bg-slate-900 p-4 shadow-xl ring-1 ring-slate-700">
    <div className="grid gap-3 md:grid-cols-[180px_1fr_auto]">
      <select className="rounded bg-slate-800 p-3" value={type} onChange={(event) => setType(event.target.value as EntityType)}>
        {entityTypes.map((entityType) => <option key={entityType} value={entityType}>{entityType}</option>)}
      </select>
      <input className="rounded bg-slate-800 p-3" value={value} onChange={(event) => setValue(event.target.value)} placeholder="Enter investigation seed" />
      <button disabled={busy} className="rounded bg-cyan-500 px-5 font-semibold text-slate-950 disabled:opacity-60">{busy ? 'Starting…' : 'Investigate'}</button>
    </div>
  </form>;
}
