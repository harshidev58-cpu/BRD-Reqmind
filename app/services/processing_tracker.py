"""Processing status tracker for real-time pipeline monitoring."""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Processing step status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStep(BaseModel):
    """Model for a processing step."""
    id: int
    name: str
    status: ProcessingStatus
    progress: int
    processed: int
    total: int
    description: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProcessingSession(BaseModel):
    """Model for a processing session."""
    session_id: str
    project_name: str
    steps: List[ProcessingStep]
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_step: int = 1


class ProcessingTracker:
    """Tracks processing status across pipeline steps."""
    
    def __init__(self):
        """Initialize the processing tracker."""
        self._sessions: Dict[str, ProcessingSession] = {}
        
    def create_session(self, session_id: str, project_name: str) -> ProcessingSession:
        """Create a new processing session.
        
        Args:
            session_id: Unique session identifier
            project_name: Name of the project being processed
            
        Returns:
            ProcessingSession instance
        """
        steps = [
            ProcessingStep(
                id=1,
                name="Collecting emails",
                status=ProcessingStatus.PENDING,
                progress=0,
                processed=0,
                total=0,
                description="Loading data from Enron email dataset"
            ),
            ProcessingStep(
                id=2,
                name="Cleaning noise",
                status=ProcessingStatus.PENDING,
                progress=0,
                processed=0,
                total=0,
                description="Filtering irrelevant content and spam"
            ),
            ProcessingStep(
                id=3,
                name="Extracting stakeholders",
                status=ProcessingStatus.PENDING,
                progress=0,
                processed=0,
                total=0,
                description="Identifying key stakeholders from communications"
            ),
            ProcessingStep(
                id=4,
                name="Generating BRD",
                status=ProcessingStatus.PENDING,
                progress=0,
                processed=0,
                total=1,
                description="Creating Business Requirements Document with Groq AI"
            ),
            ProcessingStep(
                id=5,
                name="Running alignment analysis",
                status=ProcessingStatus.PENDING,
                progress=0,
                processed=0,
                total=1,
                description="Analyzing cross-team alignment and detecting conflicts"
            )
        ]
        
        session = ProcessingSession(
            session_id=session_id,
            project_name=project_name,
            steps=steps,
            started_at=datetime.now()
        )
        
        self._sessions[session_id] = session
        logger.info(f"Created processing session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ProcessingSession]:
        """Get a processing session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ProcessingSession or None if not found
        """
        return self._sessions.get(session_id)
    
    def update_step(
        self,
        session_id: str,
        step_id: int,
        status: Optional[ProcessingStatus] = None,
        processed: Optional[int] = None,
        total: Optional[int] = None
    ) -> bool:
        """Update a processing step.
        
        Args:
            session_id: Session identifier
            step_id: Step ID (1-5)
            status: New status
            processed: Number of items processed
            total: Total number of items
            
        Returns:
            True if updated successfully
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        step = next((s for s in session.steps if s.id == step_id), None)
        if not step:
            logger.warning(f"Step not found: {step_id}")
            return False
        
        # Update status
        if status:
            old_status = step.status
            step.status = status
            
            if status == ProcessingStatus.PROCESSING and not step.started_at:
                step.started_at = datetime.now()
                session.current_step = step_id
            elif status == ProcessingStatus.COMPLETED:
                step.completed_at = datetime.now()
                step.progress = 100
                
            logger.info(f"Step {step_id} status: {old_status} -> {status}")
        
        # Update counts
        if processed is not None:
            step.processed = processed
        if total is not None:
            step.total = total
            
        # Calculate progress
        if step.total > 0:
            step.progress = int((step.processed / step.total) * 100)
        
        return True
    
    def complete_session(self, session_id: str) -> bool:
        """Mark a session as completed.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if completed successfully
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.completed_at = datetime.now()
        logger.info(f"Completed processing session: {session_id}")
        return True
    
    def get_latest_session(self) -> Optional[ProcessingSession]:
        """Get the most recent processing session.
        
        Returns:
            Latest ProcessingSession or None
        """
        if not self._sessions:
            return None
        
        return max(self._sessions.values(), key=lambda s: s.started_at)


# Global tracker instance
_tracker = ProcessingTracker()


def get_processing_tracker() -> ProcessingTracker:
    """Get the global processing tracker instance.
    
    Returns:
        ProcessingTracker instance
    """
    return _tracker
