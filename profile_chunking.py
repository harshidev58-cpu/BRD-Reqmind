"""Profiling script for chunking performance analysis.

This script profiles the chunk_text method to identify performance bottlenecks
and measure the impact of optimizations.
"""

import cProfile
import pstats
import io
from app.services.chunk_processor import ChunkProcessor


def profile_chunking():
    """Profile chunking performance with various text sizes."""
    
    # Generate test texts of different sizes
    sentence = "This is a sample sentence for testing chunking performance. "
    
    test_cases = [
        ("5K words", 5000),
        ("10K words", 10000),
        ("20K words", 20000),
        ("50K words", 50000),
    ]
    
    processor = ChunkProcessor(
        threshold_words=3000,
        chunk_size_min=1000,
        chunk_size_max=1500,
        overlap=100
    )
    
    for name, word_count in test_cases:
        # Generate text
        words_per_sentence = len(sentence.split())
        sentences_needed = (word_count // words_per_sentence) + 1
        text = sentence * sentences_needed
        
        print(f"\n{'='*60}")
        print(f"Profiling: {name}")
        print(f"{'='*60}")
        
        # Profile
        profiler = cProfile.Profile()
        profiler.enable()
        
        chunks = processor.chunk_text(text)
        
        profiler.disable()
        
        # Print results
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions
        
        print(s.getvalue())
        print(f"\nGenerated {len(chunks)} chunks")
        print(f"Average chunk size: {sum(c.word_count for c in chunks) // len(chunks)} words")


if __name__ == "__main__":
    profile_chunking()
