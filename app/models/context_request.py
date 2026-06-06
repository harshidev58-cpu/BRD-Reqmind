"""Context request and response models for the new context-aware endpoint.

This module defines the Pydantic models for the /generate_brd_with_context
endpoint that supports user instructions and ingestion transparency.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from .request import Email, SlackMessage, Meeting
from .response import BRDResponse
from .ingestion_summary import IngestionSummary


class IngestionData(BaseModel):
    """Model for multi-channel ingestion data.
    
    Represents data from multiple communication channels that will be
    processed to generate a BRD.
    
    Attributes:
        emails: List of email messages
        slack_messages: List of Slack messages
        meetings: List of meeting transcripts
    """
    
    emails: List[Email] = Field(default_factory=list, description="Email messages")
    slack_messages: List[SlackMessage] = Field(default_factory=list, description="Slack messages")
    meetings: List[Meeting] = Field(default_factory=list, description="Meeting transcripts")


class ContextRequest(BaseModel):
    """Request model for context-aware BRD generation.
    
    This model supports the new /generate_brd_with_context endpoint that
    accepts optional natural language instructions and multi-channel data.
    
    Attributes:
        instructions: Optional natural language instructions for filtering/prioritizing
        data: Multi-channel ingestion data (emails, slack, meetings)
    """
    
    instructions: Optional[str] = Field(
        None,
        description="Natural language instructions for filtering and prioritizing data",
        max_length=2000
    )
    data: IngestionData = Field(..., description="Multi-channel ingestion data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "instructions": "Focus only on MVP features and ignore marketing discussions",
                "data": {
                    "emails": [
                        {
                            "subject": "MVP scope",
                            "body": "We need core features...",
                            "sender": "pm@company.com",
                            "date": "2024-02-15"
                        }
                    ],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        }


class AlignmentAnalysis(BaseModel):
    """Model for alignment analysis results.
    
    Represents the alignment intelligence analysis including scores,
    risk level, and detected conflicts.
    
    Attributes:
        alignment_score: Overall alignment score (0-100)
        risk_level: Risk level (HIGH, MEDIUM, LOW)
        alert: Alert message describing the risk
        conflicts: List of detected conflicts
        timeline_mismatches: List of timeline inconsistencies
        requirement_volatility: Requirement stability metrics
        stakeholder_agreement_score: Stakeholder agreement score (0-100)
        timeline_consistency_score: Timeline consistency score (0-100)
        requirement_stability_score: Requirement stability score (0-100)
        decision_volatility_score: Decision volatility score (0-100)
    """
    
    alignment_score: float = Field(..., description="Overall alignment score (0-100)")
    risk_level: str = Field(..., description="Risk level (HIGH, MEDIUM, LOW)")
    alert: str = Field(..., description="Alert message")
    conflicts: List[dict] = Field(default_factory=list, description="Detected conflicts")
    timeline_mismatches: List[dict] = Field(default_factory=list, description="Timeline mismatches")
    requirement_volatility: dict = Field(default_factory=dict, description="Requirement volatility metrics")
    stakeholder_agreement_score: float = Field(..., description="Stakeholder agreement score")
    timeline_consistency_score: float = Field(..., description="Timeline consistency score")
    requirement_stability_score: float = Field(..., description="Requirement stability score")
    decision_volatility_score: float = Field(..., description="Decision volatility score")


class ContextResponse(BaseModel):
    """Response model for context-aware BRD generation.
    
    Extends the standard BRD response with alignment analysis and
    ingestion transparency summary.
    
    Attributes:
        brd: Generated Business Requirements Document
        alignment_analysis: Alignment intelligence analysis
        ingestion_summary: Summary of data sources processed
    """
    
    brd: BRDResponse = Field(..., description="Generated BRD")
    alignment_analysis: AlignmentAnalysis = Field(..., description="Alignment analysis")
    ingestion_summary: IngestionSummary = Field(..., description="Ingestion transparency summary")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brd": {
                    "projectName": "Mobile App",
                    "executiveSummary": "...",
                    "businessObjectives": ["..."],
                    "requirements": [],
                    "stakeholders": []
                },
                "alignment_analysis": {
                    "alignment_score": 78.0,
                    "risk_level": "MEDIUM",
                    "alert": "Potential misalignment detected",
                    "conflicts": [],
                    "timeline_mismatches": [],
                    "requirement_volatility": {},
                    "stakeholder_agreement_score": 85.0,
                    "timeline_consistency_score": 70.0,
                    "requirement_stability_score": 80.0,
                    "decision_volatility_score": 75.0
                },
                "ingestion_summary": {
                    "emails_used": 12,
                    "slack_messages_used": 45,
                    "meetings_used": 3,
                    "total_chunks_processed": 8,
                    "total_words_processed": 15420,
                    "processing_time_seconds": 12.5,
                    "sample_sources": []
                }
            }
        }
