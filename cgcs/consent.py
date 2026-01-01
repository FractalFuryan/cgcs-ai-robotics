"""
Consent Management System

Implements consent-first behavior where all actions require explicit approval.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class ConsentType(Enum):
    """Types of consent that can be requested."""
    ACTION = "action"
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    ROLE_ASSIGNMENT = "role_assignment"


class ConsentStatus(Enum):
    """Status of a consent request."""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class ConsentRequest:
    """Represents a request for consent."""
    request_id: str
    consent_type: ConsentType
    requester: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: ConsentStatus = ConsentStatus.PENDING
    expires_at: Optional[datetime] = None


class ConsentManager:
    """
    Manages consent for all agent actions.
    
    Implements refusal-first approach: all actions are denied by default
    until explicit consent is granted.
    """
    
    def __init__(self):
        self._consents: Dict[str, ConsentRequest] = {}
        self._granted_scopes: Set[str] = set()
    
    def request_consent(
        self,
        request_id: str,
        consent_type: ConsentType,
        requester: str,
        description: str,
        expires_at: Optional[datetime] = None
    ) -> ConsentRequest:
        """
        Request consent for an action.
        
        Args:
            request_id: Unique identifier for this request
            consent_type: Type of consent being requested
            requester: Identifier of the requesting agent
            description: Human-readable description of what consent is for
            expires_at: Optional expiration time for the consent
            
        Returns:
            ConsentRequest object representing the request
        """
        request = ConsentRequest(
            request_id=request_id,
            consent_type=consent_type,
            requester=requester,
            description=description,
            expires_at=expires_at
        )
        self._consents[request_id] = request
        return request
    
    def grant_consent(self, request_id: str) -> bool:
        """
        Grant consent for a specific request.
        
        Args:
            request_id: ID of the request to grant
            
        Returns:
            True if consent was granted, False if request not found
        """
        if request_id not in self._consents:
            return False
        
        request = self._consents[request_id]
        request.status = ConsentStatus.GRANTED
        self._granted_scopes.add(f"{request.requester}:{request.consent_type.value}")
        return True
    
    def deny_consent(self, request_id: str) -> bool:
        """
        Deny consent for a specific request.
        
        Args:
            request_id: ID of the request to deny
            
        Returns:
            True if consent was denied, False if request not found
        """
        if request_id not in self._consents:
            return False
        
        request = self._consents[request_id]
        request.status = ConsentStatus.DENIED
        return True
    
    def check_consent(
        self,
        requester: str,
        consent_type: ConsentType,
        request_id: Optional[str] = None
    ) -> bool:
        """
        Check if consent has been granted for an action.
        
        Args:
            requester: Identifier of the requesting agent
            consent_type: Type of consent to check
            request_id: Optional specific request ID to check
            
        Returns:
            True if consent is granted, False otherwise (refusal-first)
        """
        if request_id:
            request = self._consents.get(request_id)
            if not request:
                return False
            
            # Check expiration
            if request.expires_at and datetime.now() > request.expires_at:
                request.status = ConsentStatus.EXPIRED
                return False
            
            return request.status == ConsentStatus.GRANTED
        
        # Check general scope consent
        scope = f"{requester}:{consent_type.value}"
        return scope in self._granted_scopes
    
    def revoke_consent(self, request_id: str) -> bool:
        """
        Revoke previously granted consent.
        
        Args:
            request_id: ID of the request to revoke
            
        Returns:
            True if consent was revoked, False if request not found
        """
        if request_id not in self._consents:
            return False
        
        request = self._consents[request_id]
        if request.status == ConsentStatus.GRANTED:
            scope = f"{request.requester}:{request.consent_type.value}"
            self._granted_scopes.discard(scope)
        
        request.status = ConsentStatus.DENIED
        return True
    
    def get_pending_requests(self) -> List[ConsentRequest]:
        """Get all pending consent requests."""
        return [
            req for req in self._consents.values()
            if req.status == ConsentStatus.PENDING
        ]
    
    def clear_expired(self) -> int:
        """
        Clear expired consent requests.
        
        Returns:
            Number of expired requests cleared
        """
        now = datetime.now()
        expired_count = 0
        
        for request in self._consents.values():
            if request.expires_at and now > request.expires_at:
                if request.status == ConsentStatus.GRANTED:
                    scope = f"{request.requester}:{request.consent_type.value}"
                    self._granted_scopes.discard(scope)
                request.status = ConsentStatus.EXPIRED
                expired_count += 1
        
        return expired_count
