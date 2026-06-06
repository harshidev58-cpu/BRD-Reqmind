"""Processing status router for real-time pipeline monitoring."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.processing_tracker import (
    ProcessingTracker,
    ProcessingSession,
    get_processing_tracker
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ProcessingStatusResponse(BaseModel):
    """Response model for processing status."""
    session_id: Optional[str]
    project_name: Optional[str]
    steps: list
    current_step: int
    overall_progress: int
    estimated_time: str


@router.get("/status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    session_id: Optional[str] = None,
    tracker: ProcessingTracker = Depends(get_processing_tracker)
) -> ProcessingStatusResponse:
    """Get current processing status.
    
    Args:
        session_id: Optional session ID. If not provided, returns latest session.
        tracker: Injected processing tracker
        
    Returns:
        ProcessingStatusResponse with current status
    """
    # Get session
    if session_id:
        session = tracker.get_session(session_id)
    else:
        session = tracker.get_latest_session()
    
    # If no session exists, return idle state
    if not session:
        return ProcessingStatusResponse(
            session_id=None,
            project_name=None,
            steps=[],
            current_step=0,
            overall_progress=0,
            estimated_time="N/A"
        )
    
    # Calculate overall progress
    completed_steps = sum(1 for step in session.steps if step.status == "completed")
    overall_progress = int((completed_steps / len(session.steps)) * 100)
    
    # Estimate remaining time
    if overall_progress == 100:
        estimated_time = "Completed"
    elif overall_progress == 0:
        estimated_time = "~2 minutes"
    else:
        estimated_time = f"~{2 - int(overall_progress / 50)} minute(s)"
    
    # Convert steps to dict format
    steps_data = [
        {
            "id": step.id,
            "name": step.name,
            "status": step.status,
            "progress": step.progress,
            "processed": step.processed,
            "total": step.total,
            "description": step.description
        }
        for step in session.steps
    ]
    
    return ProcessingStatusResponse(
        session_id=session.session_id,
        project_name=session.project_name,
        steps=steps_data,
        current_step=session.current_step,
        overall_progress=overall_progress,
        estimated_time=estimated_time
    )
