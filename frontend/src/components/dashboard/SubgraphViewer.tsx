"use client";

import React, { useState } from "react";
import { 
  Smartphone, 
  Globe, 
  User, 
  ZoomIn, 
  ZoomOut,
  RotateCcw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { SubgraphData, GraphNode } from "@/types/fraud";
import { formatCurrency } from "@/lib/utils";

interface SubgraphViewerProps {
  subgraph: SubgraphData;
  patternDetected?: string;
  targetTransactionId?: string;
}

export function SubgraphViewer({ 
  subgraph, 
  patternDetected, 
  targetTransactionId 
}: SubgraphViewerProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState<number>(1);

  const width = 600;
  const height = 360;
  const centerX = width / 2;
  const centerY = height / 2;

  const nodePositions: Record<string, { x: number; y: number }> = {};
  
  const accountNodes = subgraph.nodes.filter(n => n.type === "account");
  const deviceNodes = subgraph.nodes.filter(n => n.type === "device");
  const ipNodes = subgraph.nodes.filter(n => n.type === "ip");

  const radius = Math.min(130, 70 + accountNodes.length * 12);
  accountNodes.forEach((node, i) => {
    const angle = (i / accountNodes.length) * 2 * Math.PI - Math.PI / 2;
    nodePositions[node.id] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });

  deviceNodes.forEach((node, i) => {
    nodePositions[node.id] = {
      x: centerX - 160 + (i * 90),
      y: 60,
    };
  });

  ipNodes.forEach((node, i) => {
    nodePositions[node.id] = {
      x: centerX + 160 - (i * 90),
      y: height - 60,
    };
  });

  return (
    <div className="rounded-xl border border-slate-800/60 bg-slate-900/20 overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-800/60 flex items-center justify-between">
        <div>
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            2-Hop Graph Topology
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Interconnected accounts, hardware, and IP infrastructure
          </p>
        </div>

        <div className="flex items-center gap-2">
          {patternDetected && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-300 font-mono">
              {patternDetected}
            </span>
          )}

          <div className="flex items-center gap-1">
            <button 
              className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
              onClick={() => setZoom(prev => Math.min(1.4, prev + 0.1))}
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button 
              className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
              onClick={() => setZoom(prev => Math.max(0.7, prev - 0.1))}
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button 
              className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
              onClick={() => setZoom(1)}
              title="Reset"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div className="relative flex-1 min-h-[320px] flex items-center justify-center overflow-hidden bg-slate-950/40">
        <svg 
          viewBox={`0 0 ${width} ${height}`} 
          className="w-full h-full transition-transform duration-200"
          style={{ transform: `scale(${zoom})` }}
        >
          <defs>
            <marker id="arrow-subtle" viewBox="0 0 10 10" refX="21" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#64748b" />
            </marker>
            <marker id="arrow-danger" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#f87171" />
            </marker>
          </defs>

          {/* Edges */}
          {subgraph.edges.map(edge => {
            const src = nodePositions[edge.source] || { x: centerX, y: centerY };
            const dst = nodePositions[edge.target] || { x: centerX, y: centerY };
            const isHighRisk = (edge.importanceScore ?? 0) > 0.6 || edge.isLaunderingPattern;

            return (
              <g key={edge.id}>
                <line
                  x1={src.x}
                  y1={src.y}
                  x2={dst.x}
                  y2={dst.y}
                  stroke={edge.type !== "sends" ? "#334155" : isHighRisk ? "#ef4444" : "#475569"}
                  strokeWidth={isHighRisk ? 2 : 1.2}
                  strokeDasharray={edge.type !== "sends" ? "3 3" : "none"}
                  markerEnd={edge.type === "sends" ? (isHighRisk ? "url(#arrow-danger)" : "url(#arrow-subtle)") : "none"}
                  className="opacity-80"
                />
                {edge.amount && (
                  <text
                    x={(src.x + dst.x) / 2}
                    y={(src.y + dst.y) / 2 - 6}
                    fill={isHighRisk ? "#fca5a5" : "#94a3b8"}
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                  >
                    {formatCurrency(edge.amount)}
                  </text>
                )}
              </g>
            );
          })}

          {/* Nodes */}
          {subgraph.nodes.map(node => {
            const pos = nodePositions[node.id] || { x: centerX, y: centerY };
            const isSelected = selectedNode?.id === node.id;
            const isSevere = node.riskScore > 0.6;
            const isModerate = node.riskScore >= 0.1 && node.riskScore <= 0.6;

            const stroke = isSevere ? "#ef4444" : isModerate ? "#f59e0b" : "#38bdf8";
            const fill = isSevere ? "#450a0a" : "#0f172a";

            return (
              <g 
                key={node.id} 
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer group"
                onClick={() => setSelectedNode(node)}
              >
                {node.type === "account" && (
                  <circle
                    r="16"
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="transition-transform group-hover:scale-105"
                  />
                )}

                {node.type === "device" && (
                  <rect
                    x="-12"
                    y="-12"
                    width="24"
                    height="24"
                    rx="5"
                    fill="#1e1b4b"
                    stroke={stroke}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="transition-transform group-hover:scale-105"
                  />
                )}

                {node.type === "ip" && (
                  <rect
                    x="-11"
                    y="-11"
                    width="22"
                    height="22"
                    rx="3"
                    transform="rotate(45)"
                    fill="#134e4a"
                    stroke={stroke}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="transition-transform group-hover:scale-105"
                  />
                )}

                <g className="pointer-events-none" transform="translate(-6, -6)">
                  {node.type === "account" && <User className="w-3 h-3 text-slate-300" />}
                  {node.type === "device" && <Smartphone className="w-3 h-3 text-indigo-300" />}
                  {node.type === "ip" && <Globe className="w-3 h-3 text-teal-300" />}
                </g>

                <text
                  y="26"
                  fill="#cbd5e1"
                  fontSize="9"
                  fontFamily="monospace"
                  textAnchor="middle"
                  className="select-none"
                >
                  {node.label.length > 13 ? `${node.label.slice(0, 11)}…` : node.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Node Overlay */}
        {selectedNode && (
          <div className="absolute bottom-2 left-2 right-2 sm:right-auto sm:w-72 bg-slate-900/95 border border-slate-700/80 rounded-lg p-3 text-xs backdrop-blur-sm">
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800">
              <span className="font-mono font-medium text-white truncate">
                {selectedNode.label}
              </span>
              <button 
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-white text-xs px-1"
              >
                ✕
              </button>
            </div>
            <div className="mt-2 space-y-1 font-mono text-[11px]">
              <div className="flex justify-between text-slate-400">
                <span>Type:</span>
                <span className="text-slate-200 capitalize">{selectedNode.type}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Attributed Risk:</span>
                <span className={selectedNode.riskScore > 0.5 ? "text-red-400 font-bold" : "text-emerald-400"}>
                  {(selectedNode.riskScore * 100).toFixed(1)}%
                </span>
              </div>
              {selectedNode.metadata?.country && (
                <div className="flex justify-between text-slate-400">
                  <span>Country:</span>
                  <span className="text-slate-200">{selectedNode.metadata.country}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Minimal Legend */}
      <div className="px-4 py-2 border-t border-slate-800/60 bg-slate-950/40 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block" /> Account
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-sm bg-indigo-400 inline-block" /> Device
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rotate-45 bg-teal-400 inline-block" /> IP Egress
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-red-400 inline-block" /> High-Risk
          </span>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">
          Click any node to inspect
        </span>
      </div>
    </div>
  );
}
