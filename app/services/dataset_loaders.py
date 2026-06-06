"""Dataset loaders for email and meeting data.

This module provides loaders for various datasets including Enron emails
and AMI meeting transcripts.
"""

import csv
import json
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EmailMessage:
    """Represents an email message from a dataset.
    
    This class encapsulates email data loaded from datasets like Enron,
    providing a structured representation of email metadata and content.
    
    Attributes:
        sender: Email address of the sender
        recipients: List of recipient email addresses
        timestamp: When the email was sent (optional)
        subject: Email subject line
        body: Email body content
        message_id: Unique message identifier (optional)
    """
    
    def __init__(
        self,
        sender: str,
        recipients: List[str],
        timestamp: Optional[datetime],
        subject: str,
        body: str,
        message_id: Optional[str] = None
    ):
        """Initialize an email message.
        
        Args:
            sender: Email address of the sender
            recipients: List of recipient email addresses
            timestamp: When the email was sent (optional)
            subject: Email subject line
            body: Email body content
            message_id: Unique message identifier (optional)
        """
        self.sender = sender
        self.recipients = recipients
        self.timestamp = timestamp
        self.subject = subject
        self.body = body
        self.message_id = message_id
    
    def to_dict(self) -> Dict:
        """Convert email to dictionary representation.
        
        Returns:
            Dictionary containing all email fields with timestamp as ISO format string
        """
        return {
            "sender": self.sender,
            "recipients": self.recipients,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "subject": self.subject,
            "body": self.body,
            "message_id": self.message_id
        }


