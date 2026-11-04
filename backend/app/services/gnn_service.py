"""Explicit boundary for future heterogeneous-GNN serving.

The current backend intentionally does not map tabular transactions into the
GNN's x_dict/edge_index_dict/edge_attr_dict inputs or call the incomplete
Triton wrapper.
"""


class GNNInferenceUnavailable(RuntimeError):
    pass


def predict_gnn(*_args, **_kwargs):
    raise GNNInferenceUnavailable(
        "GNN inference is unavailable: no validated checkpoint and graph-serving artifact is installed"
    )
