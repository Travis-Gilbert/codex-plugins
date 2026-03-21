---
description: Export, optimize, and deploy a trained model
---

Read `agents/systems-optimizer.md` and `references/evaluation-deploy.md`.

1. Profile the current model:
   - Measure inference latency (warmup + 100 runs)
   - Check GPU memory usage
   - Count parameters
2. Select optimization strategy from the inference ladder:
   - Step 1: Inference mode + no_grad
   - Step 2: torch.compile
   - Step 3: Dynamic quantization (int8, CPU)
   - Step 4: Static quantization (int8, calibration)
   - Step 5: ONNX Runtime
   - Step 6: TensorRT (GPU, NVIDIA only)
   - Step 7: Batching for throughput
3. Export the model:
   - ONNX: `torch.onnx.export` with dynamic axes, opset 17
   - TorchScript: `torch.jit.script` or `torch.jit.trace`
4. Quantize if appropriate:
   - Dynamic for CPU inference
   - Static for best quality (requires calibration data)
5. Set up serving:
   - FastAPI + ONNX Runtime for standard models
   - vLLM for LLM serving
6. Verify output correctness after optimization:
   - Compare outputs between original and optimized model
   - Measure quality metric delta
