"""
Text Splitter utility for chunking operations.
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


def split_text_at_boundary(text: str, max_length: int, overlap: int = 0) -> List[str]:
    """
    Split text at sentence boundaries.
    
    Args:
        text: Input text to split
        max_length: Maximum length per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Implementation will be added in task 6
    pass


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    return len(text.split())
