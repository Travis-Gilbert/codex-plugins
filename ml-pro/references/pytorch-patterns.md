# PyTorch Patterns Reference

## nn.Module Patterns

### Config-Driven Models
```python
@dataclass
class Config:
    dim: int = 512
    layers: int = 6
    dropout: float = 0.1

class Model(nn.Module):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        # all dimensions from config, never hardcoded
```

### Composition
```python
nn.Sequential(...)       # linear chain
nn.ModuleList([...])     # indexed, for skip connections / loops
nn.ModuleDict({...})     # named, for multi-task heads
```

### Parameter Management
```python
# Count
sum(p.numel() for p in model.parameters())
sum(p.numel() for p in model.parameters() if p.requires_grad)

# Freeze
for p in module.parameters(): p.requires_grad = False

# Differential LR
optimizer = AdamW([
    {'params': model.backbone.parameters(), 'lr': 1e-5},
    {'params': model.head.parameters(), 'lr': 1e-3},
])
```

## Training Loop Essentials

### Mixed Precision
```python
scaler = torch.cuda.amp.GradScaler()
with torch.cuda.amp.autocast(dtype=torch.bfloat16):
    output = model(x)
    loss = loss_fn(output, y)
scaler.scale(loss).backward()
scaler.unscale_(optimizer)
clip_grad_norm_(model.parameters(), 1.0)
scaler.step(optimizer)
scaler.update()
```

### Gradient Accumulation
```python
accum = 4
for i, batch in enumerate(loader):
    loss = compute_loss(batch) / accum
    loss.backward()
    if (i + 1) % accum == 0:
        clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
        scheduler.step()
```

### Reproducibility
```python
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)
random.seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

## Shape Debugging
```python
# Print hook for tracing shapes through a model
def shape_hook(name):
    def hook(module, input, output):
        in_shape = [x.shape for x in input if isinstance(x, torch.Tensor)]
        out_shape = output.shape if isinstance(output, torch.Tensor) else type(output)
        print(f"{name}: {in_shape} -> {out_shape}")
    return hook

for name, module in model.named_modules():
    module.register_forward_hook(shape_hook(name))
model(dummy_input)  # prints all shapes
```

## torch.compile
```python
model = torch.compile(model, mode='reduce-overhead')
# Modes: default, reduce-overhead, max-autotune
# Works best with static shapes
# Falls back gracefully on unsupported ops
```

## DDP Quick Setup
```python
# torchrun --nproc_per_node=N train.py
dist.init_process_group('nccl')
rank = int(os.environ['LOCAL_RANK'])
model = DDP(model.to(rank), device_ids=[rank])
sampler = DistributedSampler(dataset)
# sampler.set_epoch(epoch) in training loop
```

## Common Tensor Operations
```python
# Einops for readable reshaping
from einops import rearrange, repeat, reduce
x = rearrange(x, 'b t (h d) -> b h t d', h=n_heads)
x = repeat(x, 'b d -> b n d', n=seq_len)
x = reduce(x, 'b t d -> b d', 'mean')
```
