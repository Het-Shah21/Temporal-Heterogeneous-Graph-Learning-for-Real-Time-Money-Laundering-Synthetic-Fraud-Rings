import { 
  FraudPredictionResult, 
  PredefinedScenario, 
  SubgraphData, 
  XAIFactor, 
  TransactionSummaryKPI 
} from "@/types/fraud";

export const PREDEFINED_SCENARIOS: PredefinedScenario[] = [
  {
    id: "circular_mule_ring",
    name: "Circular Mule Ring (3-Hop Cycle)",
    category: "Fraud Ring",
    description: "Multi-account laundering circle where funds bounce through 3 mule accounts and return to an orchestrator.",
    senderAccount: "ACC_9901_MULE",
    receiverAccount: "ACC_9904_SINK",
    amount: 148500.0,
    timeDeltaHours: 0.4,
    deviceFingerprint: "DEV_TOR_0991A",
    ipAddress: "185.220.101.45",
    expectedPattern: "Circular Laundering Loop"
  },
  {
    id: "smurfing_structuring",
    name: "Structuring / Smurfing Star Pattern",
    category: "Smurfing",
    description: "Rapid burst of sub-$10,000 deposits ($9,950) aggregated from 5 separate accounts into a central consolidation wallet.",
    senderAccount: "ACC_5510_AGENT",
    receiverAccount: "ACC_5500_HUB",
    amount: 9950.0,
    timeDeltaHours: 0.1,
    deviceFingerprint: "DEV_FARM_882",
    ipAddress: "103.251.167.12",
    expectedPattern: "Smurfing / Structuring Star"
  },
  {
    id: "device_hijack",
    name: "Hardware Farm / Compromised IP",
    category: "Hardware Hijack",
    description: "Legitimate high-balance account accessed from a known bulletproof proxy IP hosting 14 distinct banking profiles.",
    senderAccount: "ACC_1024_VIP",
    receiverAccount: "ACC_7731_OFFSHORE",
    amount: 82300.0,
    timeDeltaHours: 1.2,
    deviceFingerprint: "DEV_EMULATOR_X1",
    ipAddress: "194.26.29.112",
    expectedPattern: "Shared Hardware Farm"
  },
  {
    id: "benign_payroll",
    name: "Authorized Corporate Vendor Settlement",
    category: "Benign Retail",
    description: "Routine scheduled recurring settlement between verified corporate entities over low-risk static infrastructure.",
    senderAccount: "ACC_0012_CORP",
    receiverAccount: "ACC_0088_SUPPLY",
    amount: 4500.0,
    timeDeltaHours: 72.0,
    deviceFingerprint: "DEV_OFFICE_MAC_01",
    ipAddress: "64.233.160.1",
    expectedPattern: "Standard Linear Transfer"
  }
];

export const INITIAL_SUMMARY_KPIS: TransactionSummaryKPI = {
  totalProcessed: 761752,
  flaggedCount: 1561,
  blockedCount: 420,
  approvedCount: 759771,
  fraudAlertRatePercent: 0.26,
  meanInferenceLatencyMs: 7.8,
  optimalThreshold: 0.1000
};

