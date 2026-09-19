import os
try:
    import torch
    from torch_geometric.explain import Explainer, CaptumExplainer
except ImportError:
    torch = None
    Explainer = None

class FraudExplainer:
    def __init__(self, model):
        self.model = model
        if Explainer is not None:
            self.explainer = Explainer(
                model=self.model,
                algorithm=CaptumExplainer('IntegratedGradients'),
                explanation_type='model',
                edge_mask_type='object',
                model_config=dict(
                    mode='binary_classification',
                    task_level='edge',
                    return_type='probs',
                )
            )

    def explain_transaction(self, x_dict, edge_index_dict, edge_attr_dict, target_edge_idx):
        if Explainer is None:
            return {"error": "PyTorch Geometric Explainer not installed."}

        # Generate the explanation mask for the specific edge
        explanation = self.explainer(
            x_dict, edge_index_dict,
            edge_attr_dict=edge_attr_dict,
            index=target_edge_idx
        )
        
        # Extract edge mask (importance weights from 0 to 1)
        edge_mask = explanation.edge_mask_dict[('account', 'sends', 'account')]
        
        # Top contributing edges
        top_k = min(3, edge_mask.size(0))
        top_scores, top_indices = torch.topk(edge_mask, top_k)
        
        reasons = []
        for i in range(top_k):
            idx = top_indices[i].item()
            score = top_scores[i].item()
            reasons.append({
                "edge_index": idx,
                "importance_score": round(score, 4),
                "reason": f"High risk topology connection at edge {idx}"
            })
            
        return {
            "transaction_index": target_edge_idx,
            "top_contributing_factors": reasons
        }
