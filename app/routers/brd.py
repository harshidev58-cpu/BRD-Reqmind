"""BRD Router for the BRD Generator Backend API.

This module defines the API endpoint for generating Business Requirements Documents.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import ValidationError as PydanticValidationError

from app.models.request import BRDRequest
from app.models.response import BRDResponse
from app.services.brd_generator import BRDGeneratorService
from app.services.openai_client import OpenAIClient
from app.services.alignment_intelligence import AlignmentIntelligenceEngine
from app.utils.exceptions import BRDGenerationError, OpenAIServiceError
from app.config import get_settings


router = APIRouter()
logger = logging.getLogger(__name__)


def get_brd_generator_service() -> BRDGeneratorService:
    """Dependency injection for BRDGeneratorService.
    
    Creates and returns a BRDGeneratorService instance with the
    configured OpenAI client.
    
    Returns:
        BRDGeneratorService instance
    """
    settings = get_settings()
    openai_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url
    )
    return BRDGeneratorService(openai_client)


def get_alignment_engine() -> AlignmentIntelligenceEngine:
    """Dependency injection for AlignmentIntelligenceEngine.
    
    Returns:
        AlignmentIntelligenceEngine instance
    """
    return AlignmentIntelligenceEngine()


@router.post("/generate_brd", response_model=BRDResponse, status_code=200)
async def generate_brd(
    http_request: Request,
    request: BRDRequest,
    service: BRDGeneratorService = Depends(get_brd_generator_service)
) -> BRDResponse:
    """Generate a Business Requirements Document from project information.
    
    This endpoint accepts project information from multiple sources (email, Slack,
    meetings) and generates a structured BRD using OpenAI's API.
    
    Args:
        http_request: FastAPI Request object for accessing request state
        request: BRDRequest containing projectName and optional text sources
        service: Injected BRDGeneratorService instance
        
    Returns:
        BRDResponse containing the structured BRD with project name, executive
        summary, business objectives, requirements, and stakeholders
        
    Raises:
        HTTPException: 
            - 400 for validation errors (missing projectName, no text sources)
            - 503 for OpenAI service unavailability
            - 500 for unexpected errors during BRD generation
    """
    request_id = getattr(http_request.state, 'request_id', 'N/A')
    
    try:
        logger.info(
            f"Generating BRD for project: {request.projectName}",
            extra={'request_id': request_id}
        )
        
        # Generate the BRD using the service
        brd_response = await service.generate_brd(request)
        
        logger.info(
            f"Successfully generated BRD for project: {request.projectName}",
            extra={'request_id': request_id}
        )
        
        return brd_response
        
    except PydanticValidationError as e:
        # Handle Pydantic validation errors (should be caught by FastAPI, but just in case)
        logger.warning(
            f"Validation error for project {request.projectName}: {str(e)}",
            extra={'request_id': request_id}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    
    except OpenAIServiceError as e:
        # Handle OpenAI service errors (unavailable, rate limit, etc.)
        logger.error(
            f"OpenAI service error for project {request.projectName}: {str(e)}",
            extra={'request_id': request_id}
        )
        raise HTTPException(
            status_code=503,
            detail=f"OpenAI service is currently unavailable: {str(e)}"
        )
    
    except BRDGenerationError as e:
        # Handle BRD generation errors (invalid response, parsing failures)
        logger.error(
            f"BRD generation error for project {request.projectName}: {str(e)}",
            extra={'request_id': request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the BRD: {str(e)}"
        )
    
    except Exception as e:
        # Handle any unexpected errors
        logger.error(
            f"Unexpected error for project {request.projectName}: {str(e)}",
            extra={'request_id': request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/generate_brd_with_alignment", status_code=200)
async def generate_brd_with_alignment(
    http_request: Request,
    request: BRDRequest,
    brd_service: BRDGeneratorService = Depends(get_brd_generator_service),
    alignment_engine: AlignmentIntelligenceEngine = Depends(get_alignment_engine)
) -> dict:
    """Generate a BRD with alignment intelligence analysis.
    
    This endpoint generates a structured BRD and performs alignment analysis
    to detect conflicts, timeline mismatches, and requirement volatility.
    
    Args:
        http_request: FastAPI Request object
        request: BRDRequest with project information
        brd_service: Injected BRD generation service
        alignment_engine: Injected alignment intelligence engine
        
    Returns:
        Dictionary containing BRD, alignment score, risk level, and alerts
    """
    request_id = getattr(http_request.state, 'request_id', 'N/A')
    
    try:
        logger.info(
            f"Generating BRD with alignment analysis for project: {request.projectName}",
            extra={'request_id': request_id}
        )
        
        # Generate the BRD
        brd_response = await brd_service.generate_brd(request)
        
        # Perform alignment analysis
        alignment_report = alignment_engine.analyze_alignment(
            email_content=request.emailText,
            slack_content=request.slackText,
            meeting_content=request.meetingText,
            brd_data=brd_response.model_dump()
        )
        
        # Generate conflict explanations
        conflict_explanations = alignment_engine.generate_conflict_explanations(
            alignment_report.conflicts
        )
        
        logger.info(
            f"Alignment analysis complete for project: {request.projectName} - Score: {alignment_report.alignment_score}, Risk: {alignment_report.risk_level}",
            extra={'request_id': request_id}
        )
        
        # Build response
        return {
            "brd": brd_response.model_dump(),
            "alignment_analysis": {
                "alignment_score": round(alignment_report.alignment_score, 2),
                "risk_level": alignment_report.risk_level,
                "alert": alignment_report.alert,
                "component_scores": {
                    "stakeholder_agreement": round(alignment_report.stakeholder_agreement_score, 2),
                    "timeline_consistency": round(alignment_report.timeline_consistency_score, 2),
                    "requirement_stability": round(alignment_report.requirement_stability_score, 2),
                    "decision_volatility": round(alignment_report.decision_volatility_score, 2)
                },
                "conflicts": conflict_explanations,
                "timeline_mismatches": alignment_report.timeline_mismatches,
                "requirement_volatility": alignment_report.requirement_volatility
            }
        }
        
    except Exception as e:
        logger.error(
            f"Error in alignment analysis for project {request.projectName}: {str(e)}",
            extra={'request_id': request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during alignment analysis: {str(e)}"
        )
