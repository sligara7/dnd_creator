"""Query builder for storage service."""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class StorageQuery(BaseModel):
    """Storage service query model."""
    
    type: str
    table: str
    where: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    @classmethod
    def select(
        cls,
        table: str,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> "StorageQuery":
        """Create SELECT query.
        
        Args:
            table: Table name
            where: WHERE conditions
            order_by: ORDER BY fields
            limit: LIMIT value
            offset: OFFSET value
            
        Returns:
            StorageQuery for SELECT
        """
        return cls(
            type="select",
            table=table,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
    
    @classmethod
    def insert(
        cls,
        table: str,
        data: Dict[str, Any],
    ) -> "StorageQuery":
        """Create INSERT query.
        
        Args:
            table: Table name
            data: Data to insert
            
        Returns:
            StorageQuery for INSERT
        """
        return cls(
            type="insert",
            table=table,
            data=data,
        )
    
    @classmethod
    def update(
        cls,
        table: str,
        where: Dict[str, Any],
        data: Dict[str, Any],
    ) -> "StorageQuery":
        """Create UPDATE query.
        
        Args:
            table: Table name
            where: WHERE conditions
            data: Update data
            
        Returns:
            StorageQuery for UPDATE
        """
        return cls(
            type="update",
            table=table,
            where=where,
            data=data,
        )
    
    @classmethod
    def delete(
        cls,
        table: str,
        where: Dict[str, Any],
    ) -> "StorageQuery":
        """Create DELETE query.
        
        Args:
            table: Table name
            where: WHERE conditions
            
        Returns:
            StorageQuery for DELETE
        """
        return cls(
            type="delete",
            table=table,
            where=where,
        )
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert to dict for storage service.
        
        Returns:
            Dict representation of query
        """
        data = super().model_dump(exclude_none=True)
        
        # Convert UUIDs to strings
        if data.get("where"):
            data["where"] = self._convert_uuids(data["where"])
        if data.get("data"):
            data["data"] = self._convert_uuids(data["data"])
            
        return data
    
    @staticmethod
    def _convert_uuids(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert UUIDs to strings in dict.
        
        Args:
            data: Dict potentially containing UUIDs
            
        Returns:
            Dict with UUIDs converted to strings
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, UUID):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = StorageQuery._convert_uuids(value)
            elif isinstance(value, list):
                result[key] = [
                    str(v) if isinstance(v, UUID) else v
                    for v in value
                ]
            else:
                result[key] = value
        return result