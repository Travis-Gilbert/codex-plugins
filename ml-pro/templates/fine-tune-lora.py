"""
LoRA Fine-Tuning Template
===========================
Parameter-efficient fine-tuning for HuggingFace transformer models.
Adapt the dataset and evaluation for your task.
"""

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification


@dataclass
class LoRAConfig:
    model_name: str = "bert-base-uncased"
    num_labels: int = 3
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_modules: tuple = ("query", "value")  # which attention modules
    lr: float = 2e-4
    weight_decay: float = 0.01
    batch_size: int = 16
    epochs: int = 3
    max_length: int = 512
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# === LoRA Layer ===

class LoRALinear(nn.Module):
    def __init__(self, original: nn.Linear, rank: int, alpha: int):
        super().__init__()
        self.original = original
        self.original.weight.requires_grad = False
        if original.bias is not None:
            original.bias.requires_grad = False

        in_f, out_f = original.in_features, original.out_features
        self.lora_A = nn.Linear(in_f, rank, bias=False)
        self.lora_B = nn.Linear(rank, out_f, bias=False)
        self.scaling = alpha / rank

        nn.init.kaiming_uniform_(self.lora_A.weight)
        nn.init.zeros_(self.lora_B.weight)

    def forward(self, x):
        return self.original(x) + self.lora_B(self.lora_A(x)) * self.scaling


# === Apply LoRA to Model ===

def apply_lora(model, config: LoRAConfig):
    """Replace matching linear layers with LoRA versions."""
    replaced = 0
    for name, module in model.named_modules():
        for target in config.lora_modules:
            if target in name and isinstance(module, nn.Linear):
                # Navigate to parent and replace
                parts = name.split(".")
                parent = model
                for part in parts[:-1]:
                    parent = getattr(parent, part)
                lora_layer = LoRALinear(module, config.lora_rank, config.lora_alpha)
                setattr(parent, parts[-1], lora_layer)
                replaced += 1

    # Freeze all non-LoRA parameters
    for name, param in model.named_parameters():
        if "lora_" not in name:
            param.requires_grad = False

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total params: {total:,}")
    print(f"Trainable (LoRA): {trainable:,} ({100*trainable/total:.2f}%)")
    print(f"Replaced {replaced} layers with LoRA")

    return model


# === Dataset (replace with yours) ===

class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.encodings = tokenizer(texts, truncation=True, padding="max_length",
                                    max_length=max_length, return_tensors="pt")
        self.labels = torch.tensor(labels)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.labels[idx],
        }


# === Training ===

def train_lora(config: LoRAConfig):
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.model_name, num_labels=config.num_labels)
    model = apply_lora(model, config)
    model = model.to(config.device)

    # Replace with your data
    train_texts = ["example sentence " + str(i) for i in range(100)]
    train_labels = [i % config.num_labels for i in range(100)]
    val_texts = ["val sentence " + str(i) for i in range(20)]
    val_labels = [i % config.num_labels for i in range(20)]

    train_ds = TextDataset(train_texts, train_labels, tokenizer, config.max_length)
    val_ds = TextDataset(val_texts, val_labels, tokenizer, config.max_length)

    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size * 2)

    # Only optimize LoRA parameters
    lora_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(lora_params, lr=config.lr,
                                   weight_decay=config.weight_decay)

    for epoch in range(config.epochs):
        model.train()
        total_loss = 0
        for batch in train_loader:
            batch = {k: v.to(config.device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(lora_params, 1.0)
            optimizer.step()
            total_loss += loss.item()

        # Validate
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(config.device) for k, v in batch.items()}
                outputs = model(**batch)
                preds = outputs.logits.argmax(dim=1)
                correct += (preds == batch["labels"]).sum().item()
                total += len(batch["labels"])

        print(f"Epoch {epoch} | train_loss={total_loss/len(train_loader):.4f} | "
              f"val_acc={correct/total:.4f}")

    # Save LoRA weights only
    lora_state = {k: v for k, v in model.state_dict().items() if "lora_" in k}
    torch.save(lora_state, "lora_weights.pt")
    print(f"Saved {len(lora_state)} LoRA tensors")


if __name__ == "__main__":
    train_lora(LoRAConfig())
