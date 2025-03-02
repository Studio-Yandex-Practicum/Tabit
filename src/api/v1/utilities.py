import random

from src.companies.constants import GENERATED_SLUG_SUFFIX_RANGE, SHORT_SYMBOLS


def generate_unique_slug(base_slug: str) -> str:
    """Метод формирования `slug` объектов Company или Department."""
    return base_slug + ''.join(random.choices(SHORT_SYMBOLS, k=GENERATED_SLUG_SUFFIX_RANGE))
