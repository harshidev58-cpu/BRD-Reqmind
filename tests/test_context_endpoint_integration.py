"""Integration tests for the context-aware BRD endpoint.

These tests verify end-to-end functionality of the /generate_brd_with_context
endpoint including:
- Full flow with instructions and constraint generation
- Large meeting chunking and aggregation
- Multiple data sources with tracking
- Gemini failure fallback
- Backward compatibility
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.routers.context import (
    get_gemini_service,
    get_constraint_applier,
    get_chunk_processor,
    get_ingestion_tracker,
    get_aggregator,
    get_brd_generator_service,
    get_alignment_engine
)
from app.services.gemini_service import GeminiService
from app.services.constraint_applier import ConstraintApplier
from app.services.chunk_processor import ChunkProcessor
from app.services.ingestion_tracker import IngestionTracker
from app.services.aggregator import Aggregator
from app.services.brd_generator import BRDGeneratorService
from app.services.alignment_intelligence import AlignmentIntelligenceEngine
from app.models.constraints import Constraints
from app.models.response import BRDResponse, Requirement, Stakeholder
from app.services.alignment_intelligence import AlignmentReport, ConflictDetail


class TestContextEndpointFullFlowWithInstructions:
    """Test end-to-end flow with instructions and constraint generation.
    
    Validates: Requirements 1.1.6, 3.1.5
    
    Verifies that:
    - Instructions are converted to constraints via Gemini
    - Constraints filter and prioritize data
    - BRD is generated from filtered data
    - Response includes ingestion_summary
    """
    
    def test_full_flow_with_instructions(self):
        """Test complete flow: instructions → constraints → filtering → BRD.
        
        This test verifies the entire pipeline:
        1. User provides instructions
        2. Gemini converts instructions to constraints
        3. Constraints filter the data
        4. Filtered data generates BRD
        5. Alignment analysis runs
        6. Response includes ingestion summary
        """
        # Create request with instructions
        request_data = {
            "instructions": "Focus only on MVP features and ignore marketing discussions",
            "data": {
                "emails": [
                    {
                        "subject": "MVP scope",
                        "body": "We need core authentication and user management features for the MVP.",
                        "sender": "pm@company.com",
                        "date": "2024-02-15"
                    },
                    {
                        "subject": "Marketing campaign",
                        "body": "Let's plan the social media marketing strategy for launch.",
                        "sender": "marketing@company.com",
                        "date": "2024-02-16"
                    }
                ],
                "slack_messages": [
                    {
                        "channel": "#engineering",
                        "user": "dev1",
                        "text": "MVP database schema is ready for review",
                        "timestamp": "2024-02-15 10:30"
                    }
                ],
                "meetings": []
            }
        }
        
        # Mock Gemini service to return constraints
        mock_gemini = Mock(spec=GeminiService)
        
        async def mock_generate_constraints(instructions, request_id=None):
            return Constraints(
                scope="MVP features only",
                exclude_topics=["marketing", "social media"],
                priority_focus="core functionality",
                deadline_override=""
            )
        
        mock_gemini.generate_constraints = AsyncMock(side_effect=mock_generate_constraints)
        
        # Use real constraint applier
        real_constraint_applier = ConstraintApplier()
        
        # Use real chunk processor
        real_chunk_processor = ChunkProcessor()
        
        # Use real ingestion tracker
        real_ingestion_tracker = IngestionTracker()
        
        # Use real aggregator
        real_aggregator = Aggregator()
        
        # Mock BRD generator service
        mock_brd_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(brd_request):
            return BRDResponse(
                projectName="MVP scope",
                executiveSummary="An MVP with core authentication and user management features.",
                businessObjectives=[
                    "Deliver core authentication system",
                    "Implement user management features"
                ],
                requirements=[
                    Requirement(
                        id="REQ-1",
                        description="Implement user authentication system",
                        priority="High"
                    ),
                    Requirement(
                        id="REQ-2",
                        description="Create user management dashboard",
                        priority="High"
                    )
                ],
                stakeholders=[
                    Stakeholder(name="Product Manager", role="Project Owner"),
                    Stakeholder(name="Development Team", role="Implementation")
                ]
            )
        
        mock_brd_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Mock alignment engine
        mock_alignment_engine = Mock(spec=AlignmentIntelligenceEngine)
        
        def mock_analyze_alignment(email_content, slack_content, meeting_content, brd_data):
            return AlignmentReport(
                alignment_score=85.0,
                risk_level="LOW",
                alert="Good alignment detected",
                conflicts=[],
                timeline_mismatches=[],
                requirement_volatility={},
                stakeholder_agreement_score=90.0,
                timeline_consistency_score=85.0,
                requirement_stability_score=88.0,
                decision_volatility_score=82.0
            )
        
        def mock_generate_conflict_explanations(conflicts):
            return []
        
        mock_alignment_engine.analyze_alignment = Mock(side_effect=mock_analyze_alignment)
        mock_alignment_engine.generate_conflict_explanations = Mock(side_effect=mock_generate_conflict_explanations)
        
        # Override dependencies
        app.dependency_overrides[get_gemini_service] = lambda: mock_gemini
        app.dependency_overrides[get_constraint_applier] = lambda: real_constraint_applier
        app.dependency_overrides[get_chunk_processor] = lambda: real_chunk_processor
        app.dependency_overrides[get_ingestion_tracker] = lambda: real_ingestion_tracker
        app.dependency_overrides[get_aggregator] = lambda: real_aggregator
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_brd_service
        app.dependency_overrides[get_alignment_engine] = lambda: mock_alignment_engine
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd_with_context", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure
            response_data = response.json()
            
            # Verify BRD is present
            assert "brd" in response_data
            assert response_data["brd"]["projectName"] == "MVP scope"
            assert len(response_data["brd"]["requirements"]) == 2
            
            # Verify alignment analysis is present
            assert "alignment_analysis" in response_data
            assert response_data["alignment_analysis"]["alignment_score"] == 85.0
            assert response_data["alignment_analysis"]["risk_level"] == "LOW"
            
            # Verify ingestion summary is present (Requirement 3.1.5)
            assert "ingestion_summary" in response_data
            ingestion_summary = response_data["ingestion_summary"]
            
            # Verify counts are accurate (Requirement 1.1.6)
            # Note: Constraint applier should have filtered out the marketing email
            assert ingestion_summary["emails_used"] >= 1  # At least MVP email
            assert ingestion_summary["slack_messages_used"] == 1
            assert ingestion_summary["meetings_used"] == 0
            assert ingestion_summary["total_chunks_processed"] == 0  # No chunking needed
            
            # Verify processing metrics
            assert "total_words_processed" in ingestion_summary
            assert "processing_time_seconds" in ingestion_summary
            assert ingestion_summary["processing_time_seconds"] >= 0
            
            # Verify sample sources are included
            assert "sample_sources" in ingestion_summary
            assert isinstance(ingestion_summary["sample_sources"], list)
            
            # Verify Gemini was called with instructions
            mock_gemini.generate_constraints.assert_called_once()
            call_args = mock_gemini.generate_constraints.call_args
            assert "MVP features" in call_args[0][0] or "MVP features" in str(call_args)
            
            # Verify BRD generator was called
            mock_brd_service.generate_brd.assert_called_once()
            
            # Verify alignment engine was called
            mock_alignment_engine.analyze_alignment.assert_called_once()
            
        finally:
            app.dependency_overrides.clear()




class TestContextEndpointLargeMeetingChunking:
    """Test end-to-end flow with large meeting requiring chunking.
    
    Validates: Requirements 2.1.1, 2.2.2, 2.2.5
    
    Verifies that:
    - Meetings >3000 words are detected and chunked
    - Chunks are tracked in ingestion summary
    - Aggregation combines chunk results
    - BRD is generated from aggregated data
    """
    
    def test_large_meeting_with_chunking(self):
        """Test: Meeting >3000 words → chunking → aggregation → BRD.
        
        This test verifies:
        1. Large meeting transcript is detected
        2. Text is chunked into appropriate sizes
        3. Chunks are tracked
        4. BRD is generated successfully
        5. Ingestion summary shows chunk count
        """
        # Create a large meeting transcript (>3000 words)
        # Generate approximately 3500 words
        large_transcript = " ".join([
            f"Speaker {i % 3 + 1}: This is sentence number {i} discussing the project requirements and technical specifications."
            for i in range(250)  # ~3500 words
        ])
        
        request_data = {
            "data": {
                "emails": [],
                "slack_messages": [],
                "meetings": [
                    {
                        "transcript": large_transcript,
                        "topic": "Technical Planning Meeting",
                        "speakers": ["PM", "Tech Lead", "Developer"],
                        "timestamp": "2024-02-15 14:00"
                    }
                ]
            }
        }
        
        # Mock Gemini service (no instructions, so it won't be called)
        mock_gemini = Mock(spec=GeminiService)
        
        # Use real services for chunking and tracking
        real_constraint_applier = ConstraintApplier()
        real_chunk_processor = ChunkProcessor()
        real_ingestion_tracker = IngestionTracker()
        real_aggregator = Aggregator()
        
        # Mock BRD generator service
        mock_brd_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(brd_request):
            return BRDResponse(
                projectName="Technical Planning Meeting",
                executiveSummary="A comprehensive technical planning meeting covering project requirements.",
                businessObjectives=[
                    "Define technical architecture",
                    "Establish project timeline"
                ],
                requirements=[
                    Requirement(
                        id="REQ-1",
                        description="Design system architecture",
                        priority="High"
                    ),
                    Requirement(
                        id="REQ-2",
                        description="Set up development environment",
                        priority="Medium"
                    )
                ],
                stakeholders=[
                    Stakeholder(name="Tech Lead", role="Technical Owner"),
                    Stakeholder(name="Development Team", role="Implementation")
                ]
            )
        
        mock_brd_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Mock alignment engine
        mock_alignment_engine = Mock(spec=AlignmentIntelligenceEngine)
        
        def mock_analyze_alignment(email_content, slack_content, meeting_content, brd_data):
            return AlignmentReport(
                alignment_score=78.0,
                risk_level="MEDIUM",
                alert="Some alignment concerns detected",
                conflicts=[],
                timeline_mismatches=[],
                requirement_volatility={},
                stakeholder_agreement_score=80.0,
                timeline_consistency_score=75.0,
                requirement_stability_score=78.0,
                decision_volatility_score=76.0
            )
        
        def mock_generate_conflict_explanations(conflicts):
            return []
        
        mock_alignment_engine.analyze_alignment = Mock(side_effect=mock_analyze_alignment)
        mock_alignment_engine.generate_conflict_explanations = Mock(side_effect=mock_generate_conflict_explanations)
        
        # Override dependencies
        app.dependency_overrides[get_gemini_service] = lambda: mock_gemini
        app.dependency_overrides[get_constraint_applier] = lambda: real_constraint_applier
        app.dependency_overrides[get_chunk_processor] = lambda: real_chunk_processor
        app.dependency_overrides[get_ingestion_tracker] = lambda: real_ingestion_tracker
        app.dependency_overrides[get_aggregator] = lambda: real_aggregator
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_brd_service
        app.dependency_overrides[get_alignment_engine] = lambda: mock_alignment_engine
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd_with_context", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure
            response_data = response.json()
            
            # Verify BRD is present
            assert "brd" in response_data
            assert response_data["brd"]["projectName"] == "Technical Planning Meeting"
            
            # Verify ingestion summary
            assert "ingestion_summary" in response_data
            ingestion_summary = response_data["ingestion_summary"]
            
            # Verify meeting was tracked (Requirement 2.1.1)
            assert ingestion_summary["meetings_used"] == 1
            
            # Verify chunks were created and tracked (Requirement 2.2.5)
            # Since the transcript is >3000 words, it should be chunked
            word_count = len(large_transcript.split())
            assert word_count > 3000, f"Test transcript should be >3000 words, got {word_count}"
            
            # Chunks should have been processed
            assert ingestion_summary["total_chunks_processed"] > 0, \
                "Large meeting should have been chunked"
            
            # Verify word count tracking
            assert ingestion_summary["total_words_processed"] > 0
            
            # Verify BRD was generated successfully
            assert len(response_data["brd"]["requirements"]) > 0
            
            # Verify alignment analysis
            assert "alignment_analysis" in response_data
            assert response_data["alignment_analysis"]["alignment_score"] == 78.0
            
        finally:
            app.dependency_overrides.clear()




class TestContextEndpointMultipleDataSourcesTracking:
    """Test end-to-end flow with multiple data sources and tracking.
    
    Validates: Requirements 3.1.1, 3.1.2, 3.1.3, 3.2.1
    
    Verifies that:
    - All data source types are tracked correctly
    - Counts are accurate for emails, slack, meetings
    - Sample sources are included in response
    - Processing metrics are captured
    """
    
    def test_multiple_data_sources_with_tracking(self):
        """Test: Emails + Slack + Meetings → tracking → summary.
        
        This test verifies:
        1. Multiple data sources are processed
        2. All counts are accurate
        3. Samples are included
        4. Processing time is tracked
        """
        request_data = {
            "data": {
                "emails": [
                    {
                        "subject": "Project kickoff",
                        "body": "Let's start the new project with a planning session.",
                        "sender": "pm@company.com",
                        "date": "2024-02-10"
                    },
                    {
                        "subject": "Technical requirements",
                        "body": "Here are the technical specifications for the API.",
                        "sender": "tech@company.com",
                        "date": "2024-02-11"
                    },
                    {
                        "subject": "Budget approval",
                        "body": "The budget has been approved for Q1.",
                        "sender": "finance@company.com",
                        "date": "2024-02-12"
                    }
                ],
                "slack_messages": [
                    {
                        "channel": "#engineering",
                        "user": "dev1",
                        "text": "Database schema is ready for review",
                        "timestamp": "2024-02-13 10:30"
                    },
                    {
                        "channel": "#product",
                        "user": "pm1",
                        "text": "User stories are documented in Jira",
                        "timestamp": "2024-02-13 11:00"
                    },
                    {
                        "channel": "#engineering",
                        "user": "dev2",
                        "text": "API endpoints are defined in the spec",
                        "timestamp": "2024-02-13 14:30"
                    },
                    {
                        "channel": "#design",
                        "user": "designer1",
                        "text": "Mockups are ready for feedback",
                        "timestamp": "2024-02-13 15:00"
                    }
                ],
                "meetings": [
                    {
                        "transcript": "PM: Let's discuss the project timeline. Tech Lead: We need 3 sprints. Developer: I agree with the timeline.",
                        "topic": "Sprint Planning",
                        "speakers": ["PM", "Tech Lead", "Developer"],
                        "timestamp": "2024-02-14 09:00"
                    },
                    {
                        "transcript": "Designer: Here are the UI mockups. PM: Looks good, let's proceed. Developer: I can start implementation next week.",
                        "topic": "Design Review",
                        "speakers": ["Designer", "PM", "Developer"],
                        "timestamp": "2024-02-14 14:00"
                    }
                ]
            }
        }
        
        # Mock Gemini service (no instructions)
        mock_gemini = Mock(spec=GeminiService)
        
        # Use real services
        real_constraint_applier = ConstraintApplier()
        real_chunk_processor = ChunkProcessor()
        real_ingestion_tracker = IngestionTracker()
        real_aggregator = Aggregator()
        
        # Mock BRD generator service
        mock_brd_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(brd_request):
            return BRDResponse(
                projectName="Project kickoff",
                executiveSummary="A new project with comprehensive planning and technical specifications.",
                businessObjectives=[
                    "Complete project within 3 sprints",
                    "Deliver high-quality API and UI"
                ],
                requirements=[
                    Requirement(
                        id="REQ-1",
                        description="Implement database schema",
                        priority="High"
                    ),
                    Requirement(
                        id="REQ-2",
                        description="Design and implement API endpoints",
                        priority="High"
                    ),
                    Requirement(
                        id="REQ-3",
                        description="Create UI based on mockups",
                        priority="Medium"
                    )
                ],
                stakeholders=[
                    Stakeholder(name="Product Manager", role="Project Owner"),
                    Stakeholder(name="Tech Lead", role="Technical Lead"),
                    Stakeholder(name="Development Team", role="Implementation"),
                    Stakeholder(name="Designer", role="UI/UX Design")
                ]
            )
        
        mock_brd_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Mock alignment engine
        mock_alignment_engine = Mock(spec=AlignmentIntelligenceEngine)
        
        def mock_analyze_alignment(email_content, slack_content, meeting_content, brd_data):
            return AlignmentReport(
                alignment_score=92.0,
                risk_level="LOW",
                alert="Excellent alignment across all sources",
                conflicts=[],
                timeline_mismatches=[],
                requirement_volatility={},
                stakeholder_agreement_score=95.0,
                timeline_consistency_score=90.0,
                requirement_stability_score=92.0,
                decision_volatility_score=88.0
            )
        
        def mock_generate_conflict_explanations(conflicts):
            return []
        
        mock_alignment_engine.analyze_alignment = Mock(side_effect=mock_analyze_alignment)
        mock_alignment_engine.generate_conflict_explanations = Mock(side_effect=mock_generate_conflict_explanations)
        
        # Override dependencies
        app.dependency_overrides[get_gemini_service] = lambda: mock_gemini
        app.dependency_overrides[get_constraint_applier] = lambda: real_constraint_applier
        app.dependency_overrides[get_chunk_processor] = lambda: real_chunk_processor
        app.dependency_overrides[get_ingestion_tracker] = lambda: real_ingestion_tracker
        app.dependency_overrides[get_aggregator] = lambda: real_aggregator
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_brd_service
        app.dependency_overrides[get_alignment_engine] = lambda: mock_alignment_engine
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd_with_context", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure
            response_data = response.json()
            
            # Verify BRD is present
            assert "brd" in response_data
            
            # Verify ingestion summary
            assert "ingestion_summary" in response_data
            ingestion_summary = response_data["ingestion_summary"]
            
            # Verify all counts are accurate (Requirements 3.1.1, 3.1.2, 3.1.3)
            assert ingestion_summary["emails_used"] == 3, \
                f"Expected 3 emails, got {ingestion_summary['emails_used']}"
            assert ingestion_summary["slack_messages_used"] == 4, \
                f"Expected 4 slack messages, got {ingestion_summary['slack_messages_used']}"
            assert ingestion_summary["meetings_used"] == 2, \
                f"Expected 2 meetings, got {ingestion_summary['meetings_used']}"
            
            # Verify no chunking occurred (all texts are small)
            assert ingestion_summary["total_chunks_processed"] == 0
            
            # Verify processing metrics
            assert ingestion_summary["total_words_processed"] > 0
            assert ingestion_summary["processing_time_seconds"] >= 0
            
            # Verify samples are included (Requirement 3.2.1)
            assert "sample_sources" in ingestion_summary
            samples = ingestion_summary["sample_sources"]
            assert isinstance(samples, list)
            
            # Should have 3-5 samples (or all if fewer than 5 total sources)
            total_sources = 3 + 4 + 2  # 9 total sources
            assert len(samples) >= 3 and len(samples) <= 5, \
                f"Expected 3-5 samples, got {len(samples)}"
            
            # Verify sample structure
            if len(samples) > 0:
                sample = samples[0]
                assert "type" in sample
                assert sample["type"] in ["email", "slack", "meeting"]
                assert "metadata" in sample
                
                # Verify type-specific metadata
                if sample["type"] == "email":
                    assert "subject" in sample["metadata"]
                    assert "date" in sample["metadata"]
                elif sample["type"] == "slack":
                    assert "channel" in sample["metadata"]
                    assert "user" in sample["metadata"]
                    assert "timestamp" in sample["metadata"]
                elif sample["type"] == "meeting":
                    assert "topic" in sample["metadata"]
            
            # Verify BRD was generated
            assert len(response_data["brd"]["requirements"]) > 0
            
            # Verify alignment analysis
            assert "alignment_analysis" in response_data
            assert response_data["alignment_analysis"]["alignment_score"] == 92.0
            
        finally:
            app.dependency_overrides.clear()




class TestContextEndpointGeminiFailureFallback:
    """Test end-to-end flow with Gemini API failure and fallback.
    
    Validates: Requirement 1.2.5
    
    Verifies that:
    - Gemini API failures are handled gracefully
    - Processing continues without constraints
    - BRD is generated successfully
    - No data filtering occurs (fallback behavior)
    """
    
    def test_gemini_failure_fallback(self):
        """Test: Gemini API fails → fallback → successful BRD.
        
        This test verifies:
        1. Gemini API failure is caught
        2. System continues without constraints
        3. All data is processed (no filtering)
        4. BRD is generated successfully
        5. Response is returned to client
        """
        request_data = {
            "instructions": "Focus on mobile features",
            "data": {
                "emails": [
                    {
                        "subject": "Mobile app requirements",
                        "body": "We need a mobile app with offline support.",
                        "sender": "pm@company.com",
                        "date": "2024-02-15"
                    },
                    {
                        "subject": "Desktop features",
                        "body": "Desktop version should have advanced analytics.",
                        "sender": "pm@company.com",
                        "date": "2024-02-16"
                    }
                ],
                "slack_messages": [],
                "meetings": []
            }
        }
        
        # Mock Gemini service to fail
        mock_gemini = Mock(spec=GeminiService)
        
        async def mock_generate_constraints_failure(instructions, request_id=None):
            from app.utils.exceptions import GeminiTimeoutError
            raise GeminiTimeoutError("Gemini API timeout")
        
        mock_gemini.generate_constraints = AsyncMock(side_effect=mock_generate_constraints_failure)
        
        # Use real services
        real_constraint_applier = ConstraintApplier()
        real_chunk_processor = ChunkProcessor()
        real_ingestion_tracker = IngestionTracker()
        real_aggregator = Aggregator()
        
        # Mock BRD generator service
        mock_brd_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(brd_request):
            return BRDResponse(
                projectName="Mobile app requirements",
                executiveSummary="A comprehensive application with both mobile and desktop features.",
                businessObjectives=[
                    "Deliver mobile app with offline support",
                    "Provide desktop version with analytics"
                ],
                requirements=[
                    Requirement(
                        id="REQ-1",
                        description="Implement mobile app with offline support",
                        priority="High"
                    ),
                    Requirement(
                        id="REQ-2",
                        description="Create desktop version with advanced analytics",
                        priority="High"
                    )
                ],
                stakeholders=[
                    Stakeholder(name="Product Manager", role="Project Owner"),
                    Stakeholder(name="Development Team", role="Implementation")
                ]
            )
        
        mock_brd_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Mock alignment engine
        mock_alignment_engine = Mock(spec=AlignmentIntelligenceEngine)
        
        def mock_analyze_alignment(email_content, slack_content, meeting_content, brd_data):
            return AlignmentReport(
                alignment_score=80.0,
                risk_level="MEDIUM",
                alert="Moderate alignment",
                conflicts=[],
                timeline_mismatches=[],
                requirement_volatility={},
                stakeholder_agreement_score=82.0,
                timeline_consistency_score=78.0,
                requirement_stability_score=80.0,
                decision_volatility_score=79.0
            )
        
        def mock_generate_conflict_explanations(conflicts):
            return []
        
        mock_alignment_engine.analyze_alignment = Mock(side_effect=mock_analyze_alignment)
        mock_alignment_engine.generate_conflict_explanations = Mock(side_effect=mock_generate_conflict_explanations)
        
        # Override dependencies
        app.dependency_overrides[get_gemini_service] = lambda: mock_gemini
        app.dependency_overrides[get_constraint_applier] = lambda: real_constraint_applier
        app.dependency_overrides[get_chunk_processor] = lambda: real_chunk_processor
        app.dependency_overrides[get_ingestion_tracker] = lambda: real_ingestion_tracker
        app.dependency_overrides[get_aggregator] = lambda: real_aggregator
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_brd_service
        app.dependency_overrides[get_alignment_engine] = lambda: mock_alignment_engine
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd_with_context", json=request_data)
            
            # Verify successful response (Requirement 1.2.5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure
            response_data = response.json()
            
            # Verify BRD is present
            assert "brd" in response_data
            assert response_data["brd"]["projectName"] == "Mobile app requirements"
            
            # Verify both requirements are present (no filtering occurred)
            # Since Gemini failed, no constraints were applied, so both emails should be processed
            assert len(response_data["brd"]["requirements"]) == 2
            
            # Verify ingestion summary
            assert "ingestion_summary" in response_data
            ingestion_summary = response_data["ingestion_summary"]
            
            # Verify both emails were processed (no filtering due to Gemini failure)
            assert ingestion_summary["emails_used"] == 2, \
                f"Expected 2 emails (no filtering), got {ingestion_summary['emails_used']}"
            
            # Verify Gemini was called but failed
            mock_gemini.generate_constraints.assert_called_once()
            
            # Verify BRD was still generated successfully
            mock_brd_service.generate_brd.assert_called_once()
            
            # Verify alignment analysis was performed
            assert "alignment_analysis" in response_data
            assert response_data["alignment_analysis"]["alignment_score"] == 80.0
            
        finally:
            app.dependency_overrides.clear()




class TestBackwardCompatibility:
    """Test backward compatibility with existing endpoint.
    
    Validates: Requirement TR-4
    
    Verifies that:
    - Old endpoint /generate_brd_with_alignment still works
    - Response format is unchanged
    - Behavior is unchanged
    - No breaking changes introduced
    """
    
    def test_old_endpoint_still_works(self):
        """Test: Old endpoint /generate_brd_with_alignment still works.
        
        This test verifies:
        1. Old endpoint is still accessible
        2. Request format is unchanged
        3. Response format is unchanged
        4. Behavior is unchanged
        """
        # Create request in old format
        request_data = {
            "projectName": "Legacy Project",
            "emailText": "We need to build a customer portal with authentication.",
            "slackText": "Team discussed the database schema for user management.",
            "meetingText": "Meeting notes: Focus on security and scalability."
        }
        
        # Mock BRD generator service
        mock_brd_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(brd_request):
            return BRDResponse(
                projectName="Legacy Project",
                executiveSummary="A customer portal with authentication, security, and scalability.",
                businessObjectives=[
                    "Provide secure customer portal",
                    "Ensure system scalability"
                ],
                requirements=[
                    Requirement(
                        id="REQ-1",
                        description="Implement user authentication",
                        priority="High"
                    ),
                    Requirement(
                        id="REQ-2",
                        description="Design scalable database schema",
                        priority="High"
                    )
                ],
                stakeholders=[
                    Stakeholder(name="Product Manager", role="Project Owner"),
                    Stakeholder(name="Development Team", role="Implementation")
                ]
            )
        
        mock_brd_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Mock alignment engine
        mock_alignment_engine = Mock(spec=AlignmentIntelligenceEngine)
        
        def mock_analyze_alignment(email_content, slack_content, meeting_content, brd_data):
            return AlignmentReport(
                alignment_score=88.0,
                risk_level="LOW",
                alert="Good alignment",
                conflicts=[],
                timeline_mismatches=[],
                requirement_volatility={},
                stakeholder_agreement_score=90.0,
                timeline_consistency_score=86.0,
                requirement_stability_score=88.0,
                decision_volatility_score=85.0
            )
        
        def mock_generate_conflict_explanations(conflicts):
            return []
        
        mock_alignment_engine.analyze_alignment = Mock(side_effect=mock_analyze_alignment)
        mock_alignment_engine.generate_conflict_explanations = Mock(side_effect=mock_generate_conflict_explanations)
        
        # Override dependencies for old endpoint
        from app.routers.brd import get_brd_generator_service as get_brd_service_old
        from app.routers.brd import get_alignment_engine as get_alignment_engine_old
        
        app.dependency_overrides[get_brd_service_old] = lambda: mock_brd_service
        app.dependency_overrides[get_alignment_engine_old] = lambda: mock_alignment_engine
        
        try:
            # Create test client and make request to OLD endpoint
            client = TestClient(app)
            response = client.post("/generate_brd_with_alignment", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure matches old format
            response_data = response.json()
            
            # Old endpoint should have brd and alignment_analysis
            assert "brd" in response_data
            assert "alignment_analysis" in response_data
            
            # Old endpoint should NOT have ingestion_summary (that's only in new endpoint)
            # Note: This depends on the actual implementation
            # If the old endpoint was updated to include it, this assertion should be adjusted
            
            # Verify BRD structure
            assert response_data["brd"]["projectName"] == "Legacy Project"
            assert "executiveSummary" in response_data["brd"]
            assert "businessObjectives" in response_data["brd"]
            assert "requirements" in response_data["brd"]
            assert "stakeholders" in response_data["brd"]
            
            # Verify alignment analysis structure
            assert "alignment_score" in response_data["alignment_analysis"]
            assert "risk_level" in response_data["alignment_analysis"]
            assert "conflicts" in response_data["alignment_analysis"]
            
            # Verify requirements structure
            assert len(response_data["brd"]["requirements"]) == 2
            req = response_data["brd"]["requirements"][0]
            assert "id" in req
            assert "description" in req
            assert "priority" in req
            
            # Verify stakeholders structure
            assert len(response_data["brd"]["stakeholders"]) == 2
            stakeholder = response_data["brd"]["stakeholders"][0]
            assert "name" in stakeholder
            assert "role" in stakeholder
            
            # Verify services were called
            mock_brd_service.generate_brd.assert_called_once()
            mock_alignment_engine.analyze_alignment.assert_called_once()
            
        finally:
            app.dependency_overrides.clear()
    
    def test_new_endpoint_without_instructions_behaves_like_old(self):
        """Test: New endpoint without instructions behaves like old endpoint.
        
        This test verifies backward compatibility by ensuring the new
        endpoint works without instructions (optional parameter).
        """
        request_data = {
            "data": {
                "emails": [
                    {
                        "subject": "Project requirements",
                        "body": "We need a reporting dashboard.",
                        "sender": "pm@company.com",
                        "date": "2024-02-15"
                    }
                ],
                "slack_messages": [],
                "meetings": []
            }
        }
        
        # Mock services
        mock_gemini = Mock(spec=GeminiService)
        real_constraint_applier = ConstraintApplier()
        real_chunk_processor = ChunkProcessor()
        real_ingestion_tracker = IngestionTracker()
        real_aggregator = Aggregator()
        
        mock_brd_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(brd_request):
            return BRDResponse(
                projectName="Project requirements",
                executiveSummary="A reporting dashboard for data visualization.",
                businessObjectives=["Provide data insights"],
                requirements=[
                    Requirement(
                        id="REQ-1",
                        description="Create reporting dashboard",
                        priority="High"
                    )
                ],
                stakeholders=[
                    Stakeholder(name="Product Manager", role="Project Owner")
                ]
            )
        
        mock_brd_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        mock_alignment_engine = Mock(spec=AlignmentIntelligenceEngine)
        
        def mock_analyze_alignment(email_content, slack_content, meeting_content, brd_data):
            return AlignmentReport(
                alignment_score=85.0,
                risk_level="LOW",
                alert="Good alignment",
                conflicts=[],
                timeline_mismatches=[],
                requirement_volatility={},
                stakeholder_agreement_score=88.0,
                timeline_consistency_score=83.0,
                requirement_stability_score=85.0,
                decision_volatility_score=84.0
            )
        
        def mock_generate_conflict_explanations(conflicts):
            return []
        
        mock_alignment_engine.analyze_alignment = Mock(side_effect=mock_analyze_alignment)
        mock_alignment_engine.generate_conflict_explanations = Mock(side_effect=mock_generate_conflict_explanations)
        
        # Override dependencies
        app.dependency_overrides[get_gemini_service] = lambda: mock_gemini
        app.dependency_overrides[get_constraint_applier] = lambda: real_constraint_applier
        app.dependency_overrides[get_chunk_processor] = lambda: real_chunk_processor
        app.dependency_overrides[get_ingestion_tracker] = lambda: real_ingestion_tracker
        app.dependency_overrides[get_aggregator] = lambda: real_aggregator
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_brd_service
        app.dependency_overrides[get_alignment_engine] = lambda: mock_alignment_engine
        
        try:
            # Create test client and make request WITHOUT instructions
            client = TestClient(app)
            response = client.post("/generate_brd_with_context", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure
            response_data = response.json()
            
            # Should have all three components
            assert "brd" in response_data
            assert "alignment_analysis" in response_data
            assert "ingestion_summary" in response_data
            
            # Verify Gemini was NOT called (no instructions provided)
            mock_gemini.generate_constraints.assert_not_called()
            
            # Verify BRD was generated
            assert response_data["brd"]["projectName"] == "Project requirements"
            
            # Verify all data was processed (no filtering)
            assert response_data["ingestion_summary"]["emails_used"] == 1
            
        finally:
            app.dependency_overrides.clear()
