"""Tests for async chunking functionality.

This module tests the async methods for parallel processing of multiple texts.
"""

import pytest
import asyncio
from app.services.chunk_processor import ChunkProcessor


class TestChunkProcessorAsync:
    """Test async chunking methods."""
    
    @pytest.mark.asyncio
    async def test_chunk_text_async(self):
        """Test async chunking of a single text."""
        processor = ChunkProcessor(threshold_words=3000)
        
        # Generate large text (5000 words)
        text = "Word " * 5000  # 5000 words
        
        # Chunk asynchronously
        chunks = await processor.chunk_text_async(text)
        
        # Verify results
        assert len(chunks) > 1
        assert all(chunk.word_count > 0 for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_chunk_multiple_texts_async(self):
        """Test parallel chunking of multiple texts."""
        processor = ChunkProcessor(threshold_words=3000)
        
        # Generate multiple large texts
        texts = [
            "Word " * 4000,  # 4000 words
            "Word " * 5000,  # 5000 words
            "Word " * 3500,  # 3500 words
        ]
        
        # Chunk all texts in parallel
        chunk_lists = await processor.chunk_multiple_texts_async(texts)
        
        # Verify results
        assert len(chunk_lists) == 3
        assert all(len(chunks) > 0 for chunks in chunk_lists)
        
        # All texts should have multiple chunks (all above threshold)
        for chunks in chunk_lists:
            assert len(chunks) > 1
    
    @pytest.mark.asyncio
    async def test_chunk_multiple_texts_async_with_error(self):
        """Test parallel chunking handles errors gracefully."""
        processor = ChunkProcessor(threshold_words=3000)
        
        # Include an empty text that will cause an error
        texts = [
            "Word " * 4000,  # Valid text
            "",  # This will cause an error
            "Word " * 5000,  # Valid text
        ]
        
        # Chunk all texts in parallel
        chunk_lists = await processor.chunk_multiple_texts_async(texts)
        
        # Verify results
        assert len(chunk_lists) == 3
        
        # First text should succeed
        assert len(chunk_lists[0]) > 0
        
        # Second text should have fallback single chunk
        assert len(chunk_lists[1]) == 1
        assert chunk_lists[1][0].content == ""
        
        # Third text should succeed
        assert len(chunk_lists[2]) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_processing_performance(self):
        """Test that parallel processing completes successfully."""
        processor = ChunkProcessor(threshold_words=3000)
        
        # Generate 5 large texts
        texts = ["Word " * 4000 for _ in range(5)]  # Each 4000 words
        
        # Test parallel processing completes
        chunk_lists = await processor.chunk_multiple_texts_async(texts)
        
        # Verify all texts were processed
        assert len(chunk_lists) == 5
        assert all(len(chunks) > 0 for chunks in chunk_lists)
        
        # Each should have multiple chunks
        for chunks in chunk_lists:
            assert len(chunks) > 1
        
        print(f"\nProcessed {len(texts)} texts in parallel")
        print(f"Total chunks generated: {sum(len(chunks) for chunks in chunk_lists)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
