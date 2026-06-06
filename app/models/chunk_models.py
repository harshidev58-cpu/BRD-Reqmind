"""Chunk and extraction models for large data handling.

This module defines the data models for text chunking and extraction
results used in processing large meeting transcripts.
"""

from dataclasses import dataclass
from typing import List
from pydantic import BaseModel, Field


@dataclass
class TextChunk:
    """Model for a text chunk with metadata.
    
    Represents a chunk of text split from a larger document,
    with metadata about its position and overlap.
    
    Attributes:
        content: The actual text content of the chunk
        chunk_index: Zero-based index of this chunk
        total_chunks: Total number of chunks in the document
        word_count: Number of words in this chunk
        overlap_start: Number of overlapping words from previous chunk
        overlap_end: Number of overlapping words with next chunk
    """
    
    content: str
    chunk_index: int
    total_chunks: int
    word_count: int
    overlap_start: int
    overlap_end: int


class Decision(BaseModel):
    """Model for a project decision.
    
    Represents a decision made during project discussions.
    
    Attributes:
        description: Description of the decision
        timestamp: When the decision was made
        decision_maker: Who made the decision (optional)
    """
    
    description: str = Field(..., description="Decision description")
    timestamp: str = Field(..., description="When the decision was made")
    decision_maker: str = Field(default="", description="Who made the decision")


class Timeline(BaseModel):
    """Model for a project timeline milestone.
    
    Represents a milestone or deadline in the project timeline.
    
    Attributes:
        milestone: Name or description of the milestone
        start_date: Start date (optional)
        end_date: End date or deadline (optional)
        status: Current status of the milestone (optional)
    """
    
    milestone: str = Field(..., description="Milestone name")
    start_date: str = Field(default="", description="Start date")
    end_date: str = Field(default="", description="End date or deadline")
    status: str = Field(default="", description="Milestone status")


class ExtractionResult(BaseModel):
    """Model for extraction results from a text chunk.
    
    Represents structured data extracted from a text chunk or
    full document during processing.
    
    Attributes:
        requirements: List of extracted requirements
        decisions: List of extracted decisions
        stakeholders: List of identified stakeholders
        timelines: List of extracted timeline milestones
    """
    
    requirements: List[str] = Field(default_factory=list, description="Extracted requirements")
    decisions: List[Decision] = Field(default_factory=list, description="Extracted decisions")
    stakeholders: List[str] = Field(default_factory=list, description="Identified stakeholders")
    timelines: List[Timeline] = Field(default_factory=list, description="Timeline milestones")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirements": [
                    "User authentication must support OAuth 2.0",
                    "System must handle 1000 concurrent users"
                ],
                "decisions": [
                    {
                        "description": "Use PostgreSQL for database",
                        "timestamp": "2024-02-15 10:30",
                        "decision_maker": "Tech Lead"
                    }
                ],
                "stakeholders": ["Product Manager", "Tech Lead", "UX Designer"],
                "timelines": [
                    {
                        "milestone": "MVP Release",
                        "start_date": "2024-03-01",
                        "end_date": "2024-06-30",
                        "status": "planned"
                    }
                ]
            }
        }
