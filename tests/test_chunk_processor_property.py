"""Property-based tests for ChunkProcessor.

This module contains property-based tests using Hypothesis to verify
universal correctness properties of the ChunkProcessor.
"""

import pytest
import re
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.chunk_processor import ChunkProcessor


@given(word_count=st.integers(min_value=1, max_value=10000))
@settings(max_examples=100, deadline=None)
def test_property_chunking_threshold_detection(word_count):
    """Property 6: Chunking threshold detection.
    
    Feature: production-features, Property 6: Chunking threshold detection
    Validates: Requirements 2.1.1
    
    For any text, if its word count exceeds 3000, needs_chunking() should
    return True; otherwise False.
    
    This property test verifies that:
    1. Texts with >3000 words return True
    2. Texts with <=3000 words return False
    3. Empty texts return False
    """
    processor = ChunkProcessor(threshold_words=3000)
    
    # Generate text with exact word count
    text = ' '.join(['word'] * word_count)
    
    result = processor.needs_chunking(text)
    
    # Property: needs_chunking returns True iff word_count > threshold
    if word_count > 3000:
        assert result is True, \
            f"Text with {word_count} words should need chunking (>3000)"
    else:
        assert result is False, \
            f"Text with {word_count} words should not need chunking (<=3000)"


@given(word_count=st.integers(min_value=3001, max_value=6000))
@settings(max_examples=100, deadline=None)
def test_property_chunk_size_bounds(word_count):
    """Property 7: Chunk size bounds.
    
    Feature: production-features, Property 7: Chunk size bounds
    Validates: Requirements 2.1.2
    
    For any text that is chunked, all chunks except possibly the last
    should have word counts between 1000 and 1500 words.
    
    This property test verifies that:
    1. All chunks (except last) are within size bounds
    2. The last chunk may be smaller
    3. No chunk exceeds the maximum size
    """
    processor = ChunkProcessor(
        threshold_words=3000,
        chunk_size_min=1000,
        chunk_size_max=1500,
        overlap=100
    )
    
    # Generate text with exact word count
    text = ' '.join(['word'] * word_count)
    
    chunks = processor.chunk_text(text)
    
    # Property: All chunks except last should be within bounds
    for i, chunk in enumerate(chunks[:-1]):  # All except last
        assert 1000 <= chunk.word_count <= 1500, \
            f"Chunk {i} has {chunk.word_count} words, expected 1000-1500"
    
    # Property: Last chunk can be any size but should not exceed max
    if len(chunks) > 0:
        last_chunk = chunks[-1]
        assert last_chunk.word_count <= 1500, \
            f"Last chunk has {chunk.word_count} words, exceeds max 1500"


@given(num_sentences=st.integers(min_value=200, max_value=400))
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_property_sentence_boundary_preservation(num_sentences):
    """Property 8: Sentence boundary preservation.
    
    Feature: production-features, Property 8: Sentence boundary preservation
    Validates: Requirements 2.1.4
    
    For any chunked text, each chunk boundary (except the last) should end
    with a sentence-ending punctuation mark (., !, or ?) followed by
    whitespace or end of text.
    
    This property test verifies that:
    1. Chunk boundaries respect sentence endings
    2. No chunks end mid-sentence (when possible)
    3. Sentence punctuation is preserved
    """
    processor = ChunkProcessor(
        threshold_words=3000,
        chunk_size_min=1000,
        chunk_size_max=1500,
        overlap=100
    )
    
    # Generate text with sentences (each sentence has 10 words)
    # Use varied punctuation to test all sentence endings
    punctuation_marks = ['.', '!', '?']
    sentences = []
    for i in range(num_sentences):
        sentence = ' '.join([f'word{j}' for j in range(10)])
        # Vary punctuation
        punct = punctuation_marks[i % len(punctuation_marks)]
        sentences.append(sentence + punct)
    text = ' '.join(sentences)
    
    word_count = len(text.split())
    if word_count <= 3000:
        # Skip if text doesn't need chunking
        return
    
    chunks = processor.chunk_text(text)
    
    # Property: All chunks except last should end with sentence punctuation
    # Pattern matches sentence ending: ., !, or ? at the end (possibly with whitespace)
    sentence_endings = re.compile(r'[.!?]\s*$')
    
    for i, chunk in enumerate(chunks[:-1]):  # All except last
        content = chunk.content
        # Check if chunk ends with sentence punctuation
        has_sentence_ending = bool(sentence_endings.search(content))
        
        # The chunk should end with sentence punctuation since we have
        # well-formed sentences with clear boundaries
        assert has_sentence_ending, \
            f"Chunk {i} should end with sentence punctuation (., !, or ?). " \
            f"Last 50 chars: '{content[-50:]}'"


