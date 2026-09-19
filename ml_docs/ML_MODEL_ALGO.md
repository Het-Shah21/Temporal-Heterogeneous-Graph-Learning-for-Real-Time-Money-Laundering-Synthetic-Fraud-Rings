# ML / DL / AI Algorithm Log

*This document comprehensively tracks and explains every machine learning, deep learning, or AI algorithm utilized in this project.*

*(Entries will be added here right as we implement new algorithms. Below is the strict template we will follow for every algorithm.)*

---
### [Template] Algorithm Name

**1. Mathematical Explanation**
*Detailed theoretical breakdown using pure mathematics (equations, objective functions, gradient updates, message-passing math, etc.) to explain exactly how the algorithm functions under the hood.*

**2. Where it was used**
*Specific file, module, and system where this algorithm is located.*

**3. Why it was chosen**
*Why this specific algorithm was selected over alternatives for our specific use case.*

**4. When it was used in the project timeline**
*Project phase and timeline context (e.g., Week 2, Phase 4).*

**5. What we tried to achieve**
*The high-level objective and the problem this algorithm was brought in to solve.*

**6. What was exactly implemented**
*The specific parameters, custom tweaks, library used (or custom from scratch), and exactly how it was integrated into our pipeline.*

### Algorithm: XGBoost (Extreme Gradient Boosting)

**1. Mathematical Explanation**
XGBoost is an ensemble learning method based on Gradient Boosted Decision Trees. It optimizes a regularized objective function:
Obj(θ) = L(θ) + Ω(θ)
Where L is a differentiable convex loss function (Log Loss for binary classification of fraud), and Ω penalizes the complexity of the trees (number of leaves T and L2 norm of leaf scores w).
At iteration 	, it approximates the objective using a second-order Taylor expansion:
Obj^(t) ≈ Σ [g_i f_t(x_i) + 0.5 h_i f_t(x_i)^2] + Ω(f_t)
Where g_i and h_i are the first and second order gradients of the loss function.

**2. Where it was used**
ml/models/baseline.py

**3. Why it was chosen**
XGBoost handles tabular data (our engineered features like degree, cumulative amounts) exceptionally well, deals natively with missing values, and is highly robust to class imbalance (via scale_pos_weight). It serves as the perfect non-graph baseline.

**4. When it was used in the project timeline**
Week 2, Phase 3 (Baseline Modeling).

**5. What we tried to achieve**
To establish benchmark metrics (Precision, Recall, F1, ROC-AUC) so we can mathematically prove whether our incoming Graph Neural Network (GNN) actually adds value over traditional ML.

**6. What was exactly implemented**
Implemented using xgboost.XGBClassifier. Set 
_estimators=100, learning_rate=0.1, max_depth=5, and dynamically calculated scale_pos_weight based on the exact ratio of legitimate to fraudulent transactions in the training split.
