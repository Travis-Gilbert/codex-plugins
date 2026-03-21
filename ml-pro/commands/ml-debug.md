---
description: Diagnose and fix ML training failures using the 5-step protocol
---

Read `agents/ml-debugger.md` and follow the diagnostic protocol exactly.

1. Ask for context:
   - Loss curve or training logs
   - Learning rate and batch size
   - Model architecture and size
   - Code snippet of the training loop
2. Execute the 5-step protocol in order:
   - Step 1: Overfit one batch
   - Step 2: Loss curve diagnosis
   - Step 3: Gradient inspection
   - Step 4: Data pipeline verification
   - Step 5: Simplification (if needed)
3. If loss is NaN, follow the NaN Protocol from the debugger agent.
4. For GNN-specific issues, check the GNN debugging section.
5. For transformer-specific issues, check the transformer debugging section.
6. For each finding, produce:
   - **Finding**: What the evidence shows
   - **Root cause**: What is actually wrong
   - **Fix**: Specific code changes
   - **Verification**: How to confirm the fix worked
