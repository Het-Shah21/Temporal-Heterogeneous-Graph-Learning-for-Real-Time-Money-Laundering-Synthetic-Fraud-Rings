import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 2: Core GNN Mathematics\n
**1. What was Tested?**\nThe PyTorch GNN Training and Evaluation mechanics.\n
**2. Test Methodology & Execution**\n- Scanned `gnn.py` to verify mathematical alignment with the XGBoost baseline, specifically checking Loss metrics and evaluation functions.\n
**3. Verdict**\nNEEDS OPTIMIZATION\n
**4. Issues / Loopholes Found**\n- **Flaw 3:** Missing Class Imbalance Handling. The GNN used a standard `BCEWithLogitsLoss()` which would cause it to overfit to the 99% legitimate majority class and ignore the <1% fraud minority class.\n- **Flaw 4:** Missing Evaluation Pipeline. There was no function to extract ROC-AUC and F1-Scores for the GNN to mathematically prove it outperforms XGBoost.\n
**5. Resolution & Final Solution**\n- Created `get_criterion(data)` inside `gnn.py` to dynamically calculate `scale_pos_weight` exactly like the XGBoost script.\n- Wrote `evaluate_model` inside `gnn.py` leveraging `sklearn.metrics` for an apples-to-apples performance comparison.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 007: GNN Class Imbalance Optimization\n
- **What:** Decided to dynamically apply `pos_weight` to the `BCEWithLogitsLoss` criterion inside the PyTorch GNN.\n- **Why:** Fraud constitutes <1% of the total edges. Without a proportional mathematical penalty for missing a fraudulent transaction, the GNN will suffer from the Accuracy Paradox (predicting 0 for everything and appearing 99% accurate while being completely useless for fraud detection).\n- **Where:** `ml/models/gnn.py`\n- **When:** Week 3, Post-Pipeline Audit 2.\n''')
