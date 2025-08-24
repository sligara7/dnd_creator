"""
Transaction Management

Handles distributed transactions across services with rollback support.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import structlog
from enum import Enum

from .models import ServiceType, MessageType

logger = structlog.get_logger()

class TransactionState(Enum):
    """Transaction states."""
    PENDING = "pending"    # Transaction started but not committed
    COMMITTED = "committed"  # Successfully completed
    ROLLED_BACK = "rolled_back"  # Rolled back due to failure
    FAILED = "failed"      # Failed and couldn't be rolled back

class TransactionPhase(Enum):
    """Phases of a distributed transaction."""
    PREPARE = "prepare"  # Services prepare to commit
    COMMIT = "commit"    # Services commit changes
    ROLLBACK = "rollback"  # Services rollback changes

class Transaction:
    """
    Represents a distributed transaction across services.
    
    Tracks:
    - Participating services
    - Transaction state
    - Operation history
    - Rollback operations
    """
    
    def __init__(self, transaction_id: str = None):
        """Initialize transaction."""
        self.id = transaction_id or str(uuid.uuid4())
        self.state = TransactionState.PENDING
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        
        # Track participating services and their operations
        self.participants: Dict[ServiceType, List[Dict[str, Any]]] = {}
        
        # Operation history for rollback
        self.operations: List[Dict[str, Any]] = []
        
        logger.info("transaction_created",
                   transaction_id=self.id,
                   state=self.state.value)
    
    def add_participant(self,
                      service: ServiceType,
                      operation: MessageType,
                      payload: Dict[str, Any],
                      rollback_operation: Optional[MessageType] = None):
        """Add a service participant to the transaction."""
        if service not in self.participants:
            self.participants[service] = []
        
        participant_info = {
            "operation": operation,
            "payload": payload,
            "rollback_operation": rollback_operation,
            "state": TransactionPhase.PREPARE
        }
        
        self.participants[service].append(participant_info)
        
        logger.info("transaction_participant_added",
                   transaction_id=self.id,
                   service=service.value,
                   operation=operation)
    
    def record_operation(self,
                       service: ServiceType,
                       operation: MessageType,
                       payload: Dict[str, Any],
                       result: Dict[str, Any]):
        """Record a completed operation for potential rollback."""
        operation_record = {
            "service": service,
            "operation": operation,
            "payload": payload,
            "result": result,
            "timestamp": datetime.utcnow()
        }
        
        self.operations.append(operation_record)
        
        logger.info("transaction_operation_recorded",
                   transaction_id=self.id,
                   service=service.value,
                   operation=operation)
    
    def mark_committed(self):
        """Mark transaction as successfully committed."""
        self.state = TransactionState.COMMITTED
        self.end_time = datetime.utcnow()
        
        logger.info("transaction_committed",
                   transaction_id=self.id,
                   duration=(self.end_time - self.start_time).total_seconds())
    
    def mark_rolled_back(self):
        """Mark transaction as rolled back."""
        self.state = TransactionState.ROLLED_BACK
        self.end_time = datetime.utcnow()
        
        logger.info("transaction_rolled_back",
                   transaction_id=self.id,
                   duration=(self.end_time - self.start_time).total_seconds())
    
    def mark_failed(self):
        """Mark transaction as failed (couldn't be rolled back)."""
        self.state = TransactionState.FAILED
        self.end_time = datetime.utcnow()
        
        logger.error("transaction_failed",
                    transaction_id=self.id,
                    duration=(self.end_time - self.start_time).total_seconds())
    
    def get_rollback_operations(self) -> List[Dict[str, Any]]:
        """Get list of operations needed for rollback in reverse order."""
        rollback_ops = []
        
        # Process operations in reverse order
        for op in reversed(self.operations):
            if op["operation"] in self.participants[op["service"]]:
                participant = self.participants[op["service"]]
                if participant["rollback_operation"]:
                    rollback_ops.append({
                        "service": op["service"],
                        "operation": participant["rollback_operation"],
                        "payload": {
                            "original_operation": op["operation"],
                            "original_payload": op["payload"],
                            "operation_result": op["result"]
                        }
                    })
        
        return rollback_ops
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get transaction metrics."""
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "transaction_id": self.id,
            "state": self.state.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": duration,
            "participant_count": len(self.participants),
            "operation_count": len(self.operations)
        }
