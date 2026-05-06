import re
from typing import Pattern, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1024)
def compile_pattern(keyword: str, regex_mode: int = 0) -> Pattern:
    """Compile and cache regex patterns.
    If regex_mode == 0, escape the keyword and use word boundaries.
    If regex_mode == 1, compile as provided.
    """
    flags = re.IGNORECASE | re.UNICODE
    if regex_mode:
        try:
            pat = re.compile(keyword, flags)
        except re.error:
            logger.exception('Invalid regex: %s', keyword)
            # fallback to escaped keyword
            pat = re.compile(r"\b" + re.escape(keyword) + r"\b", flags)
    else:
        safe = re.escape(keyword)
        pat = re.compile(r"\b" + safe + r"\b", flags)
    return pat


def matches(text: str, pattern: Pattern) -> bool:
    if not text:
        return False
    return bool(pattern.search(text))