export function simulateMLInference(
  senderAccount: string,
  receiverAccount: string,
  amount: number,
  timeDeltaHours: number,
  deviceFingerprint: string,
  ipAddress: string
): FraudPredictionResult {
  // Deterministic seed computation based on input string properties
  const isSuspiciousRing = senderAccount.includes("MULE") || receiverAccount.includes("SINK") || amount > 100000;
  const isSmurfing = (amount >= 9000 && amount <= 9999) || timeDeltaHours < 0.2;
  const isDeviceFarm = deviceFingerprint.includes("FARM") || deviceFingerprint.includes("TOR") || deviceFingerprint.includes("EMULATOR");
  
  let gnnScore = 0.004; // Baseline clean probability
  let xgbScore = 0.008;
  let pattern: FraudPredictionResult["topologyPatternDetected"] = "Standard Linear Transfer";

  if (isSuspiciousRing) {
    gnnScore = 0.8842;
    xgbScore = 0.6120; // GNN outperforms XGBoost due to topology cycle awareness
    pattern = "Circular Laundering Loop";
  } else if (isDeviceFarm) {
    gnnScore = 0.7415;
    xgbScore = 0.4850;
    pattern = "Shared Hardware Farm";
  } else if (isSmurfing) {
    gnnScore = 0.4280;
    xgbScore = 0.3890;
    pattern = "Smurfing / Structuring Star";
  } else if (amount > 50000) {
    gnnScore = 0.1250;
    xgbScore = 0.1800;
  } else {
    gnnScore = Math.min(0.045, Math.max(0.001, (amount / 100000) * 0.02 + 0.001));
    xgbScore = Math.min(0.055, Math.max(0.002, (amount / 80000) * 0.025 + 0.002));
  }

  // Jitter slightly for realistic demonstration
  const optimalThreshold = 0.1000;
  const decision: FraudPredictionResult["decision"] = 
    gnnScore > 0.70 ? "BLOCKED" : 
    gnnScore >= optimalThreshold ? "FLAGGED_REVIEW" : "APPROVED";

  // Measured inference latency within the <15ms Triton requirement
  const inferenceLatencyMs = Number((5.2 + (amount % 7) * 0.4).toFixed(2));

  // Synthesize localized 2-hop Subgraph
  const subgraph = generateLocalizedSubgraph(senderAccount, receiverAccount, deviceFingerprint, ipAddress, pattern, gnnScore);

  // Generate Captum Integrated Gradients XAI factors
  const xaiFactors = generateXAIFactors(pattern, gnnScore, amount, timeDeltaHours, deviceFingerprint);

  return {
    transactionId: `TXN-${Date.now().toString(36).toUpperCase()}-${Math.floor(Math.random() * 1000)}`,
    timestamp: new Date().toISOString(),
    senderAccount,
    receiverAccount,
    amount,
    timeDeltaHours,
    deviceFingerprint,
    ipAddress,
    gnnFraudProbability: Number(gnnScore.toFixed(4)),
    xgboostProbability: Number(xgbScore.toFixed(4)),
    optimalThreshold,
    decision,
    inferenceLatencyMs,
    xaiFactors,
    subgraph,
    topologyPatternDetected: pattern
  };
}

function generateLocalizedSubgraph(
  sender: string,
  receiver: string,
  device: string,
  ip: string,
  pattern: FraudPredictionResult["topologyPatternDetected"],
  riskScore: number
): SubgraphData {
  const nodes: SubgraphData["nodes"] = [
    {
      id: sender,
      label: sender,
      type: "account",
      riskScore: riskScore > 0.4 ? riskScore * 0.9 : 0.05,
      metadata: { country: "US", totalSent: 180000, out_degree: 8, isMuleCandidate: riskScore > 0.5 }
    },
    {
      id: receiver,
      label: receiver,
      type: "account",
      riskScore: riskScore,
      metadata: { country: "CY", totalReceived: 240000, isMuleCandidate: riskScore > 0.7 }
    },
    {
      id: device,
      label: device,
      type: "device",
      riskScore: pattern === "Shared Hardware Farm" ? 0.92 : riskScore > 0.5 ? 0.65 : 0.02,
      metadata: { deviceModel: "Virtual/Emulated Android", isMuleCandidate: false }
    },
    {
      id: ip,
      label: ip,
      type: "ip",
      riskScore: pattern === "Shared Hardware Farm" ? 0.88 : riskScore > 0.5 ? 0.55 : 0.01,
      metadata: { country: "NL", asn: "AS9009 Hosting/Proxy", isMuleCandidate: false }
    }
  ];

  // If circular laundering, inject intermediary hops to illustrate the cycle
  if (pattern === "Circular Laundering Loop") {
    nodes.push(
      {
        id: "ACC_MULE_INTERMEDIATE_1",
        label: "Mule Node A",
        type: "account",
        riskScore: 0.82,
        metadata: { country: "VG", isMuleCandidate: true }
      },
      {
        id: "ACC_MULE_INTERMEDIATE_2",
        label: "Mule Node B",
        type: "account",
        riskScore: 0.85,
        metadata: { country: "PA", isMuleCandidate: true }
      }
    );
  } else if (pattern === "Smurfing / Structuring Star") {
    nodes.push(
      {
        id: "ACC_FEEDER_01",
        label: "Feeder 01",
        type: "account",
        riskScore: 0.45,
        metadata: { country: "US" }
      },
      {
        id: "ACC_FEEDER_02",
        label: "Feeder 02",
        type: "account",
        riskScore: 0.42,
        metadata: { country: "US" }
      }
    );
  }

  const edges: SubgraphData["edges"] = [
    {
      id: `edge-${sender}-${receiver}`,
      source: sender,
      target: receiver,
      type: "sends",
      importanceScore: Math.max(0.3, riskScore),
      isTargetEdge: true,
      isLaunderingPattern: riskScore >= 0.1
    },
    {
      id: `edge-${sender}-${device}`,
      source: sender,
      target: device,
      type: "uses_device",
      importanceScore: pattern === "Shared Hardware Farm" ? 0.91 : 0.25
    },
    {
      id: `edge-${sender}-${ip}`,
      source: sender,
      target: ip,
      type: "uses_ip",
      importanceScore: pattern === "Shared Hardware Farm" ? 0.86 : 0.18
    }
  ];

  if (pattern === "Circular Laundering Loop") {
    edges.push(
      {
        id: `cycle-1`,
        source: receiver,
        target: "ACC_MULE_INTERMEDIATE_1",
        type: "sends",
        importanceScore: 0.88,
        isLaunderingPattern: true
      },
      {
        id: `cycle-2`,
        source: "ACC_MULE_INTERMEDIATE_1",
        target: "ACC_MULE_INTERMEDIATE_2",
        type: "sends",
        importanceScore: 0.84,
        isLaunderingPattern: true
      },
      {
        id: `cycle-3`,
        source: "ACC_MULE_INTERMEDIATE_2",
        target: sender,
        type: "sends",
        importanceScore: 0.93,
        isLaunderingPattern: true
      }
    );
  } else if (pattern === "Smurfing / Structuring Star") {
    edges.push(
      {
        id: `feeder-1`,
        source: "ACC_FEEDER_01",
        target: receiver,
        type: "sends",
        importanceScore: 0.52,
        isLaunderingPattern: true
      },
      {
        id: `feeder-2`,
        source: "ACC_FEEDER_02",
        target: receiver,
        type: "sends",
        importanceScore: 0.49,
        isLaunderingPattern: true
      }
    );
  }

  return { nodes, edges };
}

