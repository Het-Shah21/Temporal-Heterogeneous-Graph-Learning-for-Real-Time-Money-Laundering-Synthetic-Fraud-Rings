export type NodeType = "account" | "device" | "ip";

export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  riskScore: number;
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
  importanceScore?: number;
  isTargetEdge?: boolean;
  isLaunderingPattern?: boolean;
}

export interface SubgraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface XAIFactor {
  id?: string;
  factor?: string;
  featureName?: string;
  importance?: number;
  importanceScore?: number;
  impact: "CRITICAL" | "HIGH" | "NORMAL" | "LOW" | "MEDIUM";
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
  gnnFraudProbability: number;
  xgboostProbability: number;
  optimalThreshold: number;
  decision: "APPROVED" | "FLAGGED_REVIEW" | "BLOCKED" | "ALERT" | "NORMAL";
  inferenceLatencyMs: number;
  xaiFactors: XAIFactor[];
  subgraph: SubgraphData;
  topologyPatternDetected?: string;
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

export interface IBMAMLTransaction {
  Timestamp: string;
  From_Bank: string;
  From_Account: string;
  To_Bank: string;
  To_Account: string;
  Amount_Received: number;
  Receiving_Currency: string;
  Payment_Format: string;
}

export interface MLPredictionResponse {
  status: "SUCCESS" | "ERROR";
  decision: "ALERT" | "NORMAL";
  isAlert: boolean;
  modelRiskScore: number;
  xgboostScore: number;
  optimalThreshold: number;
  primaryReason: string;
  xaiFactors: XAIFactor[];
  transactionParticulars: IBMAMLTransaction;
  accountContext: {
    senderKnownInDataset: boolean;
    senderOutDegree: number;
    senderTotalSent: number;
    receiverKnownInDataset: boolean;
    receiverInDegree: number;
    receiverTotalReceived: number;
  };
}

export interface DatasetPreset {
  id: string;
  title: string;
  type: "ALERT_LAUNDERING" | "NORMAL_LEGITIMATE";
  particulars: IBMAMLTransaction;
  description: string;
}
