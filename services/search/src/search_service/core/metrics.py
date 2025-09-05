from prometheus_client import Counter, Gauge, Histogram

# Elasticsearch metrics
es_health_gauge = Gauge(
    "search_es_cluster_health",
    "Elasticsearch cluster health (0 = red, 1 = yellow, 2 = green)",
)

es_nodes_gauge = Gauge(
    "search_es_nodes_total",
    "Total number of nodes in the Elasticsearch cluster",
)

es_shards_gauge = Gauge(
    "search_es_shards_active",
    "Number of active shards in the Elasticsearch cluster",
)

es_unassigned_shards_gauge = Gauge(
    "search_es_shards_unassigned",
    "Number of unassigned shards in the Elasticsearch cluster",
)

# Cache metrics
cache_keys_gauge = Gauge(
    "search_cache_keys_total",
    "Total number of keys in the cache",
)

cache_memory_gauge = Gauge(
    "search_cache_memory_bytes",
    "Memory used by cache in bytes",
)

cache_clients_gauge = Gauge(
    "search_cache_clients_total",
    "Number of connected cache clients",
)

cache_hits_gauge = Counter(
    "search_cache_hits_total",
    "Total number of cache hits",
)

cache_misses_gauge = Counter(
    "search_cache_misses_total",
    "Total number of cache misses",
)

# Search operation metrics
search_requests = Counter(
    "search_requests_total",
    "Total number of search requests",
    ["index_type", "status"],
)

search_latency = Histogram(
    "search_request_duration_seconds",
    "Search request duration in seconds",
    ["index_type", "operation"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

search_result_count = Histogram(
    "search_result_total",
    "Number of search results",
    ["index_type"],
    buckets=(0, 1, 5, 10, 25, 50, 100, 250, 500, 1000),
)

# Index operation metrics
index_operations = Counter(
    "search_index_operations_total",
    "Total number of index operations",
    ["index_type", "operation", "status"],
)

index_latency = Histogram(
    "search_index_operation_duration_seconds",
    "Index operation duration in seconds",
    ["index_type", "operation"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

index_batch_size = Histogram(
    "search_index_batch_size",
    "Number of documents in bulk index operations",
    ["index_type"],
    buckets=(1, 10, 50, 100, 250, 500, 1000, 2500, 5000),
)

# System metrics
system_memory_usage = Gauge(
    "search_process_memory_bytes",
    "Memory usage of the search service process in bytes",
    ["type"],  # rss, vms
)

system_cpu_usage = Gauge(
    "search_process_cpu_percent",
    "CPU usage of the search service process",
)

system_open_files = Gauge(
    "search_process_open_files",
    "Number of open files by the search service process",
)

system_connections = Gauge(
    "search_process_connections",
    "Number of network connections by the search service process",
)

# Component health metrics
component_health = Gauge(
    "search_component_health",
    "Health status of service components (0 = error, 1 = ok)",
    ["component"],
)
