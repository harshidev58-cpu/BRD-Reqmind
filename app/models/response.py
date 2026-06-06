"""Response models for the BRD Generator Backend API.

This module defines the Pydantic models for structuring API responses
containing generated Business Requirements Documents.
"""

from typing import List
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """Model for a single requirement in the BRD.
    
    Represents an individual requirement with a unique identifier,
    description, and priority level.
    
    Attributes:
        id: Unique requirement identifier (e.g., "REQ-001")
        description: Detailed description of the requirement
        priority: Priority level (High, Medium, or Low)
    """
    
    id: str = Field(..., description="Unique requirement identifier")
    description: str = Field(..., description="Requirement description")
    priority: str = Field(..., description="Priority level (High, Medium, Low)")


class Stakeholder(BaseModel):
    """Model for a stakeholder in the project.
    
    Represents a person or group involved in the project with their
    name and role.
    
    Attributes:
        name: Stakeholder name or role identifier
        role: Description of the stakeholder's role in the project
    """
    
    name: str = Field(..., description="Stakeholder name or role")
    role: str = Field(..., description="Stakeholder's role in the project")


class BRDResponse(BaseModel):
    """Response model for generated BRD.
    
    This model represents the complete structure of a Business Requirements
    Document, including project overview, objectives, requirements, and
    stakeholders.
    
    Attributes:
        projectName: Name of the project
        executiveSummary: High-level overview of the project
        businessObjectives: List of business objectives the project aims to achieve
        requirements: List of detailed requirements for the project
        stakeholders: List of stakeholders involved in the project
    """
    
    projectName: str = Field(..., description="Name of the project")
    executiveSummary: str = Field(..., description="High-level project overview")
    businessObjectives: List[str] = Field(..., description="List of business objectives")
    requirements: List[Requirement] = Field(..., description="List of requirements")
    stakeholders: List[Stakeholder] = Field(..., description="List of stakeholders")
