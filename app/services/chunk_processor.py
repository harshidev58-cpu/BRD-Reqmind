"""Chunk processor service for handling large text data.

This module provides functionality to detect and split large texts into
manageable chunks for processing, maintaining context and sentence boundaries.
"""

import re
import logging
import asyncio
from typing import List
from app.models.chunk_models import TextChunk

logger = logging.getLogger(__name__)

# Compile regex pattern once for performance
SENTENCE_BOUNDARY_PATTERN = re.compile(r'[.!?](?:\s|$)')


class ChunkProcessor:
    """Service for detecting and chunking large texts.
    
    This service handles the detection of texts that exceed processing limits
    and splits them into overlapping chunks while preserving sentence boundaries
    and speaker context.
    
    Attributes:
        threshold_words: Word count threshold for chunking
        chunk_size_min: Minimum chunk size in words
        chunk_size_max: Maximum chunk size in words
        overlap: Number of overlapping words between chunks
    """
    
    def __init__(
        self,
        threshold_words: int = 3000,
        chunk_size_min: int = 1000,
        chunk_size_max: int = 1500,
        overlap: int = 100
    ):
        """Initialize chunk processor with configuration.
        
        Args:
            threshold_words: Word count threshold for chunking (default: 3000)
            chunk_size_min: Minimum chunk size in words (default: 1000)
            chunk_size_max: Maximum chunk size in words (default: 1500)
            overlap: Number of overlapping words between chunks (default: 100)
        """
        self.threshold_words = threshold_words
        self.chunk_size_min = chunk_size_min
        self.chunk_size_max = chunk_size_max
        self.overlap = overlap
        
        logger.info(
            "ChunkProcessor initialized",
            extra={
                'threshold_words': threshold_words,
                'chunk_size_min': chunk_size_min,
                'chunk_size_max': chunk_size_max,
                'overlap': overlap
            }
        )
    
    def needs_chunking(self, text: str) -> bool:
        """Check if text exceeds threshold and needs chunking.
        
        Args:
            text: Input text to check
            
        Returns:
            True if text exceeds threshold, False otherwise
        """
        if not text or not text.strip():
            return False
        
        word_count = len(text.split())
        needs_chunk = word_count > self.threshold_words
        
        logger.debug(
            "Chunking threshold check",
            extra={
                'word_count': word_count,
                'threshold': self.threshold_words,
                'needs_chunking': needs_chunk
            }
        )
        return needs_chunk
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """Split text into overlapping chunks with sentence boundary detection.
        
        This method splits large texts into chunks while:
        - Maintaining sentence boundaries (avoiding mid-sentence splits)
        - Preserving speaker context in meeting transcripts
        - Adding overlap between chunks for context continuity
        - Including metadata about chunk position and overlap
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of TextChunk objects with metadata
            
        Raises:
            ValueError: If text is empty or None
        """
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty text")
        
        words = text.split()
        word_count = len(words)
        
        # If text doesn't need chunking, return as single chunk
        if word_count <= self.threshold_words:
            logger.info(
                "Text below threshold, returning single chunk",
                extra={
                    'word_count': word_count,
                    'threshold': self.threshold_words
                }
            )
            return [TextChunk(
                content=text,
                chunk_index=0,
                total_chunks=1,
                word_count=word_count,
                overlap_start=0,
                overlap_end=0
            )]
        
        # Calculate average chunk size and total chunks needed
        chunk_size_avg = (self.chunk_size_min + self.chunk_size_max) // 2
        total_chunks = max(1, (word_count + chunk_size_avg - 1) // chunk_size_avg)
        
        logger.info(
            "Chunking text",
            extra={
                'word_count': word_count,
                'estimated_chunks': total_chunks,
                'chunk_size_avg': chunk_size_avg,
                'threshold': self.threshold_words
            }
        )
        
        chunks = []
        current_pos = 0
        chunk_index = 0
        
        while current_pos < word_count:
            # Calculate chunk boundaries
            chunk_start = max(0, current_pos - (self.overlap if chunk_index > 0 else 0))
            chunk_end = min(word_count, chunk_start + self.chunk_size_max)
            
            # Extract chunk words
            chunk_words = words[chunk_start:chunk_end]
            chunk_text = ' '.join(chunk_words)
            
            # Find sentence boundary for split (except for last chunk)
            if chunk_end < word_count:
                boundary_pos = self._split_at_sentence_boundary(chunk_text, len(chunk_text))
                if boundary_pos < len(chunk_text):
                    # Recalculate chunk_end based on sentence boundary
                    chunk_text = chunk_text[:boundary_pos].rstrip()
                    chunk_words = chunk_text.split()
                    chunk_end = chunk_start + len(chunk_words)
            
            # Calculate overlap metadata
            overlap_start = current_pos - chunk_start if chunk_index > 0 else 0
            overlap_end = min(self.overlap, word_count - chunk_end) if chunk_end < word_count else 0
            
            # Create chunk
            chunk = TextChunk(
                content=chunk_text,
                chunk_index=chunk_index,
                total_chunks=0,  # Will be updated after all chunks are created
                word_count=len(chunk_words),
                overlap_start=overlap_start,
                overlap_end=overlap_end
            )
            chunks.append(chunk)
            
            logger.debug(
                "Created chunk",
                extra={
                    'chunk_index': chunk_index,
                    'chunk_word_count': len(chunk_words),
                    'overlap_start': overlap_start,
                    'overlap_end': overlap_end,
                    'chunk_start_pos': chunk_start,
                    'chunk_end_pos': chunk_end
                }
            )
            
            # Move to next chunk position
            current_pos = chunk_end
            chunk_index += 1
        
        # Update total_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total_chunks
        
        logger.info(
            "Chunking complete",
            extra={
                'total_chunks': total_chunks,
                'original_word_count': word_count,
                'avg_chunk_size': sum(c.word_count for c in chunks) // total_chunks if total_chunks > 0 else 0,
                'min_chunk_size': min(c.word_count for c in chunks) if chunks else 0,
                'max_chunk_size': max(c.word_count for c in chunks) if chunks else 0
            }
        )
        return chunks
    
    def _split_at_sentence_boundary(self, text: str, target_pos: int) -> int:
        """Find nearest sentence boundary to target position.
        
        This method searches for sentence-ending punctuation (., !, ?)
        near the target position to avoid splitting mid-sentence.
        
        Optimized version:
        - Uses pre-compiled regex pattern
        - Searches backwards from target for efficiency
        - Limits search window to 200 characters
        
        Args:
            text: Text to search for sentence boundary
            target_pos: Target position for split
            
        Returns:
            Position of sentence boundary, or target_pos if none found
        """
        if target_pos >= len(text):
            return len(text)
        
        # Search window: 200 characters before target position
        search_start = max(0, target_pos - 200)
        search_text = text[search_start:target_pos]
        
        # Find all sentence boundaries in search window using pre-compiled pattern
        matches = list(SENTENCE_BOUNDARY_PATTERN.finditer(search_text))
        
        if matches:
            # Use the last sentence boundary found
            last_match = matches[-1]
            boundary_pos = search_start + last_match.end()
            logger.debug(
                "Found sentence boundary",
                extra={
                    'boundary_position': boundary_pos,
                    'target_position': target_pos,
                    'distance_from_target': target_pos - boundary_pos
                }
            )
            return boundary_pos
        
        # No sentence boundary found, look for word boundary
        # Search backwards from target for a space
        for i in range(target_pos - 1, max(0, target_pos - 50), -1):
            if text[i].isspace():
                logger.debug(
                    "No sentence boundary, using word boundary",
                    extra={'boundary_position': i + 1, 'target_position': target_pos}
                )
                return i + 1
        
        # No good boundary found, use target position
        logger.debug(
            "No boundary found, using target position",
            extra={'target_position': target_pos}
        )
        return target_pos

    async def chunk_text_async(self, text: str) -> List[TextChunk]:
        """Async version of chunk_text for parallel processing.
        
        This method wraps chunk_text in an async context to allow
        parallel processing of multiple large texts (e.g., multiple meetings).
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of TextChunk objects with metadata
            
        Raises:
            ValueError: If text is empty or None
        """
        # Run chunking in thread pool to avoid blocking
        return await asyncio.to_thread(self.chunk_text, text)
    
    async def chunk_multiple_texts_async(
        self,
        texts: List[str]
    ) -> List[List[TextChunk]]:
        """Process multiple texts in parallel for improved performance.
        
        This method chunks multiple texts concurrently, which is useful
        when processing multiple large meetings simultaneously.
        
        Args:
            texts: List of texts to chunk
            
        Returns:
            List of chunk lists, one for each input text
            
        Example:
            >>> processor = ChunkProcessor()
            >>> texts = [meeting1.transcript, meeting2.transcript]
            >>> chunk_lists = await processor.chunk_multiple_texts_async(texts)
            >>> # chunk_lists[0] contains chunks for meeting1
            >>> # chunk_lists[1] contains chunks for meeting2
        """
        logger.info(
            "Processing multiple texts in parallel",
            extra={'text_count': len(texts)}
        )
        
        # Create tasks for parallel processing
        tasks = [self.chunk_text_async(text) for text in texts]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        chunk_lists = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "Error chunking text",
                    extra={'text_index': i, 'error': str(result)}
                )
                # Return single chunk with original text as fallback
                chunk_lists.append([TextChunk(
                    content=texts[i],
                    chunk_index=0,
                    total_chunks=1,
                    word_count=len(texts[i].split()),
                    overlap_start=0,
                    overlap_end=0
                )])
            else:
                chunk_lists.append(result)
        
        logger.info(
            "Parallel chunking complete",
            extra={
                'text_count': len(texts),
                'total_chunks': sum(len(chunks) for chunks in chunk_lists)
            }
        )
        
        return chunk_lists
