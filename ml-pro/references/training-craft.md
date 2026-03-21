# Training Craft Reference

## Loss Function Matrix

| Task | Loss | PyTorch | Notes |
|---|---|---|---|
| Multi-class | Cross-entropy | `nn.CrossEntropyLoss()` | Logits in, not softmax |
| Binary | Binary CE | `nn.BCEWithLogitsLoss()` | pos_weight for imbalance |
| Multi-label | Binary CE per label | `nn.BCEWithLogitsLoss()` | Each output independent |
| Regression | Huber | `nn.SmoothL1Loss()` | Better default than MSE |
| Ranking | Triplet | `nn.TripletMarginLoss(margin=1.0)` | Need (anchor, pos, neg) |
| Contrastive | InfoNCE | Custom | Temperature=0.07 |
| KG embedding | Margin ranking | Custom | Score(pos) > Score(neg) + margin |
| Sequence gen | CE per token | `nn.CrossEntropyLoss(ignore_index=pad)` | Mask padding |
| Label smoothing | Smoothed CE | `nn.CrossEntropyLoss(label_smoothing=0.1)` | 0.05-0.1 typical |

## Optimizer Configs

| Model Type | Optimizer | LR | Weight Decay | Betas |
|---|---|---|---|---|
| Transformer (train) | AdamW | 1e-4 | 0.01-0.1 | (0.9, 0.95) |
| Transformer (fine-tune) | AdamW | 1e-5 to 5e-5 | 0.01 | (0.9, 0.999) |
| CNN | SGD+momentum | 1e-2 | 1e-4 | momentum=0.9 |
| CNN | AdamW | 1e-3 | 1e-4 | (0.9, 0.999) |
| GNN | Adam | 1e-3 to 5e-3 | 5e-4 | (0.9, 0.999) |
| LoRA | AdamW | 1e-4 to 2e-4 | 0.01 | (0.9, 0.999) |
| RL (PPO) | Adam | 3e-4 | 0 | (0.9, 0.999) |

## LR Schedule Patterns

### Cosine with Warmup (standard for transformers)
```python
from torch.optim.lr_scheduler import CosineAnnealingLR, LinearLR, SequentialLR

warmup = LinearLR(optimizer, start_factor=0.01, total_iters=warmup_steps)
cosine = CosineAnnealingLR(optimizer, T_max=total_steps - warmup_steps)
scheduler = SequentialLR(optimizer, [warmup, cosine], milestones=[warmup_steps])
```

### OneCycleLR (simple, works well)
```python
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=1e-3,
    total_steps=epochs * len(loader),
    pct_start=0.1,
)
```

### ReduceOnPlateau (adaptive)
```python
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=5)
# scheduler.step(val_loss) after each epoch
```

## Regularization Quick Reference

| Method | Where | Default | Effect |
|---|---|---|---|
| Dropout | After activations | 0.1 | Zero random activations |
| Weight decay | Optimizer | 0.01 (AdamW) | L2 penalty on weights |
| LayerNorm | Before attention/FFN | Always for transformers | Stabilize activations |
| BatchNorm | After conv layers | Standard for CNNs | Normalize across batch |
| Label smoothing | Loss function | 0.05-0.1 | Soften targets |
| Gradient clipping | After backward | max_norm=1.0 | Prevent exploding gradients |
| Early stopping | Training loop | patience=5-10 | Stop when val plateaus |
| Stochastic depth | Residual blocks | 0.1-0.3 | Skip random layers |

## Data Loading Checklist

```python
DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,           # True for train, False for val/test
    num_workers=4,          # 2-8, adjust for system
    pin_memory=True,        # always with GPU
    persistent_workers=True,# keep workers alive between epochs
    prefetch_factor=2,      # batches to prefetch per worker
    drop_last=True,         # drop incomplete last batch (train only)
)
```

## Checkpoint Pattern

```python
def save_checkpoint(path, model, optimizer, scheduler, epoch, best_metric, config):
    torch.save({
        'model': model.state_dict(),
        'optimizer': optimizer.state_dict(),
        'scheduler': scheduler.state_dict(),
        'epoch': epoch,
        'best_metric': best_metric,
        'config': config.__dict__ if hasattr(config, '__dict__') else config,
    }, path)

def load_checkpoint(path, model, optimizer=None, scheduler=None):
    ckpt = torch.load(path, map_location='cpu', weights_only=False)
    model.load_state_dict(ckpt['model'])
    if optimizer and 'optimizer' in ckpt:
        optimizer.load_state_dict(ckpt['optimizer'])
    if scheduler and 'scheduler' in ckpt:
        scheduler.load_state_dict(ckpt['scheduler'])
    return ckpt.get('epoch', 0), ckpt.get('best_metric', float('inf'))
```

## Experiment Tracking (wandb)

```python
import wandb

wandb.init(project="ml-pro", config=config.__dict__,
           name=f"{config.model_type}-{config.lr}")

# In training loop
wandb.log({"train/loss": loss, "train/lr": lr, "epoch": epoch})

# After eval
wandb.log({"val/loss": val_loss, "val/accuracy": val_acc})

# At end
wandb.finish()
```
