"""
Aggregator for combining extraction results from multiple chunks.
"""

from typing import List
from difflib import SequenceMatcher
from datetime import datetime
import logging

from app.models.chunk_models import ExtractionResult, Decision, Timeline

logger = logging.getLogger(__name__)


class Aggregator:
    """Service for aggregating results from multiple chunks.
    
    This service combines extraction results from multiple text chunks,
    deduplicating requirements, merging decisions, stakeholders, and timelines.
    """
    
    def aggregate_chunks(self, chunk_results: List[ExtractionResult]) -> ExtractionResult:
        """
        Aggregate results from multiple chunks.
        
        Args:
            chunk_results: List of extraction results from each chunk
            
        Returns:
            Single aggregated ExtractionResult
        """
        if not chunk_results:
            logger.warning("No chunk results to aggregate")
            return ExtractionResult()
        
        if len(chunk_results) == 1:
            logger.info(
                "Single chunk result, returning as-is",
                extra={
                    'requirements_count': len(chunk_results[0].requirements),
                    'decisions_count': len(chunk_results[0].decisions),
                    'stakeholders_count': len(chunk_results[0].stakeholders),
                    'timelines_count': len(chunk_results[0].timelines)
                }
            )
            return chunk_results[0]
        
        logger.info(
            "Aggregating chunk results",
            extra={'chunk_count': len(chunk_results)}
        )
        
        # Collect all items from all chunks
        all_requirements = []
        all_decisions = []
        all_stakeholders = []
        all_timelines = []
        
        for result in chunk_results:
            all_requirements.extend(result.requirements)
            all_decisions.extend(result.decisions)
            all_stakeholders.extend(result.stakeholders)
            all_timelines.extend(result.timelines)
        
        # Deduplicate and merge
        deduplicated_requirements = self._deduplicate_requirements(all_requirements)
        merged_decisions = self._merge_decisions(all_decisions)
        merged_stakeholders = self._merge_stakeholders(all_stakeholders)
        merged_timelines = self._merge_timelines(all_timelines)
        
        # Log deduplication statistics
        logger.info(
            "Aggregation complete",
            extra={
                'requirements_before': len(all_requirements),
                'requirements_after': len(deduplicated_requirements),
                'decisions_before': len(all_decisions),
                'decisions_after': len(merged_decisions),
                'stakeholders_before': len(all_stakeholders),
                'stakeholders_after': len(merged_stakeholders),
                'timelines_before': len(all_timelines),
                'timelines_after': len(merged_timelines)
            }
        )
        
        return ExtractionResult(
            requirements=deduplicated_requirements,
            decisions=merged_decisions,
            stakeholders=merged_stakeholders,
            timelines=merged_timelines
        )
    
    def _deduplicate_requirements(self, requirements: List[str]) -> List[str]:
        """Remove duplicate requirements using similarity matching.
        
        Uses fuzzy string matching with >80% similarity threshold to identify
        and remove duplicate requirements.
        
        Args:
            requirements: List of requirement strings
            
        Returns:
            Deduplicated list of requirements
        """
        if not requirements:
            return []
        
        deduplicated = []
        
        for req in requirements:
            # Check if this requirement is similar to any already added
            is_duplicate = False
            for existing_req in deduplicated:
                similarity = SequenceMatcher(None, req.lower(), existing_req.lower()).ratio()
                if similarity > 0.80:
                    is_duplicate = True
                    logger.debug(
                        "Duplicate requirement found",
                        extra={
                            'similarity': round(similarity, 2),
                            'requirement_preview': req[:50] + '...' if len(req) > 50 else req
                        }
                    )
                    break
            
            if not is_duplicate:
                deduplicated.append(req)
        
        return deduplicated
    
    def _merge_decisions(self, decisions: List[Decision]) -> List[Decision]:
        """Merge decisions, keeping most recent.
        
        Groups decisions by description and keeps the one with the latest timestamp.
        
        Args:
            decisions: List of Decision objects
            
        Returns:
            Merged list of decisions
        """
        if not decisions:
            return []
        
        # Group decisions by description (case-insensitive)
        decision_map = {}
        
        for decision in decisions:
            key = decision.description.lower().strip()
            
            if key not in decision_map:
                decision_map[key] = decision
            else:
                # Keep the decision with the latest timestamp
                existing_decision = decision_map[key]
                try:
                    # Try to parse timestamps for comparison
                    existing_time = self._parse_timestamp(existing_decision.timestamp)
                    new_time = self._parse_timestamp(decision.timestamp)
                    
                    if new_time > existing_time:
                        decision_map[key] = decision
                        logger.debug(
                            "Replaced decision with newer timestamp",
                            extra={
                                'decision_preview': decision.description[:50] + '...' if len(decision.description) > 50 else decision.description,
                                'old_timestamp': existing_decision.timestamp,
                                'new_timestamp': decision.timestamp
                            }
                        )
                except Exception as e:
                    # If timestamp parsing fails, keep the first one
                    logger.debug(f"Could not parse timestamps for decision comparison: {e}")
        
        return list(decision_map.values())
    
    def _merge_stakeholders(self, stakeholders: List[str]) -> List[str]:
        """Merge stakeholder lists, removing duplicates.
        
        Uses case-insensitive set-based deduplication.
        
        Args:
            stakeholders: List of stakeholder names
            
        Returns:
            Deduplicated list of stakeholders
        """
        if not stakeholders:
            return []
        
        # Use a dict to preserve order while deduplicating (case-insensitive)
        seen = {}
        for stakeholder in stakeholders:
            key = stakeholder.lower().strip()
            if key and key not in seen:
                seen[key] = stakeholder
        
        return list(seen.values())
    
    def _merge_timelines(self, timelines: List[Timeline]) -> List[Timeline]:
        """Merge timelines, resolving conflicts.
        
        Groups timelines by milestone name and resolves conflicts by:
        - Keeping earliest start date
        - Keeping latest end date
        - Preferring non-empty status values
        
        Args:
            timelines: List of Timeline objects
            
        Returns:
            Merged list of timelines
        """
        if not timelines:
            return []
        
        # Group timelines by milestone (case-insensitive)
        timeline_map = {}
        
        for timeline in timelines:
            key = timeline.milestone.lower().strip()
            
            if key not in timeline_map:
                timeline_map[key] = timeline
            else:
                # Merge with existing timeline
                existing = timeline_map[key]
                
                # Keep earliest start date
                start_date = self._select_earliest_date(existing.start_date, timeline.start_date)
                
                # Keep latest end date
                end_date = self._select_latest_date(existing.end_date, timeline.end_date)
                
                # Prefer non-empty status
                status = timeline.status if timeline.status else existing.status
                
                timeline_map[key] = Timeline(
                    milestone=existing.milestone,  # Keep original casing from first occurrence
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )
                
                logger.debug(
                    "Merged timeline for milestone",
                    extra={
                        'milestone': existing.milestone,
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': status
                    }
                )
        
        return list(timeline_map.values())
    
    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse timestamp string to datetime object.
        
        Tries multiple common timestamp formats.
        
        Args:
            timestamp: Timestamp string
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If timestamp cannot be parsed
        """
        if not timestamp:
            return datetime.min
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse timestamp: {timestamp}")
    
    def _select_earliest_date(self, date1: str, date2: str) -> str:
        """Select the earliest of two date strings.
        
        Args:
            date1: First date string
            date2: Second date string
            
        Returns:
            The earliest date string, or the non-empty one if only one is provided
        """
        if not date1:
            return date2
        if not date2:
            return date1
        
        try:
            dt1 = self._parse_timestamp(date1)
            dt2 = self._parse_timestamp(date2)
            return date1 if dt1 <= dt2 else date2
        except ValueError:
            # If parsing fails, return the first one
            return date1
    
    def _select_latest_date(self, date1: str, date2: str) -> str:
        """Select the latest of two date strings.
        
        Args:
            date1: First date string
            date2: Second date string
            
        Returns:
            The latest date string, or the non-empty one if only one is provided
        """
        if not date1:
            return date2
        if not date2:
            return date1
        
        try:
            dt1 = self._parse_timestamp(date1)
            dt2 = self._parse_timestamp(date2)
            return date1 if dt1 >= dt2 else date2
        except ValueError:
            # If parsing fails, return the first one
            return date1
