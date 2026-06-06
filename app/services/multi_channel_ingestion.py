"""Multi-channel ingestion service for processing various data sources.

This service handles ingestion from multiple channels including direct input,
email datasets, meeting transcripts, and simulated Slack data.
"""

from typing import List, Dict, Optional, Union
from dataclasses import dataclass
import logging

from app.services.dataset_loaders import (
    EmailDatasetLoader,
    MeetingDatasetLoader,
    SlackSimulator,
    EmailMessage,
    MeetingTranscript
)
from app.models.request import BRDRequest

logger = logging.getLogger(__name__)


@dataclass
class UnifiedInput:
    """Unified input format for all data sources."""
    
    project_name: str
    email_content: Optional[str] = None
    slack_content: Optional[str] = None
    meeting_content: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class DatasetConfig:
    """Configuration for dataset-based ingestion."""
    
    enabled: bool = False
    email_dataset_path: Optional[str] = None
    meeting_dataset_path: Optional[str] = None
    max_emails: int = 1000
    max_meetings: int = 100
    project_keywords: Optional[List[str]] = None
    sample_size: int = 50  # Number of items to sample for BRD generation


class MultiChannelIngestionService:
    """Service for ingesting data from multiple channels."""
    
    def __init__(self, config: DatasetConfig):
        """Initialize the multi-channel ingestion service.
        
        Args:
            config: Dataset configuration
        """
        self.config = config
        self.email_loader = None
        self.meeting_loader = None
        self.slack_simulator = SlackSimulator()
        
        if config.enabled:
            self._initialize_loaders()
    
    def _initialize_loaders(self):
        """Initialize dataset loaders if paths are provided."""
        if self.config.email_dataset_path:
            self.email_loader = EmailDatasetLoader(
                self.config.email_dataset_path,
                self.config.max_emails
            )
        
        if self.config.meeting_dataset_path:
            self.meeting_loader = MeetingDatasetLoader(
                self.config.meeting_dataset_path,
                self.config.max_meetings
            )
    
    def process_direct_input(self, request: BRDRequest) -> UnifiedInput:
        """Process direct API input.
        
        Args:
            request: BRD request from API
            
        Returns:
            UnifiedInput object
        """
        return UnifiedInput(
            project_name=request.projectName,
            email_content=request.emailText,
            slack_content=request.slackText,
            meeting_content=request.meetingText,
            metadata={"source": "direct_input"}
        )
    
    def process_dataset_input(
        self,
        project_name: str,
        keywords: Optional[List[str]] = None
    ) -> UnifiedInput:
        """Process dataset-based input.
        
        Args:
            project_name: Name of the project
            keywords: Keywords to filter dataset content
            
        Returns:
            UnifiedInput object with dataset content
        """
        if not self.config.enabled:
            raise ValueError("Dataset mode is not enabled")
        
        # Use provided keywords or fall back to config
        filter_keywords = keywords or self.config.project_keywords
        
        # Load and process emails
        email_content = None
        if self.email_loader:
            emails = self.email_loader.load_emails(
                keywords=filter_keywords,
                limit=self.config.sample_size
            )
            email_content = self._format_emails_for_brd(emails)
        
        # Load and process meeting transcripts
        meeting_content = None
        if self.meeting_loader:
            transcripts = self.meeting_loader.load_transcripts(
                keywords=filter_keywords,
                limit=self.config.sample_size // 2  # Fewer meetings than emails
            )
            meeting_content = self._format_transcripts_for_brd(transcripts)
        
        # Generate Slack content from emails
        slack_content = None
        if self.email_loader and emails:
            # Take a subset of emails for Slack simulation
            slack_emails = emails[:min(20, len(emails))]
            slack_messages = self.slack_simulator.convert_emails_to_slack(slack_emails)
            slack_content = self._format_slack_for_brd(slack_messages)
        
        return UnifiedInput(
            project_name=project_name,
            email_content=email_content,
            slack_content=slack_content,
            meeting_content=meeting_content,
            metadata={
                "source": "dataset",
                "keywords_used": filter_keywords,
                "email_count": len(emails) if emails else 0,
                "meeting_count": len(transcripts) if transcripts else 0
            }
        )
    
    def _format_emails_for_brd(self, emails: List[EmailMessage]) -> Optional[str]:
        """Format emails for BRD generation.
        
        Args:
            emails: List of email messages
            
        Returns:
            Formatted email content string
        """
        if not emails:
            return None
        
        formatted_parts = []
        for email in emails:
            parts = []
            if email.subject:
                parts.append(f"Subject: {email.subject}")
            if email.sender:
                parts.append(f"From: {email.sender}")
            if email.body:
                # Truncate very long emails
                body = email.body[:500] + "..." if len(email.body) > 500 else email.body
                parts.append(f"Content: {body}")
            
            if parts:
                formatted_parts.append("\n".join(parts))
        
        return "\n\n---\n\n".join(formatted_parts)
    
    def _format_transcripts_for_brd(self, transcripts: List[MeetingTranscript]) -> Optional[str]:
        """Format meeting transcripts for BRD generation.
        
        Args:
            transcripts: List of meeting transcripts
            
        Returns:
            Formatted transcript content string
        """
        if not transcripts:
            return None
        
        formatted_parts = []
        for transcript in transcripts:
            parts = [f"Meeting: {transcript.meeting_id}"]
            
            # Format utterances
            utterance_texts = []
            for utterance in transcript.utterances[:20]:  # Limit utterances
                speaker = utterance.get('speaker', 'Unknown')
                text = utterance.get('text', '')
                if text:
                    utterance_texts.append(f"{speaker}: {text}")
            
            if utterance_texts:
                parts.append("Transcript:\n" + "\n".join(utterance_texts))
            
            formatted_parts.append("\n".join(parts))
        
        return "\n\n---\n\n".join(formatted_parts)
    
    def _format_slack_for_brd(self, slack_messages: List[Dict]) -> Optional[str]:
        """Format Slack messages for BRD generation.
        
        Args:
            slack_messages: List of Slack message dictionaries
            
        Returns:
            Formatted Slack content string
        """
        if not slack_messages:
            return None
        
        formatted_parts = []
        for message in slack_messages:
            user = message.get('user', 'Unknown')
            text = message.get('text', '')
            if text:
                formatted_parts.append(f"{user}: {text}")
        
        return "\n".join(formatted_parts)
    
    def detect_conflicts(self, unified_input: UnifiedInput) -> List[Dict]:
        """Detect conflicts across different data sources.
        
        Args:
            unified_input: Unified input from all sources
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Simple conflict detection based on contradictory keywords
        conflict_patterns = [
            ("urgent", "low priority"),
            ("immediate", "future"),
            ("simple", "complex"),
            ("small", "large"),
            ("basic", "advanced")
        ]
        
        # Collect all text content
        all_content = []
        if unified_input.email_content:
            all_content.append(("email", unified_input.email_content.lower()))
        if unified_input.slack_content:
            all_content.append(("slack", unified_input.slack_content.lower()))
        if unified_input.meeting_content:
            all_content.append(("meeting", unified_input.meeting_content.lower()))
        
        # Check for conflicts
        for pattern1, pattern2 in conflict_patterns:
            sources_with_pattern1 = [source for source, content in all_content if pattern1 in content]
            sources_with_pattern2 = [source for source, content in all_content if pattern2 in content]
            
            if sources_with_pattern1 and sources_with_pattern2:
                conflicts.append({
                    "type": "contradictory_requirements",
                    "pattern1": pattern1,
                    "pattern2": pattern2,
                    "sources_pattern1": sources_with_pattern1,
                    "sources_pattern2": sources_with_pattern2,
                    "severity": "medium"
                })
        
        logger.info(f"Detected {len(conflicts)} potential conflicts")
        return conflicts
    
    def normalize_to_brd_request(self, unified_input: UnifiedInput) -> BRDRequest:
        """Convert unified input to BRDRequest format.
        
        Args:
            unified_input: Unified input object
            
        Returns:
            BRDRequest object
        """
        return BRDRequest(
            projectName=unified_input.project_name,
            emailText=unified_input.email_content,
            slackText=unified_input.slack_content,
            meetingText=unified_input.meeting_content
        )