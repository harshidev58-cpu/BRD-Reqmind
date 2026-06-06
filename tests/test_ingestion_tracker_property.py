"""Property-based tests for IngestionTracker.

This module contains property-based tests using Hypothesis to verify
universal correctness properties of the IngestionTracker.
"""

import pytest
from hypothesis import given, strategies as st, settings
from app.services.ingestion_tracker import IngestionTracker
from app.models.request import Email, SlackMessage, Meeting
from app.models.chunk_models import TextChunk


# Strategy for generating Email objects
@st.composite
def email_strategy(draw):
    """Generate random Email objects."""
    subject = draw(st.text(min_size=1, max_size=100))
    body = draw(st.text(min_size=1, max_size=500))
    sender = draw(st.text(min_size=0, max_size=50))
    date = draw(st.text(min_size=0, max_size=20))
    return Email(subject=subject, body=body, sender=sender, date=date)


# Strategy for generating SlackMessage objects
@st.composite
def slack_message_strategy(draw):
    """Generate random SlackMessage objects."""
    channel = draw(st.text(min_size=1, max_size=50))
    user = draw(st.text(min_size=1, max_size=50))
    text = draw(st.text(min_size=1, max_size=500))
    timestamp = draw(st.text(min_size=0, max_size=20))
    return SlackMessage(channel=channel, user=user, text=text, timestamp=timestamp)


# Strategy for generating Meeting objects
@st.composite
def meeting_strategy(draw):
    """Generate random Meeting objects."""
    transcript = draw(st.text(min_size=1, max_size=1000))
    topic = draw(st.text(min_size=0, max_size=100))
    speakers = draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5))
    timestamp = draw(st.text(min_size=0, max_size=20))
    return Meeting(transcript=transcript, topic=topic, speakers=speakers, timestamp=timestamp)


# Strategy for generating TextChunk objects
@st.composite
def text_chunk_strategy(draw):
    """Generate random TextChunk objects."""
    content = draw(st.text(min_size=1, max_size=500))
    chunk_index = draw(st.integers(min_value=0, max_value=10))
    total_chunks = draw(st.integers(min_value=chunk_index + 1, max_value=20))
    word_count = len(content.split())
    overlap_start = draw(st.integers(min_value=0, max_value=100))
    overlap_end = draw(st.integers(min_value=0, max_value=100))
    return TextChunk(
        content=content,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        word_count=word_count,
        overlap_start=overlap_start,
        overlap_end=overlap_end
    )


@given(
    emails=st.lists(email_strategy(), min_size=0, max_size=20),
    slack_messages=st.lists(slack_message_strategy(), min_size=0, max_size=20),
    meetings=st.lists(meeting_strategy(), min_size=0, max_size=20),
    chunks=st.lists(text_chunk_strategy(), min_size=0, max_size=20)
)
@settings(max_examples=100, deadline=None)
def test_property_source_counting_accuracy(emails, slack_messages, meetings, chunks):
    """Property 13: Source counting accuracy.
    
    Feature: production-features, Property 13: Source counting accuracy
    Validates: Requirements 3.1.1, 3.1.2, 3.1.3, 3.1.4
    
    For any processing session, the counts in the ingestion summary
    (emails_used, slack_messages_used, meetings_used, total_chunks_processed)
    should exactly match the number of items actually processed.
    
    This property test verifies that:
    1. Email count matches actual emails tracked
    2. Slack message count matches actual messages tracked
    3. Meeting count matches actual meetings tracked
    4. Chunk count matches actual chunks tracked
    5. All counts are accurate regardless of input size
    """
    # Initialize tracker
    tracker = IngestionTracker(sample_count=5)
    
    # Start tracking session
    tracking_id = tracker.start_tracking()
    
    # Track all emails
    for email in emails:
        tracker.track_email(tracking_id, email)
    
    # Track all Slack messages
    for message in slack_messages:
        tracker.track_slack_message(tracking_id, message)
    
    # Track all meetings
    for meeting in meetings:
        tracker.track_meeting(tracking_id, meeting)
    
    # Track all chunks
    for chunk in chunks:
        tracker.track_chunk(tracking_id, chunk)
    
    # Get summary
    summary = tracker.get_summary(tracking_id)
    
    # Property: Email count must match exactly
    assert summary.emails_used == len(emails), \
        f"Expected {len(emails)} emails, but summary shows {summary.emails_used}"
    
    # Property: Slack message count must match exactly
    assert summary.slack_messages_used == len(slack_messages), \
        f"Expected {len(slack_messages)} slack messages, but summary shows {summary.slack_messages_used}"
    
    # Property: Meeting count must match exactly
    assert summary.meetings_used == len(meetings), \
        f"Expected {len(meetings)} meetings, but summary shows {summary.meetings_used}"
    
    # Property: Chunk count must match exactly
    assert summary.total_chunks_processed == len(chunks), \
        f"Expected {len(chunks)} chunks, but summary shows {summary.total_chunks_processed}"
    
    # Property: Total words should be sum of all text content
    expected_words = 0
    for email in emails:
        expected_words += len(email.body.split())
    for message in slack_messages:
        expected_words += len(message.text.split())
    for meeting in meetings:
        expected_words += len(meeting.transcript.split())
    
    assert summary.total_words_processed == expected_words, \
        f"Expected {expected_words} total words, but summary shows {summary.total_words_processed}"
    
    # Property: Processing time should be non-negative
    assert summary.processing_time_seconds >= 0, \
        f"Processing time should be non-negative, got {summary.processing_time_seconds}"
    
    # Property: Sample sources should not exceed total sources
    total_sources = len(emails) + len(slack_messages) + len(meetings)
    assert len(summary.sample_sources) <= total_sources, \
        f"Sample sources ({len(summary.sample_sources)}) exceeds total sources ({total_sources})"
    
    # Property: Sample sources should not exceed configured sample count
    assert len(summary.sample_sources) <= tracker.sample_count, \
        f"Sample sources ({len(summary.sample_sources)}) exceeds sample count ({tracker.sample_count})"


