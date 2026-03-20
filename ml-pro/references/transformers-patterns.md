# Transformer Patterns Reference

## Attention Implementation

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        B, T, C = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_heads, self.d_k)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # (3, B, H, T, D_k)
        q, k, v = qkv.unbind(0)

        attn = (q @ k.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))
        attn = self.dropout(torch.softmax(attn, dim=-1))
        out = (attn @ v).transpose(1, 2).reshape(B, T, C)
        return self.out(out)
```

## Causal Mask

```python
def causal_mask(T, device):
    return torch.tril(torch.ones(T, T, device=device)).bool()
```

## Transformer Block (Pre-Norm)

```python
class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff=None, dropout=0.1):
        super().__init__()
        d_ff = d_ff or 4 * d_model
        self.attn = MultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model), nn.Dropout(dropout),
        )
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        x = x + self.attn(self.ln1(x), mask)
        x = x + self.ffn(self.ln2(x))
        return x
```

## Positional Encoding

### Sinusoidal (original, no learned params)
```python
class SinusoidalPE(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float()
                        * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

### Learned (simpler, common)
```python
self.pos_emb = nn.Embedding(max_seq_len, d_model)
# In forward: x = x + self.pos_emb(positions)
```

### RoPE (modern, used in LLaMA/etc.)
Use torchtune or custom implementation. Rotates Q and K by
position-dependent angles. Enables relative position awareness
without explicit position embeddings.

## Configuration Presets

| Scale | d_model | heads | layers | FFN | Params |
|---|---|---|---|---|---|
| Tiny | 256 | 4 | 4 | 1024 | ~5M |
| Small | 512 | 8 | 6 | 2048 | ~30M |
| Base | 768 | 12 | 12 | 3072 | ~110M |
| Large | 1024 | 16 | 24 | 4096 | ~340M |
| XL | 2048 | 32 | 48 | 8192 | ~1.5B |

## HuggingFace Integration

### Load Pre-Trained
```python
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')

inputs = tokenizer(texts, return_tensors='pt', padding=True,
                   truncation=True, max_length=512)
outputs = model(**inputs)
# outputs.last_hidden_state: (B, T, 768)
```

### Fine-Tune for Classification
```python
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    'bert-base-uncased', num_labels=3)

outputs = model(**inputs, labels=labels)
loss = outputs.loss
logits = outputs.logits
```

### Custom Head
```python
class CustomModel(nn.Module):
    def __init__(self, pretrained_name, num_classes):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(pretrained_name)
        self.head = nn.Linear(self.backbone.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        out = self.backbone(input_ids=input_ids,
                            attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0]  # [CLS] token
        return self.head(cls)
```

## LoRA with torchtune

```python
from torchtune.models.llama2 import lora_llama2_7b
from torchtune.modules.peft import get_adapter_params

model = lora_llama2_7b(
    lora_attn_modules=['q_proj', 'v_proj'],
    lora_rank=8,
    lora_alpha=16,
)

adapter_params = get_adapter_params(model)
optimizer = torch.optim.AdamW(adapter_params, lr=2e-4)
```

## LoRA Manual Implementation

```python
class LoRALinear(nn.Module):
    def __init__(self, original: nn.Linear, rank=16, alpha=32):
        super().__init__()
        self.original = original
        self.original.weight.requires_grad = False
        if original.bias is not None:
            original.bias.requires_grad = False

        self.A = nn.Linear(original.in_features, rank, bias=False)
        self.B = nn.Linear(rank, original.out_features, bias=False)
        self.scaling = alpha / rank
        nn.init.kaiming_uniform_(self.A.weight)
        nn.init.zeros_(self.B.weight)

    def forward(self, x):
        return self.original(x) + self.B(self.A(x)) * self.scaling
```

## Tokenizer Patterns

```python
tokens = tokenizer(text, return_tensors='pt',
                   padding='max_length', truncation=True,
                   max_length=512)
text = tokenizer.decode(token_ids, skip_special_tokens=True)
tokens = tokenizer(texts, return_tensors='pt',
                   padding=True, truncation=True)
```

## Flash Attention

```python
# PyTorch 2.0+ native
with torch.backends.cuda.sdp_kernel(
    enable_flash=True, enable_math=False, enable_mem_efficient=False
):
    out = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
```
