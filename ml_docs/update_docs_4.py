import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### System 4: Explainability (XAI) & Triton Export\n
**1. What was Tested?**\nThe `FraudExplainer` initialization (Captum/Integrated Gradients) and the `TritonExporter` (Dynamic ONNX tracing & Config Generation).\n
**2. Test Methodology & Execution**\n- Wrote `test_xai_export.py`.\n- Validated that the `config.pbtxt` is dynamically generated strictly matching Triton's required JSON-like Protobuf syntax.\n
**3. Verdict**\nPASS\n
**4. Issues / Loopholes Found**\nONNX export of PyTorch Geographic's `HeteroData` dictionary natively fails in standard `torch.onnx.export` due to lack of dictionary support in older ONNX versions. \n
**5. Resolution & Final Solution**\nAdded specific logic to mandate explicit defining of Dynamic Axes (`dynamic_axes={"x_dict": {0: "num_nodes"}}`) and designed the exporter to flatten the dictionaries into tuples before tracing.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 005: Triton ONNX over TorchServe\n
- **What:** Decided to export the model exclusively to ONNX format using Dynamic Axes for serving on NVIDIA Triton Inference Server, rather than deploying natively with FastAPI + PyTorch or TorchServe.\n- **Why:** The strict <15ms latency target cannot be met by standard Python-GIL bound PyTorch inference under heavy load. Triton provides native C++ TensorRT optimization and dynamic batching.\n- **Where:** `ml/export/triton_exporter.py`\n- **When:** Week 3, Phase 5 (XAI & Deployment Prep).\n''')

with open(os.path.join(docs_dir, 'ML_MODEL_ALGO.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Algorithm: Integrated Gradients (Captum Shapley Approximation)\n
**1. Mathematical Explanation**\nIntegrated Gradients calculates the path integral of the gradients along the straightline path from a baseline (zero tensor) to the input graph.\n`IG_i(x) = (x_i - x'_i) \int_{0}^{1} \frac{\partial F(x' + \alpha(x - x'))}{\partial x_i} d\alpha`\nThis mathematically satisfies two axiomatic properties of Shapley values: Sensitivity (if two graphs differ in one edge and have different predictions, that edge gets a non-zero attribution) and Implementation Invariance.\n
**2. Where it was used**\n`ml/xai/explainer.py`\n
**3. Why it was chosen**\nCalculating exact Shapley values on graph topologies is NP-Hard. Integrated Gradients provides a highly accurate, mathematically provable approximation that runs fast enough to serve to the dashboard without blocking the main event loop.\n
**4. When it was used in the project timeline**\nWeek 3, Phase 5.\n
**5. What we tried to achieve**\nTo provide auditable reasons for compliance flags (e.g., "Transaction flagged due to shared IP address").\n
**6. What was exactly implemented**\nIntegrated `torch_geometric.explain.Explainer` with `CaptumExplainer('IntegratedGradients')` targeting Edge masks on binary classification.\n''')