@given(
    emails=st.lists(email_strategy(), min_size=0, max_size=30),
    slack_messages=st.lists(slack_message_strategy(), min_size=0, max_size=30),
    meetings=st.lists(meeting_strategy(), min_size=0, max_size=30),
    sample_count=st.integers(min_value=3, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_property_sample_size_bounds(emails, slack_messages, meetings, sample_count):
    """Property 14: Sample size bounds.
    
    Feature: production-features, Property 14: Sample size bounds
    Validates: Requirements 3.2.1
    
    For any tracking session with at least sample_count sources, the sample_sources
    list should contain exactly sample_count items; for sessions with fewer sources,
    it should contain all available sources.
    
    This property test verifies that:
    1. When total sources >= sample_count, samples = sample_count
    2. When total sources < sample_count, samples = total sources
    3. Sample size is always within bounds [0, sample_count]
    4. Sample size never exceeds total available sources
    """
    # Initialize tracker with the generated sample_count
    tracker = IngestionTracker(sample_count=sample_count)
    
    # Start tracking session
    tracking_id = tracker.start_tracking()
    
    # Track all emails
    for email in emails:
        tracker.track_email(tracking_id, email)
    
    # Track all Slack messages
    for message in slack_messages:
        tracker.track_slack_message(tracking_id, message)
    
    # Track all meetings
    for meeting in meetings:
        tracker.track_meeting(tracking_id, meeting)
    
    # Get summary
    summary = tracker.get_summary(tracking_id)
    
    # Calculate total sources (chunks are not included in samples)
    total_sources = len(emails) + len(slack_messages) + len(meetings)
    
    # Property: Sample size should be min(total_sources, sample_count)
    expected_sample_size = min(total_sources, sample_count)
    actual_sample_size = len(summary.sample_sources)
    
    assert actual_sample_size == expected_sample_size, \
        f"Expected {expected_sample_size} samples (total={total_sources}, sample_count={sample_count}), " \
        f"but got {actual_sample_size}"
    
    # Property: Sample size should never exceed sample_count
    assert actual_sample_size <= sample_count, \
        f"Sample size ({actual_sample_size}) exceeds configured sample_count ({sample_count})"
    
    # Property: Sample size should never exceed total sources
    assert actual_sample_size <= total_sources, \
        f"Sample size ({actual_sample_size}) exceeds total sources ({total_sources})"
    
    # Property: When total sources >= sample_count, should have exactly sample_count samples
    if total_sources >= sample_count:
        assert actual_sample_size == sample_count, \
            f"With {total_sources} sources and sample_count={sample_count}, " \
            f"expected exactly {sample_count} samples, got {actual_sample_size}"
    
    # Property: When total sources < sample_count, should have all sources as samples
    if total_sources < sample_count:
        assert actual_sample_size == total_sources, \
            f"With {total_sources} sources and sample_count={sample_count}, " \
            f"expected all {total_sources} sources as samples, got {actual_sample_size}"
    
    # Property: Sample size should be non-negative
    assert actual_sample_size >= 0, \
        f"Sample size should be non-negative, got {actual_sample_size}"


@given(
    emails=st.lists(email_strategy(), min_size=0, max_size=20),
    slack_messages=st.lists(slack_message_strategy(), min_size=0, max_size=20),
    meetings=st.lists(meeting_strategy(), min_size=0, max_size=20)
)
@settings(max_examples=100, deadline=None)
def test_property_sample_metadata_completeness(emails, slack_messages, meetings):
    """Property 15: Sample metadata completeness.
    
    Feature: production-features, Property 15: Sample metadata completeness
    Validates: Requirements 3.2.2, 3.2.3, 3.2.4
    
    For any sample source in the ingestion summary, it should include all
    required metadata fields for its type:
    - Email samples: subject, date, sender
    - Meeting samples: timestamp, topic, speakers
    - Slack samples: channel, user, timestamp, preview
    
    This property test verifies that:
    1. All email samples have subject, date, and sender fields
    2. All meeting samples have timestamp, topic, and speakers fields
    3. All slack samples have channel, user, timestamp, and preview fields
    4. Metadata fields are present regardless of whether they're empty
    5. All samples have the correct type field
    """
    # Initialize tracker
    tracker = IngestionTracker(sample_count=5)
    
    # Start tracking session
    tracking_id = tracker.start_tracking()
    
    # Track all emails
    for email in emails:
        tracker.track_email(tracking_id, email)
    
    # Track all Slack messages
    for message in slack_messages:
        tracker.track_slack_message(tracking_id, message)
    
    # Track all meetings
    for meeting in meetings:
        tracker.track_meeting(tracking_id, meeting)
    
    # Get summary
    summary = tracker.get_summary(tracking_id)
    
    # Verify each sample has complete metadata for its type
    for sample in summary.sample_sources:
        # Property: Sample must have a valid type
        assert sample.type in ["email", "slack", "meeting"], \
            f"Sample has invalid type: {sample.type}"
        
        # Property: Sample must have metadata dictionary
        assert isinstance(sample.metadata, dict), \
            f"Sample metadata should be a dict, got {type(sample.metadata)}"
        
        # Property: Email samples must have required fields
        if sample.type == "email":
            required_fields = ["subject", "date", "sender"]
            for field in required_fields:
                assert field in sample.metadata, \
                    f"Email sample missing required field '{field}'. " \
                    f"Available fields: {list(sample.metadata.keys())}"
                
                # Field can be empty string but must exist
                assert sample.metadata[field] is not None, \
                    f"Email sample field '{field}' should not be None"
        
        # Property: Meeting samples must have required fields
        elif sample.type == "meeting":
            required_fields = ["timestamp", "topic", "speakers"]
            for field in required_fields:
                assert field in sample.metadata, \
                    f"Meeting sample missing required field '{field}'. " \
                    f"Available fields: {list(sample.metadata.keys())}"
                
                # Field can be empty but must exist
                assert sample.metadata[field] is not None, \
                    f"Meeting sample field '{field}' should not be None"
            
            # Property: speakers should be a list
            assert isinstance(sample.metadata["speakers"], list), \
                f"Meeting speakers should be a list, got {type(sample.metadata['speakers'])}"
        
        # Property: Slack samples must have required fields
        elif sample.type == "slack":
            required_fields = ["channel", "user", "timestamp", "preview"]
            for field in required_fields:
                assert field in sample.metadata, \
                    f"Slack sample missing required field '{field}'. " \
                    f"Available fields: {list(sample.metadata.keys())}"
                
                # Field can be empty string but must exist
                assert sample.metadata[field] is not None, \
                    f"Slack sample field '{field}' should not be None"
            
            # Property: preview should be a string
            assert isinstance(sample.metadata["preview"], str), \
                f"Slack preview should be a string, got {type(sample.metadata['preview'])}"
    
    # Property: If there are samples, they should match tracked sources
    if len(summary.sample_sources) > 0:
        total_sources = len(emails) + len(slack_messages) + len(meetings)
        assert total_sources > 0, \
            "If there are samples, there must be tracked sources"
        
        # Count samples by type
        email_samples = sum(1 for s in summary.sample_sources if s.type == "email")
        slack_samples = sum(1 for s in summary.sample_sources if s.type == "slack")
        meeting_samples = sum(1 for s in summary.sample_sources if s.type == "meeting")
        
        # Property: Sample counts should not exceed actual source counts
        assert email_samples <= len(emails), \
            f"Email samples ({email_samples}) exceed actual emails ({len(emails)})"
        assert slack_samples <= len(slack_messages), \
            f"Slack samples ({slack_samples}) exceed actual messages ({len(slack_messages)})"
        assert meeting_samples <= len(meetings), \
            f"Meeting samples ({meeting_samples}) exceed actual meetings ({len(meetings)})"
