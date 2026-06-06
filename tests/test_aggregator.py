"""Unit tests for Aggregator.

This module contains unit tests for the Aggregator service,
testing specific examples and edge cases.
"""

import pytest
from app.services.aggregator import Aggregator
from app.models.chunk_models import ExtractionResult, Decision, Timeline


class TestAggregator:
    """Unit tests for Aggregator class."""
    
    def test_aggregate_empty_chunk_results(self):
        """Test aggregation with empty chunk results list."""
        aggregator = Aggregator()
        result = aggregator.aggregate_chunks([])
        
        assert isinstance(result, ExtractionResult)
        assert result.requirements == []
        assert result.decisions == []
        assert result.stakeholders == []
        assert result.timelines == []
    
    def test_aggregate_single_chunk(self):
        """Test aggregation with single chunk (should return as-is)."""
        aggregator = Aggregator()
        
        chunk = ExtractionResult(
            requirements=["Requirement 1", "Requirement 2"],
            decisions=[Decision(description="Decision 1", timestamp="2024-02-15 10:00", decision_maker="PM")],
            stakeholders=["PM", "Tech Lead"],
            timelines=[Timeline(milestone="MVP", start_date="2024-03-01", end_date="2024-06-30", status="planned")]
        )
        
        result = aggregator.aggregate_chunks([chunk])
        
        assert result == chunk
        assert len(result.requirements) == 2
        assert len(result.decisions) == 1
        assert len(result.stakeholders) == 2
        assert len(result.timelines) == 1
    
    def test_deduplicate_exact_requirements(self):
        """Test deduplication of exact duplicate requirements."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=["User authentication required", "Database must be PostgreSQL"],
            decisions=[],
            stakeholders=[],
            timelines=[]
        )
        
        chunk2 = ExtractionResult(
            requirements=["User authentication required", "API must be RESTful"],
            decisions=[],
            stakeholders=[],
            timelines=[]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 3 unique requirements (duplicate removed)
        assert len(result.requirements) == 3
        assert "User authentication required" in result.requirements
        assert "Database must be PostgreSQL" in result.requirements
        assert "API must be RESTful" in result.requirements
    
    def test_deduplicate_similar_requirements(self):
        """Test deduplication of similar requirements (>80% similarity)."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=["User authentication is required"],
            decisions=[],
            stakeholders=[],
            timelines=[]
        )
        
        chunk2 = ExtractionResult(
            requirements=["User authentication is required."],  # Very similar (just added period)
            decisions=[],
            stakeholders=[],
            timelines=[]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 1 requirement (similar one deduplicated)
        assert len(result.requirements) == 1
    
    def test_merge_decisions_keep_latest(self):
        """Test that decisions with same description keep the latest timestamp."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=[],
            decisions=[
                Decision(description="Use React", timestamp="2024-02-15 10:00", decision_maker="Tech Lead")
            ],
            stakeholders=[],
            timelines=[]
        )
        
        chunk2 = ExtractionResult(
            requirements=[],
            decisions=[
                Decision(description="Use React", timestamp="2024-02-16 11:00", decision_maker="CTO")
            ],
            stakeholders=[],
            timelines=[]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 1 decision with latest timestamp
        assert len(result.decisions) == 1
        assert result.decisions[0].timestamp == "2024-02-16 11:00"
        assert result.decisions[0].decision_maker == "CTO"
    
    def test_merge_decisions_different_descriptions(self):
        """Test that decisions with different descriptions are all kept."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=[],
            decisions=[
                Decision(description="Use React", timestamp="2024-02-15 10:00", decision_maker="Tech Lead"),
                Decision(description="Use PostgreSQL", timestamp="2024-02-14 09:00", decision_maker="DBA")
            ],
            stakeholders=[],
            timelines=[]
        )
        
        chunk2 = ExtractionResult(
            requirements=[],
            decisions=[
                Decision(description="Use MongoDB", timestamp="2024-02-15 10:00", decision_maker="Architect")
            ],
            stakeholders=[],
            timelines=[]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 3 different decisions
        assert len(result.decisions) == 3
        descriptions = [d.description for d in result.decisions]
        assert "Use React" in descriptions
        assert "Use PostgreSQL" in descriptions
        assert "Use MongoDB" in descriptions
    
    def test_merge_stakeholders_case_insensitive(self):
        """Test that stakeholders are deduplicated case-insensitively."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=[],
            decisions=[],
            stakeholders=["PM", "Tech Lead", "Designer"],
            timelines=[]
        )
        
        chunk2 = ExtractionResult(
            requirements=[],
            decisions=[],
            stakeholders=["tech lead", "Developer", "pm"],  # Duplicates with different case
            timelines=[]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 4 unique stakeholders (PM, Tech Lead, Designer, Developer)
        assert len(result.stakeholders) == 4
        
        # Check that we have the unique ones (case-insensitive)
        stakeholders_lower = [s.lower() for s in result.stakeholders]
        assert "pm" in stakeholders_lower
        assert "tech lead" in stakeholders_lower
        assert "designer" in stakeholders_lower
        assert "developer" in stakeholders_lower
    
    def test_merge_timelines_earliest_start_latest_end(self):
        """Test that timelines merge with earliest start and latest end dates."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=[],
            decisions=[],
            stakeholders=[],
            timelines=[
                Timeline(milestone="MVP", start_date="2024-03-01", end_date="2024-06-30", status="planned")
            ]
        )
        
        chunk2 = ExtractionResult(
            requirements=[],
            decisions=[],
            stakeholders=[],
            timelines=[
                Timeline(milestone="MVP", start_date="2024-02-15", end_date="2024-07-15", status="active")
            ]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 1 timeline with earliest start and latest end
        assert len(result.timelines) == 1
        assert result.timelines[0].milestone == "MVP"
        assert result.timelines[0].start_date == "2024-02-15"  # Earliest
        assert result.timelines[0].end_date == "2024-07-15"    # Latest
        assert result.timelines[0].status == "active"  # Non-empty status preferred
    
    def test_merge_timelines_different_milestones(self):
        """Test that timelines with different milestones are all kept."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=[],
            decisions=[],
            stakeholders=[],
            timelines=[
                Timeline(milestone="MVP", start_date="2024-03-01", end_date="2024-06-30", status="planned"),
                Timeline(milestone="Beta", start_date="2024-07-01", end_date="2024-08-31", status="planned")
            ]
        )
        
        chunk2 = ExtractionResult(
            requirements=[],
            decisions=[],
            stakeholders=[],
            timelines=[
                Timeline(milestone="GA", start_date="2024-09-01", end_date="2024-12-31", status="planned")
            ]
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2])
        
        # Should have 3 different timelines
        assert len(result.timelines) == 3
        milestones = [t.milestone for t in result.timelines]
        assert "MVP" in milestones
        assert "Beta" in milestones
        assert "GA" in milestones
    
    def test_aggregate_multiple_chunks_comprehensive(self):
        """Test comprehensive aggregation with multiple chunks and all field types."""
        aggregator = Aggregator()
        
        chunk1 = ExtractionResult(
            requirements=["User authentication must support OAuth 2.0", "Database must be PostgreSQL"],
            decisions=[Decision(description="Decision 1", timestamp="2024-02-15 10:00", decision_maker="PM")],
            stakeholders=["PM", "Tech Lead"],
            timelines=[Timeline(milestone="MVP", start_date="2024-03-01", end_date="2024-06-30", status="planned")]
        )
        
        chunk2 = ExtractionResult(
            requirements=["Database must be PostgreSQL", "API must be RESTful"],  # Duplicate Database requirement
            decisions=[Decision(description="Decision 2", timestamp="2024-02-16 11:00", decision_maker="CTO")],
            stakeholders=["Tech Lead", "Designer"],  # Duplicate Tech Lead
            timelines=[Timeline(milestone="Beta", start_date="2024-07-01", end_date="2024-08-31", status="planned")]
        )
        
        chunk3 = ExtractionResult(
            requirements=["System must handle 1000 concurrent users"],
            decisions=[Decision(description="Decision 1", timestamp="2024-02-17 09:00", decision_maker="Architect")],  # Duplicate Decision 1
            stakeholders=["Developer"],
            timelines=[Timeline(milestone="MVP", start_date="2024-02-15", end_date="2024-07-15", status="active")]  # Duplicate MVP
        )
        
        result = aggregator.aggregate_chunks([chunk1, chunk2, chunk3])
        
        # Requirements: 4 unique (Database requirement deduplicated)
        assert len(result.requirements) == 4
        
        # Decisions: 2 unique (Decision 1 merged, keeping latest)
        assert len(result.decisions) == 2
        decision_1 = [d for d in result.decisions if d.description == "Decision 1"][0]
        assert decision_1.timestamp == "2024-02-17 09:00"  # Latest timestamp
        
        # Stakeholders: 4 unique (Tech Lead deduplicated)
        assert len(result.stakeholders) == 4
        
        # Timelines: 2 unique (MVP merged with earliest start, latest end)
        assert len(result.timelines) == 2
        mvp_timeline = [t for t in result.timelines if t.milestone == "MVP"][0]
        assert mvp_timeline.start_date == "2024-02-15"  # Earliest
        assert mvp_timeline.end_date == "2024-07-15"    # Latest
        assert mvp_timeline.status == "active"  # Non-empty status
