# Product Requirements Document (PRD): ML Portion

## 1. Project Overview
**Name:** Real-Time Fraud Graph Neural Network
**Objective:** Build an ultra-low-latency (<15ms) heterogeneous graph anomaly detector to identify decentralized circular mule networks and synthetic identities.

## 2. Dataset Requirements & Analysis
Based on the requirement for real-world complexity rather than pure simulation:
- **Primary Option - IBM Transactions for Anti-Money Laundering (AML):** A highly realistic, multi-agent virtual world dataset containing bank transfers, purchases, and laundering tags. This dataset contains the specific network typologies (cycles, stars, bipartite structures) used by real money launderers.
- **Alternative 1 - PaySim:** Simulates mobile money networks based on real African financial logs. Excellent for tabular + basic network structures.
- **Alternative 2 - Elliptic Data Set:** Real Bitcoin transactions (Graph structure) labeled for illicit activity.
*Decision:* We will adopt the **IBM AML Dataset** format and principles, as it perfectly aligns with our multi-entity (User, Account, IP, Device) heterogeneous requirements.

## 3. Core ML Requirements
- **Latency:** Inference and subgraph extraction must occur in under 15ms.
- **Model Type:** Heterogeneous Graph Neural Network with Temporal edge features.
- **Explainability:** Must provide mathematically auditable XAI (Shapley Values) detailing why a node/graph was flagged.
- **Baselines:** Must compare GNN performance against traditional XGBoost/Random Forest models.
