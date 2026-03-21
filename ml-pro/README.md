# ML-Pro

Claude Code plugin for building, training, debugging, and deploying machine learning systems with verified API knowledge.

## What It Does

ML-Pro grounds Claude Code in reference material and enforced engineering standards for ML work. Instead of relying on training data for library APIs (which change frequently), it verifies against cloned source repos and curated reference files.

## Components

### Agents (5)

| Agent | Color | Routes On |
|-------|-------|-----------|
| **model-architect** | Blue | "build a model," "design the architecture" |
| **training-engineer** | Green | "write the training loop," "train this model" |
| **ml-debugger** | Red | "loss is stuck," "loss is NaN," "model isn't learning" |
| **graph-engineer** | Magenta | "GNN," "knowledge graph," "link prediction," "PyG" |
| **systems-optimizer** | Yellow | "make this faster," "deploy," "quantize," "reduce memory" |

### Commands (4)

| Command | Description |
|---------|-------------|
| `/ml-build` | Build an ML system from a handoff doc or problem description |
| `/ml-debug` | Diagnose training failures using the 5-step protocol |
| `/ml-train` | Generate a complete training pipeline |
| `/ml-deploy` | Export, optimize, and deploy a trained model |

### References (6)

Curated, verified API patterns and decision matrices:

- `pytorch-patterns.md` - nn.Module, training loops, DDP/FSDP, torch.compile
- `gnn-cookbook.md` - PyG layers, data format, mini-batching, link prediction
- `transformers-patterns.md` - Attention, positional encoding, LoRA, HuggingFace
- `training-craft.md` - Loss selection, optimizer configs, LR schedules, regularization
- `evaluation-deploy.md` - Metrics, ONNX export, quantization, serving
- `advanced-systems.md` - RL, KGE, contrastive, diffusion, evolutionary, meta-learning

### Templates (5)

Complete, runnable starting points:

- `train-loop.py` - Standard supervised training with AMP, grad clip, wandb
- `gnn-pipeline.py` - GNN node classification + link prediction (PyG)
- `fine-tune-lora.py` - LoRA fine-tuning for HuggingFace models
- `kge-pipeline.py` - Knowledge graph embeddings with PyKEEN
- `rl-agent.py` - RL agent with stable-baselines3

### Source Repos (refs/)

Cloned by `install.sh` for API verification:

- pytorch, pytorch-geometric, transformers, pykeen
- stable-baselines3, torchtune, sentence-transformers, optuna

## Installation

```bash
# Clone and install
cd ml-pro
./install.sh
```

The install script clones 8 source repos (shallow, ~depth 1) into `refs/` and registers the slash commands.

## Relationship to Other Plugins

- **ml-builder** (Claude.ai chat skill) plans architectures and emits handoff documents
- **ML-Pro** (this plugin) receives handoffs and implements with verified code
- **D3-Pro** handles visualization of training metrics, embeddings, attention patterns
- **Three-Pro** handles 3D visualization of graph embeddings or spatial ML data

## 10 Mandatory Rules

1. Verify APIs against refs/ before writing code
2. Shape comments on every tensor operation
3. Every model testable on one batch (`if __name__ == "__main__"`)
4. Config dataclass for all hyperparameters
5. Gradient clipping is not optional (default max_norm=1.0)
6. Mixed precision by default (autocast + GradScaler)
7. Evaluation must compare to a baseline
8. Checkpoints save full state (model + optimizer + scheduler + epoch + metric)
9. Data pipelines must be verifiable (--verify-data flag)
10. Imports are explicit (no `from module import *`)