class MeetingTranscript:
    """Represents a meeting transcript from a dataset.
    
    This class encapsulates meeting transcript data loaded from datasets
    like AMI, providing structured access to utterances and metadata.
    
    Attributes:
        meeting_id: Unique identifier for the meeting
        utterances: List of utterance dictionaries with speaker and text
        metadata: Additional meeting metadata (optional)
    """
    
    def __init__(
        self,
        meeting_id: str,
        utterances: List[Dict[str, str]],
        metadata: Optional[Dict] = None
    ):
        """Initialize a meeting transcript.
        
        Args:
            meeting_id: Unique identifier for the meeting
            utterances: List of dicts with 'speaker' and 'text' keys
            metadata: Additional meeting metadata (optional)
        """
        self.meeting_id = meeting_id
        self.utterances = utterances  # List of {"speaker": str, "text": str}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert meeting transcript to dictionary representation.
        
        Returns:
            Dictionary containing meeting ID, utterances, and metadata
        """
        return {
            "meeting_id": self.meeting_id,
            "utterances": self.utterances,
            "metadata": self.metadata
        }


class EmailDatasetLoader:
    """Loader for Enron email dataset."""
    
    def __init__(self, dataset_path: str, max_emails: int = 1000):
        """Initialize the email dataset loader.
        
        Args:
            dataset_path: Path to the Enron email CSV file
            max_emails: Maximum number of emails to load
        """
        self.dataset_path = Path(dataset_path)
        self.max_emails = max_emails
    
    def load_emails(
        self,
        keywords: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[EmailMessage]:
        """Load emails from the dataset.
        
        Args:
            keywords: Optional list of keywords to filter emails
            limit: Optional limit on number of emails to return
            
        Returns:
            List of EmailMessage objects
        """
        if not self.dataset_path.exists():
            logger.warning(f"Dataset file not found: {self.dataset_path}")
            return []
        
        emails = []
        max_to_load = limit if limit else self.max_emails
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    if i >= max_to_load:
                        break
                    
                    # Extract email fields
                    sender = row.get('From', row.get('sender', ''))
                    recipients_str = row.get('To', row.get('recipients', ''))
                    recipients = [r.strip() for r in recipients_str.split(',') if r.strip()]
                    subject = row.get('Subject', row.get('subject', ''))
                    body = row.get('Body', row.get('body', row.get('content', '')))
                    message_id = row.get('Message-ID', row.get('message_id', f'email_{i}'))
                    
                    # Parse timestamp if available
                    timestamp = None
                    date_str = row.get('Date', row.get('timestamp', ''))
                    if date_str:
                        try:
                            timestamp = datetime.fromisoformat(date_str)
                        except:
                            pass
                    
                    # Filter by keywords if provided
                    if keywords:
                        text_to_search = f"{subject} {body}".lower()
                        if not any(keyword.lower() in text_to_search for keyword in keywords):
                            continue
                    
                    email = EmailMessage(
                        sender=sender,
                        recipients=recipients,
                        timestamp=timestamp,
                        subject=subject,
                        body=body,
                        message_id=message_id
                    )
                    emails.append(email)
            
            logger.info(f"Loaded {len(emails)} emails from dataset")
            return emails
            
        except Exception as e:
            logger.error(f"Error loading emails: {e}")
            return []
    
    def filter_by_keywords(
        self,
        emails: List[EmailMessage],
        keywords: List[str]
    ) -> List[EmailMessage]:
        """Filter emails by keywords.
        
        Args:
            emails: List of email messages
            keywords: Keywords to filter by
            
        Returns:
            Filtered list of emails
        """
        filtered = []
        for email in emails:
            text_to_search = f"{email.subject} {email.body}".lower()
            if any(keyword.lower() in text_to_search for keyword in keywords):
                filtered.append(email)
        
        return filtered


class MeetingDatasetLoader:
    """Loader for AMI meeting transcript dataset."""
    
    def __init__(self, dataset_path: str, max_meetings: int = 100):
        """Initialize the meeting dataset loader.
        
        Args:
            dataset_path: Path to the AMI transcript directory or file
            max_meetings: Maximum number of meetings to load
        """
        self.dataset_path = Path(dataset_path)
        self.max_meetings = max_meetings
    
    def load_transcripts(
        self,
        keywords: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[MeetingTranscript]:
        """Load meeting transcripts from the dataset.
        
        Args:
            keywords: Optional keywords to filter transcripts
            limit: Optional limit on number of transcripts
            
        Returns:
            List of MeetingTranscript objects
        """
        if not self.dataset_path.exists():
            logger.warning(f"Dataset path not found: {self.dataset_path}")
            return []
        
        transcripts = []
        max_to_load = limit if limit else self.max_meetings
        
        try:
            # Handle both directory and single file
            if self.dataset_path.is_dir():
                files = list(self.dataset_path.glob("*.json"))[:max_to_load]
            else:
                files = [self.dataset_path]
            
            for file_path in files:
                transcript = self._load_transcript_file(file_path, keywords)
                if transcript:
                    transcripts.append(transcript)
            
            logger.info(f"Loaded {len(transcripts)} meeting transcripts")
            return transcripts
            
        except Exception as e:
            logger.error(f"Error loading transcripts: {e}")
            return []
    
    def _load_transcript_file(
        self,
        file_path: Path,
        keywords: Optional[List[str]] = None
    ) -> Optional[MeetingTranscript]:
        """Load a single transcript file.
        
        Args:
            file_path: Path to transcript file
            keywords: Optional keywords to filter
            
        Returns:
            MeetingTranscript object or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            meeting_id = data.get('meeting_id', file_path.stem)
            utterances = data.get('utterances', [])
            metadata = data.get('metadata', {})
            
            # Filter by keywords if provided
            if keywords:
                full_text = ' '.join([u.get('text', '') for u in utterances]).lower()
                if not any(keyword.lower() in full_text for keyword in keywords):
                    return None
            
            return MeetingTranscript(
                meeting_id=meeting_id,
                utterances=utterances,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error loading transcript file {file_path}: {e}")
            return None


class SlackSimulator:
    """Simulates Slack-style messages from email threads."""
    
    def __init__(self):
        """Initialize the Slack simulator."""
        pass
    
    def convert_emails_to_slack(
        self,
        emails: List[EmailMessage],
        channel_name: str = "project-discussion"
    ) -> List[Dict]:
        """Convert email threads to Slack-style messages.
        
        Args:
            emails: List of email messages
            channel_name: Name of the simulated Slack channel
            
        Returns:
            List of Slack-style message dictionaries
        """
        slack_messages = []
        
        for email in emails:
            # Convert email to Slack message format
            message = {
                "channel": channel_name,
                "user": self._extract_username(email.sender),
                "timestamp": email.timestamp.isoformat() if email.timestamp else None,
                "text": self._format_email_as_slack(email),
                "thread_ts": email.message_id,
                "metadata": {
                    "original_subject": email.subject,
                    "recipients": email.recipients
                }
            }
            slack_messages.append(message)
        
        logger.info(f"Converted {len(emails)} emails to Slack messages")
        return slack_messages
    
    def _extract_username(self, email_address: str) -> str:
        """Extract username from email address.
        
        Args:
            email_address: Email address
            
        Returns:
            Username portion
        """
        if '@' in email_address:
            return email_address.split('@')[0]
        return email_address
    
    def _format_email_as_slack(self, email: EmailMessage) -> str:
        """Format email content as Slack message.
        
        Args:
            email: Email message
            
        Returns:
            Formatted Slack message text
        """
        # Include subject as bold text if present
        text_parts = []
        
        if email.subject:
            text_parts.append(f"*{email.subject}*")
        
        if email.body:
            # Truncate very long bodies
            body = email.body[:1000] + "..." if len(email.body) > 1000 else email.body
            text_parts.append(body)
        
        return "\n\n".join(text_parts)
