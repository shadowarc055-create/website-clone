import cytoscape from 'cytoscape';
import { useEffect, useRef } from 'react';
import type { GraphResponse } from '../types/investigation';

export function GraphView({ graph }: { graph?: GraphResponse }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current || !graph) return;
    const cy = cytoscape({
      container: ref.current,
      elements: [
        ...graph.nodes.map((node) => ({ data: { id: node.id, label: node.label, type: node.type } })),
        ...graph.edges.map((edge) => ({ data: { id: edge.id, source: edge.source, target: edge.target, label: edge.label } }))
      ],
      style: [
        { selector: 'node', style: { label: 'data(label)', 'background-color': '#06b6d4', color: '#e2e8f0', 'font-size': 10 } },
        { selector: 'edge', style: { label: 'data(label)', width: 2, 'line-color': '#64748b', 'target-arrow-color': '#64748b', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'font-size': 8, color: '#cbd5e1' } }
      ],
      layout: { name: 'cose', animate: false }
    });
    return () => cy.destroy();
  }, [graph]);
  return <div className="h-[520px] rounded-xl bg-slate-950 ring-1 ring-slate-700" ref={ref} />;
}
