"""Profiling script for chunk processor performance.

This script profiles the chunking performance with various text sizes
to identify bottlenecks and measure optimization improvements.
"""

import time
import asyncio
import cProfile
import pstats
import io
from typing import List, Tuple
from app.services.chunk_processor import ChunkProcessor


def generate_test_text(word_count: int) -> str:
    """Generate test text with specified word count.
    
    Args:
        word_count: Number of words to generate
        
    Returns:
        Generated text with sentences
    """
    # Generate realistic sentences with punctuation
    sentence_templates = [
        "The project requirements include {} functionality.",
        "We need to implement {} by the deadline.",
        "The stakeholders discussed {} in the meeting.",
        "The technical team proposed {} as a solution.",
        "The client requested {} for the next phase.",
    ]
    
    words = []
    sentence_idx = 0
    
    while len(words) < word_count:
        template = sentence_templates[sentence_idx % len(sentence_templates)]
        filler = f"feature{sentence_idx} and component{sentence_idx}"
        sentence = template.format(filler)
        words.extend(sentence.split())
        sentence_idx += 1
    
    return ' '.join(words[:word_count])


def profile_chunking_sync(processor: ChunkProcessor, text: str) -> Tuple[float, int]:
    """Profile synchronous chunking.
    
    Args:
        processor: ChunkProcessor instance
        text: Text to chunk
        
    Returns:
        Tuple of (execution_time, chunk_count)
    """
    start_time = time.perf_counter()
    chunks = processor.chunk_text(text)
    end_time = time.perf_counter()
    
    return end_time - start_time, len(chunks)


async def profile_chunking_async(processor: ChunkProcessor, texts: List[str]) -> Tuple[float, int]:
    """Profile asynchronous chunking of multiple texts.
    
    Args:
        processor: ChunkProcessor instance
        texts: List of texts to chunk
        
    Returns:
        Tuple of (execution_time, total_chunk_count)
    """
    start_time = time.perf_counter()
    chunk_lists = await processor.chunk_multiple_texts_async(texts)
    end_time = time.perf_counter()
    
    total_chunks = sum(len(chunks) for chunks in chunk_lists)
    return end_time - start_time, total_chunks


def run_profiling():
    """Run comprehensive profiling tests."""
    processor = ChunkProcessor()
    
    print("=" * 80)
    print("CHUNK PROCESSOR PERFORMANCE PROFILING")
    print("=" * 80)
    print()
    
    # Test 1: Single text - 10,000 words
    print("Test 1: Single text - 10,000 words")
    print("-" * 80)
    text_10k = generate_test_text(10000)
    exec_time, chunk_count = profile_chunking_sync(processor, text_10k)
    print(f"Execution time: {exec_time:.4f} seconds")
    print(f"Chunks created: {chunk_count}")
    print(f"Words per second: {10000 / exec_time:.0f}")
    print(f"✓ PASS" if exec_time < 1.0 else f"✗ FAIL (target: < 1.0s)")
    print()
    
    # Test 2: Single text - 50,000 words
    print("Test 2: Single text - 50,000 words")
    print("-" * 80)
    text_50k = generate_test_text(50000)
    exec_time, chunk_count = profile_chunking_sync(processor, text_50k)
    print(f"Execution time: {exec_time:.4f} seconds")
    print(f"Chunks created: {chunk_count}")
    print(f"Words per second: {50000 / exec_time:.0f}")
    print(f"✓ PASS" if exec_time < 5.0 else f"✗ FAIL (target: < 5.0s)")
    print()
    
    # Test 3: Multiple texts - async processing
    print("Test 3: Multiple texts (5 x 10,000 words) - Async")
    print("-" * 80)
    texts_multiple = [generate_test_text(10000) for _ in range(5)]
    exec_time, total_chunks = asyncio.run(profile_chunking_async(processor, texts_multiple))
    print(f"Execution time: {exec_time:.4f} seconds")
    print(f"Total chunks created: {total_chunks}")
    print(f"Words per second: {50000 / exec_time:.0f}")
    print(f"Speedup vs sequential: {(5 * 1.0) / exec_time:.2f}x (estimated)")
    print()
    
    # Test 4: Detailed profiling with cProfile
    print("Test 4: Detailed profiling (10,000 words)")
    print("-" * 80)
    profiler = cProfile.Profile()
    profiler.enable()
    
    text_profile = generate_test_text(10000)
    processor.chunk_text(text_profile)
    
    profiler.disable()
    
    # Print top 20 time-consuming functions
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())
    
    # Test 5: Sentence boundary detection performance
    print("Test 5: Sentence boundary detection")
    print("-" * 80)
    test_text = generate_test_text(1500)
    iterations = 1000
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        processor._split_at_sentence_boundary(test_text, len(test_text) - 100)
    end_time = time.perf_counter()
    
    avg_time = (end_time - start_time) / iterations
    print(f"Average time per call: {avg_time * 1000:.4f} ms")
    print(f"Calls per second: {iterations / (end_time - start_time):.0f}")
    print()
    
    print("=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_profiling()
