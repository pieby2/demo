"""
Data Handler for TalentScout Hiring Assistant.
Manages candidate data storage with GDPR compliance considerations.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
import hashlib


class DataHandler:
    """
    Handles secure storage and retrieval of candidate data.
    Implements basic GDPR compliance measures.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data handler.
        
        Args:
            data_dir: Directory for storing candidate data
        """
        self.data_dir = data_dir
        self.candidates_file = os.path.join(data_dir, "candidates.json")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID for the candidate.
        
        Returns:
            Unique session identifier
        """
        timestamp = datetime.now().isoformat()
        unique_string = f"{timestamp}-{os.urandom(8).hex()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _anonymize_email(self, email: str) -> str:
        """
        Partially anonymize email for display purposes.
        
        Args:
            email: Full email address
        
        Returns:
            Anonymized email (e.g., j***@example.com)
        """
        if not email or "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            anonymized_local = local[0] + "***"
        else:
            anonymized_local = local[0] + "***" + local[-1]
        
        return f"{anonymized_local}@{domain}"
    
    def _anonymize_phone(self, phone: str) -> str:
        """
        Partially anonymize phone number for display.
        
        Args:
            phone: Full phone number
        
        Returns:
            Anonymized phone (e.g., ***-***-1234)
        """
        if not phone:
            return phone
        
        # Keep only last 4 digits visible
        cleaned = ''.join(filter(str.isdigit, phone))
        if len(cleaned) >= 4:
            return "***-***-" + cleaned[-4:]
        return "***"
    
    def save_candidate(self, candidate_info: Dict, conversation_history: List[Dict]) -> str:
        """
        Save candidate information and conversation to file.
        
        Args:
            candidate_info: Dictionary of candidate details
            conversation_history: List of conversation messages
        
        Returns:
            Session ID for the saved record
        """
        session_id = self._generate_session_id()
        
        # Create record with metadata
        record = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "candidate_info": candidate_info,
            "conversation_history": conversation_history,
            "status": "pending_review",
            "gdpr_consent": True,  # Assumed consent by using the service
            "data_retention_until": self._calculate_retention_date()
        }
        
        # Load existing data or create new
        candidates = self._load_candidates()
        candidates.append(record)
        
        # Save to file
        self._save_candidates(candidates)
        
        return session_id
    
    def _calculate_retention_date(self) -> str:
        """
        Calculate data retention date (90 days from now per GDPR guidelines).
        
        Returns:
            ISO format date string
        """
        from datetime import timedelta
        retention_date = datetime.now() + timedelta(days=90)
        return retention_date.isoformat()
    
    def _load_candidates(self) -> List[Dict]:
        """
        Load existing candidates from file.
        
        Returns:
            List of candidate records
        """
        if not os.path.exists(self.candidates_file):
            return []
        
        try:
            with open(self.candidates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_candidates(self, candidates: List[Dict]):
        """
        Save candidates to file.
        
        Args:
            candidates: List of candidate records to save
        """
        with open(self.candidates_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
    
    def get_candidate_by_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve candidate record by session ID.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            Candidate record or None if not found
        """
        candidates = self._load_candidates()
        for candidate in candidates:
            if candidate.get("session_id") == session_id:
                return candidate
        return None
    
    def delete_candidate_data(self, session_id: str) -> bool:
        """
        Delete candidate data (GDPR right to erasure).
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            True if deleted, False if not found
        """
        candidates = self._load_candidates()
        original_length = len(candidates)
        
        candidates = [c for c in candidates if c.get("session_id") != session_id]
        
        if len(candidates) < original_length:
            self._save_candidates(candidates)
            return True
        return False
    
    def get_anonymized_summary(self, candidate_info: Dict) -> Dict:
        """
        Get anonymized summary of candidate info for display.
        
        Args:
            candidate_info: Full candidate information
        
        Returns:
            Anonymized version safe for logging/display
        """
        return {
            "full_name": candidate_info.get("full_name", "Not provided"),
            "email": self._anonymize_email(candidate_info.get("email", "")),
            "phone": self._anonymize_phone(candidate_info.get("phone", "")),
            "years_of_experience": candidate_info.get("years_of_experience", "Not provided"),
            "desired_positions": candidate_info.get("desired_positions", "Not provided"),
            "current_location": candidate_info.get("current_location", "Not provided"),
            "tech_stack": candidate_info.get("tech_stack", "Not provided")
        }
    
    def cleanup_expired_records(self):
        """
        Remove records past their retention date (GDPR compliance).
        Should be run periodically in production.
        """
        candidates = self._load_candidates()
        current_time = datetime.now()
        
        active_candidates = []
        for candidate in candidates:
            retention_date_str = candidate.get("data_retention_until")
            if retention_date_str:
                try:
                    retention_date = datetime.fromisoformat(retention_date_str)
                    if retention_date > current_time:
                        active_candidates.append(candidate)
                except ValueError:
                    active_candidates.append(candidate)
            else:
                active_candidates.append(candidate)
        
        if len(active_candidates) < len(candidates):
            self._save_candidates(active_candidates)
