"""
Transaction Manager

Coordinates distributed transactions across services.
"""

import asyncio
from typing import Dict, Optional, List, Any
import structlog
from datetime import datetime, timedelta

from .transaction import Transaction, TransactionState, TransactionPhase
from .models import ServiceType, MessageType, ServiceMessage, ServiceResponse

logger = structlog.get_logger()

class TransactionManager:
    """
    Manages distributed transactions across services.
    
    Responsibilities:
    - Transaction creation and tracking
    - Two-phase commit coordination
    - Rollback coordination
    - Transaction monitoring
    """
    
    def __init__(self, message_router=None):
        """Initialize transaction manager."""
        self.message_router = message_router
        self.active_transactions: Dict[str, Transaction] = {}
        self.completed_transactions: Dict[str, Transaction] = {}
        
        # Configuration
        self.transaction_timeout = 30  # seconds
        self.max_completed_transactions = 1000
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_transactions())
    
    async def begin_transaction(self) -> Transaction:
        """Start a new transaction."""
        transaction = Transaction()
        self.active_transactions[transaction.id] = transaction
        
        logger.info("transaction_started",
                   transaction_id=transaction.id)
        
        return transaction
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """
        Commit a transaction using two-phase commit.
        
        Returns:
            bool: True if commit successful, False if rollback required
        """
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"Unknown transaction: {transaction_id}")
        
        try:
            # Phase 1: Prepare
            await self._prepare_all_participants(transaction)
            
            # Phase 2: Commit
            await self._commit_all_participants(transaction)
            
            # Mark transaction complete
            transaction.mark_committed()
            self._move_to_completed(transaction)
            return True
            
        except Exception as e:
            logger.error("transaction_commit_failed",
                        transaction_id=transaction_id,
                        error=str(e))
            
            # Attempt rollback
            await self.rollback_transaction(transaction_id)
            return False
    
    async def rollback_transaction(self, transaction_id: str):
        """Rollback a transaction by reversing all operations."""
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"Unknown transaction: {transaction_id}")
        
        try:
            rollback_ops = transaction.get_rollback_operations()
            
            # Execute rollback operations in reverse order
            for op in rollback_ops:
                try:
                    message = ServiceMessage(
                        source=ServiceType.MESSAGE_HUB,
                        destination=op["service"],
                        message_type=op["operation"],
                        payload=op["payload"]
                    )
                    
                    await self.message_router.route_message(message)
                    
                except Exception as e:
                    logger.error("rollback_operation_failed",
                               transaction_id=transaction_id,
                               service=op["service"].value,
                               operation=op["operation"],
                               error=str(e))
            
            transaction.mark_rolled_back()
            
        except Exception as e:
            logger.error("transaction_rollback_failed",
                        transaction_id=transaction_id,
                        error=str(e))
            transaction.mark_failed()
        
        finally:
            self._move_to_completed(transaction)
    
    async def _prepare_all_participants(self, transaction: Transaction):
        """Prepare phase: ask all participants to prepare for commit."""
        prepare_tasks = []
        
        for service, operations in transaction.participants.items():
            for op in operations:
                message = ServiceMessage(
                    source=ServiceType.MESSAGE_HUB,
                    destination=service,
                        message_type=MessageType.TRANSACTION_PREPARE,
                    payload={
                        "transaction_id": transaction.id,
                        "operation": op["operation"],
                        "original_payload": op["payload"]
                    }
                )
                
                prepare_tasks.append(
                    self.message_router.route_message(message)
                )
        
        # Wait for all prepare responses
        prepare_results = await asyncio.gather(*prepare_tasks, return_exceptions=True)
        
        # Check for any failures
        for result in prepare_results:
            if isinstance(result, Exception) or result.status == "error":
                raise Exception("Prepare phase failed")
    
    async def _commit_all_participants(self, transaction: Transaction):
        """Commit phase: tell all participants to commit."""
        commit_tasks = []
        
        for service, operations in transaction.participants.items():
            for op in operations:
                message = ServiceMessage(
                    source=ServiceType.MESSAGE_HUB,
                    destination=service,
                        message_type=MessageType.TRANSACTION_COMMIT,
                    payload={
                        "transaction_id": transaction.id,
                        "operation": op["operation"],
                        "original_payload": op["payload"]
                    }
                )
                
                commit_tasks.append(
                    self.message_router.route_message(message)
                )
        
        # Wait for all commit responses
        commit_results = await asyncio.gather(*commit_tasks, return_exceptions=True)
        
        # Check for any failures
        for result in commit_results:
            if isinstance(result, Exception) or result.status == "error":
                raise Exception("Commit phase failed")
    
    def _move_to_completed(self, transaction: Transaction):
        """Move transaction from active to completed."""
        if transaction.id in self.active_transactions:
            del self.active_transactions[transaction.id]
            
        self.completed_transactions[transaction.id] = transaction
        
        # Trim completed transactions if needed
        if len(self.completed_transactions) > self.max_completed_transactions:
            oldest_id = min(
                self.completed_transactions.keys(),
                key=lambda x: self.completed_transactions[x].start_time
            )
            del self.completed_transactions[oldest_id]
    
    async def _cleanup_old_transactions(self):
        """Periodically clean up timed out transactions."""
        while True:
            try:
                current_time = datetime.utcnow()
                timeout_threshold = current_time - timedelta(
                    seconds=self.transaction_timeout
                )
                
                # Find timed out transactions
                timed_out = [
                    tx_id for tx_id, tx in self.active_transactions.items()
                    if tx.start_time < timeout_threshold
                ]
                
                # Rollback timed out transactions
                for tx_id in timed_out:
                    logger.warning("transaction_timeout",
                                 transaction_id=tx_id)
                    await self.rollback_transaction(tx_id)
                
            except Exception as e:
                logger.error("transaction_cleanup_error",
                           error=str(e))
            
            # Sleep before next cleanup
            await asyncio.sleep(10)  # Check every 10 seconds
    
    def get_metrics(self) -> Dict[str, any]:
        """Get transaction manager metrics."""
        return {
            "active_transactions": list(self.active_transactions.keys()),
            "completed_transactions": list(self.completed_transactions.keys()),
            "transactions": {
                "active": {
                    tx_id: tx.get_metrics()
                    for tx_id, tx in self.active_transactions.items()
                },
                "completed": {
                    tx_id: tx.get_metrics()
                    for tx_id, tx in self.completed_transactions.items()
                }
            }
        }
