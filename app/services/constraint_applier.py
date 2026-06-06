"""Constraint applier service for filtering and prioritizing data.

This module implements the ConstraintApplier class that applies structured
constraints to filter and prioritize ingested data based on user instructions.
"""

import logging
from typing import Optional, List, Union
from ..models.constraints import Constraints
from ..models.context_request import IngestionData
from ..models.request import Email, SlackMessage, Meeting

logger = logging.getLogger(__name__)


class ConstraintApplier:
    """Service for applying constraints to filter and prioritize data.
    
    This class implements filtering and prioritization logic based on
    structured constraints generated from user instructions. It supports:
    - Scope-based filtering
    - Topic exclusion
    - Priority scoring and ranking
    
    The applier handles None constraints gracefully by returning data unchanged.
    """
    
    def apply_constraints(
        self,
        data: IngestionData,
        constraints: Optional[Constraints]
    ) -> IngestionData:
        """Apply constraints to filter and prioritize data.
        
        Filters and reorders ingestion data based on the provided constraints.
        If constraints is None, returns data unchanged.
        
        Args:
            data: Raw ingestion data (emails, slack messages, meetings)
            constraints: Structured constraints from Gemini (or None)
            
        Returns:
            Filtered and prioritized IngestionData
            
        Example:
            >>> applier = ConstraintApplier()
            >>> constraints = Constraints(
            ...     scope="MVP features",
            ...     exclude_topics=["marketing"],
            ...     priority_focus="core functionality"
            ... )
            >>> filtered_data = applier.apply_constraints(data, constraints)
        """
        # Handle None constraints - return data unchanged
        if constraints is None:
            logger.info("No constraints provided, returning data unchanged")
            return data
        
        # Log initial counts
        initial_counts = {
            "emails": len(data.emails),
            "slack_messages": len(data.slack_messages),
            "meetings": len(data.meetings)
        }
        logger.info(f"Applying constraints to data: {initial_counts}")
        
        # Filter and prioritize each data type
        filtered_emails = self._filter_and_prioritize(
            data.emails,
            constraints,
            lambda e: f"{e.subject} {e.body}"
        )
        
        filtered_slack = self._filter_and_prioritize(
            data.slack_messages,
            constraints,
            lambda s: s.text
        )
        
        filtered_meetings = self._filter_and_prioritize(
            data.meetings,
            constraints,
            lambda m: f"{m.topic} {m.transcript}"
        )
        
        # Log filtering statistics
        final_counts = {
            "emails": len(filtered_emails),
            "slack_messages": len(filtered_slack),
            "meetings": len(filtered_meetings)
        }
        
        excluded_counts = {
            "emails": initial_counts["emails"] - final_counts["emails"],
            "slack_messages": initial_counts["slack_messages"] - final_counts["slack_messages"],
            "meetings": initial_counts["meetings"] - final_counts["meetings"]
        }
        
        logger.info(
            f"Filtering complete. Final counts: {final_counts}, "
            f"Excluded: {excluded_counts}"
        )
        
        # Return filtered data
        return IngestionData(
            emails=filtered_emails,
            slack_messages=filtered_slack,
            meetings=filtered_meetings
        )
    
    def _filter_and_prioritize(
        self,
        items: List[Union[Email, SlackMessage, Meeting]],
        constraints: Constraints,
        text_extractor: callable
    ) -> List[Union[Email, SlackMessage, Meeting]]:
        """Filter and prioritize a list of items.
        
        Args:
            items: List of items to filter
            constraints: Constraints to apply
            text_extractor: Function to extract text from an item
            
        Returns:
            Filtered and prioritized list of items
        """
        # Filter out excluded topics
        filtered_items = []
        for item in items:
            text = text_extractor(item)
            if not self._contains_excluded_topics(text, constraints.exclude_topics):
                filtered_items.append(item)
        
        # Calculate priority scores and sort
        if constraints.scope or constraints.priority_focus:
            scored_items = []
            for item in filtered_items:
                text = text_extractor(item)
                score = self._calculate_priority_score(
                    text,
                    constraints.scope,
                    constraints.priority_focus
                )
                scored_items.append((score, item))
            
            # Sort by score (descending) and extract items
            scored_items.sort(key=lambda x: x[0], reverse=True)
            return [item for score, item in scored_items]
        
        return filtered_items
    
    def _filter_by_scope(self, text: str, scope: str) -> bool:
        """Check if text matches the specified scope.
        
        Uses case-insensitive keyword matching to determine if the text
        is relevant to the specified scope.
        
        Args:
            text: Text content to check
            scope: Scope description to match against
            
        Returns:
            True if text matches scope, False otherwise
            
        Example:
            >>> applier = ConstraintApplier()
            >>> applier._filter_by_scope("MVP features discussion", "MVP")
            True
            >>> applier._filter_by_scope("Phase 2 planning", "MVP")
            False
        """
        if not scope or not text:
            return False
        
        # Extract keywords from scope (split on spaces and common separators)
        scope_keywords = scope.lower().replace(",", " ").split()
        text_lower = text.lower()
        
        # Check if any scope keyword appears in text
        return any(keyword in text_lower for keyword in scope_keywords if len(keyword) > 2)
    
    def _contains_excluded_topics(self, text: str, exclude_topics: List[str]) -> bool:
        """Check if text contains any excluded topics.
        
        Uses case-insensitive matching to detect excluded topics in the text.
        
        Args:
            text: Text content to check
            exclude_topics: List of topics to exclude
            
        Returns:
            True if text contains any excluded topic, False otherwise
            
        Example:
            >>> applier = ConstraintApplier()
            >>> applier._contains_excluded_topics(
            ...     "Marketing strategy discussion",
            ...     ["marketing", "sales"]
            ... )
            True
        """
        if not exclude_topics or not text:
            return False
        
        text_lower = text.lower()
        
        # Check if any excluded topic appears in text
        for topic in exclude_topics:
            if topic.lower() in text_lower:
                return True
        
        return False
    
    def _calculate_priority_score(
        self,
        text: str,
        scope: str,
        priority_focus: str
    ) -> float:
        """Calculate priority score for text based on scope and focus.
        
        Scores text based on how well it matches the scope and priority focus.
        Higher scores indicate higher priority.
        
        Args:
            text: Text content to score
            scope: Scope description
            priority_focus: Priority focus description
            
        Returns:
            Priority score (0.0 to 1.0+)
            
        Example:
            >>> applier = ConstraintApplier()
            >>> score = applier._calculate_priority_score(
            ...     "MVP core features",
            ...     "MVP",
            ...     "core functionality"
            ... )
            >>> score > 0.5
            True
        """
        if not text:
            return 0.0
        
        score = 0.0
        text_lower = text.lower()
        
        # Score based on scope match
        if scope:
            scope_keywords = scope.lower().replace(",", " ").split()
            scope_matches = sum(
                1 for keyword in scope_keywords
                if len(keyword) > 2 and keyword in text_lower
            )
            # Normalize by number of keywords
            if scope_keywords:
                score += (scope_matches / len(scope_keywords)) * 0.5
        
        # Score based on priority focus match
        if priority_focus:
            focus_keywords = priority_focus.lower().replace(",", " ").split()
            focus_matches = sum(
                1 for keyword in focus_keywords
                if len(keyword) > 2 and keyword in text_lower
            )
            # Normalize by number of keywords
            if focus_keywords:
                score += (focus_matches / len(focus_keywords)) * 0.5
        
        return score
