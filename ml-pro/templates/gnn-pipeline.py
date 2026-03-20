"""
GNN Pipeline Template (PyG)
============================
Covers node classification and link prediction.
Adapt model, data loading, and evaluation for your task.
"""

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch_geometric.nn as pyg_nn
from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
from torch_geometric.transforms import RandomLinkSplit
from torch_geometric.utils import negative_sampling


@dataclass
class GNNConfig:
    in_dim: int = 128
    hidden_dim: int = 128
    out_dim: int = 7
    num_layers: int = 2
    num_relations: int = 0      # 0 = homogeneous, >0 = R-GCN
    heads: int = 1              # >1 = GAT
    dropout: float = 0.5
    lr: float = 1e-2
    weight_decay: float = 5e-4
    epochs: int = 200
    task: str = "node"          # "node" or "link"


# === Node Classification Model ===

class NodeClassifier(nn.Module):
    def __init__(self, config: GNNConfig):
        super().__init__()
        self.convs = nn.ModuleList()

        in_dim = config.in_dim
        for i in range(config.num_layers):
            out_dim = config.out_dim if i == config.num_layers - 1 else config.hidden_dim

            if config.num_relations > 0:
                conv = pyg_nn.RGCNConv(in_dim, out_dim, config.num_relations)
            elif config.heads > 1 and i < config.num_layers - 1:
                conv = pyg_nn.GATConv(in_dim, out_dim, heads=config.heads, concat=True)
                out_dim = out_dim * config.heads
            else:
                conv = pyg_nn.GCNConv(in_dim, out_dim)

            self.convs.append(conv)
            in_dim = out_dim

        self.dropout = config.dropout

    def forward(self, x, edge_index, edge_type=None):
        for i, conv in enumerate(self.convs[:-1]):
            args = (x, edge_index, edge_type) if edge_type is not None else (x, edge_index)
            x = conv(*args)                           # (N, H)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        # Last layer: no activation, no dropout
        args = (x, edge_index, edge_type) if edge_type is not None else (x, edge_index)
        return self.convs[-1](*args)                  # (N, out_dim)


# === Link Prediction Model ===

class LinkPredictor(nn.Module):
    def __init__(self, config: GNNConfig):
        super().__init__()
        self.convs = nn.ModuleList()

        in_dim = config.in_dim
        for _ in range(config.num_layers):
            if config.num_relations > 0:
                conv = pyg_nn.RGCNConv(in_dim, config.hidden_dim, config.num_relations)
            else:
                conv = pyg_nn.GCNConv(in_dim, config.hidden_dim)
            self.convs.append(conv)
            in_dim = config.hidden_dim

        self.dropout = config.dropout

    def encode(self, x, edge_index, edge_type=None):
        for conv in self.convs:
            args = (x, edge_index, edge_type) if edge_type is not None else (x, edge_index)
            x = conv(*args)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        return x  # (N, hidden_dim)

    def decode(self, z, edge_label_index):
        src, dst = edge_label_index
        return (z[src] * z[dst]).sum(dim=-1)  # (E,)

    def forward(self, x, edge_index, edge_label_index, edge_type=None):
        z = self.encode(x, edge_index, edge_type)
        return self.decode(z, edge_label_index)


# === Training: Node Classification ===

def train_node(model, data, optimizer, device):
    model.train()
    data = data.to(device)
    out = model(data.x, data.edge_index,
                getattr(data, 'edge_type', None))
    loss = F.cross_entropy(out[data.train_mask], data.y[data.train_mask])
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    return loss.item()


@torch.no_grad()
def eval_node(model, data, device):
    model.eval()
    data = data.to(device)
    out = model(data.x, data.edge_index,
                getattr(data, 'edge_type', None))
    pred = out.argmax(dim=1)

    results = {}
    for split, mask in [("train", data.train_mask),
                         ("val", data.val_mask),
                         ("test", data.test_mask)]:
        correct = (pred[mask] == data.y[mask]).sum().item()
        total = mask.sum().item()
        results[f"{split}_acc"] = correct / total
    return results


# === Training: Link Prediction ===

def train_link(model, train_data, optimizer, device):
    model.train()
    train_data = train_data.to(device)

    out = model(train_data.x, train_data.edge_index,
                train_data.edge_label_index,
                getattr(train_data, 'edge_type', None))
    loss = F.binary_cross_entropy_with_logits(out, train_data.edge_label.float())

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    return loss.item()


@torch.no_grad()
def eval_link(model, data, device):
    from sklearn.metrics import roc_auc_score, average_precision_score

    model.eval()
    data = data.to(device)
    out = model(data.x, data.edge_index, data.edge_label_index,
                getattr(data, 'edge_type', None)).sigmoid()

    y_true = data.edge_label.cpu().numpy()
    y_score = out.cpu().numpy()

    return {
        "auc": roc_auc_score(y_true, y_score),
        "ap": average_precision_score(y_true, y_score),
    }


# === Main ===

def main():
    config = GNNConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Replace with your data loading
    from torch_geometric.datasets import Planetoid
    dataset = Planetoid(root="/tmp/Cora", name="Cora")
    data = dataset[0]

    print(f"Nodes: {data.num_nodes}, Edges: {data.num_edges}, "
          f"Features: {data.num_node_features}, Classes: {dataset.num_classes}")

    config.in_dim = data.num_node_features
    config.out_dim = dataset.num_classes

    if config.task == "node":
        model = NodeClassifier(config).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.lr,
                                      weight_decay=config.weight_decay)
        for epoch in range(config.epochs):
            loss = train_node(model, data, optimizer, device)
            if epoch % 10 == 0:
                metrics = eval_node(model, data, device)
                print(f"Epoch {epoch:3d} | loss={loss:.4f} | "
                      f"val_acc={metrics['val_acc']:.4f} | "
                      f"test_acc={metrics['test_acc']:.4f}")

    elif config.task == "link":
        transform = RandomLinkSplit(num_val=0.1, num_test=0.1,
                                     is_undirected=True,
                                     add_negative_train_samples=True)
        train_data, val_data, test_data = transform(data)

        config.out_dim = config.hidden_dim  # not used for link pred
        model = LinkPredictor(config).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

        for epoch in range(config.epochs):
            loss = train_link(model, train_data, optimizer, device)
            if epoch % 10 == 0:
                val_metrics = eval_link(model, val_data, device)
                print(f"Epoch {epoch:3d} | loss={loss:.4f} | "
                      f"val_auc={val_metrics['auc']:.4f}")

    total = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {total:,}")


if __name__ == "__main__":
    main()
