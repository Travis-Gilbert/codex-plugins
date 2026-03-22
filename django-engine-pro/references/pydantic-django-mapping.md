# Pydantic + Django: The Three-Layer Mapping

## The Three Layers

```
Django Model          DRF Serializer          Pydantic Schema
-----------          ---------------         ---------------
Database truth       API representation      Structural validation
Fields + types       Nested relations        Type narrowing
Managers + methods   Read/write split        Computed fields
Migrations           Validation messages     JSON Schema output
```

## When You Need Each Layer

### All Three
When a Django model serves a DRF API AND feeds data into a Pydantic-validated
pipeline (LLM output parsing, scientific computation, external service).

### Skip Pydantic
When DRF serializers handle all validation and no pipeline/LLM boundary exists.

### Skip DRF
When using Django Ninja (Pydantic schemas replace serializers) or when the model
only feeds internal pipelines (no REST API).

### Skip Nothing
When the same data flows through API, computation pipeline, AND LLM agents.

## Mapping Patterns

### Django Model to Pydantic Schema (Manual)

```python
from pydantic import BaseModel, Field
from datetime import datetime

class ObservationSchema(BaseModel):
    """Contract for observation data at boundaries.

    Intentionally NOT auto-generated from the Django model.
    The schema defines the contract; the model defines storage.
    """
    id: int
    timestamp: datetime
    value: float
    unit: str = Field(max_length=20)
    metadata: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}

# Convert: schema = ObservationSchema.model_validate(instance)
```

### Django Ninja ModelSchema (Auto)

```python
from ninja import ModelSchema
from .models import Observation

class ObservationOut(ModelSchema):
    class Meta:
        model = Observation
        fields = ["id", "timestamp", "value", "unit", "metadata"]
```

### DRF Serializer alongside Pydantic

```python
# serializers.py — handles API representation
class ObservationSerializer(serializers.ModelSerializer):
    experiment_title = serializers.CharField(source="experiment.title", read_only=True)

    class Meta:
        model = Observation
        fields = ["id", "timestamp", "value", "unit", "experiment_title"]

# schemas.py — handles pipeline validation
class ObservationInput(BaseModel):
    """Validates data before entering computation pipeline."""
    values: list[float]
    experiment_id: int

    @field_validator("values")
    @classmethod
    def no_nans(cls, v):
        if any(math.isnan(x) for x in v):
            raise ValueError("NaN values not permitted")
        return v
```

## PydanticAI Integration

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    """Structured output from AI analysis."""
    key_findings: list[str]
    confidence: float = Field(ge=0, le=1)
    suggested_connections: list[str]

agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    output_type=AnalysisResult,
)

async def analyze(source_id: int) -> AnalysisResult:
    source = await Source.objects.aget(id=source_id)
    result = await agent.run(f"Analyze: {source.title}\n{source.body}")
    return result.output
```

## Anti-Patterns

1. **Collapsing layers**: Using Pydantic schema AS the serializer when you need
   DRF's nested write support. They serve different purposes.
2. **Auto-generating everything**: ModelSchema is convenient but hides the
   contract. Manual schemas make the boundary explicit.
3. **Skipping from_attributes**: Pydantic can't read Django model instances
   without `model_config = {"from_attributes": True}`.
4. **Mixing validation concerns**: Pydantic validates structure. DRF validates
   business rules. Django validates database constraints. Keep them separate.
