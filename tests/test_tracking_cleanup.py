"""Tests for tracking session cleanup functionality.

This module tests the background cleanup task that removes expired sessions.
"""

import time
import pytest
from app.services.ingestion_tracker import IngestionTracker
from app.models.request import Email


class TestTrackingCleanup:
    """Test tracking session cleanup."""
    
    def test_cleanup_expired_sessions(self):
        """Test that expired sessions are cleaned up."""
        # Create tracker with short TTL (1 second)
        tracker = IngestionTracker(sample_count=5, session_ttl=1)
        
        # Create a session
        tracking_id = tracker.start_tracking()
        
        # Verify session exists
        assert tracker.get_active_session_count() == 1
        
        # Wait for session to expire
        time.sleep(1.5)
        
        # Trigger cleanup by starting a new session
        # (cleanup is called during start_tracking)
        new_tracking_id = tracker.start_tracking()
        
        # Verify old session was cleaned up
        assert tracker.get_active_session_count() == 1
        
        # Verify we can't get summary for expired session
        with pytest.raises(KeyError):
            tracker.get_summary(tracking_id)
        
        # Verify new session still works
        summary = tracker.get_summary(new_tracking_id)
        assert summary is not None
    
    def test_cleanup_keeps_active_sessions(self):
        """Test that active sessions are not cleaned up."""
        # Create tracker with 5 second TTL
        tracker = IngestionTracker(sample_count=5, session_ttl=5)
        
        # Create multiple sessions
        id1 = tracker.start_tracking()
        time.sleep(1.0)
        id2 = tracker.start_tracking()
        id3 = tracker.start_tracking()
        
        # All sessions should be active
        assert tracker.get_active_session_count() == 3
        
        # Wait for first session to expire (but not others)
        time.sleep(4.5)  # Total: 5.5s for id1, 4.5s for id2 and id3
        
        # Trigger cleanup
        id4 = tracker.start_tracking()
        
        # First session should be expired, others should remain
        assert tracker.get_active_session_count() == 3  # id2, id3, id4
        
        # Verify expired session is gone
        with pytest.raises(KeyError):
            tracker.get_summary(id1)
        
        # Verify active sessions still work
        assert tracker.get_summary(id2) is not None
        assert tracker.get_summary(id3) is not None
        assert tracker.get_summary(id4) is not None
    
    def test_background_cleanup_task(self):
        """Test that background cleanup task runs periodically."""
        # Create tracker with short TTL and cleanup interval
        tracker = IngestionTracker(sample_count=5, session_ttl=1)
        
        # Start background cleanup task (runs every 2 seconds)
        tracker.start_cleanup_task(cleanup_interval=2)
        
        # Create a session
        tracking_id = tracker.start_tracking()
        assert tracker.get_active_session_count() == 1
        
        # Wait for session to expire
        time.sleep(1.5)
        
        # Session should still exist (cleanup hasn't run yet)
        assert tracker.get_active_session_count() == 1
        
        # Wait for cleanup task to run
        time.sleep(1.0)  # Total: 2.5s, cleanup should have run at 2s
        
        # Session should be cleaned up
        assert tracker.get_active_session_count() == 0
    
    def test_get_active_session_count(self):
        """Test getting the count of active sessions."""
        tracker = IngestionTracker(sample_count=5)
        
        # Initially no sessions
        assert tracker.get_active_session_count() == 0
        
        # Create sessions
        id1 = tracker.start_tracking()
        assert tracker.get_active_session_count() == 1
        
        id2 = tracker.start_tracking()
        assert tracker.get_active_session_count() == 2
        
        id3 = tracker.start_tracking()
        assert tracker.get_active_session_count() == 3
    
    def test_cleanup_with_no_expired_sessions(self):
        """Test cleanup when no sessions are expired."""
        tracker = IngestionTracker(sample_count=5, session_ttl=10)
        
        # Create sessions
        id1 = tracker.start_tracking()
        id2 = tracker.start_tracking()
        id3 = tracker.start_tracking()
        
        assert tracker.get_active_session_count() == 3
        
        # Trigger cleanup (no sessions should be expired)
        id4 = tracker.start_tracking()
        
        # All sessions should still exist
        assert tracker.get_active_session_count() == 4
    
    def test_cleanup_with_all_expired_sessions(self):
        """Test cleanup when all sessions are expired."""
        tracker = IngestionTracker(sample_count=5, session_ttl=1)
        
        # Create sessions
        id1 = tracker.start_tracking()
        id2 = tracker.start_tracking()
        id3 = tracker.start_tracking()
        
        assert tracker.get_active_session_count() == 3
        
        # Wait for all sessions to expire
        time.sleep(1.5)
        
        # Trigger cleanup
        id4 = tracker.start_tracking()
        
        # Only new session should exist
        assert tracker.get_active_session_count() == 1
        
        # Verify only new session works
        assert tracker.get_summary(id4) is not None
        
        with pytest.raises(KeyError):
            tracker.get_summary(id1)
        with pytest.raises(KeyError):
            tracker.get_summary(id2)
        with pytest.raises(KeyError):
            tracker.get_summary(id3)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
