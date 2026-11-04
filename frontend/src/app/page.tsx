"use client";

import React, { useState } from "react";
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight, 
  Database, 
  Cpu, 
  Layers, 
  Sparkles,
  HelpCircle,
  FileSpreadsheet
} from "lucide-react";
import { IBM_DATASET_PRESETS } from "@/lib/dataset-presets";
import { IBMAMLTransaction, MLPredictionResponse } from "@/types/fraud";
import { formatCurrency } from "@/lib/utils";

export default function Home() {
  const initialPreset = IBM_DATASET_PRESETS[0];

  // Transaction form state strictly matching IBM AML dataset schema
  const [timestamp, setTimestamp] = useState<string>(initialPreset.particulars.Timestamp);
  const [fromBank, setFromBank] = useState<string>(initialPreset.particulars.From_Bank);
  const [fromAccount, setFromAccount] = useState<string>(initialPreset.particulars.From_Account);
  const [toBank, setToBank] = useState<string>(initialPreset.particulars.To_Bank);
  const [toAccount, setToAccount] = useState<string>(initialPreset.particulars.To_Account);
  const [amountReceived, setAmountReceived] = useState<number>(initialPreset.particulars.Amount_Received);
  const [currency, setCurrency] = useState<string>(initialPreset.particulars.Receiving_Currency);
  const [paymentFormat, setPaymentFormat] = useState<string>(initialPreset.particulars.Payment_Format);

  // Model Evaluation Result State
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<MLPredictionResponse | null>(null);

  const handleApplyPreset = (preset: typeof initialPreset) => {
    setTimestamp(preset.particulars.Timestamp);
    setFromBank(preset.particulars.From_Bank);
    setFromAccount(preset.particulars.From_Account);
    setToBank(preset.particulars.To_Bank);
    setToAccount(preset.particulars.To_Account);
    setAmountReceived(preset.particulars.Amount_Received);
    setCurrency(preset.particulars.Receiving_Currency);
    setPaymentFormat(preset.particulars.Payment_Format);
    setErrorMessage(null);
  };

  const handleEvaluateTransaction = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Timestamp: timestamp,
          From_Bank: fromBank,
          From_Account: fromAccount,
          To_Bank: toBank,
          To_Account: toAccount,
          Amount_Received: Number(amountReceived),
          Receiving_Currency: currency,
          Payment_Format: paymentFormat
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP Error ${response.status}`);
      }

      const predictionData: MLPredictionResponse = await response.json();
      setResult(predictionData);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Inference failed";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      
      {/* 1. Header */}
      <header className="border-b border-slate-800/70 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-tight text-white">
                AEGIS <span className="text-slate-500 font-normal">/</span> AML Transaction Evaluator
              </h1>
              <p className="text-[11px] text-slate-400">
                Standard Reference: IBM AML Dataset &bull; 100% Genuine ML Inference
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              PyTorch + XGBoost Active
            </span>
          </div>
        </div>
      </header>

      {/* 2. Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 space-y-6">
        
        {/* Dataset Reference Presets */}
        <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/30 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <FileSpreadsheet className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                IBM AML Dataset Quick-Load Samples
              </span>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">
              HI-Small_Trans.csv Format
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {IBM_DATASET_PRESETS.map((preset) => {
              const isAlert = preset.type === "ALERT_LAUNDERING";
              return (
                <button
                  key={preset.id}
                  onClick={() => handleApplyPreset(preset)}
                  className="p-2.5 rounded-lg border border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900/60 transition-all text-left cursor-pointer group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-200 group-hover:text-indigo-300">
                      {preset.title}
                    </span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-bold ${
                      isAlert ? "bg-red-950 text-red-300 border border-red-900/60" : "bg-emerald-950 text-emerald-300 border border-emerald-900/60"
                    }`}>
                      {isAlert ? "FLAGGED CASE" : "CLEAN CASE"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                    {preset.description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Transaction Entry Form */}
        <div className="p-5 rounded-xl border border-slate-800/80 bg-slate-900/30 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <div>
              <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
                Transaction Particulars
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Input any transaction in the exact format of the IBM AML training dataset
              </p>
            </div>
            <span className="text-[11px] font-mono text-slate-500">
              515,080 Accounts Indexed
            </span>
          </div>

          {/* Form Fields matching IBM AML Schema */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            
            {/* Timestamp */}
            <div className="sm:col-span-2">
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                Timestamp (YYYY/MM/DD HH:MM:SS)
              </label>
              <input
                type="text"
                value={timestamp}
                onChange={(e) => setTimestamp(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                placeholder="2022/09/01 14:30:00"
              />
            </div>

            {/* Payment Format */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                Payment Format
              </label>
              <select
                value={paymentFormat}
                onChange={(e) => setPaymentFormat(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500 cursor-pointer"
              >
                <option value="Wire">Wire</option>
                <option value="Cash">Cash</option>
                <option value="ACH">ACH</option>
                <option value="Cheque">Cheque</option>
                <option value="Credit Card">Credit Card</option>
              </select>
            </div>

            {/* Receiving Currency */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                Receiving Currency
              </label>
              <input
                type="text"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                placeholder="US Dollar"
              />
            </div>

            {/* From Bank */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                From Bank (Origin)
              </label>
              <input
                type="text"
                value={fromBank}
                onChange={(e) => setFromBank(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                placeholder="010"
              />
            </div>

            {/* From Account */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                From Account (Sender)
              </label>
              <input
                type="text"
                value={fromAccount}
                onChange={(e) => setFromAccount(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                placeholder="800E8B7F0"
              />
            </div>

            {/* To Bank */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                To Bank (Destination)
              </label>
              <input
                type="text"
                value={toBank}
                onChange={(e) => setToBank(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                placeholder="022"
              />
            </div>

            {/* To Account */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                To Account (Receiver)
              </label>
              <input
                type="text"
                value={toAccount}
                onChange={(e) => setToAccount(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                placeholder="8123FB9B0"
              />
            </div>

            {/* Amount Received */}
            <div className="sm:col-span-4">
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                Amount Received (USD / Value)
              </label>
              <input
                type="number"
                step="0.01"
                value={amountReceived}
                onChange={(e) => setAmountReceived(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono font-semibold focus:outline-none focus:border-indigo-500"
                placeholder="145000.00"
              />
            </div>

          </div>

          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-950/50 border border-red-900/60 text-red-300 text-xs">
              Error: {errorMessage}
            </div>
          )}

          {/* Action Button */}
          <button
            onClick={handleEvaluateTransaction}
            disabled={isLoading}
            className="w-full h-10 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold text-xs rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Running Machine Learning Pipeline (Python GNN + XGBoost)...</span>
              </>
            ) : (
              <>
                <span>Add Transaction &amp; Evaluate with ML Model</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* 3. Output Section: Real ML Model Decision & Explainable AI */}
        {result && (
          <div className="space-y-4 animate-in fade-in duration-300">
            
            {/* Primary Model Decision Card */}
            <div className={`p-5 rounded-xl border ${
              result.isAlert 
                ? "border-red-900/60 bg-red-950/20" 
                : "border-emerald-900/60 bg-emerald-950/20"
            }`}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl border ${
                    result.isAlert 
                      ? "bg-red-950/80 border-red-800 text-red-400" 
                      : "bg-emerald-950/80 border-emerald-800 text-emerald-400"
                  }`}>
                    {result.isAlert ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle className="w-6 h-6" />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                        ML Model Verdict
                      </span>
                      <span className={`text-xs px-2.5 py-0.5 rounded font-mono font-bold ${
                        result.isAlert 
                          ? "bg-red-900/50 text-red-300 border border-red-700" 
                          : "bg-emerald-900/50 text-emerald-300 border border-emerald-700"
                      }`}>
                        {result.decision === "ALERT" ? "ALERT: SUSPICIOUS LAUNDERING" : "NORMAL: LEGITIMATE TRANSFER"}
                      </span>
                    </div>

                    <div className="mt-1 flex items-baseline gap-2">
                      <span className="text-xl font-bold font-mono text-white">
                        Risk Score: {(result.modelRiskScore * 100).toFixed(2)}%
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        (Cutoff Threshold: {(result.optimalThreshold * 100).toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>

                {/* Score Comparison */}
                <div className="text-right font-mono text-xs border-t sm:border-t-0 sm:border-l border-slate-800 pt-2 sm:pt-0 sm:pl-4">
                  <span className="text-slate-400 block text-[11px]">XGBoost Baseline:</span>
                  <span className="text-slate-300 font-bold">{(result.xgboostScore * 100).toFixed(2)}%</span>
                  <span className="text-indigo-400 block text-[10px] mt-0.5">
                    GNN Topology Lift: +{Math.max(0, (result.modelRiskScore - result.xgboostScore) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Plain English Reason */}
              <div className="mt-3.5 pt-3 border-t border-slate-800/60 text-xs text-slate-300">
                <span className="font-semibold text-white">Model Conclusion: </span>
                <span>{result.primaryReason}</span>
              </div>
            </div>

            {/* Explainable AI (XAI) Attribution Breakdown */}
            <div className="p-5 rounded-xl border border-slate-800/80 bg-slate-900/30 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
                <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                  Explainable AI (XAI) Factor Attribution
                </h3>
                <span className="text-[10px] font-mono text-slate-500">
                  Feature Weight Contribution
                </span>
              </div>

              <div className="space-y-3">
                {result.xaiFactors.map((factor, idx) => {
                  const pct = Math.round((factor.importance ?? factor.importanceScore ?? 0) * 100);
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-slate-300">
                          {factor.factor}
                        </span>
                        <span className="font-mono text-indigo-400 font-semibold text-[11px]">
                          {pct}% Impact
                        </span>
                      </div>

                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
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

            {/* Account Context from Real IBM AML Dataset */}
            <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/30 font-mono text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/60 text-slate-400 text-[11px]">
                <span className="uppercase tracking-wider">Historical Account Profile (IBM AML Graph)</span>
                <span>Verified Data Store</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <span className="text-slate-500 text-[10px] block">Sender Account: {result.transactionParticulars.From_Account}</span>
                  <div className="mt-1 space-y-0.5 text-[11px] text-slate-300">
                    <div>Historical Out-Degree: <span className="text-white font-bold">{result.accountContext.senderOutDegree}</span></div>
                    <div>Historical Outflow: <span className="text-white font-bold">{result.accountContext.senderTotalSent}</span> (Scaled)</div>
                    <div className="text-[10px] text-emerald-400">
                      {result.accountContext.senderKnownInDataset ? "✓ Verified Account in IBM AML Graph" : "New Account Node"}
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <span className="text-slate-500 text-[10px] block">Receiver Account: {result.transactionParticulars.To_Account}</span>
                  <div className="mt-1 space-y-0.5 text-[11px] text-slate-300">
                    <div>Historical In-Degree: <span className="text-white font-bold">{result.accountContext.receiverInDegree}</span></div>
                    <div>Historical Inflow: <span className="text-white font-bold">{result.accountContext.receiverTotalReceived}</span> (Scaled)</div>
                    <div className="text-[10px] text-emerald-400">
                      {result.accountContext.receiverKnownInDataset ? "✓ Verified Account in IBM AML Graph" : "New Account Node"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-3 text-center text-[11px] text-slate-500 font-mono">
        AEGIS Fraud Screener &bull; Heterogeneous Graph Neural Network (PyTorch) &bull; IBM Transactions for Anti-Money Laundering
      </footer>

    </div>
  );
}
