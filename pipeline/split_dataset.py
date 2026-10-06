from __future__ import annotations

import random
from typing import Any


def split_examples(
    examples: list[dict[str, Any]],
    train_ratio: float,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> dict[str, list[dict[str, Any]]]:
    if abs(train_ratio + validation_ratio + test_ratio - 1.0) > 1e-9:
        raise ValueError("Dataset split ratios must total 1.0")
    shuffled = list(examples)
    random.Random(seed).shuffle(shuffled)
    total = len(shuffled)
    validation_count = round(total * validation_ratio)
    test_count = round(total * test_ratio)
    if total >= 3:
        validation_count = max(1, validation_count)
        test_count = max(1, test_count)
    train_count = total - validation_count - test_count
    if train_count < 1 and total:
        raise ValueError("Dataset is too small for the requested split")
    return {
        "train": shuffled[:train_count],
        "validation": shuffled[train_count : train_count + validation_count],
        "test": shuffled[train_count + validation_count :],
    }
