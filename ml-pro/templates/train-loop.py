"""
Standard PyTorch Training Loop Template
========================================
Copy and adapt for any supervised learning task.
Includes: mixed precision, gradient clipping, LR scheduling,
validation, checkpointing, early stopping, wandb logging.
"""

import math
import os
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# Optional: uncomment for experiment tracking
# import wandb


@dataclass
class Config:
    """All hyperparameters. Never hardcode elsewhere."""
    # Data
    batch_size: int = 32
    num_workers: int = 4
    # Model
    input_dim: int = 768
    hidden_dim: int = 512
    output_dim: int = 10
    num_layers: int = 4
    dropout: float = 0.1
    # Optimization
    lr: float = 1e-3
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    # Schedule
    warmup_fraction: float = 0.1
    num_epochs: int = 50
    # Regularization
    label_smoothing: float = 0.0
    # Infrastructure
    mixed_precision: bool = True
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 42
    # Checkpointing
    checkpoint_dir: str = "checkpoints"
    patience: int = 10
    # Tracking
    project_name: str = "ml-pro"
    run_name: str = ""


# === Reproducibility ===

def set_seed(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


# === Model (replace with your architecture) ===

class Model(nn.Module):
    """
    Replace this with your actual model.
    Input:  (B, input_dim)
    Output: (B, output_dim)
    """
    def __init__(self, config: Config):
        super().__init__()
        layers = []
        prev = config.input_dim
        for _ in range(config.num_layers - 1):
            layers.extend([
                nn.Linear(prev, config.hidden_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout),
            ])
            prev = config.hidden_dim
        layers.append(nn.Linear(prev, config.output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)  # (B, output_dim)


# === Data (replace with your dataset) ===

class DummyDataset(Dataset):
    """Replace with your actual dataset."""
    def __init__(self, n_samples, input_dim, num_classes):
        self.x = torch.randn(n_samples, input_dim)
        self.y = torch.randint(0, num_classes, (n_samples,))

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


# === LR Schedule ===

def get_scheduler(optimizer, config, total_steps):
    warmup_steps = int(config.warmup_fraction * total_steps)

    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)


# === Checkpointing ===

def save_checkpoint(path, model, optimizer, scheduler, epoch, best_val, config):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict(),
        "epoch": epoch,
        "best_val": best_val,
        "config": asdict(config),
    }, path)


def load_checkpoint(path, model, optimizer=None, scheduler=None):
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model"])
    if optimizer and "optimizer" in ckpt:
        optimizer.load_state_dict(ckpt["optimizer"])
    if scheduler and "scheduler" in ckpt:
        scheduler.load_state_dict(ckpt["scheduler"])
    return ckpt["epoch"], ckpt["best_val"]


# === Evaluation ===

@torch.no_grad()
def evaluate(model, loader, loss_fn, device, mixed_precision=True):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    for x, y in loader:
        x, y = x.to(device), y.to(device)
        with torch.cuda.amp.autocast(enabled=mixed_precision):
            logits = model(x)
            loss = loss_fn(logits, y)
        total_loss += loss.item() * len(y)
        correct += (logits.argmax(1) == y).sum().item()
        total += len(y)

    return {
        "loss": total_loss / total,
        "accuracy": correct / total,
    }


# === Verify Data ===

def verify_data(loader, name="train"):
    x, y = next(iter(loader))
    print(f"[{name}] x: shape={x.shape}, dtype={x.dtype}, "
          f"range=[{x.min():.3f}, {x.max():.3f}]")
    print(f"[{name}] y: shape={y.shape}, dtype={y.dtype}, "
          f"unique values={y.unique().tolist()[:20]}")


# === Main ===

def main():
    config = Config()
    set_seed(config.seed)

    # Data
    train_ds = DummyDataset(1000, config.input_dim, config.output_dim)
    val_ds = DummyDataset(200, config.input_dim, config.output_dim)

    train_loader = DataLoader(
        train_ds, batch_size=config.batch_size, shuffle=True,
        num_workers=config.num_workers, pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=config.batch_size * 2,
        num_workers=config.num_workers, pin_memory=True,
    )

    verify_data(train_loader, "train")
    verify_data(val_loader, "val")

    # Model
    model = Model(config).to(config.device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {total_params:,}")

    # Optimization
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    total_steps = config.num_epochs * len(train_loader)
    scheduler = get_scheduler(optimizer, config, total_steps)
    scaler = torch.cuda.amp.GradScaler(enabled=config.mixed_precision)
    loss_fn = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)

    # Training
    best_val = float("inf")
    no_improve = 0

    for epoch in range(config.num_epochs):
        model.train()
        epoch_loss = 0
        t0 = time.time()

        for x, y in train_loader:
            x, y = x.to(config.device), y.to(config.device)

            with torch.cuda.amp.autocast(enabled=config.mixed_precision):
                logits = model(x)
                loss = loss_fn(logits, y)

            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            epoch_loss += loss.item()

        # Validate
        val_metrics = evaluate(model, val_loader, loss_fn,
                               config.device, config.mixed_precision)
        train_loss = epoch_loss / len(train_loader)
        elapsed = time.time() - t0

        print(f"Epoch {epoch:3d} | train_loss={train_loss:.4f} | "
              f"val_loss={val_metrics['loss']:.4f} | "
              f"val_acc={val_metrics['accuracy']:.4f} | "
              f"lr={optimizer.param_groups[0]['lr']:.2e} | "
              f"{elapsed:.1f}s")

        # Checkpoint + early stopping
        if val_metrics["loss"] < best_val:
            best_val = val_metrics["loss"]
            no_improve = 0
            save_checkpoint(
                f"{config.checkpoint_dir}/best.pt",
                model, optimizer, scheduler, epoch, best_val, config)
        else:
            no_improve += 1
            if no_improve >= config.patience:
                print(f"Early stopping at epoch {epoch}")
                break

    print(f"Best val loss: {best_val:.4f}")


if __name__ == "__main__":
    main()
