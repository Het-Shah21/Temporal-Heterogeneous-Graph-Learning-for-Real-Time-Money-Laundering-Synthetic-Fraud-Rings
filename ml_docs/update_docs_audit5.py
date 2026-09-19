import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 5: Conceptual Logic & Data Integration\n
**1. What was Tested?**\nScanned the mathematical formulation of the Node features to ensure the GNN isn't conceptually \"blind\", and audited the external boundaries (e.g. Redis integration) outlined in the original architecture.\n
**2. Test Methodology & Execution**\n- Cross-referenced PyG `HeteroData` initialization with the theoretical GraphSAGE message passing equations.\n- Cross-referenced the pipeline outputs against the original System Design spec.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Conceptual Failure)\n
**4. Issues / Loopholes Found**\n- **Flaw 9 (Logic):** Node Feature Collapse. `graph_builder.py` initialized all Accounts as `[1.0, 1.0, 1.0]`. The GNN mathematically could not distinguish between a high-volume mule account and a new user, rendering 50% of its predictive capability useless.\n- **Flaw 10 (Integration):** The Redis Feature Vacuum. The ML pipeline trained and discarded the calculated historical features, leaving the FastAPI backend with no O(1) feature store to fetch data from during live inference.\n
**5. Resolution & Final Solution**\n- Re-engineered `graph_builder.py` to aggregate historical metrics (`out_degree`, `total_sent`, `in_degree`, `total_received`), scale them via `StandardScaler`, and inject them directly into the PyG `data['account'].x` tensor.\n- Implemented a JSON exporter in `graph_builder.py` that serializes the raw historical dictionary into `models/artifacts/redis_node_features.json`, creating a frictionless bulk-load file for the Backend Redis layer.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 010: Dynamic Node Features & Redis Export\n
- **What:** Decided to dynamically map real-world aggregated account statistics directly into the PyG Node Tensors, and simultaneously export these raw baseline statistics to `redis_node_features.json`.\n- **Why:** 1) A GNN cannot effectively detect complex fraud rings using only topology; it requires rich, distinct node histories. 2) The backend requires an instantly accessible O(1) state cache (Redis) to serve the Triton Inference model in <15ms without recalculating global transaction sums.\n- **Where:** `ml/preprocessing/graph_builder.py`\n- **When:** Week 3, Post-Pipeline Audit 5.\n''')
