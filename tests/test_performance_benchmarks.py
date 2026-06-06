"""Performance benchmarks for production features.

This module contains performance benchmarks to ensure the system meets
performance requirements specified in TR-7:
- Gemini API call: < 2 seconds (mocked)
- Chunking 10,000 words: < 1 second
- Tracking overhead: < 100ms
- Full request: < 5 seconds (excluding LLM)
"""

import time
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.gemini_service import GeminiService
from app.services.chunk_processor import ChunkProcessor
from app.services.ingestion_tracker import IngestionTracker
from app.models.request import Email, SlackMessage, Meeting


class TestPerformanceBenchmarks:
    """Performance benchmark tests for production features."""
    
    @pytest.mark.asyncio
    async def test_gemini_api_call_performance(self):
        """Benchmark: Gemini API call should complete in < 2 seconds (mocked).
        
        Requirements: TR-7
        """
        # Mock Gemini API response
        mock_response = Mock()
        mock_response.text = '''```json
{
  "scope": "MVP features only",
  "exclude_topics": ["marketing", "internal"],
  "priority_focus": "core functionality",
  "deadline_override": "June 2024"
}
```'''
        
        with patch('app.services.gemini_service.genai') as mock_genai:
            # Configure mock
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Initialize service
            service = GeminiService(api_key="test_key", timeout=10)
            
            # Benchmark
            start_time = time.time()
            result = await service.generate_constraints(
                "Focus on MVP features and ignore marketing discussions"
            )
            elapsed_time = time.time() - start_time
            
            # Assertions
            assert result is not None
            assert elapsed_time < 2.0, f"Gemini API call took {elapsed_time:.3f}s, expected < 2s"
            
            print(f"\n✓ Gemini API call: {elapsed_time:.3f}s (target: < 2s)")
    
    def test_chunking_10k_words_performance(self):
        """Benchmark: Chunking 10,000 words should complete in < 1 second.
        
        Requirements: TR-7
        """
        # Generate 10,000 word text
        # Use realistic text with sentences
        sentence = "This is a sample sentence for testing chunking performance. "
        words_per_sentence = len(sentence.split())
        sentences_needed = (10000 // words_per_sentence) + 1
        text = sentence * sentences_needed
        
        # Verify word count
        actual_word_count = len(text.split())
        assert actual_word_count >= 10000, f"Generated text has only {actual_word_count} words"
        
        # Initialize processor
        processor = ChunkProcessor(
            threshold_words=3000,
            chunk_size_min=1000,
            chunk_size_max=1500,
            overlap=100
        )
        
        # Benchmark
        start_time = time.time()
        chunks = processor.chunk_text(text)
        elapsed_time = time.time() - start_time
        
        # Assertions
        assert len(chunks) > 0
        assert elapsed_time < 1.0, f"Chunking took {elapsed_time:.3f}s, expected < 1s"
        
        print(f"\n✓ Chunking 10,000 words: {elapsed_time:.3f}s (target: < 1s)")
        print(f"  - Generated {len(chunks)} chunks")
        print(f"  - Average chunk size: {sum(c.word_count for c in chunks) // len(chunks)} words")
    
    def test_tracking_overhead_performance(self):
        """Benchmark: Tracking overhead should be < 100ms.
        
        Requirements: TR-7
        """
        # Initialize tracker
        tracker = IngestionTracker(sample_count=5)
        
        # Create test data
        emails = [
            Email(
                subject=f"Test email {i}",
                body="This is a test email body with some content. " * 10,
                sender=f"user{i}@example.com",
                date="2024-02-21"
            )
            for i in range(10)
        ]
        
        slack_messages = [
            SlackMessage(
                channel="#test-channel",
                user=f"user{i}",
                text="This is a test Slack message. " * 5,
                timestamp="2024-02-21T10:00:00Z"
            )
            for i in range(10)
        ]
        
        meetings = [
            Meeting(
                transcript="This is a test meeting transcript. " * 20,
                topic=f"Meeting {i}",
                speakers=["Speaker1", "Speaker2"],
                timestamp="2024-02-21T14:00:00Z"
            )
            for i in range(5)
        ]
        
        # Benchmark tracking operations
        start_time = time.time()
        
        # Start tracking
        tracking_id = tracker.start_tracking()
        
        # Track all items
        for email in emails:
            tracker.track_email(tracking_id, email)
        
        for message in slack_messages:
            tracker.track_slack_message(tracking_id, message)
        
        for meeting in meetings:
            tracker.track_meeting(tracking_id, meeting)
        
        # Get summary
        summary = tracker.get_summary(tracking_id)
        
        elapsed_time = time.time() - start_time
        
        # Assertions
        assert summary.emails_used == 10
        assert summary.slack_messages_used == 10
        assert summary.meetings_used == 5
        assert elapsed_time < 0.1, f"Tracking overhead was {elapsed_time:.3f}s, expected < 0.1s"
        
        print(f"\n✓ Tracking overhead: {elapsed_time * 1000:.1f}ms (target: < 100ms)")
        print(f"  - Tracked {summary.emails_used} emails, {summary.slack_messages_used} Slack messages, {summary.meetings_used} meetings")
    
    @pytest.mark.asyncio
    async def test_full_request_performance(self):
        """Benchmark: Full request should complete in < 5 seconds (excluding LLM).
        
        This test simulates a full request flow:
        1. Generate constraints (mocked Gemini)
        2. Apply constraints (filtering)
        3. Start tracking
        4. Process data sources
        5. Chunk large texts
        6. Track all sources
        7. Get summary
        
        Requirements: TR-7
        """
        # Mock Gemini API
        mock_response = Mock()
        mock_response.text = '''```json
{
  "scope": "MVP features",
  "exclude_topics": ["marketing"],
  "priority_focus": "core functionality",
  "deadline_override": ""
}
```'''
        
        with patch('app.services.gemini_service.genai') as mock_genai:
            # Configure mock
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Initialize services
            gemini_service = GeminiService(api_key="test_key", timeout=10)
            chunk_processor = ChunkProcessor()
            tracker = IngestionTracker(sample_count=5)
            
            # Create test data
            emails = [
                Email(
                    subject=f"Email {i}",
                    body="This is an email about MVP features. " * 20,
                    sender=f"user{i}@example.com",
                    date="2024-02-21"
                )
                for i in range(20)
            ]
            
            slack_messages = [
                SlackMessage(
                    channel="#project",
                    user=f"user{i}",
                    text="Discussion about core functionality. " * 10,
                    timestamp="2024-02-21T10:00:00Z"
                )
                for i in range(30)
            ]
            
            # Large meeting that needs chunking (5000 words)
            large_meeting = Meeting(
                transcript="This is a meeting transcript discussing MVP features and core functionality. " * 500,
                topic="Project Planning",
                speakers=["PM", "Tech Lead", "Designer"],
                timestamp="2024-02-21T14:00:00Z"
            )
            
            # Benchmark full flow
            start_time = time.time()
            
            # 1. Generate constraints
            constraints = await gemini_service.generate_constraints(
                "Focus on MVP features and ignore marketing"
            )
            
            # 2. Start tracking
            tracking_id = tracker.start_tracking()
            
            # 3. Track emails
            for email in emails:
                tracker.track_email(tracking_id, email)
            
            # 4. Track Slack messages
            for message in slack_messages:
                tracker.track_slack_message(tracking_id, message)
            
            # 5. Track meeting
            tracker.track_meeting(tracking_id, large_meeting)
            
            # 6. Check if meeting needs chunking
            if chunk_processor.needs_chunking(large_meeting.transcript):
                chunks = chunk_processor.chunk_text(large_meeting.transcript)
                for chunk in chunks:
                    tracker.track_chunk(tracking_id, chunk)
            
            # 7. Get summary
            summary = tracker.get_summary(tracking_id)
            
            elapsed_time = time.time() - start_time
            
            # Assertions
            assert constraints is not None
            assert summary.emails_used == 20
            assert summary.slack_messages_used == 30
            assert summary.meetings_used == 1
            assert summary.total_chunks_processed > 0
            assert elapsed_time < 5.0, f"Full request took {elapsed_time:.3f}s, expected < 5s"
            
            print(f"\n✓ Full request flow: {elapsed_time:.3f}s (target: < 5s)")
            print(f"  - Processed {summary.emails_used} emails")
            print(f"  - Processed {summary.slack_messages_used} Slack messages")
            print(f"  - Processed {summary.meetings_used} meetings")
            print(f"  - Generated {summary.total_chunks_processed} chunks")
            print(f"  - Total words: {summary.total_words_processed}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
