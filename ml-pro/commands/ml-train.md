---
description: Generate a complete training pipeline for a model
---

Read `agents/training-engineer.md` and `references/training-craft.md`.

1. Identify the task type and model:
   - Classification, regression, ranking, generation, etc.
   - Architecture family (transformer, CNN, GNN, MLP, etc.)
2. Select loss function, optimizer, and LR schedule from reference tables:
   - Loss: Match task type to loss function matrix
   - Optimizer: Match model type to optimizer config
   - Schedule: cosine+warmup for transformers, OneCycleLR for CNNs
3. Start from the matching template in `templates/`:
   - `templates/train-loop.py` for standard supervised training
   - `templates/gnn-pipeline.py` for graph tasks
   - `templates/fine-tune-lora.py` for LLM fine-tuning
   - `templates/kge-pipeline.py` for knowledge graph embeddings
   - `templates/rl-agent.py` for reinforcement learning
4. Customize for the specific model and data.
5. Include all required components:
   - Config dataclass with all hyperparameters
   - Reproducibility (set_seed)
   - Data verification (--verify-data)
   - Training loop with AMP + grad clipping + scheduling
   - Checkpointing (full state: model + optimizer + scheduler + epoch + metric)
   - Validation with baseline comparison
   - Experiment tracking (wandb)
