"""Unit tests for IngestionTracker service.

Tests cover:
- Thread safety with concurrent tracking
- Session expiration and cleanup
- Empty data handling
- Sample selection randomness
"""

import time
import threading
import pytest
from unittest.mock import patch

from app.services.ingestion_tracker import IngestionTracker
from app.models.request import Email, SlackMessage, Meeting
from app.models.chunk_models import TextChunk


class TestIngestionTrackerThreadSafety:
    """Test thread safety with concurrent tracking operations."""
    
    def test_concurrent_tracking_different_sessions(self):
        """Test concurrent tracking in different sessions is thread-safe."""
        tracker = IngestionTracker(sample_count=5)
        results = []
        errors = []
        
        def track_emails(session_id: str, count: int):
            """Track multiple emails in a session."""
            try:
                for i in range(count):
                    email = Email(
                        subject=f"Email {i}",
                        body=f"Body {i}",
                        sender=f"sender{i}@test.com",
                        date="2024-02-21"
                    )
                    tracker.track_email(session_id, email)
                results.append((session_id, count))
            except Exception as e:
                errors.append(e)
        
        # Create multiple sessions
        session1 = tracker.start_tracking()
        session2 = tracker.start_tracking()
        session3 = tracker.start_tracking()
        
        # Track concurrently
        threads = [
            threading.Thread(target=track_emails, args=(session1, 10)),
            threading.Thread(target=track_emails, args=(session2, 15)),
            threading.Thread(target=track_emails, args=(session3, 20)),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # Verify all sessions have correct counts
        summary1 = tracker.get_summary(session1)
        summary2 = tracker.get_summary(session2)
        summary3 = tracker.get_summary(session3)
        
        assert summary1.emails_used == 10
        assert summary2.emails_used == 15
        assert summary3.emails_used == 20
    
    def test_concurrent_tracking_same_session(self):
        """Test concurrent tracking in the same session is thread-safe."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        errors = []
        
        def track_mixed_sources():
            """Track different types of sources."""
            try:
                # Track email
                email = Email(
                    subject="Test",
                    body="Test body",
                    sender="test@test.com",
                    date="2024-02-21"
                )
                tracker.track_email(session_id, email)
                
                # Track Slack message
                slack = SlackMessage(
                    channel="#test",
                    user="testuser",
                    text="Test message",
                    timestamp="2024-02-21 10:00"
                )
                tracker.track_slack_message(session_id, slack)
                
                # Track meeting
                meeting = Meeting(
                    transcript="Test transcript",
                    topic="Test topic",
                    speakers=["Speaker1"],
                    timestamp="10:00"
                )
                tracker.track_meeting(session_id, meeting)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads tracking to same session
        threads = [threading.Thread(target=track_mixed_sources) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # Verify counts (5 threads * 1 of each type)
        summary = tracker.get_summary(session_id)
        assert summary.emails_used == 5
        assert summary.slack_messages_used == 5
        assert summary.meetings_used == 5
    
    def test_concurrent_session_creation(self):
        """Test concurrent session creation is thread-safe."""
        tracker = IngestionTracker(sample_count=5)
        session_ids = []
        errors = []
        lock = threading.Lock()
        
        def create_session():
            """Create a session and store its ID."""
            try:
                session_id = tracker.start_tracking()
                with lock:
                    session_ids.append(session_id)
            except Exception as e:
                errors.append(e)
        
        # Create sessions concurrently
        threads = [threading.Thread(target=create_session) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # Verify all session IDs are unique
        assert len(session_ids) == 10
        assert len(set(session_ids)) == 10


class TestIngestionTrackerSessionExpiration:
    """Test session expiration and cleanup."""
    
    def test_expired_sessions_cleaned_up(self):
        """Test that expired sessions are removed during cleanup."""
        # Use very short TTL for testing
        tracker = IngestionTracker(sample_count=5, session_ttl=1)
        
        # Create a session
        session1 = tracker.start_tracking()
        email = Email(
            subject="Test",
            body="Test body",
            sender="test@test.com",
            date="2024-02-21"
        )
        tracker.track_email(session1, email)
        
        # Verify session exists
        summary = tracker.get_summary(session1)
        assert summary.emails_used == 1
        
        # Wait for session to expire
        time.sleep(1.5)
        
        # Create new session to trigger cleanup
        session2 = tracker.start_tracking()
        
        # Verify old session is gone
        with pytest.raises(KeyError, match="not found"):
            tracker.get_summary(session1)
        
        # Verify new session still works
        tracker.track_email(session2, email)
        summary2 = tracker.get_summary(session2)
        assert summary2.emails_used == 1
    
    def test_active_sessions_not_cleaned_up(self):
        """Test that active sessions are not removed during cleanup."""
        tracker = IngestionTracker(sample_count=5, session_ttl=10)
        
        # Create sessions
        session1 = tracker.start_tracking()
        session2 = tracker.start_tracking()
        
        email = Email(
            subject="Test",
            body="Test body",
            sender="test@test.com",
            date="2024-02-21"
        )
        
        tracker.track_email(session1, email)
        tracker.track_email(session2, email)
        
        # Create another session to trigger cleanup
        session3 = tracker.start_tracking()
        
        # Verify all sessions still exist
        summary1 = tracker.get_summary(session1)
        summary2 = tracker.get_summary(session2)
        summary3 = tracker.get_summary(session3)
        
        assert summary1.emails_used == 1
        assert summary2.emails_used == 1
        assert summary3.emails_used == 0
    
    def test_cleanup_multiple_expired_sessions(self):
        """Test cleanup removes multiple expired sessions."""
        tracker = IngestionTracker(sample_count=5, session_ttl=1)
        
        # Create multiple sessions
        sessions = [tracker.start_tracking() for _ in range(5)]
        
        # Add data to each
        email = Email(
            subject="Test",
            body="Test body",
            sender="test@test.com",
            date="2024-02-21"
        )
        
        for session_id in sessions:
            tracker.track_email(session_id, email)
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Create new session to trigger cleanup
        new_session = tracker.start_tracking()
        
        # Verify all old sessions are gone
        for session_id in sessions:
            with pytest.raises(KeyError, match="not found"):
                tracker.get_summary(session_id)
        
        # Verify new session works
        tracker.track_email(new_session, email)
        summary = tracker.get_summary(new_session)
        assert summary.emails_used == 1


class TestIngestionTrackerEmptyData:
    """Test handling of empty data scenarios."""
    
    def test_empty_session_summary(self):
        """Test getting summary from session with no tracked data."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        # Get summary immediately without tracking anything
        summary = tracker.get_summary(session_id)
        
        assert summary.emails_used == 0
        assert summary.slack_messages_used == 0
        assert summary.meetings_used == 0
        assert summary.total_chunks_processed == 0
        assert summary.total_words_processed == 0
        assert summary.processing_time_seconds >= 0
        assert len(summary.sample_sources) == 0
    
    def test_track_empty_email_body(self):
        """Test tracking email with empty body."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        email = Email(
            subject="Empty email",
            body="",
            sender="test@test.com",
            date="2024-02-21"
        )
        
        tracker.track_email(session_id, email)
        summary = tracker.get_summary(session_id)
        
        assert summary.emails_used == 1
        assert summary.total_words_processed == 0
        assert len(summary.sample_sources) == 1
    
    def test_track_empty_slack_message(self):
        """Test tracking Slack message with empty text."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        message = SlackMessage(
            channel="#test",
            user="testuser",
            text="",
            timestamp="2024-02-21 10:00"
        )
        
        tracker.track_slack_message(session_id, message)
        summary = tracker.get_summary(session_id)
        
        assert summary.slack_messages_used == 1
        assert summary.total_words_processed == 0
        assert len(summary.sample_sources) == 1
    
    def test_track_empty_meeting_transcript(self):
        """Test tracking meeting with empty transcript."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        meeting = Meeting(
            transcript="",
            topic="Empty meeting",
            speakers=[],
            timestamp="10:00"
        )
        
        tracker.track_meeting(session_id, meeting)
        summary = tracker.get_summary(session_id)
        
        assert summary.meetings_used == 1
        assert summary.total_words_processed == 0
        assert len(summary.sample_sources) == 1
    
    def test_invalid_tracking_id(self):
        """Test tracking with non-existent session ID raises error."""
        tracker = IngestionTracker(sample_count=5)
        
        email = Email(
            subject="Test",
            body="Test body",
            sender="test@test.com",
            date="2024-02-21"
        )
        
        with pytest.raises(KeyError, match="not found"):
            tracker.track_email("invalid-id", email)
    
    def test_get_summary_invalid_id(self):
        """Test getting summary with non-existent session ID raises error."""
        tracker = IngestionTracker(sample_count=5)
        
        with pytest.raises(KeyError, match="not found"):
            tracker.get_summary("invalid-id")


class TestIngestionTrackerSampleSelection:
    """Test sample selection randomness and behavior."""
    
    def test_sample_selection_fewer_than_limit(self):
        """Test that all items are returned when fewer than sample_count."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        # Track only 3 items
        for i in range(3):
            email = Email(
                subject=f"Email {i}",
                body=f"Body {i}",
                sender=f"sender{i}@test.com",
                date="2024-02-21"
            )
            tracker.track_email(session_id, email)
        
        summary = tracker.get_summary(session_id)
        
        # Should return all 3 items
        assert len(summary.sample_sources) == 3
        assert all(s.type == "email" for s in summary.sample_sources)
    
    def test_sample_selection_exactly_limit(self):
        """Test that all items are returned when exactly sample_count."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        # Track exactly 5 items
        for i in range(5):
            email = Email(
                subject=f"Email {i}",
                body=f"Body {i}",
                sender=f"sender{i}@test.com",
                date="2024-02-21"
            )
            tracker.track_email(session_id, email)
        
        summary = tracker.get_summary(session_id)
        
        # Should return all 5 items
        assert len(summary.sample_sources) == 5
    
    def test_sample_selection_more_than_limit(self):
        """Test that sample_count items are returned when more available."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        # Track 10 items
        for i in range(10):
            email = Email(
                subject=f"Email {i}",
                body=f"Body {i}",
                sender=f"sender{i}@test.com",
                date="2024-02-21"
            )
            tracker.track_email(session_id, email)
        
        summary = tracker.get_summary(session_id)
        
        # Should return exactly 5 items
        assert len(summary.sample_sources) == 5
    
    def test_sample_selection_randomness(self):
        """Test that sample selection uses randomness."""
        tracker = IngestionTracker(sample_count=3)
        
        # Track 10 items in multiple sessions
        samples_collected = []
        
        for _ in range(5):
            session_id = tracker.start_tracking()
            
            for i in range(10):
                email = Email(
                    subject=f"Email {i}",
                    body=f"Body {i}",
                    sender=f"sender{i}@test.com",
                    date="2024-02-21"
                )
                tracker.track_email(session_id, email)
            
            summary = tracker.get_summary(session_id)
            
            # Extract subjects from samples
            subjects = [s.metadata["subject"] for s in summary.sample_sources]
            samples_collected.append(tuple(sorted(subjects)))
        
        # Verify we got different samples (at least 2 different combinations)
        unique_samples = set(samples_collected)
        assert len(unique_samples) >= 2, "Sample selection should be random"
    
    def test_sample_selection_mixed_types(self):
        """Test sample selection from mixed source types."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        # Track 2 emails
        for i in range(2):
            email = Email(
                subject=f"Email {i}",
                body=f"Body {i}",
                sender=f"sender{i}@test.com",
                date="2024-02-21"
            )
            tracker.track_email(session_id, email)
        
        # Track 2 Slack messages
        for i in range(2):
            message = SlackMessage(
                channel=f"#channel{i}",
                user=f"user{i}",
                text=f"Message {i}",
                timestamp="2024-02-21 10:00"
            )
            tracker.track_slack_message(session_id, message)
        
        # Track 2 meetings
        for i in range(2):
            meeting = Meeting(
                transcript=f"Transcript {i}",
                topic=f"Topic {i}",
                speakers=[f"Speaker{i}"],
                timestamp="10:00"
            )
            tracker.track_meeting(session_id, meeting)
        
        summary = tracker.get_summary(session_id)
        
        # Should return 5 samples (we have 6 total)
        assert len(summary.sample_sources) == 5
        
        # Verify we have mixed types
        types = [s.type for s in summary.sample_sources]
        assert "email" in types or "slack" in types or "meeting" in types
    
    def test_sample_metadata_completeness(self):
        """Test that sample metadata includes all required fields."""
        tracker = IngestionTracker(sample_count=5)
        session_id = tracker.start_tracking()
        
        # Track email
        email = Email(
            subject="Test Email",
            body="Test body",
            sender="test@test.com",
            date="2024-02-21"
        )
        tracker.track_email(session_id, email)
        
        # Track Slack message
        slack = SlackMessage(
            channel="#test",
            user="testuser",
            text="This is a test message with more than 50 characters to test preview truncation",
            timestamp="2024-02-21 10:00"
        )
        tracker.track_slack_message(session_id, slack)
        
        # Track meeting
        meeting = Meeting(
            transcript="Test transcript",
            topic="Test topic",
            speakers=["Speaker1", "Speaker2"],
            timestamp="10:00"
        )
        tracker.track_meeting(session_id, meeting)
        
        summary = tracker.get_summary(session_id)
        
        # Verify email sample metadata
        email_sample = next(s for s in summary.sample_sources if s.type == "email")
        assert "subject" in email_sample.metadata
        assert "date" in email_sample.metadata
        assert "sender" in email_sample.metadata
        assert email_sample.metadata["subject"] == "Test Email"
        
        # Verify Slack sample metadata
        slack_sample = next(s for s in summary.sample_sources if s.type == "slack")
        assert "channel" in slack_sample.metadata
        assert "user" in slack_sample.metadata
        assert "timestamp" in slack_sample.metadata
        assert "preview" in slack_sample.metadata
        assert len(slack_sample.metadata["preview"]) <= 53  # 50 chars + "..."
        assert slack_sample.metadata["preview"].endswith("...")
        
        # Verify meeting sample metadata
        meeting_sample = next(s for s in summary.sample_sources if s.type == "meeting")
        assert "timestamp" in meeting_sample.metadata
        assert "topic" in meeting_sample.metadata
        assert "speakers" in meeting_sample.metadata
        assert meeting_sample.metadata["speakers"] == ["Speaker1", "Speaker2"]
