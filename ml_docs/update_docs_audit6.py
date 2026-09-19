import os

docs_dir = r'd:\het\SELF\RP\MLE\MLE_FINAL_SEM_PROJECT\ml_docs'

with open(os.path.join(docs_dir, 'ML_TESTS_LOG.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Codebase Audit Phase 6: The "Chicken and Egg" Inference Loophole\n
**1. What was Tested?**\nAn absolute simulation of real-time production inference. We traced a hypothetical live transaction from FastAPI -> Triton Client -> PyG NeighborLoader -> Triton Server.\n
**2. Test Methodology & Execution**\n- Mapped exactly what data exists in the Memgraph database at the exact millisecond a pending transaction arrives.\n
**3. Verdict**\nNEEDS OPTIMIZATION (Catastrophic Logic Failure)\n
**4. Issues / Loopholes Found**\n- **Flaw 11 (Logic):** The "Chicken and Egg" Edge Classification Bug. The AI is designed to classify an edge. But when a live transaction arrives, that edge hasn't been approved yet, so it doesn't exist in Memgraph or the extracted subgraph! The AI would crash trying to score an edge that isn't in the tensor.\n- **Flaw 12 (Open-Ended):** Missing Dependency Manifest. The environment libraries were never locked down, making CI/CD deployment impossible.\n
**5. Resolution & Final Solution**\n- Rewrote the Numpy matrix mathematics inside `ml/export/triton_client.py`. When a live transaction hits the server, the client now fetches the subgraphs of Sender A and Receiver B, and *artificially injects* the proposed new transaction edge directly into the NumPy matrix (`np.hstack`, `np.vstack`) before pinging Triton. The AI now scores the simulated future state!\n- Created `ml/requirements.txt` locking exact production versions for `torch`, `torch-geometric`, `tritonclient`, and `captum`.\n''')

with open(os.path.join(docs_dir, 'ML_DECISIONS.md'), 'a', encoding='utf-8') as f:
    f.write('''\n### Decision 011: Artificial Edge Injection for Real-Time Inference\n
- **What:** Decided to force the FastAPI Triton client to artificially inject the pending transaction into the NumPy edge tensors before sending the payload to the GNN.\n- **Why:** In an Edge Classification paradigm, you cannot score an edge that doesn't exist. Since the transaction is pending (not written to the database yet), we must simulate it mathematically inside the localized subgraph so the GNN can "see" the proposed connection and evaluate its fraud probability.\n- **Where:** `ml/export/triton_client.py`\n- **When:** Week 3, Post-Pipeline Audit 6.\n''')
