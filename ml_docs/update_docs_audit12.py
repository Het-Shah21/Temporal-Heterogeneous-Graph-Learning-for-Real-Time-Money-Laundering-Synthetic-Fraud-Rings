import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 12: ONNX Compilation & Dictionary Flattening\n
**1. What was Tested?**\nAn extremely deep audit of the PyTorch compilation engine (`torch.onnx.export`) and its compatibility with the Triton Inference C++ backend.\n
**2. Test Methodology & Execution**\n- Mapped PyTorch Geometric's nested dictionary architecture against ONNX runtime constraints.\n- Verified `config.pbtxt` tensor dimensionalities against the updated scaling logic.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Fatal Compilation Crash)\n
**4. Issues / Loopholes Found**\n- **Flaw 22 (Incomplete Connection):** The ONNX Mock Trap. `triton_exporter.py` was generating a fake text string instead of a true compiled binary, meaning the Triton Server would immediately fail to boot. Additionally, the `config.pbtxt` was fundamentally out of sync, defining 3 dimensions for node features when our upgrades shifted them to 4.\n- **Flaw 23 (Conceptual Logic):** ONNX Dictionary Crash. PyTorch ONNX export *does not support Python dictionaries*. Because the GNN expected `x_dict` and `edge_index_dict`, compiling it directly would throw an instant API mapping crash inside the C++ backend.\n
**5. Resolution & Final Solution**\n- Authored a `GNNONNXWrapper` class inside `triton_exporter.py` that accepts flat C++ numerical tensors (`x_account`, `edge_index_sends`, `edge_attr_sends`) and dynamically reconstructs the complex Python dictionaries internally before feeding them to the AI.\n- Executed a true `torch.onnx.export` compilation run, producing a mathematically identical binary graph. Updated `config.pbtxt` and `triton_client.py` to perfectly map to these new flattened inputs, guaranteeing zero compilation crashes during inference.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 018: Flat Tensor ONNX Wrapper Architecture\n
- **What:** Decided to wrap the GNN inside a flattened PyTorch `nn.Module` translation layer before initiating the ONNX export, rather than attempting to export the raw PyG dictionaries.\n- **Why:** The NVIDIA Triton Inference Server operates on flat C++ HTTP/gRPC arrays. PyTorch Geometric relies on highly nested Python dictionaries. Bypassing this incompatibility via a native translation wrapper ensures the C++ execution engine can seamlessly communicate with the PyTorch logic without raising dimensionality exceptions.\n- **Where:** `ml/export/triton_exporter.py`\n- **When:** Week 3, Final Inference Architecture Sweep.\n''')
