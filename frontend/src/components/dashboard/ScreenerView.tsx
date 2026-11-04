"use client";

import React, { useState } from "react";
import { Zap, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PREDEFINED_SCENARIOS } from "@/lib/ml-simulator";
import { FraudPredictionResult, PredefinedScenario } from "@/types/fraud";
import { SubgraphViewer } from "./SubgraphViewer";
import { XAIInspector } from "./XAIInspector";

interface ScreenerViewProps {
  initialPrediction: FraudPredictionResult;
}

export function ScreenerView({ initialPrediction }: ScreenerViewProps) {
  const [selectedScenario, setSelectedScenario] = useState<string>("circular_mule_ring");
  const [senderAccount, setSenderAccount] = useState<string>(initialPrediction.senderAccount);
  const [receiverAccount, setReceiverAccount] = useState<string>(initialPrediction.receiverAccount);
  const [amount, setAmount] = useState<number>(initialPrediction.amount);
  const [timeDeltaHours, setTimeDeltaHours] = useState<number>(initialPrediction.timeDeltaHours);
  const [deviceFingerprint, setDeviceFingerprint] = useState<string>(initialPrediction.deviceFingerprint);
  const [ipAddress, setIpAddress] = useState<string>(initialPrediction.ipAddress);

  const [prediction, setPrediction] = useState<FraudPredictionResult>(initialPrediction);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleApplyScenario = (scenario: PredefinedScenario) => {
    setSelectedScenario(scenario.id);
    setSenderAccount(scenario.senderAccount);
    setReceiverAccount(scenario.receiverAccount);
    setAmount(scenario.amount);
    setTimeDeltaHours(scenario.timeDeltaHours);
    setDeviceFingerprint(scenario.deviceFingerprint);
    setIpAddress(scenario.ipAddress);
    setErrorMessage(null);
  };

  const handleRunInference = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          senderAccount,
          receiverAccount,
          amount: Number(amount),
          timeDeltaHours: Number(timeDeltaHours),
          deviceFingerprint,
          ipAddress,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || `HTTP error ${response.status}`);
      }

      const result: FraudPredictionResult = await response.json();
      setPrediction(result);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Inference failed";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      
      {/* Sleek Archetype Quick Select */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl border border-slate-800/60 bg-slate-900/30">
        <span className="text-xs font-medium text-slate-300">
          Archetype Templates:
        </span>
        <div className="flex flex-wrap gap-1.5">
          {PREDEFINED_SCENARIOS.map((scenario) => {
            const isSelected = selectedScenario === scenario.id;
            return (
              <button
                key={scenario.id}
                onClick={() => handleApplyScenario(scenario)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  isSelected
                    ? "bg-indigo-600 text-white font-semibold shadow-sm"
                    : "bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                {scenario.name.split("(")[0].trim()}
              </button>
            );
          })}
        </div>
      </div>

      {/* Two Column Layout: Parameters & Live Output */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* Left Column: Form & XAI (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="p-4 rounded-xl border border-slate-800/60 bg-slate-900/30 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                Transaction Parameters
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                Real-Time Edge
              </span>
            </div>

            {/* Transfer Endpoints */}
            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Sender Account
                </label>
                <input
                  type="text"
                  value={senderAccount}
                  onChange={(e) => setSenderAccount(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Receiver Account
                </label>
                <input
                  type="text"
                  value={receiverAccount}
                  onChange={(e) => setReceiverAccount(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Amount & Time Delta */}
            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Amount ($ USD)
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Time Delta (Hours)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={timeDeltaHours}
                  onChange={(e) => setTimeDeltaHours(Number(e.target.value))}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Device & IP */}
            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Device Fingerprint
                </label>
                <input
                  type="text"
                  value={deviceFingerprint}
                  onChange={(e) => setDeviceFingerprint(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  IP Address
                </label>
                <input
                  type="text"
                  value={ipAddress}
                  onChange={(e) => setIpAddress(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {errorMessage && (
              <div className="p-2 rounded-lg bg-red-950/40 border border-red-900/50 text-red-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-3.5 h-3.5 shrink-0 text-red-400" />
                <span>{errorMessage}</span>
              </div>
            )}

            <Button
              onClick={handleRunInference}
              disabled={isLoading}
              className="w-full h-9 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-lg transition-colors"
            >
              {isLoading ? "Evaluating GNN Subgraph..." : "Screen Transaction"}
            </Button>
          </div>

          {/* Explainable AI breakdown */}
          <XAIInspector prediction={prediction} />
        </div>

        {/* Right Column: 2-Hop Subgraph Topology Visualizer (7 cols) */}
        <div className="lg:col-span-7">
          <SubgraphViewer 
            subgraph={prediction.subgraph}
            patternDetected={prediction.topologyPatternDetected}
            targetTransactionId={prediction.transactionId}
          />
        </div>

      </div>

    </div>
  );
}
