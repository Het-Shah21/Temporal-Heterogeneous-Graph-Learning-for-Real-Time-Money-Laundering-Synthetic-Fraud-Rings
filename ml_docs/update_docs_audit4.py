import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 4: Production Inference Reliability\n
**1. What was Tested?**\nEnd-to-end integration safety checks: ensuring the PyTorch model mathematically trains stably and that the FastAPI backend can practically interface with Triton.\n
**2. Test Methodology & Execution**\n- Inspected `feature_engineering.py` and `graph_builder.py` for mathematical tensor scaling.\n- Inspected the API boundary between the ML models and the upcoming FastAPI backend.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Integration Failure)\n
**4. Issues / Loopholes Found**\n- **Flaw 7:** Exploding Gradients. Raw financial amounts (e.g. $50,000) and time deltas were passed unscaled to PyTorch's linear layers, causing gradient instability and `NaN` loss degradation over 100 epochs.\n- **Flaw 8:** The Missing API Bridge. The ONNX model existed, but the FastAPI backend team had no Python interface to transform a raw JSON transaction into the multi-dimensional NumPy arrays Triton expects over gRPC.\n
**5. Resolution & Final Solution**\n- Integrated `StandardScaler` from `scikit-learn` to normalize amounts and time deltas, saving the fitted scaler via `pickle` to `models/artifacts/scaler.pkl`.\n- Authored `ml/export/triton_client.py`, which provides a clean `predict_fraud()` wrapper for the backend team that handles automated feature scaling, NumPy array packing, and Triton Inference Server communication.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 009: Decoupled Triton Inference Client\n
- **What:** Decided to author a decoupled inference wrapper (`triton_client.py`) that strictly manages stateful transformations (loading the `StandardScaler` from pickle and formatting PyTorch-compatible NumPy arrays) independently of the FastAPI routes.\n- **Why:** This enforces a strict separation of concerns. The backend teammate building FastAPI endpoints does not need to know PyTorch Geometric or tensor mathematics; they just pass raw JSON to this client and receive a clean fraud probability.\n- **Where:** `ml/export/triton_client.py`\n- **When:** Week 3, Post-Pipeline Audit 4.\n''')
