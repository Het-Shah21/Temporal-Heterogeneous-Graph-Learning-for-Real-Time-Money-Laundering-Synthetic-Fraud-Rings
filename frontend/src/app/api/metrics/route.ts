import { NextResponse } from "next/server";
import { INITIAL_SUMMARY_KPIS } from "@/lib/ml-simulator";

export async function GET() {
  return NextResponse.json({
    kpis: INITIAL_SUMMARY_KPIS,
    models: {
      gnn: {
        name: "Heterogeneous SAGEConv GNN (PyTorch)",
        rocAuc: 0.8062,
        recall: 0.8000,
        precision: 0.0100,
        f1Score: 0.0151,
        optimalThreshold: 0.1000,
        latencyMs: 7.4,
        featuresUsed: ["2-hop topology", "transaction amount", "time delta", "device co-usage", "ip threat level"]
      },
      baselineXGB: {
        name: "Temporal Gradient Boosted Trees (XGBoost)",
        rocAuc: 0.8856,
        recall: 0.7900,
        precision: 0.0100,
        f1Score: 0.0155,
        defaultThreshold: 0.5000,
        latencyMs: 12.1,
        featuresUsed: ["rolling volume (1h/24h/7d)", "cumulative count", "velocity delta"]
      }
    },
    confusionMatrixGNN: {
      trueLegitimate: 760191,
      falsePositives: 152038,
      falseNegatives: 312,
      trueFraud: 1249,
      totalTestSamples: 761752,
      fraudBaseRate: "0.20%"
    }
  }, { status: 200 });
}
