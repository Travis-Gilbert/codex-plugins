"""
Embedding client for Phase 2 semantic search.

Phase 1: This module is a no-op placeholder.
Phase 2: Will use OpenAI text-embedding-3-small to generate embeddings.
"""


def generate_embeddings(texts: list[str]) -> list[list[float] | None]:
    """
    Phase 2: Generate embeddings for a batch of texts.
    Returns list of embedding vectors (or None for failures).
    """
    # Phase 1: return None for all texts
    return [None] * len(texts)