function generateXAIFactors(
  pattern: FraudPredictionResult["topologyPatternDetected"],
  riskScore: number,
  amount: number,
  timeDelta: number,
  device: string
): XAIFactor[] {
  const factors: XAIFactor[] = [];

  if (pattern === "Circular Laundering Loop") {
    factors.push({
      id: "xai_cycle",
      featureName: "Directed 3-Hop Cycle Graph Anomaly",
      importanceScore: 0.942,
      impact: "CRITICAL",
      description: "GNN detected closed flow cycle (Sender -> Receiver -> Mule_A -> Mule_B -> Sender) with 94.2% topological attribution."
    });
    factors.push({
      id: "xai_velocity",
      featureName: "Rapid Velocity Dispersal (<30 mins)",
      importanceScore: 0.781,
      impact: "HIGH",
      description: `Funds transfer executed ${timeDelta * 60}m after deposit, heavily characteristic of automated pass-through accounts.`
    });
    factors.push({
      id: "xai_amount",
      featureName: "High Value Outlier ($100k+)",
      importanceScore: 0.655,
      impact: "HIGH",
      description: `Transaction value ($${amount.toLocaleString()}) deviates by +4.8σ from the account's 30-day historical baseline.`
    });
  } else if (pattern === "Shared Hardware Farm") {
    factors.push({
      id: "xai_device_density",
      featureName: "Device Multi-Tenancy (Farm)",
      importanceScore: 0.912,
      impact: "CRITICAL",
      description: `Device ${device} is linked to 14 distinct accounts across 3 jurisdictions in the last 48 hours.`
    });
    factors.push({
      id: "xai_vpn_ip",
      featureName: "Hosting / Bulletproof Proxy ASN",
      importanceScore: 0.834,
      impact: "HIGH",
      description: "Network egress originates from commercial datacenter known for obfuscating botnet traffic."
    });
  } else if (pattern === "Smurfing / Structuring Star") {
    factors.push({
      id: "xai_structuring_threshold",
      featureName: "BSA Structuring Proximity ($10,000 threshold)",
      importanceScore: 0.887,
      impact: "CRITICAL",
      description: `Amount of $${amount.toLocaleString()} is calibrated immediately below the mandatory $10,000 CTR filing threshold.`
    });
    factors.push({
      id: "xai_fan_in",
      featureName: "High In-Degree Fan-In Convergence",
      importanceScore: 0.760,
      impact: "HIGH",
      description: "Destination account received 6 parallel micro-transfers within a 15-minute operational window."
    });
  } else {
    factors.push({
      id: "xai_clean_baseline",
      featureName: "Consistent Historical Profile",
      importanceScore: 0.082,
      impact: "LOW",
      description: "Transaction amount and temporal cadence match verified 6-month commercial settlement history."
    });
    factors.push({
      id: "xai_trusted_device",
      featureName: "Verified Hardware Biometric",
      importanceScore: 0.041,
      impact: "LOW",
      description: "Device fingerprint has 100% authorization history with 0 chargebacks or suspicious velocity spikes."
    });
  }

  return factors;
}
