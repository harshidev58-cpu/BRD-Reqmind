"""Ingestion summary models for transparency and explainability.

This module defines the Pydantic models for tracking and reporting
what data sources were used during BRD generation.
"""

from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field


class SampleSource(BaseModel):
    """Model for a sample data source used in analysis.
    
    Represents a sample source that was analyzed during BRD generation,
    including type-specific metadata for transparency.
    
    Attributes:
        type: Type of the source (email, slack, or meeting)
        metadata: Type-specific metadata dictionary containing relevant fields
    """
    
    type: Literal["email", "slack", "meeting"] = Field(
        ...,
        description="Type of the data source"
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Type-specific metadata for the source"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "type": "email",
                    "metadata": {
                        "subject": "Deadline discussion",
                        "date": "2024-02-12",
                        "sender": "john.pm@company.com"
                    }
                },
                {
                    "type": "meeting",
                    "metadata": {
                        "timestamp": "01:15:30",
                        "topic": "API dependency risk",
                        "speakers": ["PM", "Tech Lead"]
                    }
                },
                {
                    "type": "slack",
                    "metadata": {
                        "channel": "#project-alpha",
                        "user": "sarah.dev",
                        "timestamp": "2024-02-15 14:30",
                        "preview": "We need to prioritize mobile..."
                    }
                }
            ]
        }


class IngestionSummary(BaseModel):
    """Model for ingestion transparency summary.
    
    Provides a comprehensive summary of what data sources were used
    during BRD generation, including counts, processing metrics, and
    sample sources for verification.
    
    Attributes:
        emails_used: Number of emails processed
        slack_messages_used: Number of Slack messages processed
        meetings_used: Number of meetings processed
        total_chunks_processed: Total number of text chunks processed
        total_words_processed: Total word count across all sources
        processing_time_seconds: Time taken to process all sources
        sample_sources: List of 3-5 representative sample sources
    """
    
    emails_used: int = Field(
        default=0,
        ge=0,
        description="Number of emails used in analysis"
    )
    slack_messages_used: int = Field(
        default=0,
        ge=0,
        description="Number of Slack messages used in analysis"
    )
    meetings_used: int = Field(
        default=0,
        ge=0,
        description="Number of meetings used in analysis"
    )
    total_chunks_processed: int = Field(
        default=0,
        ge=0,
        description="Total number of text chunks processed"
    )
    total_words_processed: int = Field(
        default=0,
        ge=0,
        description="Total word count across all processed sources"
    )
    processing_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to process all sources in seconds"
    )
    sample_sources: List[SampleSource] = Field(
        default_factory=list,
        description="List of 3-5 representative sample sources"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "emails_used": 12,
                "slack_messages_used": 45,
                "meetings_used": 3,
                "total_chunks_processed": 8,
                "total_words_processed": 15420,
                "processing_time_seconds": 12.5,
                "sample_sources": [
                    {
                        "type": "email",
                        "metadata": {
                            "subject": "Deadline discussion",
                            "date": "2024-02-12",
                            "sender": "john.pm@company.com"
                        }
                    },
                    {
                        "type": "meeting",
                        "metadata": {
                            "timestamp": "01:15:30",
                            "topic": "API dependency risk",
                            "speakers": ["PM", "Tech Lead"]
                        }
                    },
                    {
                        "type": "slack",
                        "metadata": {
                            "channel": "#project-alpha",
                            "user": "sarah.dev",
                            "timestamp": "2024-02-15 14:30",
                            "preview": "We need to prioritize mobile..."
                        }
                    }
                ]
            }
        }
