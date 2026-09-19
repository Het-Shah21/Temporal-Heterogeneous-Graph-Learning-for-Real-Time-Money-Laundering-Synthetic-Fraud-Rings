import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 16: Inference Math & API Metric Alignment\n
**1. What was Tested?**\nAn end-to-end mathematical trace comparing the PyTorch evaluation logic during training against the C++ execution logic during real-time backend inference.\n
**2. Test Methodology & Execution**\n- Mapped PyTorch's `BCEWithLogitsLoss` scalar outputs to the Triton Inference API response payload.\n
**3. Verdict**\nNEEDS OPTIMIZATION (API Metric Disconnect)\n
**4. Issues / Loopholes Found**\n- **Flaw 30 (Conceptual Logic):** Logit vs. Probability Disconnect. The PyTorch GNN accurately predicts raw mathematical logits (e.g., `-2.4` to `3.5`) to optimize the loss function. However, the `GNNONNXWrapper` exported these raw logits directly to the C++ server. The `triton_client.py` API blindly assumed these outputs were percentages (`0.0` to `1.0`), meaning the frontend dashboard would display completely meaningless fraud probabilities, causing backend threshold logic (`if prob > 0.5`) to fatally crash.\n
**5. Resolution & Final Solution**\n- Injected a native `torch.sigmoid` activation mathematically directly into the ONNX execution graph inside `triton_exporter.py`. The C++ model now natively compresses all raw logits into a perfect 0-to-1 probability curve natively on the GPU/CPU before transmitting them across the network, guaranteeing perfectly accurate percentages for the backend API.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 022: Native ONNX Sigmoid Activation\n
- **What:** Decided to inject a mathematical Sigmoid function directly into the ONNX wrapper compilation, forcing the deployed C++ model to output probabilities rather than training logits.\n- **Why:** Training stability requires raw logits (to prevent gradient saturation), but real-time production inference strictly requires understandable probabilities. By hardcoding the Sigmoid directly into the ONNX graph, we ensure the backend API requires zero complex mathematical decoding—it just reads the number and routes the transaction.\n- **Where:** `ml/export/triton_exporter.py`\n- **When:** Week 3, Ultimate API Metric Alignment Sweep.\n''')
