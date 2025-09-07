"""Policy Service for lifecycle management operations."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.policy import PolicyRepository
from ..repositories.asset import AssetRepository
from ..integrations.s3_client import S3StorageClient
from ..models.policy import LifecyclePolicy, PolicyRule, RuleType
from ..models.asset import Asset
from ..utils.logging import get_logger

logger = get_logger(__name__)


class PolicyService:
    """Service for lifecycle policy management operations."""
    
    def __init__(self, db: AsyncSession, s3_client: Optional[S3StorageClient] = None):
        """Initialize service with dependencies."""
        self.db = db
        self.policy_repo = PolicyRepository(db)
        self.asset_repo = AssetRepository(db)
        self.s3_client = s3_client or S3StorageClient()
    
    async def create_policy(
        self,
        name: str,
        description: Optional[str] = None,
        target_services: Optional[List[str]] = None,
        target_types: Optional[List[str]] = None,
        target_tags: Optional[List[str]] = None,
        enabled: bool = True
    ) -> LifecyclePolicy:
        """Create a new lifecycle policy."""
        try:
            policy_data = {
                'name': name,
                'description': description,
                'target_services': target_services,
                'target_types': target_types,
                'target_tags': target_tags,
                'enabled': enabled
            }
            
            policy = await self.policy_repo.create_policy(policy_data)
            await self.db.commit()
            
            logger.info(f"Created policy: {name}")
            return policy
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create policy: {str(e)}")
            raise
    
    async def get_policy(self, policy_id: UUID) -> Optional[LifecyclePolicy]:
        """Get a policy by ID."""
        return await self.policy_repo.get_policy(policy_id)
    
    async def list_policies(
        self,
        service: Optional[str] = None,
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[LifecyclePolicy]:
        """List all policies."""
        return await self.policy_repo.list_policies(
            service=service,
            enabled_only=enabled_only,
            limit=limit,
            offset=offset
        )
    
    async def update_policy(
        self,
        policy_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[LifecyclePolicy]:
        """Update a policy."""
        try:
            policy = await self.policy_repo.update_policy(policy_id, updates)
            if policy:
                await self.db.commit()
                logger.info(f"Updated policy: {policy_id}")
            return policy
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update policy: {str(e)}")
            raise
    
    async def delete_policy(self, policy_id: UUID) -> bool:
        """Delete a policy."""
        try:
            success = await self.policy_repo.delete_policy(policy_id)
            if success:
                await self.db.commit()
                logger.info(f"Deleted policy: {policy_id}")
            return success
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete policy: {str(e)}")
            raise
    
    async def add_rule_to_policy(
        self,
        policy_id: UUID,
        rule_type: RuleType,
        condition: Dict[str, Any],
        action: Dict[str, Any]
    ) -> PolicyRule:
        """Add a rule to a policy."""
        try:
            rule_data = {
                'rule_type': rule_type,
                'condition': condition,
                'action': action
            }
            
            rule = await self.policy_repo.add_rule(policy_id, rule_data)
            await self.db.commit()
            
            logger.info(f"Added rule to policy {policy_id}")
            return rule
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add rule: {str(e)}")
            raise
    
    async def execute_policy(
        self,
        policy_id: UUID,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Execute a lifecycle policy."""
        try:
            policy = await self.policy_repo.get_policy(policy_id)
            if not policy:
                raise ValueError(f"Policy {policy_id} not found")
            
            if not policy.enabled:
                logger.warning(f"Policy {policy_id} is disabled")
                return {'status': 'skipped', 'reason': 'policy_disabled'}
            
            results = {
                'policy_id': str(policy_id),
                'policy_name': policy.name,
                'executed_at': datetime.utcnow().isoformat(),
                'dry_run': dry_run,
                'rules_executed': [],
                'assets_affected': 0,
                'errors': []
            }
            
            # Get applicable assets
            assets = await self._get_policy_assets(policy)
            
            for rule in policy.rules:
                try:
                    rule_result = await self._execute_rule(
                        rule, assets, dry_run
                    )
                    results['rules_executed'].append(rule_result)
                    results['assets_affected'] += rule_result.get('assets_affected', 0)
                except Exception as e:
                    results['errors'].append({
                        'rule_id': str(rule.id),
                        'error': str(e)
                    })
            
            # Record execution
            if not dry_run:
                await self.policy_repo.record_execution(
                    policy_id,
                    datetime.utcnow(),
                    success=len(results['errors']) == 0,
                    details=results
                )
                await self.db.commit()
            
            logger.info(f"Executed policy {policy_id} (dry_run: {dry_run})")
            return results
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to execute policy: {str(e)}")
            raise
    
    async def execute_all_policies(
        self,
        service: Optional[str] = None,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Execute all enabled policies."""
        try:
            policies = await self.policy_repo.list_policies(
                service=service,
                enabled_only=True
            )
            
            results = []
            for policy in policies:
                try:
                    result = await self.execute_policy(policy.id, dry_run)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to execute policy {policy.id}: {str(e)}")
                    results.append({
                        'policy_id': str(policy.id),
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute policies: {str(e)}")
            raise
    
    async def _get_policy_assets(
        self,
        policy: LifecyclePolicy
    ) -> List[Asset]:
        """Get assets that match policy criteria."""
        assets = []
        
        # Get assets for each target service
        if policy.target_services:
            for service in policy.target_services:
                service_assets = await self.asset_repo.list(
                    service=service,
                    limit=1000  # Adjust as needed
                )
                assets.extend(service_assets)
        else:
            # Get all assets if no specific services
            assets = await self.asset_repo.list(limit=1000)
        
        # Filter by type if specified
        if policy.target_types:
            assets = [a for a in assets if str(a.asset_type) in policy.target_types]
        
        # Filter by tags if specified
        if policy.target_tags:
            assets = [
                a for a in assets
                if any(tag in (a.tags or []) for tag in policy.target_tags)
            ]
        
        return assets
    
    async def _execute_rule(
        self,
        rule: PolicyRule,
        assets: List[Asset],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute a single rule on assets."""
        result = {
            'rule_id': str(rule.id),
            'rule_type': rule.rule_type.value,
            'assets_affected': 0,
            'actions_taken': []
        }
        
        for asset in assets:
            if await self._matches_condition(asset, rule.condition):
                if not dry_run:
                    await self._apply_action(asset, rule.action)
                
                result['assets_affected'] += 1
                result['actions_taken'].append({
                    'asset_id': str(asset.id),
                    'action': rule.action
                })
        
        return result
    
    async def _matches_condition(
        self,
        asset: Asset,
        condition: Dict[str, Any]
    ) -> bool:
        """Check if an asset matches a rule condition."""
        # Check age condition
        if 'age_days' in condition:
            age = datetime.utcnow() - asset.created_at
            if age.days < condition['age_days']:
                return False
        
        # Check size condition
        if 'size_greater_than' in condition:
            if asset.size <= condition['size_greater_than']:
                return False
        
        # Check access time
        if 'not_accessed_days' in condition:
            last_accessed = asset.metadata.get('last_accessed')
            if last_accessed:
                last_accessed_dt = datetime.fromisoformat(last_accessed)
                days_since = (datetime.utcnow() - last_accessed_dt).days
                if days_since < condition['not_accessed_days']:
                    return False
        
        return True
    
    async def _apply_action(
        self,
        asset: Asset,
        action: Dict[str, Any]
    ) -> None:
        """Apply an action to an asset."""
        action_type = action.get('type')
        
        if action_type == 'delete':
            await self.asset_repo.soft_delete(asset.id)
        
        elif action_type == 'change_storage_class':
            new_class = action.get('storage_class')
            if new_class:
                # This would involve S3 storage class transition
                await self.s3_client.change_storage_class(
                    asset.s3_key,
                    new_class
                )
        
        elif action_type == 'archive':
            # Move to archive storage
            pass
        
        elif action_type == 'tag':
            # Add tag to asset
            tags = asset.tags or []
            tags.append(action.get('tag', 'lifecycle_processed'))
            await self.asset_repo.update(asset.id, {'tags': tags})
