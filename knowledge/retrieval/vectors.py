import math
from collections.abc import Sequence


def normalize_vector(vector: Sequence[float]) -> list[float]:
    values = [float(value) for value in vector]
    if not values:
        raise ValueError("Embedding vectors must not be empty")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Embedding vectors must contain only finite values")

    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        raise ValueError("Embedding vectors must have a non-zero norm")
    return [value / norm for value in values]
