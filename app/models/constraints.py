"""Constraints model for user instruction layer.

This module defines the Pydantic model for structured constraints
generated from natural language instructions via Gemini API.
"""

from typing import List
from pydantic import BaseModel, Field


class Constraints(BaseModel):
    """Structured constraints for filtering and prioritizing data.
    
    This model represents constraints extracted from natural language
    instructions using the Gemini API. These constraints are used to
    filter and prioritize ingested data before BRD generation.
    
    Attributes:
        scope: Description of the project scope to focus on
        exclude_topics: List of topics to exclude from processing
        priority_focus: Description of what to prioritize
        deadline_override: Deadline information if mentioned in instructions
    """
    
    scope: str = Field(
        default="",
        description="Project scope to focus on (e.g., 'MVP features only')"
    )
    exclude_topics: List[str] = Field(
        default_factory=list,
        description="List of topics to exclude from processing"
    )
    priority_focus: str = Field(
        default="",
        description="What to prioritize in the analysis"
    )
    deadline_override: str = Field(
        default="",
        description="Deadline information if mentioned in instructions"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "scope": "MVP features only",
                "exclude_topics": ["marketing", "internal discussions"],
                "priority_focus": "core functionality",
                "deadline_override": "June 2024"
            }
        }
