"""Policy Repository for storage service."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.policy import LifecyclePolicy, PolicyRule, RuleType
from ..utils.logging import get_logger

logger = get_logger(__name__)


class PolicyRepository:
    """Repository for lifecycle policy operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create_policy(self, policy_data: Dict[str, Any]) -> LifecyclePolicy:
        """Create a new lifecycle policy."""
        try:
            policy = LifecyclePolicy(**policy_data)
            self.db.add(policy)
            await self.db.flush()
            await self.db.refresh(policy)
            logger.info(f"Created policy: {policy.name} (ID: {policy.id})")
            return policy
        except Exception as e:
            logger.error(f"Failed to create policy: {str(e)}")
            raise
    
    async def get_policy(self, policy_id: UUID) -> Optional[LifecyclePolicy]:
        """Get policy by ID."""
        try:
            query = select(LifecyclePolicy).where(
                LifecyclePolicy.id == policy_id,
                LifecyclePolicy.is_deleted == False
            ).options(selectinload(LifecyclePolicy.rules))
            
            result = await self.db.execute(query)
            policy = result.scalar_one_or_none()
            
            if policy:
                logger.debug(f"Retrieved policy: {policy_id}")
            else:
                logger.warning(f"Policy not found: {policy_id}")
            
            return policy
        except Exception as e:
            logger.error(f"Failed to get policy {policy_id}: {str(e)}")
            raise
    
    async def get_policy_by_name(self, name: str) -> Optional[LifecyclePolicy]:
        """Get policy by name."""
        try:
            query = select(LifecyclePolicy).where(
                LifecyclePolicy.name == name,
                LifecyclePolicy.is_deleted == False
            ).options(selectinload(LifecyclePolicy.rules))
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get policy by name: {str(e)}")
            raise
    
    async def list_policies(
        self,
        service: Optional[str] = None,
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[LifecyclePolicy]:
        """List all policies."""
        try:
            query = select(LifecyclePolicy).where(
                LifecyclePolicy.is_deleted == False
            ).options(selectinload(LifecyclePolicy.rules))
            
            if service:
                query = query.where(
                    or_(
                        LifecyclePolicy.target_services.contains([service]),
                        LifecyclePolicy.target_services == None
                    )
                )
            
            if enabled_only:
                query = query.where(LifecyclePolicy.enabled == True)
            
            query = query.limit(limit).offset(offset)
            query = query.order_by(LifecyclePolicy.created_at.desc())
            
            result = await self.db.execute(query)
            policies = result.scalars().all()
            
            logger.debug(f"Listed {len(policies)} policies")
            return policies
        except Exception as e:
            logger.error(f"Failed to list policies: {str(e)}")
            raise
    
    async def update_policy(
        self,
        policy_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[LifecyclePolicy]:
        """Update a policy."""
        try:
            # Don't allow updating certain fields
            protected_fields = ['id', 'created_at']
            for field in protected_fields:
                updates.pop(field, None)
            
            updates['updated_at'] = datetime.utcnow()
            
            query = (
                update(LifecyclePolicy)
                .where(
                    LifecyclePolicy.id == policy_id,
                    LifecyclePolicy.is_deleted == False
                )
                .values(**updates)
                .returning(LifecyclePolicy)
            )
            
            result = await self.db.execute(query)
            updated_policy = result.scalar_one_or_none()
            
            if updated_policy:
                logger.info(f"Updated policy: {policy_id}")
            else:
                logger.warning(f"Policy not found for update: {policy_id}")
            
            return updated_policy
        except Exception as e:
            logger.error(f"Failed to update policy {policy_id}: {str(e)}")
            raise
    
    async def delete_policy(self, policy_id: UUID) -> bool:
        """Soft delete a policy."""
        try:
            query = (
                update(LifecyclePolicy)
                .where(
                    LifecyclePolicy.id == policy_id,
                    LifecyclePolicy.is_deleted == False
                )
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    enabled=False  # Disable policy on deletion
                )
            )
            
            result = await self.db.execute(query)
            success = result.rowcount > 0
            
            if success:
                logger.info(f"Soft deleted policy: {policy_id}")
            else:
                logger.warning(f"Policy not found for deletion: {policy_id}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to delete policy {policy_id}: {str(e)}")
            raise
    
    async def add_rule(
        self,
        policy_id: UUID,
        rule_data: Dict[str, Any]
    ) -> PolicyRule:
        """Add a rule to a policy."""
        try:
            rule_data['policy_id'] = policy_id
            rule = PolicyRule(**rule_data)
            self.db.add(rule)
            await self.db.flush()
            await self.db.refresh(rule)
            
            # Update policy modified time
            await self.update_policy(policy_id, {'updated_at': datetime.utcnow()})
            
            logger.info(f"Added rule to policy {policy_id}")
            return rule
        except Exception as e:
            logger.error(f"Failed to add rule: {str(e)}")
            raise
    
    async def update_rule(
        self,
        rule_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[PolicyRule]:
        """Update a policy rule."""
        try:
            updates['updated_at'] = datetime.utcnow()
            
            query = (
                update(PolicyRule)
                .where(PolicyRule.id == rule_id)
                .values(**updates)
                .returning(PolicyRule)
            )
            
            result = await self.db.execute(query)
            updated_rule = result.scalar_one_or_none()
            
            if updated_rule:
                # Update parent policy modified time
                await self.update_policy(
                    updated_rule.policy_id,
                    {'updated_at': datetime.utcnow()}
                )
                logger.info(f"Updated rule: {rule_id}")
            
            return updated_rule
        except Exception as e:
            logger.error(f"Failed to update rule {rule_id}: {str(e)}")
            raise
    
    async def delete_rule(self, rule_id: UUID) -> bool:
        """Delete a policy rule."""
        try:
            # Get the rule to find parent policy
            rule_query = select(PolicyRule).where(PolicyRule.id == rule_id)
            rule_result = await self.db.execute(rule_query)
            rule = rule_result.scalar_one_or_none()
            
            if not rule:
                return False
            
            # Delete the rule
            await self.db.delete(rule)
            
            # Update parent policy modified time
            await self.update_policy(
                rule.policy_id,
                {'updated_at': datetime.utcnow()}
            )
            
            logger.info(f"Deleted rule: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete rule {rule_id}: {str(e)}")
            raise
    
    async def get_applicable_policies(
        self,
        service: str,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[LifecyclePolicy]:
        """Get policies applicable to given criteria."""
        try:
            query = select(LifecyclePolicy).where(
                and_(
                    LifecyclePolicy.is_deleted == False,
                    LifecyclePolicy.enabled == True
                )
            ).options(selectinload(LifecyclePolicy.rules))
            
            # Filter by service
            query = query.where(
                or_(
                    LifecyclePolicy.target_services.contains([service]),
                    LifecyclePolicy.target_services == None
                )
            )
            
            # Filter by asset type if specified
            if asset_type:
                query = query.where(
                    or_(
                        LifecyclePolicy.target_types.contains([asset_type]),
                        LifecyclePolicy.target_types == None
                    )
                )
            
            # Filter by tags if specified
            if tags:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(
                        or_(
                            LifecyclePolicy.target_tags.contains([tag]),
                            LifecyclePolicy.target_tags == None
                        )
                    )
                query = query.where(or_(*tag_conditions))
            
            result = await self.db.execute(query)
            policies = result.scalars().all()
            
            logger.debug(f"Found {len(policies)} applicable policies")
            return policies
        except Exception as e:
            logger.error(f"Failed to get applicable policies: {str(e)}")
            raise
    
    async def record_execution(
        self,
        policy_id: UUID,
        execution_time: datetime,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record policy execution."""
        try:
            updates = {
                'last_executed_at': execution_time,
                'updated_at': datetime.utcnow()
            }
            
            if details:
                # Store execution details in metadata if needed
                policy = await self.get_policy(policy_id)
                if policy:
                    metadata = policy.metadata or {}
                    metadata['last_execution'] = {
                        'time': execution_time.isoformat(),
                        'success': success,
                        'details': details
                    }
                    updates['metadata'] = metadata
            
            await self.update_policy(policy_id, updates)
            logger.info(f"Recorded execution for policy {policy_id}")
        except Exception as e:
            logger.error(f"Failed to record execution: {str(e)}")
            raise
