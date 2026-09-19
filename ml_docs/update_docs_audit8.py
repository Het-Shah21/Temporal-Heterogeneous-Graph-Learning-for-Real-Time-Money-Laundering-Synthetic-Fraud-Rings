import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 8: Hardware Acceleration & Dead-Code Eradication\n
**1. What was Tested?**\nA strict audit of Hardware Device Mapping (CPU vs CUDA) and a check for orphaned features (dead code) that were promised in the architecture but never executed in the pipeline.\n
**2. Test Methodology & Execution**\n- Scanned tensor allocation parameters (`.to(device)`) in PyTorch.\n- Traced the execution tree of `train_pipeline.py` to ensure every module (`data`, `preprocessing`, `models`, `xai`, `export`) is actively utilized.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Hardware Bottleneck & Orphaned Feature)\n
**4. Issues / Loopholes Found**\n- **Flaw 15 (Hardware Logic):** CPU Defaulting. The PyTorch GNN and the Heterogeneous PyG graph were never mapped to a CUDA device. Training this massive matrix on a CPU would take hours instead of minutes, causing a catastrophic performance bottleneck.\n- **Flaw 16 (Unexecuted Feature):** The Orphaned Explainer. `ml/xai/explainer.py` was built but never executed in the pipeline. Without it, the frontend dashboard has no Shapley values to explain *why* an account was flagged.\n
**5. Resolution & Final Solution**\n- Injected dynamic `torch.cuda.is_available()` device mapping into `train_pipeline.py`. The pipeline now automatically pushes the `HeteroData` matrix and the GNN to the NVIDIA GPU for extreme acceleration.\n- Integrated `FraudExplainer` into `train_pipeline.py`. Post-training, the pipeline now automatically executes a test explanation on a fraudulent transaction and serializes the topological reasons to `models/artifacts/xai_sample.json`, guaranteeing the frontend explanation feature is alive.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 013: GPU Acceleration & Automated XAI Validation\n
- **What:** Decided to force strict GPU (`.to(device)`) tensor mapping globally and embed an automated XAI verification step directly into the CI/CD training orchestrator.\n- **Why:** 1) GNNs on Heterogeneous datasets will memory-thrash a CPU; CUDA is required for the low-latency engineering constraint. 2) Unused code becomes dead code. By forcing the Explainer to generate a JSON artifact on every training run, we guarantee the mathematical explainer logic remains synchronized with the model architecture over time.\n- **Where:** `ml/train_pipeline.py`\n- **When:** Week 3, Post-Pipeline Audit 8.\n''')
