"""Data models for BRD Generator API.

This package contains Pydantic models for request validation and
response serialization.
"""

from .request import BRDRequest, Email, SlackMessage, Meeting
from .response import BRDResponse, Requirement, Stakeholder
from .constraints import Constraints
from .ingestion_summary import IngestionSummary, SampleSource
from .context_request import (
    IngestionData,
    ContextRequest,
    ContextResponse,
    AlignmentAnalysis
)
from .chunk_models import TextChunk, Decision, Timeline, ExtractionResult

__all__ = [
    'BRDRequest',
    'BRDResponse',
    'Requirement',
    'Stakeholder',
    'Email',
    'SlackMessage',
    'Meeting',
    'Constraints',
    'IngestionSummary',
    'SampleSource',
    'IngestionData',
    'ContextRequest',
    'ContextResponse',
    'AlignmentAnalysis',
    'TextChunk',
    'Decision',
    'Timeline',
    'ExtractionResult'
]
