"""Alignment Intelligence Engine for ReqMind AI.

This module provides scoring and risk analysis to evaluate project alignment
by detecting conflicts, volatility, and stakeholder disagreement.
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConflictDetail:
    """Details about a detected conflict."""
    
    type: str  # "stakeholder_disagreement", "timeline_mismatch", "requirement_change"
    description: str
    sources: List[str]
    severity: str  # "high", "medium", "low"
    entities_involved: List[str]


@dataclass
class AlignmentReport:
    """Complete alignment analysis report."""
    
    alignment_score: float
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    alert: str
    conflicts: List[ConflictDetail]
    timeline_mismatches: List[Dict]
    requirement_volatility: Dict
    stakeholder_agreement_score: float
    timeline_consistency_score: float
    requirement_stability_score: float
    decision_volatility_score: float


class AlignmentIntelligenceEngine:
    """Engine for analyzing project alignment and detecting risks."""
    
    def __init__(self):
        """Initialize the alignment intelligence engine."""
        self.conflict_weight = 10
        self.timeline_weight = 15
        self.requirement_change_weight = 5
        self.decision_reversal_weight = 8
    
    def analyze_alignment(
        self,
        email_content: Optional[str],
        slack_content: Optional[str],
        meeting_content: Optional[str],
        brd_data: Dict
    ) -> AlignmentReport:
        """Analyze alignment across all communication channels.
        
        Args:
            email_content: Email communication text
            slack_content: Slack communication text
            meeting_content: Meeting transcript text
            brd_data: Generated BRD data
            
        Returns:
            AlignmentReport with scores and risk analysis
        """
        # Collect all content
        all_content = self._collect_content(email_content, slack_content, meeting_content)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(all_content, brd_data)
        
        # Analyze timeline consistency
        timeline_mismatches = self._analyze_timeline_consistency(all_content)
        
        # Analyze requirement stability
        requirement_volatility = self._analyze_requirement_stability(all_content, brd_data)
        
        # Analyze decision volatility
        decision_volatility = self._analyze_decision_volatility(all_content)
        
        # Calculate component scores
        stakeholder_agreement_score = self._calculate_stakeholder_agreement(conflicts)
        timeline_consistency_score = self._calculate_timeline_consistency(timeline_mismatches)
        requirement_stability_score = self._calculate_requirement_stability(requirement_volatility)
        decision_volatility_score = self._calculate_decision_volatility(decision_volatility)
        
        # Calculate overall alignment score
        alignment_score = self._calculate_alignment_score(
            len(conflicts),
            len(timeline_mismatches),
            requirement_volatility.get('change_count', 0),
            decision_volatility
        )
        
        # Determine risk level and alert
        risk_level, alert = self._determine_risk_level(alignment_score, conflicts, timeline_mismatches)
        
        return AlignmentReport(
            alignment_score=alignment_score,
            risk_level=risk_level,
            alert=alert,
            conflicts=conflicts,
            timeline_mismatches=timeline_mismatches,
            requirement_volatility=requirement_volatility,
            stakeholder_agreement_score=stakeholder_agreement_score,
            timeline_consistency_score=timeline_consistency_score,
            requirement_stability_score=requirement_stability_score,
            decision_volatility_score=decision_volatility_score
        )
    
    def _collect_content(
        self,
        email: Optional[str],
        slack: Optional[str],
        meeting: Optional[str]
    ) -> Dict[str, str]:
        """Collect and organize content by source."""
        content = {}
        if email:
            content['email'] = email
        if slack:
            content['slack'] = slack
        if meeting:
            content['meeting'] = meeting
        return content
    
    def _detect_conflicts(self, all_content: Dict[str, str], brd_data: Dict) -> List[ConflictDetail]:
        """Detect conflicts across communication channels.
        
        Args:
            all_content: Dictionary of content by source
            brd_data: BRD data structure
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Detect stakeholder disagreements
        stakeholder_conflicts = self._detect_stakeholder_disagreements(all_content)
        conflicts.extend(stakeholder_conflicts)
        
        # Detect priority conflicts
        priority_conflicts = self._detect_priority_conflicts(all_content)
        conflicts.extend(priority_conflicts)
        
        # Detect scope conflicts
        scope_conflicts = self._detect_scope_conflicts(all_content)
        conflicts.extend(scope_conflicts)
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        return conflicts
    
    def _detect_stakeholder_disagreements(self, all_content: Dict[str, str]) -> List[ConflictDetail]:
        """Detect disagreements between stakeholders."""
        conflicts = []
        
        # Patterns indicating disagreement
        disagreement_patterns = [
            (r"(?i)(disagree|don't agree|cannot agree)", "disagree"),
            (r"(?i)(but|however|on the other hand)", "contradiction"),
            (r"(?i)(instead|rather than|not)", "alternative"),
            (r"(?i)(wrong|incorrect|mistake)", "correction")
        ]
        
        sources_with_disagreement = []
        for source, content in all_content.items():
            for pattern, conflict_type in disagreement_patterns:
                if re.search(pattern, content):
                    sources_with_disagreement.append((source, conflict_type))
        
        if len(sources_with_disagreement) >= 2:
            conflicts.append(ConflictDetail(
                type="stakeholder_disagreement",
                description="Multiple stakeholders express conflicting views or disagreements",
                sources=[s[0] for s in sources_with_disagreement],
                severity="high",
                entities_involved=list(set([s[1] for s in sources_with_disagreement]))
            ))
        
        return conflicts
    
    def _detect_priority_conflicts(self, all_content: Dict[str, str]) -> List[ConflictDetail]:
        """Detect conflicts in priority assignments."""
        conflicts = []
        
        priority_mentions = {}
        for source, content in all_content.items():
            # Look for priority keywords
            if re.search(r"(?i)(urgent|critical|high priority|immediate)", content):
                priority_mentions[source] = "high"
            elif re.search(r"(?i)(low priority|future|later|not urgent)", content):
                priority_mentions[source] = "low"
        
        # Check for conflicting priorities
        if "high" in priority_mentions.values() and "low" in priority_mentions.values():
            high_sources = [s for s, p in priority_mentions.items() if p == "high"]
            low_sources = [s for s, p in priority_mentions.items() if p == "low"]
            
            conflicts.append(ConflictDetail(
                type="priority_conflict",
                description=f"Priority mismatch: {', '.join(high_sources)} indicate high priority while {', '.join(low_sources)} indicate low priority",
                sources=list(priority_mentions.keys()),
                severity="high",
                entities_involved=["priority"]
            ))
        
        return conflicts
    
    def _detect_scope_conflicts(self, all_content: Dict[str, str]) -> List[ConflictDetail]:
        """Detect conflicts in project scope."""
        conflicts = []
        
        scope_mentions = {}
        for source, content in all_content.items():
            if re.search(r"(?i)(simple|basic|minimal|small)", content):
                scope_mentions[source] = "small"
            elif re.search(r"(?i)(complex|advanced|comprehensive|large)", content):
                scope_mentions[source] = "large"
        
        # Check for conflicting scope
        if "small" in scope_mentions.values() and "large" in scope_mentions.values():
            small_sources = [s for s, p in scope_mentions.items() if p == "small"]
            large_sources = [s for s, p in scope_mentions.items() if p == "large"]
            
            conflicts.append(ConflictDetail(
                type="scope_conflict",
                description=f"Scope mismatch: {', '.join(small_sources)} suggest simple implementation while {', '.join(large_sources)} suggest complex implementation",
                sources=list(scope_mentions.keys()),
                severity="medium",
                entities_involved=["scope"]
            ))
        
        return conflicts
    
    def _analyze_timeline_consistency(self, all_content: Dict[str, str]) -> List[Dict]:
        """Analyze timeline consistency across sources."""
        timeline_mismatches = []
        
        # Extract dates from content
        date_patterns = [
            r"(?i)(?:by|before|deadline|due|deliver(?:y)?)\s+(?:by\s+)?([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
            r"(?i)(?:by|before|deadline|due)\s+(\d{1,2}/\d{1,2}(?:/\d{2,4})?)",
            r"(?i)(\d{1,2}\s+(?:days?|weeks?|months?))",
        ]
        
        dates_by_source = {}
        for source, content in all_content.items():
            dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, content)
                dates.extend(matches)
            if dates:
                dates_by_source[source] = dates
        
        # Check for mismatches
        if len(dates_by_source) >= 2:
            sources = list(dates_by_source.keys())
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    source1, source2 = sources[i], sources[j]
                    dates1, dates2 = dates_by_source[source1], dates_by_source[source2]
                    
                    # Simple check: if dates are different, flag as mismatch
                    if dates1 != dates2:
                        timeline_mismatches.append({
                            "source1": source1,
                            "source2": source2,
                            "dates1": dates1,
                            "dates2": dates2,
                            "description": f"Timeline mismatch between {source1} ({', '.join(dates1)}) and {source2} ({', '.join(dates2)})"
                        })
        
        logger.info(f"Detected {len(timeline_mismatches)} timeline mismatches")
        return timeline_mismatches
    
    def _analyze_requirement_stability(
        self,
        all_content: Dict[str, str],
        brd_data: Dict
    ) -> Dict:
        """Analyze how stable requirements are across communications."""
        
        # Keywords indicating changes
        change_keywords = [
            "change", "update", "modify", "revise", "adjust",
            "instead", "actually", "correction", "new version"
        ]
        
        change_count = 0
        change_sources = []
        
        for source, content in all_content.items():
            content_lower = content.lower()
            for keyword in change_keywords:
                if keyword in content_lower:
                    change_count += 1
                    change_sources.append(source)
                    break
        
        # Calculate stability score
        total_sources = len(all_content)
        stability_percentage = 100 - (change_count / max(total_sources, 1) * 100)
        
        return {
            "change_count": change_count,
            "change_sources": change_sources,
            "stability_percentage": round(stability_percentage, 2),
            "total_requirements": len(brd_data.get('requirements', []))
        }
    
    def _analyze_decision_volatility(self, all_content: Dict[str, str]) -> int:
        """Analyze frequency of decision changes or reversals."""
        
        reversal_patterns = [
            r"(?i)(changed my mind|reconsidered|actually|instead)",
            r"(?i)(no longer|not anymore|cancel|revert)",
            r"(?i)(new decision|different approach|alternative)"
        ]
        
        reversal_count = 0
        for content in all_content.values():
            for pattern in reversal_patterns:
                reversal_count += len(re.findall(pattern, content))
        
        return reversal_count
    
    def _calculate_stakeholder_agreement(self, conflicts: List[ConflictDetail]) -> float:
        """Calculate stakeholder agreement score."""
        stakeholder_conflicts = [c for c in conflicts if c.type == "stakeholder_disagreement"]
        if not stakeholder_conflicts:
            return 100.0
        
        # Reduce score based on number and severity of conflicts
        score = 100.0
        for conflict in stakeholder_conflicts:
            if conflict.severity == "high":
                score -= 20
            elif conflict.severity == "medium":
                score -= 10
            else:
                score -= 5
        
        return max(0.0, score)
    
    def _calculate_timeline_consistency(self, timeline_mismatches: List[Dict]) -> float:
        """Calculate timeline consistency score."""
        if not timeline_mismatches:
            return 100.0
        
        # Each mismatch reduces score
        score = 100.0 - (len(timeline_mismatches) * 15)
        return max(0.0, score)
    
    def _calculate_requirement_stability(self, volatility: Dict) -> float:
        """Calculate requirement stability score."""
        return volatility.get('stability_percentage', 100.0)
    
    def _calculate_decision_volatility(self, reversal_count: int) -> float:
        """Calculate decision volatility score."""
        if reversal_count == 0:
            return 100.0
        
        score = 100.0 - (reversal_count * 8)
        return max(0.0, score)
    
    def _calculate_alignment_score(
        self,
        conflict_count: int,
        timeline_mismatch_count: int,
        requirement_change_count: int,
        decision_reversal_count: int
    ) -> float:
        """Calculate overall alignment score.
        
        Formula: 100 - (conflicts × 10) - (timeline_mismatches × 15) - (req_changes × 5) - (reversals × 8)
        """
        score = 100.0
        score -= conflict_count * self.conflict_weight
        score -= timeline_mismatch_count * self.timeline_weight
        score -= requirement_change_count * self.requirement_change_weight
        score -= decision_reversal_count * self.decision_reversal_weight
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    def _determine_risk_level(
        self,
        alignment_score: float,
        conflicts: List[ConflictDetail],
        timeline_mismatches: List[Dict]
    ) -> Tuple[str, str]:
        """Determine risk level and generate alert message.
        
        Args:
            alignment_score: Overall alignment score
            conflicts: List of detected conflicts
            timeline_mismatches: List of timeline mismatches
            
        Returns:
            Tuple of (risk_level, alert_message)
        """
        if alignment_score < 70:
            risk_level = "HIGH"
            
            # Build detailed alert
            issues = []
            if conflicts:
                issues.append(f"{len(conflicts)} conflict(s)")
            if timeline_mismatches:
                issues.append(f"{len(timeline_mismatches)} timeline mismatch(es)")
            
            if issues:
                alert = f"Stakeholder disagreement detected: {', '.join(issues)}. Immediate review required."
            else:
                alert = "Stakeholder disagreement detected. Immediate review required."
        
        elif alignment_score < 85:
            risk_level = "MEDIUM"
            alert = "Potential misalignment detected. Monitor changes closely."
        
        else:
            risk_level = "LOW"
            alert = "Project alignment is stable. Continue monitoring."
        
        return risk_level, alert
    
    def generate_conflict_explanations(self, conflicts: List[ConflictDetail]) -> List[Dict]:
        """Generate detailed explanations for each conflict with source references.
        
        Args:
            conflicts: List of detected conflicts
            
        Returns:
            List of conflict explanations with sources
        """
        explanations = []
        
        for conflict in conflicts:
            explanation = {
                "type": conflict.type,
                "description": conflict.description,
                "severity": conflict.severity,
                "sources": conflict.sources,
                "entities_involved": conflict.entities_involved,
                "recommendation": self._get_conflict_recommendation(conflict)
            }
            explanations.append(explanation)
        
        return explanations
    
    def _get_conflict_recommendation(self, conflict: ConflictDetail) -> str:
        """Get recommendation for resolving a conflict."""
        recommendations = {
            "stakeholder_disagreement": "Schedule alignment meeting with all stakeholders to resolve disagreements",
            "priority_conflict": "Clarify priority with project sponsor and document in requirements",
            "scope_conflict": "Define clear scope boundaries and get stakeholder sign-off",
            "timeline_mismatch": "Establish single source of truth for deadlines and communicate to all parties"
        }
        
        return recommendations.get(conflict.type, "Review with stakeholders and document resolution")
