"""
Context Router for the new /generate_brd_with_context endpoint.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
import logging
import time
import uuid

from app.models.context_request import ContextRequest, ContextResponse
from app.models.request import BRDRequest
from app.services.gemini_service import GeminiService
from app.services.constraint_applier import ConstraintApplier
from app.services.chunk_processor import ChunkProcessor
from app.services.ingestion_tracker import IngestionTracker
from app.services.brd_generator import BRDGeneratorService
from app.services.openai_client import OpenAIClient
from app.services.alignment_intelligence import AlignmentIntelligenceEngine
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


def get_gemini_service() -> GeminiService:
    settings = get_settings()
    return GeminiService(api_key=settings.gemini_api_key, model=settings.gemini_model, timeout=settings.gemini_timeout)


def get_chunk_processor() -> ChunkProcessor:
    settings = get_settings()
    return ChunkProcessor(
        threshold_words=settings.chunk_threshold_words,
        chunk_size_min=settings.chunk_size_min,
        chunk_size_max=settings.chunk_size_max,
        overlap=settings.chunk_overlap
    )


def get_ingestion_tracker() -> IngestionTracker:
    return IngestionTracker(sample_count=get_settings().sample_sources_count)


def get_constraint_applier() -> ConstraintApplier:
    return ConstraintApplier()


def get_brd_generator_service() -> BRDGeneratorService:
    settings = get_settings()
    openai_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url
    )
    return BRDGeneratorService(openai_client)


def get_alignment_engine() -> AlignmentIntelligenceEngine:
    return AlignmentIntelligenceEngine()


@router.post("/generate_brd_with_context", response_model=ContextResponse)
async def generate_brd_with_context(
    http_request: Request,
    request: ContextRequest,
    gemini: GeminiService = Depends(get_gemini_service),
    constraint_applier: ConstraintApplier = Depends(get_constraint_applier),
    chunk_processor: ChunkProcessor = Depends(get_chunk_processor),
    tracker: IngestionTracker = Depends(get_ingestion_tracker),
    brd_service: BRDGeneratorService = Depends(get_brd_generator_service),
    alignment_engine: AlignmentIntelligenceEngine = Depends(get_alignment_engine)
):
    request_id = getattr(http_request.state, 'request_id', 'N/A')
    start_time = time.time()

    try:
        logger.info(f"Context BRD request received", extra={'request_id': request_id})

        # 1. Generate constraints via Gemini
        constraints = None
        try:
            constraints = await gemini.generate_constraints(request.instructions or "")
        except Exception as e:
            logger.error(f"Gemini constraint generation failed: {e}", extra={'request_id': request_id})
            constraints = None

        # 2. Apply constraints
        filtered_data = constraint_applier.apply_constraints(request.data, constraints)

        # 3. Start ingestion tracking
        tracking_id = tracker.start_tracking()

        # Track emails and slack
        for e in getattr(filtered_data, 'emails', []):
            tracker.track_email(tracking_id, e)
        for s in getattr(filtered_data, 'slack_messages', []):
            tracker.track_slack_message(tracking_id, s)

        # 4. Handle meetings (chunking)
        meeting_texts = []
        total_chunks = 0
        for m in getattr(filtered_data, 'meetings', []):
            tracker.track_meeting(tracking_id, m)
            transcript = getattr(m, 'transcript', '') or ''
            if chunk_processor.needs_chunking(transcript):
                chunks = chunk_processor.chunk_text(transcript)
                total_chunks += len(chunks)
                for c in chunks:
                    tracker.track_chunk(tracking_id, c)
                    meeting_texts.append(c.text)
            else:
                meeting_texts.append(transcript)

        # 5. Aggregate source texts into strings for BRD generator
        email_text = '\n\n'.join([f"{getattr(e,'subject','')}: {getattr(e,'body','')}" for e in getattr(filtered_data, 'emails', [])])
        slack_text = '\n\n'.join([getattr(s,'text','') for s in getattr(filtered_data, 'slack_messages', [])])
        meeting_text = '\n\n'.join(meeting_texts)

        # 6. Build BRDRequest (projectName is optional in this endpoint)
        project_name = f"Context BRD {str(uuid.uuid4())[:8]}"
        brd_req = BRDRequest(projectName=project_name, emailText=email_text or None, slackText=slack_text or None, meetingText=meeting_text or None)

        # 7. Generate BRD
        brd_response = await brd_service.generate_brd(brd_req)

        # 8. Alignment analysis
        alignment_report = alignment_engine.analyze_alignment(
            email_content=brd_req.emailText,
            slack_content=brd_req.slackText,
            meeting_content=brd_req.meetingText,
            brd_data=brd_response.model_dump()
        )

        conflict_explanations = alignment_engine.generate_conflict_explanations(alignment_report.conflicts)

        # 9. Build ingestion summary
        ingestion_summary = tracker.get_summary(tracking_id)
        # ensure total_chunks_processed reflects what we counted
        if ingestion_summary:
            ingestion_summary.total_chunks_processed = ingestion_summary.total_chunks_processed or total_chunks

        processing_time = round(time.time() - start_time, 3)
        if ingestion_summary:
            ingestion_summary.processing_time_seconds = processing_time

        response = {
            'brd': brd_response.model_dump(),
            'alignment_analysis': {
                'alignment_score': round(alignment_report.alignment_score, 2),
                'risk_level': alignment_report.risk_level,
                'alert': alignment_report.alert,
                'component_scores': {
                    'stakeholder_agreement': round(alignment_report.stakeholder_agreement_score, 2),
                    'timeline_consistency': round(alignment_report.timeline_consistency_score, 2),
                    'requirement_stability': round(alignment_report.requirement_stability_score, 2),
                    'decision_volatility': round(alignment_report.decision_volatility_score, 2)
                },
                'conflicts': conflict_explanations,
                'timeline_mismatches': alignment_report.timeline_mismatches,
                'requirement_volatility': alignment_report.requirement_volatility
            },
            'ingestion_summary': ingestion_summary.model_dump() if ingestion_summary else None
        }

        logger.info(f"Context BRD generation complete for request", extra={'request_id': request_id})
        return response

    except Exception as e:
        logger.error(f"Error generating context BRD: {e}", extra={'request_id': request_id})
        raise HTTPException(status_code=500, detail=str(e))
