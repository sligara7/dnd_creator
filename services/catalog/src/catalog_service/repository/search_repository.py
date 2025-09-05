from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from catalog_service.domain.models import BaseContent, ContentType


class SearchRepository:
    """Repository for search operations"""

    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index_name = "catalog"
        self._mappings = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "description": {"type": "text"},
                    "source": {"type": "keyword"},
                    "properties": {"type": "object"},
                    "themes": {"type": "keyword"},
                    "balance_score": {"type": "float"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "dnd_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"],
                        }
                    }
                },
            },
        }

    async def setup(self):
        """Create index and mappings if they don't exist"""
        if not await self.es.indices.exists(index=self.index_name):
            await self.es.indices.create(
                index=self.index_name, body=self._mappings
            )

    async def index_content(self, content: BaseContent):
        """Index content for search"""
        doc = self._to_search_doc(content)
        await self.es.index(
            index=self.index_name,
            id=str(content.id),
            document=doc,
            refresh=True,
        )

    async def update_content(self, content: BaseContent):
        """Update indexed content"""
        doc = self._to_search_doc(content)
        await self.es.update(
            index=self.index_name,
            id=str(content.id),
            doc=doc,
            refresh=True,
        )

    async def remove_content(self, content_type: ContentType, content_id: UUID):
        """Remove content from index"""
        await self.es.delete(
            index=self.index_name,
            id=str(content_id),
            refresh=True,
        )

    async def search(
        self,
        query: str,
        content_type: Optional[ContentType] = None,
        theme: Optional[str] = None,
        filters: Optional[Dict] = None,
        sort: Optional[Dict] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict:
        """Search content items"""
        # Build query
        must = [{"query_string": {"query": query, "fields": ["name^3", "description"]}}]
        filter_clauses = []
        
        if content_type:
            filter_clauses.append({"term": {"type": content_type}})
            
        if theme:
            filter_clauses.append({"term": {"themes": theme}})
            
        if filters:
            for field, value in filters.items():
                if isinstance(value, (list, tuple)):
                    filter_clauses.append({"terms": {field: value}})
                elif isinstance(value, dict):
                    if "min" in value or "max" in value:
                        range_filter = {"range": {field: {}}}
                        if "min" in value:
                            range_filter["range"][field]["gte"] = value["min"]
                        if "max" in value:
                            range_filter["range"][field]["lte"] = value["max"]
                        filter_clauses.append(range_filter)
                else:
                    filter_clauses.append({"term": {field: value}})
                    
        body = {
            "query": {
                "bool": {
                    "must": must,
                    "filter": filter_clauses,
                }
            },
            "from": (page - 1) * size,
            "size": size,
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {},
                },
            },
        }
        
        if sort:
            body["sort"] = [{sort["field"]: {"order": sort["order"]}}]
            
        # Execute search
        result = await self.es.search(
            index=self.index_name,
            body=body,
        )
        
        # Process results
        total = result["hits"]["total"]["value"]
        items = []
        
        for hit in result["hits"]["hits"]:
            item = {
                "id": hit["_source"]["id"],
                "type": hit["_source"]["type"],
                "name": hit["_source"]["name"],
                "description": hit["_source"]["description"],
                "score": hit["_score"],
            }
            
            if "highlight" in hit:
                item["highlight"] = hit["highlight"]
                
            items.append(item)
            
        return {
            "total": total,
            "page": page,
            "items": items,
        }

    def _to_search_doc(self, content: BaseContent) -> Dict:
        """Convert content to search document"""
        return {
            "id": str(content.id),
            "type": content.type,
            "name": content.name,
            "description": content.description,
            "source": content.source,
            "properties": content.properties,
            "themes": [t for t in content.theme_data.themes],
            "balance_score": content.validation.balance_score,
            "created_at": content.metadata.created_at.isoformat(),
            "updated_at": content.metadata.updated_at.isoformat(),
        }
