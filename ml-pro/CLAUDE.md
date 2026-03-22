# ML-Pro Plugin

You have deep ML engineering knowledge encoded in reference files, agent
instructions, and implementation templates. Use them. Do NOT rely on
training data for library APIs, hyperparameter defaults, or architecture
details. Verify against references before writing code.

## When You Start an ML Task

1. Read the handoff document (if one exists from the ml-builder chat skill).
   It contains: problem definition, architecture spec, training config,
   evaluation plan, risks, and file manifest.

2. Determine the task type. Route to the appropriate agent:
   - Building a model architecture: `agents/model-architect.md`
   - Writing a training pipeline: `agents/training-engineer.md`
   - Debugging training or inference: `agents/ml-debugger.md`
   - Working with graph data or GNNs: `agents/graph-engineer.md`
   - Optimizing performance or deployment: `agents/systems-optimizer.md`

3. Before writing model code, read the relevant reference in `references/`
   to verify API signatures, default parameters, and known failure modes.

4. Use templates in `templates/` as starting points. They encode
   battle-tested patterns for common ML tasks. Never start from scratch
   when a template exists.

## Reference Library

References in `references/` provide verified API details, parameter
guidance, and integration patterns:

- **references/pytorch-patterns.md** - nn.Module patterns, training loop
  variants, gradient mechanics, mixed precision, torch.compile, DDP/FSDP.
  Read before any PyTorch code.

- **references/gnn-cookbook.md** - PyG message passing, GCN/GAT/R-GCN/
  GraphSAGE patterns, graph data handling, batching, NeighborLoader,
  over-smoothing mitigation. Read before any GNN code.

- **references/transformers-patterns.md** - Attention implementation,
  positional encoding, HuggingFace integration, LoRA/QLoRA with
  torchtune, tokenizer handling, KV-cache. Read before any transformer
  or LLM code.

- **references/training-craft.md** - Loss function selection matrix,
  optimizer configs, LR schedules, regularization, data loading, mixed
  precision, gradient accumulation, early stopping, experiment tracking.
  Read when writing or debugging any training loop.

- **references/evaluation-deploy.md** - Metric implementations, cross-
  validation, ensembling, model export (ONNX, TorchScript), quantization,
  serving patterns. Read before evaluation or deployment code.

- **references/advanced-systems.md** - RL (PPO/DQN via stable-baselines3),
  KG embeddings (PyKEEN), contrastive learning (InfoNCE), diffusion models,
  evolutionary optimization (Optuna/DEAP/CMA-ES), meta-learning (MAML),
  Bayesian methods, neuro-symbolic patterns. Read for any advanced paradigm.

## Agent Instructions

Agents in `agents/` provide deep task-specific guidance:

- **agents/model-architect.md** - Designs model architectures. Selects
  layers, dimensions, activations, normalization, skip connections.
  Produces complete nn.Module code with parameter counts and shape
  annotations.

- **agents/training-engineer.md** - Builds training pipelines. Data
  loading, loss functions, optimizers, schedulers, training loops,
  validation, checkpointing, experiment tracking. Produces complete
  train.py files.

- **agents/ml-debugger.md** - Diagnoses training failures. Follows a
  systematic protocol: overfit-one-batch, loss curve analysis, gradient
  inspection, data pipeline verification, simplification. Produces
  targeted fixes with explanations.

- **agents/graph-engineer.md** - Specializes in graph ML. GNN
  architecture selection, PyG data handling, message passing customization,
  knowledge graph embeddings, link prediction, node classification.
  Handles the full PyG + NetworkX + PyKEEN stack.

- **agents/systems-optimizer.md** - Optimizes ML systems for production.
  Mixed precision, torch.compile, distributed training, quantization,
  profiling, memory optimization, inference serving. Produces deployment-
  ready configurations.

## Templates

Templates in `templates/` provide complete starting points:

- **templates/train-loop.py** - Standard PyTorch training loop with
  mixed precision, gradient clipping, LR scheduling, validation,
  checkpointing, and wandb logging.

- **templates/gnn-pipeline.py** - Complete GNN pipeline with PyG:
  data loading, model definition, training, evaluation for node
  classification and link prediction.

- **templates/fine-tune-lora.py** - LoRA fine-tuning template for
  HuggingFace models with torchtune.

- **templates/kge-pipeline.py** - Knowledge graph embedding training
  and evaluation with PyKEEN.

- **templates/rl-agent.py** - RL agent template with stable-baselines3,
  custom environment wrapper, and reward shaping.

## Commands

- `/ml-build` - Plan and build an ML system from a handoff doc or description
- `/ml-debug` - Run the 5-step diagnostic protocol for training failures
- `/ml-train` - Generate a complete training pipeline for a model
- `/ml-deploy` - Export, optimize, and deploy a trained model

## Rules

1. **Verify APIs against references.** Do not rely on training data for
   PyTorch, PyG, HuggingFace, or any ML library API. Read the reference
   file first. Grep source repos when references do not cover the
   specific API in question.

