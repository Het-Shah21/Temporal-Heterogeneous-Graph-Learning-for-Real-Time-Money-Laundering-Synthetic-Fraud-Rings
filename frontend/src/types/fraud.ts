export type NodeType = "account" | "device" | "ip";

export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  riskScore: number; // 0 to 1
  metadata?: {
    country?: string;
    totalSent?: number;
    totalReceived?: number;
    transactionCount?: number;
    out_degree?: number;
    in_degree?: number;
    deviceModel?: string;
    asn?: string;
    isMuleCandidate?: boolean;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: "sends" | "uses_device" | "uses_ip";
  amount?: number;
  timestamp?: string;
  importanceScore?: number; // 0 to 1 (from Captum XAI)
  isTargetEdge?: boolean;
  isLaunderingPattern?: boolean;
}

export interface SubgraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface XAIFactor {
  id: string;
  edgeIndex?: number;
  featureName: string;
  importanceScore: number; // 0 to 1
  impact: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  description: string;
}

export interface FraudPredictionResult {
  transactionId: string;
  timestamp: string;
  senderAccount: string;
  receiverAccount: string;
  amount: number;
  timeDeltaHours: number;
  deviceFingerprint: string;
  ipAddress: string;
  
  // Model Metrics
  gnnFraudProbability: number;
  xgboostProbability: number;
  optimalThreshold: number;
  decision: "APPROVED" | "FLAGGED_REVIEW" | "BLOCKED";
  inferenceLatencyMs: number;
  
  // Explainability
  xaiFactors: XAIFactor[];
  subgraph: SubgraphData;
  topologyPatternDetected?: "Circular Laundering Loop" | "Smurfing / Structuring Star" | "Shared Hardware Farm" | "Standard Linear Transfer";
}

export interface TransactionSummaryKPI {
  totalProcessed: number;
  flaggedCount: number;
  blockedCount: number;
  approvedCount: number;
  fraudAlertRatePercent: number;
  meanInferenceLatencyMs: number;
  optimalThreshold: number;
}

export interface PredefinedScenario {
  id: string;
  name: string;
  category: "Fraud Ring" | "Hardware Hijack" | "Smurfing" | "Benign Retail";
  description: string;
  senderAccount: string;
  receiverAccount: string;
  amount: number;
  timeDeltaHours: number;
  deviceFingerprint: string;
  ipAddress: string;
  expectedPattern: string;
}
