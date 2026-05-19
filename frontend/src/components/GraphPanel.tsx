"use client";

import cytoscape from "cytoscape";
import { useEffect, useRef } from "react";
import type { GraphData } from "@/lib/api";

export function GraphPanel({ graph }: { graph: GraphData | null }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !graph) {
      return;
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...graph.nodes.map((node) => ({ data: { id: node.id, label: node.name, type: node.label } })),
        ...graph.edges.map((edge, index) => ({
          data: { id: `e-${index}`, source: edge.source, target: edge.target, label: edge.type }
        }))
      ],
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#2f7d5c",
            label: "data(label)",
            color: "#18202a",
            "font-size": 10,
            "text-wrap": "wrap",
            "text-max-width": "90px"
          }
        },
        {
          selector: "node[type='Article']",
          style: { "background-color": "#1d6f99", width: 34, height: 34 }
        },
        {
          selector: "node[type='Publisher']",
          style: { "background-color": "#b7791f" }
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#9aa79b",
            "target-arrow-color": "#9aa79b",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier"
          }
        }
      ],
      layout: { name: "cose", animate: false, fit: true, padding: 24 }
    });

    return () => cy.destroy();
  }, [graph]);

  return <div ref={containerRef} className="h-[460px] w-full rounded-lg border border-line bg-white" />;
}
