# Evaluation and Deployment Reference

## Metric Implementations

### Classification
```python
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, classification_report, confusion_matrix
)

preds = logits.argmax(dim=1).cpu().numpy()
labels = targets.cpu().numpy()

acc = accuracy_score(labels, preds)
f1 = f1_score(labels, preds, average='macro')  # 'micro', 'weighted'
report = classification_report(labels, preds, target_names=class_names)
```

### Ranking / Retrieval
```python
def mrr(rankings):
    """Mean Reciprocal Rank."""
    return np.mean([1.0 / r for r in rankings])

def precision_at_k(predictions, relevant, k):
    top_k = predictions[:k]
    return len(set(top_k) & set(relevant)) / k

def ndcg_at_k(scores, k):
    """Normalized Discounted Cumulative Gain."""
    dcg = sum(s / np.log2(i + 2) for i, s in enumerate(scores[:k]))
    ideal = sorted(scores, reverse=True)
    idcg = sum(s / np.log2(i + 2) for i, s in enumerate(ideal[:k]))
    return dcg / idcg if idcg > 0 else 0
```

### KG Completion
```python
from pykeen.evaluation import RankBasedEvaluator
evaluator = RankBasedEvaluator()
# Key metrics: MRR (realistic, both), Hits@1, Hits@3, Hits@10
```

## Cross-Validation

```python
from sklearn.model_selection import StratifiedKFold

kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
fold_scores = []
for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    model = build_model()
    train(model, X[train_idx], y[train_idx])
    score = evaluate(model, X[val_idx], y[val_idx])
    fold_scores.append(score)
    print(f"Fold {fold}: {score:.4f}")
print(f"CV: {np.mean(fold_scores):.4f} +/- {np.std(fold_scores):.4f}")
```

## Ensembling

```python
def ensemble_predict(models, x):
    with torch.no_grad():
        preds = torch.stack([m(x) for m in models])
    return preds.mean(dim=0)

def weighted_ensemble(models, weights, x):
    with torch.no_grad():
        preds = torch.stack([w * m(x) for m, w in zip(models, weights)])
    return preds.sum(dim=0)
```

## Model Export

### ONNX
```python
model.eval().cpu()
dummy = torch.randn(1, *input_shape)
torch.onnx.export(
    model, dummy, "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=17,
)

# Verify
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
ort_out = session.run(None, {"input": dummy.numpy()})
torch_out = model(dummy).detach().numpy()
assert np.allclose(ort_out[0], torch_out, atol=1e-5)
```

### TorchScript
```python
scripted = torch.jit.script(model)
traced = torch.jit.trace(model, dummy)
scripted.save("model.pt")
```

## Quantization

### Dynamic (CPU, easiest)
```python
model_q = torch.quantization.quantize_dynamic(
    model.cpu(), {nn.Linear}, dtype=torch.qint8)
```

### Static (better, needs calibration)
```python
model.eval()
model.qconfig = torch.quantization.get_default_qconfig('x86')
prepared = torch.quantization.prepare(model)
for batch in calib_loader:
    prepared(batch)
quantized = torch.quantization.convert(prepared)
```

## Serving

### FastAPI + ONNX
```python
from fastapi import FastAPI
import onnxruntime as ort

app = FastAPI()
session = ort.InferenceSession("model.onnx",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

@app.post("/predict")
async def predict(data: PredictRequest):
    inputs = preprocess(data)
    result = session.run(None, {"input": inputs})
    return {"prediction": postprocess(result)}
```

### Batch Inference
```python
def batch_predict(model, dataset, batch_size=256):
    loader = DataLoader(dataset, batch_size=batch_size, num_workers=4)
    model.eval()
    all_preds = []
    with torch.no_grad():
        for batch in tqdm(loader):
            preds = model(batch.to(device))
            all_preds.append(preds.cpu())
    return torch.cat(all_preds)
```
