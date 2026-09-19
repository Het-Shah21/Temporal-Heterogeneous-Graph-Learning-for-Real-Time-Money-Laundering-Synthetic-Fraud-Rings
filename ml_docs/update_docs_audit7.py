import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 7: The "Syntax & Semantics" Final Sweep\n
**1. What was Tested?**\nAn extremely aggressive line-by-line semantic and architectural scan checking for unexecuted pipelines and mathematical desyncs.\n
**2. Test Methodology & Execution**\n- Traced the `StandardScaler` objects from memory instantiation to `.pkl` disk serialization.\n- Traced the `train_pipeline.py` execution path across all Phase modules.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Semantic Desync)\n
**4. Issues / Loopholes Found**\n- **Flaw 13 (Semantic Bug):** The "Double-Scaler" Desync. `feature_engineering.py` fitted a scaler and saved it to disk. But `graph_builder.py` created a *second, new* scaler for the PyG GNN. The backend was therefore loading a different mathematical scale than what the AI was trained on, which destroys inference accuracy.\n- **Flaw 14 (Unexecuted Feature):** The XGBoost baseline (`baseline.py`) was entirely bypassed by the master orchestrator (`train_pipeline.py`), meaning the benchmark metrics were never dynamically generated during a CI/CD run.\n
**5. Resolution & Final Solution**\n- Refactored `graph_builder.py` to instantiate `FeatureEngineer` directly. Both edge and node features are now strictly normalized using unified scalers, and both are saved to `scaler.pkl` and `node_scaler.pkl`.\n- Refactored `triton_client.py` to load and apply both scalers simultaneously.\n- Injected `BaselineModel.train_and_evaluate()` explicitly into `train_pipeline.py` before the GNN initialization, securing the 1-to-1 dashboard metric generation.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 012: Unified Mathematical Normalization (Single-Source Scaling)\n
- **What:** Decided to strictly route all data normalization through the `FeatureEngineer` class and export both node and edge `StandardScaler` objects to disk.\n- **Why:** To prevent "Double-Scaler Desyncs". If the backend Triton Client normalizes live JSON transactions using different mean/standard deviation parameters than what the PyTorch GNN was trained on, the mathematical inputs shift drastically, causing the model to incorrectly classify fraud patterns.\n- **Where:** `ml/preprocessing/graph_builder.py` & `ml/export/triton_client.py`\n- **When:** Week 3, Post-Pipeline Audit 7.\n''')
