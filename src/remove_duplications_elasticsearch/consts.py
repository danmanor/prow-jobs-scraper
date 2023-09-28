from typing import Any, Final

OPENSEARCH_QUERY_ALL_INDEX_DOCUMENTS: Final[dict[str, Any]] = {
    "query": {"match_all": {}}
}
