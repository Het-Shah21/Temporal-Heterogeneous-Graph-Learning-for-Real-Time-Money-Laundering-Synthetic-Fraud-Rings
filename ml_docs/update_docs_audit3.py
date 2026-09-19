import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 3: The Operational Pipeline\n
**1. What was Tested?**\nThe overall structural sequence of the repository to determine if a new developer or CI/CD pipeline could successfully train and deploy the model.\n
**2. Test Methodology & Execution**\n- Traced the execution flow from data downloading to ONNX export.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Operational Failure)\n
**4. Issues / Loopholes Found**\n- **Flaw 5:** Missing Pipeline Orchestrator. There was no single execution script. Training required manually running 6 disjointed python files in exact order.\n- **Flaw 6:** Unsaved Model Weights. The GNN architecture was defined, but `torch.save()` was never actually called, meaning the backend API had no `.pth` file to load.\n
**5. Resolution & Final Solution**\n- Authored `ml/train_pipeline.py`. This master script handles Dataset Loading -> Graph Building -> Model Initialization -> Training (100 Epochs) -> Checkpointing -> Final Evaluation -> ONNX Triton Export.\n- Implemented `torch.save(model.state_dict())` during the multi-epoch validation loop to guarantee the backend team receives the mathematically optimal model weights.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 008: Automated ML Pipeline Orchestration\n
- **What:** Decided to write a monolithic `train_pipeline.py` script that orchestrates the entire ML lifecycle from raw data to Triton ONNX export in a single command.\n- **Why:** To eliminate manual operational errors, enable future CI/CD pipeline automation (e.g., Jenkins/GitHub Actions), and guarantee the backend team always receives a synchronized `gnn_model.pth` and `model.onnx`.\n- **Where:** `ml/train_pipeline.py`\n- **When:** Week 3, Post-Pipeline Audit 3.\n''')