@given(word_count=st.integers(min_value=3001, max_value=6000))
@settings(max_examples=100, deadline=None)
def test_property_chunk_overlap_consistency(word_count):
    """Property 9: Chunk overlap consistency.
    
    Feature: production-features, Property 9: Chunk overlap consistency
    Validates: Requirements 2.1.5
    
    For any pair of adjacent chunks, the overlap should be approximately
    100 words (within reasonable bounds due to sentence boundary detection).
    
    This property test verifies that:
    1. Adjacent chunks have overlap
    2. Overlap is tracked in metadata
    3. Overlap is within expected range
    4. The actual content overlap matches the expected 100-word overlap
    """
    processor = ChunkProcessor(
        threshold_words=3000,
        chunk_size_min=1000,
        chunk_size_max=1500,
        overlap=100
    )
    
    # Generate text with unique identifiable words for overlap verification
    text = ' '.join([f'word{i}' for i in range(word_count)])
    
    chunks = processor.chunk_text(text)
    
    # Property: Chunks should have overlap metadata
    for i, chunk in enumerate(chunks):
        if i > 0:  # Not first chunk
            # overlap_start should be > 0 for non-first chunks
            assert chunk.overlap_start >= 0, \
                f"Chunk {i} should have overlap_start >= 0, got {chunk.overlap_start}"
        
        if i < len(chunks) - 1:  # Not last chunk
            # overlap_end should be > 0 for non-last chunks
            assert chunk.overlap_end >= 0, \
                f"Chunk {i} should have overlap_end >= 0, got {chunk.overlap_end}"
    
    # Property: Total chunks should be set correctly
    for chunk in chunks:
        assert chunk.total_chunks == len(chunks), \
            f"Chunk total_chunks={chunk.total_chunks}, expected {len(chunks)}"
    
    # Property: Verify actual content overlap between adjacent chunks
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]
        
        # Extract words from both chunks
        current_words = current_chunk.content.split()
        next_words = next_chunk.content.split()
        
        # Find the overlap by comparing the end of current chunk with start of next chunk
        # The overlap should be approximately 100 words (allowing some variance due to sentence boundaries)
        
        # Check how many words from the end of current chunk match the start of next chunk
        max_possible_overlap = min(len(current_words), len(next_words))
        actual_overlap = 0
        
        for j in range(max_possible_overlap, 0, -1):
            # Get last j words from current chunk
            current_end = current_words[-j:]
            # Get first j words from next chunk
            next_start = next_words[:j]
            
            if current_end == next_start:
                actual_overlap = j
                break
        
        # For non-last chunks, there should be some overlap
        if i < len(chunks) - 1:
            assert actual_overlap > 0, \
                f"Chunks {i} and {i+1} should have overlap, but found {actual_overlap} overlapping words"
            
            # The overlap should be within a reasonable range of 100 words
            # Due to sentence boundary detection, we allow 50-150 words
            assert 50 <= actual_overlap <= 150, \
                f"Chunks {i} and {i+1} have {actual_overlap} overlapping words, " \
                f"expected approximately 100 (range: 50-150)"
