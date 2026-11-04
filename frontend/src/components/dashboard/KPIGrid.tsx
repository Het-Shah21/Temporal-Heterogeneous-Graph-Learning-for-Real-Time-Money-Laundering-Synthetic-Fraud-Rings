"use client";

import React from "react";
import { TransactionSummaryKPI } from "@/types/fraud";

interface KPIGridProps {
  kpis: TransactionSummaryKPI;
}

export function KPIGrid({ kpis }: KPIGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      
      {/* 1. Scanned */}
      <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <span className="text-[11px] text-slate-400 font-medium block">
          Transactions Evaluated
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-xl sm:text-2xl font-semibold font-mono text-white tracking-tight">
            {kpis.totalProcessed.toLocaleString()}
          </span>
        </div>
        <span className="text-[11px] text-slate-500 block mt-0.5">
          Temporal test dataset
        </span>
      </div>

      {/* 2. Catch Rate */}
      <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <span className="text-[11px] text-slate-400 font-medium block">
          Fraud Catch Rate (Recall)
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-xl sm:text-2xl font-semibold font-mono text-emerald-400 tracking-tight">
            80.0%
          </span>
        </div>
        <span className="text-[11px] text-slate-500 block mt-0.5">
          8 of 10 launderers caught
        </span>
      </div>

      {/* 3. Alert Rate */}
      <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <span className="text-[11px] text-slate-400 font-medium block">
          Alert Screening Rate
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-xl sm:text-2xl font-semibold font-mono text-amber-300 tracking-tight">
            0.26%
          </span>
        </div>
        <span className="text-[11px] text-slate-500 block mt-0.5">
          1,561 alerts generated
        </span>
      </div>

      {/* 4. Latency */}
      <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <span className="text-[11px] text-slate-400 font-medium block">
          Decision Latency
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-xl sm:text-2xl font-semibold font-mono text-indigo-300 tracking-tight">
            7.4 ms
          </span>
        </div>
        <span className="text-[11px] text-slate-500 block mt-0.5">
          Well within &lt;15ms target
        </span>
      </div>

    </div>
  );
}
