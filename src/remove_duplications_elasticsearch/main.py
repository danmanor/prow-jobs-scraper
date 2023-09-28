"""This script is used for removing duplicate documents from an OpenSearch index.

The main logic includes:
1. Setting up the OpenSearch client.
2. Fetching all documents from the specified OpenSearch index.
3. Identifying duplicate documents based on a comparison field.
4. Removing the duplicates if not in dry-run mode or logging the bulk actions if in dry-run mode.
"""

import json
import logging
from itertools import tee
from typing import Any, Generator, Tuple

from opensearchpy import OpenSearch, helpers

from remove_duplications_elasticsearch import config, consts

from remove_duplications_elasticsearch.logger import get_logger
from remove_duplications_elasticsearch.utils import str_to_bool

logger = get_logger(config.LOG_LEVEL)


def remove_documents(
    opensearch_client: OpenSearch,
    actions: list[dict[str, str]],
    index: str,
    logger: logging.Logger,
):
    """Removes specified documents from the OpenSearch index.

    Args:
        opensearch_client: The client to communicate with OpenSearch.
        actions: List of actions to remove documents.
        index: The name of the index.
        logger: Logger for logging info and exceptions.

    Raises:
        FailedToRefreshIndex: If unable to refresh the index.
        ExceptionGroup: If there are errors in bulk removal of documents.
    """
    bulk_errors = helpers.bulk(client=opensearch_client, actions=actions)
    logger.info(f"Removed '{len(actions)}' duplicates from '{index}'.")

    opensearch_client.indices.refresh(index=index)

    if len(bulk_errors) > 0:
        logger.exception("bulk errors")
        for err in bulk_errors:
            logger.exception("bulk error: ", exc_info=err)  # type: ignore


def get_bulk_actions(
    documents: Generator,
    comparison_field: str,
    index: str,
    logger: logging.Logger,
) -> Tuple[list[dict[str, str]], list[str]]:
    """Generates bulk actions for documents based on a comparison field.

    Args:
        documents: List of documents to be compared.
        comparison_field: The field for comparison to identify unique documents.
        index: The name of the index.
        logger: Logger for logging info and exceptions.

    Returns:
        List of bulk actions for the documents.

    Raises:
        ExceptionGroup: If there are issues retrieving the comparable field from all documents.
    """
    seen_values = set()
    bulk_actions = []
    failures = []

    for doc in documents:
        try:
            unique_field_value = get_value_from_dict(
                dot_notation_string=comparison_field,
                data=doc["_source"],
            )

        except Exception as e:
            logger.exception(
                f"failed to get the document _id '{doc['_id']}' comparison field '{comparison_field}' value",
                exc_info=e,
            )
            failures.append(doc["_id"])

        else:
            if unique_field_value in seen_values:
                bulk_actions.append(
                    {
                        "_op_type": "delete",
                        "_index": index,
                        "_id": doc["_id"],
                    }
                )
            else:
                seen_values.add(unique_field_value)

    return bulk_actions, failures


def fetch_all_documents(
    opensearch_client: OpenSearch,
    index_name: str,
    query: dict[str, Any],
) -> Generator:
    """Fetches all documents from an OpenSearch index based on a query.

    Args:
        opensearch_client: The client to communicate with OpenSearch.
        index_name: The name of the index.
        query: The query to filter documents.

    Returns:
        A generator that yields fetched documents.
    """
    return helpers.scan(
        opensearch_client,
        index=index_name,
        query=query,
        ignore_unavailable=True,
    )


def get_value_from_dict(dot_notation_string: str, data: dict[str, Any]) -> Any:
    """Retrieves a value from a dictionary based on dot notation string.

    Args:
        dot_notation_string: The string in dot notation representing keys in the dictionary.
        data: The dictionary to extract data from.

    Returns:
        The value extracted from the dictionary based on the dot notation string.

    Raises:
        ValueError: If any key in the dot notation string is not found in the dictionary.
    """
    keys = dot_notation_string.split(".")

    for key in keys:
        if key in data.keys():
            data = data[key]
        else:
            raise ValueError(f"Key {key} not found in the dictionary")

    return data


def main() -> None:
    if (
        config.ES_INDEX is None
        or config.ES_URL is None
        or config.ES_USER is None
        or config.ES_PASSWORD is None
        or config.DOCUMENT_COMPARISON_FIELD is None
    ):
        raise FailedToGetAllEnvironmentVariables()

    opensearch_client = OpenSearch(
        config.ES_URL,
        http_auth=(config.ES_USER, config.ES_PASSWORD),
        verify_certs=False,
        ssl_show_warn=False,
    )

    documents = fetch_all_documents(
        opensearch_client=opensearch_client,
        index_name=config.ES_INDEX,
        query=consts.OPENSEARCH_QUERY_ALL_INDEX_DOCUMENTS,
    )

    log_documents = tee(documents, 1)
    logger.info(
        f"Found '{len(list(log_documents))}' documents inside '{config.ES_INDEX}' index"
    )

    bulk_actions, failures = get_bulk_actions(
        documents=documents,
        comparison_field=config.DOCUMENT_COMPARISON_FIELD,
        index=config.ES_INDEX,
        logger=logger,
    )
    logger.info(f"Found '{len(bulk_actions)}' duplicated documents")

    if len(bulk_actions) == 0:
        logger.info(f"No duplicates found in '{config.ES_INDEX}'.")
        return

    if len(failures) > 0:
        logger.exception("failed to process the following documents ids:")
        for document in failures:
            logger.exception(document)

    dry_run_mode: bool = str_to_bool(config.DRY_RUN)
    if dry_run_mode:
        logger.info("Bulk Actions:")
        for action in bulk_actions:
            logger.info(json.dumps(action, indent=4))

        return

    remove_documents(
        opensearch_client=opensearch_client,
        actions=bulk_actions,
        index=config.ES_INDEX,
        logger=logger,
    )


if __name__ == "__main__":
    main()