2. **Always include shape comments.** Every tensor operation in model
   code must have a comment showing the expected shape:
   ```python
   x = self.encoder(x)  # (B, T, D) -> (B, T, H)
   ```

3. **Every model must be testable on one batch.** Include an
   `if __name__ == "__main__"` block that creates dummy data and runs
   a forward pass. This catches shape mismatches immediately.

4. **Never hardcode hyperparameters in model code.** Use a config
   object or dataclass. Training parameters (lr, batch_size, epochs)
   go in config, not scattered through the code.

5. **Gradient clipping is not optional.** Every training loop must
   include `clip_grad_norm_` with a configurable max_norm (default 1.0).

6. **Mixed precision by default.** Use `torch.cuda.amp.autocast` and
   `GradScaler` unless there is a specific reason not to (e.g., CPU-only,
   numerical sensitivity in the loss function).

7. **Evaluation must compare to a baseline.** Every evaluation script
   must compute and report a baseline metric (most-frequent class, mean
   prediction, BM25, etc.) alongside the model metric.

8. **Checkpoints save the full state.** Save model state_dict, optimizer
   state_dict, scheduler state_dict, epoch, and best metric. Load all
   of them when resuming.

9. **Data pipelines must be verifiable.** Include a `--verify-data` flag
   or equivalent that prints shapes, dtypes, value ranges, and label
   distributions for one batch before training starts.

10. **Imports are explicit.** Do not use `from module import *`. Every
    imported name must be visible in the import block.

## Quality Gates

Before considering any ML code complete, verify:

**Architecture**
- [ ] Forward pass runs without error on dummy data
- [ ] Parameter count matches expectation
- [ ] All tensor shapes are annotated in comments
- [ ] Config/dataclass controls all hyperparameters

**Training**
- [ ] Overfit-one-batch test passes (loss reaches near-zero)
- [ ] Gradient clipping is present
- [ ] Mixed precision is enabled (or explicitly justified not to be)
- [ ] Checkpointing saves full training state
- [ ] Experiment tracking is configured (wandb or MLflow)

**Evaluation**
- [ ] Baseline metric is computed and reported
- [ ] Evaluation uses inference mode and no_grad
- [ ] Metrics match the task (not just accuracy for imbalanced data)

**Data**
- [ ] Data pipeline has a verification mode
- [ ] Train/val/test split is correct (no leakage)
- [ ] Normalization matches training expectations

## Cross-References

| Plugin | Relationship |
|---|---|
| **ml-builder** (chat skill) | Produces handoff documents that this plugin implements. Shared vocabulary: problem formulation, architecture spec, training config. |
| **D3-Pro** | For visualization of training metrics, embedding projections, attention patterns, or graph structures. Route viz tasks there. |
| **Three-Pro** | For 3D visualization of graph embeddings, high-dimensional projections, or spatial ML data. |

## Epistemic Knowledge System

This plugin maintains structured, evolving knowledge in `knowledge/`. Claims carry confidence scores, evidence tracking, and domain tags. Over time, accepted claims strengthen and rejected claims weaken through Bayesian updates.

### Session Start Protocol

1. Read `knowledge/manifest.json` for current state and last update time.
2. Read `knowledge/claims.jsonl` and filter for `status: "active"`.
3. Sort active claims by confidence (descending) and load the top 15-20 into working context.
4. Check `knowledge/tensions.jsonl` for unresolved tensions in the domains relevant to the current task. If the task touches a tension, surface it to the user BEFORE making a decision.
5. Check `knowledge/preferences.jsonl` for user-specific defaults that may override generic best practices.

### During Work

6. When your reasoning draws on a specific claim, note its ID internally.
7. When you make a suggestion informed by a claim, track which claims influenced the decision.
8. When the user accepts, modifies, or rejects a suggestion, note the outcome.

### Session End Protocol

9. Run `/session-save` to write session observations to `knowledge/session_log/{timestamp}.jsonl`. This captures agents invoked, claims consulted, suggestions made, and their outcomes.
10. If you discovered something that contradicts an existing claim, flag it as a HIGH-PRIORITY tension signal in the session log.
11. If you noticed a recurring pattern the knowledge base doesn't cover, note it as a candidate claim in the session log.

### Knowledge Priority Rules

- Active claims with confidence > 0.8 take precedence over static prose when they conflict.
- Draft claims are informational only — they never override static agent instructions.
- Preferences defer to explicit user instructions in the current session. Preferences inform defaults, not mandates.
- When two active claims conflict, check `knowledge/tensions.jsonl` for a resolution. If none exists, surface the conflict to the user and let them decide.
- Tensions are information, not blockers. Surface them, let the user decide, log the decision.

### Commands

- `/knowledge-status` — View claim counts, confidence distribution, tensions, questions
- `/knowledge-review` — Activate draft claims, resolve tensions, triage questions
- `/knowledge-update` — Run between-session learning pipeline (all 8 stages)
- `/session-save` — Flush session observations to the session log
