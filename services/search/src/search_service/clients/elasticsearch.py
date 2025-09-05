from typing import Any, Dict, List, Optional
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError

from search_service.core.config import settings
from search_service.core.exceptions import (
    ElasticsearchError,
    IndexNotFoundError,
    DocumentNotFoundError,
)


class ElasticsearchClient:
    """Elasticsearch client wrapper"""

    def __init__(self) -> None:
        """Initialize Elasticsearch client"""
        self.client = AsyncElasticsearch(
            hosts=settings.get_elasticsearch_hosts,
            basic_auth=(
                settings.ELASTICSEARCH_USERNAME,
                settings.ELASTICSEARCH_PASSWORD,
            ) if settings.ELASTICSEARCH_USERNAME else None,
            verify_certs=settings.ELASTICSEARCH_VERIFY_CERTS,
            retry_on_timeout=True,
            max_retries=settings.MAX_RETRIES,
        )

    async def close(self) -> None:
        """Close client connection"""
        await self.client.close()

    async def create_index(self, index: str, mappings: Dict[str, Any]) -> None:
        """Create index with mappings"""
        try:
            await self.client.indices.create(
                index=settings.get_index_name(index),
                body={
                    "settings": {
                        "number_of_shards": settings.ES_NUMBER_OF_SHARDS,
                        "number_of_replicas": settings.ES_NUMBER_OF_REPLICAS,
                        "refresh_interval": settings.INDEX_REFRESH_INTERVAL,
                        "analysis": {
                            "analyzer": {
                                "dnd_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": [
                                        "lowercase",
                                        "stop",
                                        "snowball",
                                        "synonym",
                                        "word_delimiter",
                                    ],
                                }
                            },
                            "filter": {
                                "synonym": {
                                    "type": "synonym",
                                    "synonyms_path": "synonyms/dnd_synonyms.txt",
                                }
                            },
                        },
                    },
                    "mappings": mappings,
                },
            )
        except RequestError as e:
            raise ElasticsearchError(str(e), "create_index")

    async def delete_index(self, index: str) -> None:
        """Delete index"""
        try:
            await self.client.indices.delete(index=settings.get_index_name(index))
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "delete_index")

    async def index_document(
        self,
        index: str,
        document: Dict[str, Any],
        document_id: Optional[str] = None,
    ) -> str:
        """Index a document"""
        try:
            result = await self.client.index(
                index=settings.get_index_name(index),
                body=document,
                id=document_id,
                refresh=True,
            )
            return result["_id"]
        except RequestError as e:
            raise ElasticsearchError(str(e), "index_document")

    async def bulk_index(
        self,
        index: str,
        documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Bulk index documents"""
        operations = []
        for doc in documents:
            operations.extend([
                {"index": {"_index": settings.get_index_name(index)}},
                doc,
            ])
        try:
            return await self.client.bulk(
                operations=operations,
                refresh=True,
            )
        except RequestError as e:
            raise ElasticsearchError(str(e), "bulk_index")

    async def get_document(
        self,
        index: str,
        document_id: str,
    ) -> Dict[str, Any]:
        """Get document by ID"""
        try:
            result = await self.client.get(
                index=settings.get_index_name(index),
                id=document_id,
            )
            return result["_source"]
        except NotFoundError:
            raise DocumentNotFoundError(document_id, index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "get_document")

    async def update_document(
        self,
        index: str,
        document_id: str,
        update: Dict[str, Any],
    ) -> None:
        """Update document by ID"""
        try:
            await self.client.update(
                index=settings.get_index_name(index),
                id=document_id,
                body={"doc": update},
                refresh=True,
            )
        except NotFoundError:
            raise DocumentNotFoundError(document_id, index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "update_document")

    async def delete_document(
        self,
        index: str,
        document_id: str,
    ) -> None:
        """Delete document by ID"""
        try:
            await self.client.delete(
                index=settings.get_index_name(index),
                id=document_id,
                refresh=True,
            )
        except NotFoundError:
            raise DocumentNotFoundError(document_id, index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "delete_document")

    async def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: Optional[int] = None,
        from_: Optional[int] = None,
        sort: Optional[List[Dict[str, Any]]] = None,
        source: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute search query"""
        try:
            return await self.client.search(
                index=settings.get_index_name(index),
                body=query,
                size=size or settings.DEFAULT_PAGE_SIZE,
                from_=from_ or 0,
                sort=sort,
                _source=source,
            )
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "search")

    async def count(self, index: str, query: Dict[str, Any]) -> int:
        """Get document count for query"""
        try:
            result = await self.client.count(
                index=settings.get_index_name(index),
                body=query,
            )
            return result["count"]
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "count")

    async def refresh(self, index: str) -> None:
        """Refresh index"""
        try:
            await self.client.indices.refresh(
                index=settings.get_index_name(index)
            )
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "refresh")

    async def get_mapping(self, index: str) -> Dict[str, Any]:
        """Get index mapping"""
        try:
            return await self.client.indices.get_mapping(
                index=settings.get_index_name(index)
            )
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "get_mapping")

    async def update_mapping(self, index: str, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Update index mapping"""
        try:
            return await self.client.indices.put_mapping(
                index=settings.get_index_name(index),
                body=mapping,
            )
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "update_mapping")

    async def analyze_text(
        self,
        index: str,
        text: str,
        analyzer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze text using index analyzer"""
        try:
            body = {
                "text": text,
            }
            if analyzer:
                body["analyzer"] = analyzer

            return await self.client.indices.analyze(
                index=settings.get_index_name(index),
                body=body,
            )
        except NotFoundError:
            raise IndexNotFoundError(index)
        except RequestError as e:
            raise ElasticsearchError(str(e), "analyze_text")
