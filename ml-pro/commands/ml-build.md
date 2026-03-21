---
description: Build an ML system from a handoff document or problem description
---

Read the handoff document (if provided) or ask the user to describe the problem.

1. Read `agents/model-architect.md` for architecture design guidance.
2. Read the relevant reference files based on the architecture type:
   - Transformers/LLMs: `references/transformers-patterns.md`
   - GNNs/graphs: `references/gnn-cookbook.md`
   - General PyTorch: `references/pytorch-patterns.md`
   - RL: `references/advanced-systems.md`
3. Check `templates/` for a matching starting point:
   - Standard training: `templates/train-loop.py`
   - GNN pipeline: `templates/gnn-pipeline.py`
   - LoRA fine-tuning: `templates/fine-tune-lora.py`
   - KGE: `templates/kge-pipeline.py`
   - RL: `templates/rl-agent.py`
4. Produce these files:
   - `model.py` - nn.Module with config dataclass, shape comments, smoke test
   - `dataset.py` - Data loading with verification mode
   - `train.py` - Complete training pipeline (AMP, grad clip, checkpointing)
   - `config.py` - All hyperparameters in dataclasses
5. Run the quality gate checklist from CLAUDE.md before presenting code.
