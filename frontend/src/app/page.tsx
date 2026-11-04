"use client";

import React, { useState } from "react";
import { Header } from "@/components/dashboard/Header";
import { KPIGrid } from "@/components/dashboard/KPIGrid";
import { LiveStreamView } from "@/components/dashboard/LiveStreamView";
import { ScreenerView } from "@/components/dashboard/ScreenerView";
import { BenchmarkView } from "@/components/dashboard/BenchmarkView";
import { INITIAL_SUMMARY_KPIS, PREDEFINED_SCENARIOS, simulateMLInference } from "@/lib/ml-simulator";
import { FraudPredictionResult } from "@/types/fraud";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"screener" | "stream" | "benchmark">("screener");
  
  const defaultScenario = PREDEFINED_SCENARIOS[0];
  const [activePrediction, setActivePrediction] = useState<FraudPredictionResult>(() => {
    return simulateMLInference(
      defaultScenario.senderAccount,
      defaultScenario.receiverAccount,
      defaultScenario.amount,
      defaultScenario.timeDeltaHours,
      defaultScenario.deviceFingerprint,
      defaultScenario.ipAddress
    );
  });

  const handleSelectFromStream = (result: FraudPredictionResult) => {
    setActivePrediction(result);
    setActiveTab("screener");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      
      {/* Minimal Header */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-5 space-y-4">
        
        {/* KPI Summary Tiles */}
        <KPIGrid kpis={INITIAL_SUMMARY_KPIS} />

        {/* Clean Segmented Tab Control */}
        <div className="flex items-center justify-between border-b border-slate-800/60 pb-2.5 pt-1">
          <div className="flex items-center gap-1 bg-slate-900/60 border border-slate-800/80 p-1 rounded-xl">
            
            <button
              onClick={() => setActiveTab("screener")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                activeTab === "screener"
                  ? "bg-slate-800 text-white font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Transaction Screener &amp; Graph
            </button>

            <button
              onClick={() => setActiveTab("stream")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                activeTab === "stream"
                  ? "bg-slate-800 text-white font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Live Stream
            </button>

            <button
              onClick={() => setActiveTab("benchmark")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                activeTab === "benchmark"
                  ? "bg-slate-800 text-white font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Model Benchmarks
            </button>

          </div>

          <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
            Triton Serving &bull; &lt;15ms SLA
          </span>
        </div>

        {/* Active Tab View */}
        {activeTab === "screener" && (
          <ScreenerView initialPrediction={activePrediction} />
        )}

        {activeTab === "stream" && (
          <LiveStreamView onSelectTransaction={handleSelectFromStream} />
        )}

        {activeTab === "benchmark" && (
          <BenchmarkView />
        )}

      </main>

      {/* Clean Minimal Footer */}
      <footer className="border-t border-slate-900 py-3 text-center text-[11px] text-slate-400 font-mono">
        AEGIS &bull; Heterogeneous Graph Neural Network (PyTorch Geometric SAGEConv)
      </footer>

    </div>
  );
}
