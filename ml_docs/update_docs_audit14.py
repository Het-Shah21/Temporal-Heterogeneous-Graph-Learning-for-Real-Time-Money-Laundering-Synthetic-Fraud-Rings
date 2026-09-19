import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 14: Data Integrity & Metric Stability\n
**1. What was Tested?**\nAn enterprise stability scan evaluating how the pipeline reacts to corrupted raw CSV data and mathematical anomalies during early-epoch evaluation.\n
**2. Test Methodology & Execution**\n- Simulated referential integrity failures (orphaned edges) within `graph_builder.py`.\n- Traced Scikit-Learn evaluation functions when the Neural Network predicts a homogenous output matrix.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Data Crash & Metric Spam)\n
**4. Issues / Loopholes Found**\n- **Flaw 26 (Conceptual Logic):** Relational Integrity `KeyError` Crash. `graph_builder.py` assumed 100% perfect referential integrity between node and edge CSVs. If a single transaction referenced a deleted account, the list comprehension dictionary mapping would instantly throw a fatal `KeyError`, halting the entire pipeline.\n- **Flaw 27 (Mathematical Logic):** Zero-Division Metric Spam. During the highly imbalanced early epochs, the AI frequently predicts all zeros. Scikit-Learn calculates precision as `TP / (TP + FP)`. This `0/0` math would throw aggressive `UndefinedMetricWarning` stack traces, polluting the professional audit log.\n
**5. Resolution & Final Solution**\n- Authored a `safe_map_edges` function in `graph_builder.py`. It uses defensive `.get()` style checks to identify and silently drop orphaned edges. The script now gracefully warns the user about dropped corrupt data without ever halting execution.\n- Injected explicit `zero_division=0` arguments into `f1_score` and `classification_report` within `gnn.py`. This safely bypasses early-epoch anomalies, keeping the logs pristine.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 020: Defensive Relational Mapping & Metric Zero-Division Patch\n
- **What:** Decided to replace strict list comprehensions with defensive mapping functions in the graph builder, and enforced zero-division handling in Scikit-Learn evaluation metrics.\n- **Why:** Real-world enterprise datasets are messy. A robust machine learning pipeline must dynamically catch and ignore orphaned data (like broken Foreign Keys) rather than suffering a hard crash. Similarly, early-epoch AI behavior naturally results in zero-division math anomalies, which must be systematically suppressed to maintain log integrity.\n- **Where:** `ml/preprocessing/graph_builder.py` & `ml/models/gnn.py`\n- **When:** Week 3, Ultimate Data Integrity Sweep.\n''')
