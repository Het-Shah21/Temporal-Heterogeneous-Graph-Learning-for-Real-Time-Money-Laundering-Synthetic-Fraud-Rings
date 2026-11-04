"use client";

import React, { useState, useEffect } from "react";
import { Pause, Play, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { FraudPredictionResult } from "@/types/fraud";
import { simulateMLInference } from "@/lib/ml-simulator";

interface LiveStreamViewProps {
  onSelectTransaction: (result: FraudPredictionResult) => void;
}

const STREAM_ACCOUNTS = [
  "ACC_8812_CORP", "ACC_9901_MULE", "ACC_3304_RETAIL", 
  "ACC_5500_HUB", "ACC_1024_VIP", "ACC_7731_OFFSHORE", 
  "ACC_0012_BIZ", "ACC_9904_SINK", "ACC_4421_PAYROLL"
];

export function LiveStreamView({ onSelectTransaction }: LiveStreamViewProps) {
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [transactions, setTransactions] = useState<FraudPredictionResult[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<"ALL" | "ALERTS_ONLY">("ALL");

  useEffect(() => {
    const initialBatch: FraudPredictionResult[] = [];
    for (let i = 0; i < 8; i++) {
      const sender = STREAM_ACCOUNTS[i % STREAM_ACCOUNTS.length];
      const receiver = STREAM_ACCOUNTS[(i + 2) % STREAM_ACCOUNTS.length];
      const isLaunderingSeed = i === 1 || i === 4;
      const amount = isLaunderingSeed ? 125000 + i * 8000 : 250 + i * 450;
      const res = simulateMLInference(
        sender, 
        receiver, 
        amount, 
        0.5 + i * 0.2, 
        isLaunderingSeed ? "DEV_TOR_0991A" : "DEV_SAFARI_MAC", 
        isLaunderingSeed ? "185.220.101.45" : "72.14.201.2"
      );
      initialBatch.push(res);
    }
    setTransactions(initialBatch);
  }, []);

  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(() => {
      const randomIdx = Math.floor(Math.random() * STREAM_ACCOUNTS.length);
      const sender = STREAM_ACCOUNTS[randomIdx];
      const receiver = STREAM_ACCOUNTS[(randomIdx + 3) % STREAM_ACCOUNTS.length];
      const isBurst = Math.random() < 0.25;
      const amount = isBurst 
        ? Math.floor(80000 + Math.random() * 95000) 
        : Math.floor(45 + Math.random() * 3200);

      const newTxn = simulateMLInference(
        sender,
        receiver,
        amount,
        Number((Math.random() * 3).toFixed(1)),
        isBurst ? "DEV_FARM_882" : "DEV_CLIENT_IOS",
        isBurst ? "103.251.167.12" : "198.51.100.4"
      );

      setTransactions((prev) => [newTxn, ...prev.slice(0, 24)]);
    }, 2800);

    return () => clearInterval(interval);
  }, [isStreaming]);

  const filteredTxns = transactions.filter((t) => {
    if (filterSeverity === "ALERTS_ONLY") {
      return t.decision !== "APPROVED";
    }
    return true;
  });

  return (
    <div className="rounded-xl border border-slate-800/60 bg-slate-900/30 overflow-hidden">
      {/* Header Bar */}
      <div className="px-4 py-3 border-b border-slate-800/60 flex items-center justify-between">
        <div>
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Surveillance Stream
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Real-time transaction events evaluated by GNN
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-950/80 border border-slate-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setFilterSeverity("ALL")}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterSeverity === "ALL" ? "bg-slate-800 text-white font-medium" : "text-slate-400 hover:text-white"
              }`}
            >
              All Events
            </button>
            <button
              onClick={() => setFilterSeverity("ALERTS_ONLY")}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterSeverity === "ALERTS_ONLY" ? "bg-amber-950/80 text-amber-300 font-medium" : "text-slate-400 hover:text-white"
              }`}
            >
              Alerts Only
            </button>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsStreaming(!isStreaming)}
            className="h-7 px-2.5 border-slate-800 bg-slate-950 text-xs"
          >
            {isStreaming ? (
              <>
                <Pause className="w-3 h-3 mr-1 text-slate-400" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-3 h-3 mr-1 text-emerald-400" />
                Resume
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Stream Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800/60 text-slate-400 font-mono text-[11px]">
              <th className="py-2.5 px-4 font-normal">Time</th>
              <th className="py-2.5 px-4 font-normal">Flow</th>
              <th className="py-2.5 px-4 font-normal">Amount</th>
              <th className="py-2.5 px-4 font-normal">GNN Score</th>
              <th className="py-2.5 px-4 font-normal">Status</th>
              <th className="py-2.5 px-4 font-normal">Pattern</th>
              <th className="py-2.5 px-4 font-normal text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40 font-mono text-[11px]">
            {filteredTxns.map((txn) => {
              const isBlocked = txn.decision === "BLOCKED";
              const isFlagged = txn.decision === "FLAGGED_REVIEW";

              return (
                <tr 
                  key={txn.transactionId}
                  className="hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-2.5 px-4 text-slate-400">
                    {new Date(txn.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-2.5 px-4 text-slate-300">
                    <span>{txn.senderAccount}</span>
                    <span className="text-slate-500 mx-1.5">→</span>
                    <span>{txn.receiverAccount}</span>
                  </td>
                  <td className="py-2.5 px-4 font-medium text-slate-100">
                    {formatCurrency(txn.amount)}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className={isBlocked ? "text-red-400 font-bold" : isFlagged ? "text-amber-400 font-bold" : "text-emerald-400"}>
                      {formatPercent(txn.gnnFraudProbability)}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="inline-flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        isBlocked ? "bg-red-400" : isFlagged ? "bg-amber-400" : "bg-emerald-400"
                      }`} />
                      <span className={isBlocked ? "text-red-300" : isFlagged ? "text-amber-300" : "text-emerald-300"}>
                        {txn.decision === "FLAGGED_REVIEW" ? "Review" : txn.decision === "BLOCKED" ? "Blocked" : "Approved"}
                      </span>
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 text-[10px]">
                    {txn.topologyPatternDetected}
                  </td>
                  <td className="py-2.5 px-4 text-right">
                    <button
                      onClick={() => onSelectTransaction(txn)}
                      className="text-indigo-400 hover:text-white inline-flex items-center gap-1 text-[11px] transition-colors"
                    >
                      Inspect <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
