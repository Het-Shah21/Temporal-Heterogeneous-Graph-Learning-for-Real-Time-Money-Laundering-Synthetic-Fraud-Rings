import torch
try:
    from torch_geometric.data import HeteroData
    from torch_geometric.loader import NeighborLoader
except ImportError:
    HeteroData = None

class KHopExtractor:
    def __init__(self, global_graph, num_hops=2):
        self.global_graph = global_graph
        self.num_hops = num_hops

    def extract_subgraph_for_transaction(self, sender_idx, receiver_idx):
        if HeteroData is None:
            return None
            
        print(f"Extracting {self.num_hops}-hop localized subgraph around sender {sender_idx} and receiver {receiver_idx} for ultra-fast inference...")
        
        # NeighborLoader instantly slices the graph traversing outward from target nodes
        loader = NeighborLoader(
            self.global_graph,
            num_neighbors=[15] * self.num_hops, # Sample up to 15 neighbors per hop
            input_nodes=('account', torch.tensor([sender_idx, receiver_idx])),
            batch_size=2
        )
        
        # The first batch represents the isolated, localized subgraph surrounding the transaction
        subgraph = next(iter(loader))
        return subgraph
