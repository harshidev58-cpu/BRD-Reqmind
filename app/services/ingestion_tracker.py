"""Ingestion tracking service for transparency and explainability.

This module provides the IngestionTracker class for tracking data sources
and processing metrics during BRD generation.
"""

import time
import uuid
import random
import threading
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from app.models.ingestion_summary import IngestionSummary, SampleSource
from app.models.request import Email, SlackMessage, Meeting
from app.models.chunk_models import TextChunk

logger = logging.getLogger(__name__)


class TrackingSession:
    """Internal class to store tracking data for a session.
    
    Attributes:
        tracking_id: Unique identifier for the session
        start_time: When tracking started
        emails: List of tracked emails
        slack_messages: List of tracked Slack messages
        meetings: List of tracked meetings
        chunks: List of tracked chunks
        total_words: Total word count across all sources
    """
    
    def __init__(self, tracking_id: str):
        """Initialize a new tracking session.
        
        Args:
            tracking_id: Unique identifier for this session
        """
        self.tracking_id = tracking_id
        self.start_time = time.time()
        self.emails: List[Email] = []
        self.slack_messages: List[SlackMessage] = []
        self.meetings: List[Meeting] = []
        self.chunks: List[TextChunk] = []
        self.total_words = 0


class IngestionTracker:
    """Service for tracking data sources and processing metrics.
    
    Provides thread-safe tracking of emails, Slack messages, meetings,
    and text chunks during BRD generation. Generates ingestion summaries
    with counts, samples, and processing metrics.
    
    Attributes:
        sample_count: Number of sample sources to include in summary
        session_ttl: Time-to-live for tracking sessions in seconds
    """
    
    def __init__(self, sample_count: int = 5, session_ttl: int = 3600):
        """Initialize the ingestion tracker.
        
        Args:
            sample_count: Number of sample sources to include (default: 5)
            session_ttl: Session expiration time in seconds (default: 3600 = 1 hour)
        """
        self.sample_count = sample_count
        self.session_ttl = session_ttl
        self._sessions: Dict[str, TrackingSession] = {}
        self._lock = threading.Lock()
        
        logger.info(
            "IngestionTracker initialized",
            extra={
                'sample_count': sample_count,
                'session_ttl_seconds': session_ttl
            }
        )
    
    def start_tracking(self) -> str:
        """Start a new tracking session.
        
        Creates a new tracking session with a unique ID and initializes
        tracking data structures.
        
        Returns:
            str: Unique tracking ID for this session
        """
        tracking_id = str(uuid.uuid4())
        
        with self._lock:
            session = TrackingSession(tracking_id)
            self._sessions[tracking_id] = session
            
            # Clean up expired sessions
            self._cleanup_expired_sessions()
        
        logger.info(
            "Started tracking session",
            extra={'tracking_id': tracking_id}
        )
        
        return tracking_id
    
    def track_email(self, tracking_id: str, email: Email) -> None:
        """Track an email being processed.
        
        Args:
            tracking_id: ID of the tracking session
            email: Email object to track
            
        Raises:
            KeyError: If tracking_id is not found
        """
        with self._lock:
            if tracking_id not in self._sessions:
                raise KeyError(f"Tracking session {tracking_id} not found")
            
            session = self._sessions[tracking_id]
            session.emails.append(email)
            
            # Count words in email body
            word_count = len(email.body.split())
            session.total_words += word_count
            
            logger.debug(
                "Tracked email",
                extra={
                    'tracking_id': tracking_id,
                    'email_subject': email.subject[:50] if email.subject else 'N/A',
                    'word_count': word_count,
                    'total_emails': len(session.emails)
                }
            )
    
    def track_slack_message(self, tracking_id: str, message: SlackMessage) -> None:
        """Track a Slack message being processed.
        
        Args:
            tracking_id: ID of the tracking session
            message: SlackMessage object to track
            
        Raises:
            KeyError: If tracking_id is not found
        """
        with self._lock:
            if tracking_id not in self._sessions:
                raise KeyError(f"Tracking session {tracking_id} not found")
            
            session = self._sessions[tracking_id]
            session.slack_messages.append(message)
            
            # Count words in message text
            word_count = len(message.text.split())
            session.total_words += word_count
            
            logger.debug(
                "Tracked Slack message",
                extra={
                    'tracking_id': tracking_id,
                    'channel': message.channel,
                    'word_count': word_count,
                    'total_slack_messages': len(session.slack_messages)
                }
            )
    
    def track_meeting(self, tracking_id: str, meeting: Meeting) -> None:
        """Track a meeting being processed.
        
        Args:
            tracking_id: ID of the tracking session
            meeting: Meeting object to track
            
        Raises:
            KeyError: If tracking_id is not found
        """
        with self._lock:
            if tracking_id not in self._sessions:
                raise KeyError(f"Tracking session {tracking_id} not found")
            
            session = self._sessions[tracking_id]
            session.meetings.append(meeting)
            
            # Count words in meeting transcript
            word_count = len(meeting.transcript.split())
            session.total_words += word_count
            
            logger.debug(
                "Tracked meeting",
                extra={
                    'tracking_id': tracking_id,
                    'meeting_topic': meeting.topic[:50] if meeting.topic else 'N/A',
                    'word_count': word_count,
                    'total_meetings': len(session.meetings)
                }
            )
    
    def track_chunk(self, tracking_id: str, chunk: TextChunk) -> None:
        """Track a text chunk being processed.
        
        Args:
            tracking_id: ID of the tracking session
            chunk: TextChunk object to track
            
        Raises:
            KeyError: If tracking_id is not found
        """
        with self._lock:
            if tracking_id not in self._sessions:
                raise KeyError(f"Tracking session {tracking_id} not found")
            
            session = self._sessions[tracking_id]
            session.chunks.append(chunk)
            
            logger.debug(
                "Tracked chunk",
                extra={
                    'tracking_id': tracking_id,
                    'chunk_index': chunk.chunk_index,
                    'chunk_word_count': chunk.word_count,
                    'total_chunks': len(session.chunks)
                }
            )
    
    def get_summary(self, tracking_id: str) -> IngestionSummary:
        """Get ingestion summary for a tracking session.
        
        Builds a comprehensive summary including counts, processing time,
        and representative sample sources.
        
        Args:
            tracking_id: ID of the tracking session
            
        Returns:
            IngestionSummary: Summary with all tracking data
            
        Raises:
            KeyError: If tracking_id is not found
        """
        with self._lock:
            if tracking_id not in self._sessions:
                raise KeyError(f"Tracking session {tracking_id} not found")
            
            session = self._sessions[tracking_id]
            
            # Calculate processing time
            processing_time = time.time() - session.start_time
            
            # Select sample sources
            sample_sources = self._select_samples(session)
            
            # Build summary
            summary = IngestionSummary(
                emails_used=len(session.emails),
                slack_messages_used=len(session.slack_messages),
                meetings_used=len(session.meetings),
                total_chunks_processed=len(session.chunks),
                total_words_processed=session.total_words,
                processing_time_seconds=round(processing_time, 2),
                sample_sources=sample_sources
            )
            
            logger.info(
                "Generated ingestion summary",
                extra={
                    'tracking_id': tracking_id,
                    'emails_used': summary.emails_used,
                    'slack_messages_used': summary.slack_messages_used,
                    'meetings_used': summary.meetings_used,
                    'total_chunks_processed': summary.total_chunks_processed,
                    'total_words_processed': summary.total_words_processed,
                    'processing_time_seconds': summary.processing_time_seconds,
                    'sample_count': len(summary.sample_sources)
                }
            )
            
            return summary
    
    def _select_samples(self, session: TrackingSession) -> List[SampleSource]:
        """Select representative samples from tracked items.
        
        Uses random sampling to select up to sample_count items from
        all tracked sources. If fewer items are available, returns all.
        
        Args:
            session: TrackingSession to sample from
            
        Returns:
            List[SampleSource]: List of sample sources with metadata
        """
        all_samples: List[SampleSource] = []
        
        # Convert emails to samples
        for email in session.emails:
            sample = SampleSource(
                type="email",
                metadata={
                    "subject": email.subject,
                    "date": email.date,
                    "sender": email.sender
                }
            )
            all_samples.append(sample)
        
        # Convert Slack messages to samples
        for message in session.slack_messages:
            # Create preview (first 50 chars)
            preview = message.text[:50]
            if len(message.text) > 50:
                preview += "..."
            
            sample = SampleSource(
                type="slack",
                metadata={
                    "channel": message.channel,
                    "user": message.user,
                    "timestamp": message.timestamp,
                    "preview": preview
                }
            )
            all_samples.append(sample)
        
        # Convert meetings to samples
        for meeting in session.meetings:
            sample = SampleSource(
                type="meeting",
                metadata={
                    "timestamp": meeting.timestamp,
                    "topic": meeting.topic,
                    "speakers": meeting.speakers
                }
            )
            all_samples.append(sample)
        
        # Random sampling
        if len(all_samples) <= self.sample_count:
            return all_samples
        
        # Use random.sample for reproducible sampling
        return random.sample(all_samples, self.sample_count)
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired tracking sessions.
        
        Removes sessions that have exceeded the TTL. This method should
        be called periodically or during new session creation.
        
        Note: This method assumes the lock is already held by the caller.
        """
        current_time = time.time()
        expired_ids = []
        
        for tracking_id, session in self._sessions.items():
            if current_time - session.start_time > self.session_ttl:
                expired_ids.append(tracking_id)
        
        for tracking_id in expired_ids:
            del self._sessions[tracking_id]
        
        if expired_ids:
            logger.info(
                "Cleaned up expired tracking sessions",
                extra={
                    'expired_count': len(expired_ids),
                    'remaining_sessions': len(self._sessions)
                }
            )

    def start_cleanup_task(self, cleanup_interval: int = 600) -> None:
        """Start background task to clean up expired sessions.
        
        This method starts a background thread that periodically cleans up
        expired tracking sessions. The cleanup runs every cleanup_interval
        seconds (default: 10 minutes).
        
        Args:
            cleanup_interval: Interval between cleanup runs in seconds (default: 600 = 10 minutes)
            
        Note:
            This method should be called once during application startup.
            The cleanup task runs in a daemon thread and will stop when
            the main application exits.
        """
        def cleanup_loop():
            """Background loop for periodic cleanup."""
            while True:
                try:
                    time.sleep(cleanup_interval)
                    with self._lock:
                        self._cleanup_expired_sessions()
                except Exception as e:
                    logger.error(
                        "Error in cleanup task",
                        extra={'error': str(e)},
                        exc_info=True
                    )
        
        # Start cleanup thread as daemon
        cleanup_thread = threading.Thread(
            target=cleanup_loop,
            daemon=True,
            name="IngestionTrackerCleanup"
        )
        cleanup_thread.start()
        
        logger.info(
            "Started tracking session cleanup task",
            extra={
                'cleanup_interval_seconds': cleanup_interval,
                'session_ttl_seconds': self.session_ttl
            }
        )
    
    def get_active_session_count(self) -> int:
        """Get the number of active tracking sessions.
        
        Returns:
            int: Number of active sessions
        """
        with self._lock:
            return len(self._sessions)
