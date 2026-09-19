import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 15: Cross-Hardware Checkpoint Defense\n
**1. What was Tested?**\nAnalyzed the binary serialization format of the PyTorch neural weights (`gnn_model.pth`) as it transitions from a Cloud GPU training environment to a local CPU inference environment.\n
**2. Test Methodology & Execution**\n- Simulated loading a CUDA-generated `.pth` dictionary on a machine completely lacking NVIDIA drivers.\n- Audited `baseline.py` data ingestion to verify it inherited the Pandas Downcasting patch.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Hardware Poisoning)\n
**4. Issues / Loopholes Found**\n- **Flaw 28 (Open-Ended Connection):** GPU-to-CPU Checkpoint Poisoning. When PyTorch executes `torch.save(model.state_dict())` on Google Colab, it natively saves the model as a CUDA-mapped binary. If a developer downloads this artifact and runs `torch.load()` on their local CPU-only laptop, the PyTorch engine will immediately crash with a `RuntimeError: Attempting to deserialize object on a CUDA device`.\n- *(False Alarm / Proof of Architecture):* I audited `baseline.py` expecting it to bypass our previous Colab Memory Downcasting fix. However, because we engineered `FeatureEngineer` as a modular dependency, `baseline.py` natively inherited the RAM protection, proving the codebase is highly resilient.\n
**5. Resolution & Final Solution**\n- Injected aggressive hardware stripping into `train_pipeline.py`. The model is now forced into CPU mode (`model.cpu().state_dict()`) right before saving to disk, ensuring the downloaded `.pth` file is universally compatible. Furthermore, `map_location=torch.device('cpu')` was enforced on all load operations to completely shield local machines from CUDA poisoning.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 021: Hardware-Agnostic PyTorch Serialization\n
- **What:** Decided to strip all CUDA hardware mappings from the neural network weights prior to binary serialization, and enforced CPU-mapped deserialization globally.\n- **Why:** Machine Learning artifacts must be highly portable. A model trained on an advanced cloud GPU must be seamlessly deployable to a local CPU without requiring the backend engineering team to reverse-engineer hardware tensor configurations. This guarantees true "train once, run anywhere" capabilities.\n- **Where:** `ml/train_pipeline.py`\n- **When:** Week 3, Hardware Portability Sweep.\n''')
