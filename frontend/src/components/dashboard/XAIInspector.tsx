"use client";

import React from "react";
import { FraudPredictionResult } from "@/types/fraud";
import { formatPercent } from "@/lib/utils";

interface XAIInspectorProps {
  prediction: FraudPredictionResult;
}

export function XAIInspector({ prediction }: XAIInspectorProps) {
  const isBlocked = prediction.decision === "BLOCKED";
  const isFlagged = prediction.decision === "FLAGGED_REVIEW";

  return (
    <div className="space-y-3">
      
      {/* Risk Decision Card */}
      <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[11px] font-medium text-slate-400 block uppercase tracking-wider">
              Risk Assessment
            </span>
            <div className="flex items-baseline gap-2 mt-0.5">
              <span className={`text-2xl font-bold font-mono tracking-tight ${
                isBlocked ? "text-red-400" : isFlagged ? "text-amber-400" : "text-emerald-400"
              }`}>
                {formatPercent(prediction.gnnFraudProbability)}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded font-mono font-medium ${
                isBlocked 
                  ? "bg-red-950/60 text-red-300 border border-red-900/50" 
                  : isFlagged 
                  ? "bg-amber-950/60 text-amber-300 border border-amber-900/50" 
                  : "bg-emerald-950/60 text-emerald-300 border border-emerald-900/50"
              }`}>
                {prediction.decision === "FLAGGED_REVIEW" ? "Flagged for Review" : prediction.decision}
              </span>
            </div>
          </div>

          {/* Model Lift Pill */}
          <div className="text-right font-mono text-[11px]">
            <span className="text-slate-400 block">Tabular XGBoost:</span>
            <span className="text-slate-300 font-medium">{formatPercent(prediction.xgboostProbability)}</span>
            <span className="text-[10px] text-cyan-400 block">
              +{(Math.max(0, prediction.gnnFraudProbability - prediction.xgboostProbability) * 100).toFixed(1)}% GNN Lift
            </span>
          </div>
        </div>
      </div>

      {/* Attribution Factors (Why this was flagged) */}
      <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Explainable AI (XAI) Attribution
          </span>
          <span className="text-[10px] text-slate-400 font-mono">
            Captum Integrated Gradients
          </span>
        </div>

        <div className="space-y-3">
          {prediction.xaiFactors.map((factor) => {
            const pct = Math.round(factor.importanceScore * 100);
            return (
              <div key={factor.id} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-300">
                    {factor.featureName}
                  </span>
                  <span className="font-mono text-indigo-400 font-semibold text-[11px]">
                    {pct}%
                  </span>
                </div>

                {/* Minimal bar */}
                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-300 ${
                      factor.impact === "CRITICAL" ? "bg-red-400" :
                      factor.impact === "HIGH" ? "bg-amber-400" : "bg-indigo-400"
                    }`}
                    style={{ width: `${pct}%` }}
                  />
                </div>

                <p className="text-[11px] text-slate-400 leading-normal">
                  {factor.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
