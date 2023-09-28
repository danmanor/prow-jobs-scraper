import json
from typing import Any
from unittest.mock import MagicMock, patch

import pkg_resources
import pytest

from remove_duplications_elasticsearch import main


@pytest.fixture(autouse=True)
def str_to_bool():
    with patch("remove_duplications_elasticsearch.main.str_to_bool") as func:
        func.return_value = False

        yield func


@pytest.fixture(autouse=True)
def mock_config():
    with patch("remove_duplications_elasticsearch.main.config") as config:
        config.ES_URL = ""
        config.ES_USER = ""
        config.ES_PASSWORD = ""
        config.ES_INDEX = "jobs-*"
        config.DOCUMENT_COMPARISON_FIELD = "job.build_id"

        yield config


@pytest.fixture()
def documents() -> list[dict[str, Any]]:
    return json.loads(
        pkg_resources.resource_string(__name__, f"assets/job_assets.json")
    )


@pytest.fixture(autouse=True)
def mock_opensearch_helpers(documents) -> MagicMock:
    with patch("remove_duplications_elasticsearch.main.helpers") as os_helpers:
        os_helpers.scan.return_value = documents
        yield os_helpers


@pytest.fixture(autouse=True)
def mock_opensearch_client() -> MagicMock:
    with patch("remove_duplications_elasticsearch.main.OpenSearch") as opensearch:
        yield opensearch()


def test_get_bulk_actions_with_compatibale_arguments_should_be_successfull(
    documents,
):
    bulk_actions = main.get_bulk_actions(
        documents, "job.build_id", "jobs-*", MagicMock()
    )

    assert len(bulk_actions) == 2


def test_get_bulk_actions_with_incompatibale_arguments_should_be_unsuccessfull(
    documents,
):
    
    _ , failures = main.get_bulk_actions(
        documents,
        "job.build_id.missing_field",
        "jobs-*",
        MagicMock(),
    )

    assert len(failures) > 0


def test_get_value_from_dict_with_compatible_arguments_should_be_successfull(
    documents,
):
    document = documents[0]

    assert main.get_value_from_dict("job.refs.org", document["_source"]) == "openshift"


def test_get_value_from_dict_with_incompatible_arguments_should_be_unsuccessfull(
    documents,
):
    document = documents[0]

    with pytest.raises(ValueError):
        main.get_value_from_dict("job.refs.nonexisting_field", document["_source"])


def test_full_flow_should_be_successfull(
    mock_opensearch_helpers, mock_opensearch_client
):
    main.main()

    mock_opensearch_helpers.scan.assert_called_once()
    mock_opensearch_helpers.bulk.assert_called_once()
    mock_opensearch_client.indices.refresh.assert_called_once()


def test_dry_run_flow_should_be_successfull(
    mock_opensearch_helpers, mock_opensearch_client, str_to_bool
):
    str_to_bool.return_value = True

    main.main()

    mock_opensearch_helpers.scan.assert_called_once()
    mock_opensearch_helpers.bulk.asser_not_called()
    mock_opensearch_client.indices.refresh.assert_not_called()
