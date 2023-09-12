from unittest.mock import MagicMock, patch

import pytest

from jobsautoreport.models import (
    FeatureFlags,
    JobIdentifier,
    JobTypeMetrics,
    MachineMetrics,
    Report,
    Trends,
)
from jobsautoreport.slack.slack_report import SlackReporter


@pytest.fixture
def mock_thread_time_stamp() -> dict[str, str]:
    return {"ts": "test-thread-time-stamp"}


@pytest.fixture
def slack_reporter(mock_thread_time_stamp) -> SlackReporter:
    test_channel = "test-channel"
    web_client_mock = MagicMock()
    response_mock = MagicMock()
    response_mock.validate.return_value = True
    response_mock.__getitem__.side_effect = mock_thread_time_stamp.__getitem__
    web_client_mock.chat_postMessage.return_value = response_mock
    web_client_mock.files_upload.return_value = response_mock

    return SlackReporter(web_client=web_client_mock, channel_id=test_channel)


@pytest.fixture
def mock_trends() -> Trends:
    return Trends(
        number_of_e2e_or_subsystem_periodic_jobs=10,
        success_rate_for_e2e_or_subsystem_periodic_jobs=0.03,
        number_of_e2e_or_subsystem_presubmit_jobs=5,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=None,
        number_of_rehearsal_jobs=0,
        number_of_postsubmit_jobs=5,
        success_rate_for_postsubmit_jobs=-0.02,
        total_number_of_machine_leased=50,
        number_of_unsuccessful_machine_leases=-3,
        total_equinix_machines_cost=1000,
    )


@pytest.fixture(autouse=True)
def mock_plotter() -> MagicMock:
    with patch("jobsautoreport.plot.Plotter") as plotter:
        plotter_graph_creation_returned_value = ("test-filename", "test-file-path")
        plotter.create_most_failing_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        plotter.create_most_triggered_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        plotter.create_flaky_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        plotter.create_most_expensive_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        plotter.create_pie_chart.return_value = plotter_graph_creation_returned_value
        yield plotter


@pytest.fixture(autouse=True)
def mock_slack_generator() -> MagicMock:
    with patch("jobsautoreport.slack.slack_report.SlackGenerator") as slack_generator:
        yield slack_generator


@pytest.fixture(autouse=True)
def mock_trend_slack_integrator() -> MagicMock:
    with patch(
        "jobsautoreport.slack.slack_report.TrendSlackIntegrator"
    ) as trend_slack_integrator:
        yield trend_slack_integrator


def test__send_success_rates_with_trends(
    mock_report_1: Report,
    mock_trends: Trends,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    mock_slack_generator: MagicMock,
    slack_reporter: SlackReporter,
    mock_trend_slack_integrator: MagicMock,
):
    slack_reporter._send_success_rates(
        report=mock_report_1,
        trends=mock_trends,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )
    # periodics
    mock_slack_generator.create_periodic_comment.assert_called_once()
    mock_trend_slack_integrator.add_periodic_trends.assert_called_once()

    # presubmits
    mock_slack_generator.create_presubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_presubmit_trends.assert_called_once()

    # postsubmits
    mock_slack_generator.create_postsubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_postsubmit_trends.assert_called_once()

    # graphs
    assert mock_plotter.create_most_failing_jobs_graph.call_count == 3
    assert mock_plotter.create_most_triggered_jobs_graph.call_count == 1
    assert slack_reporter._client.files_upload.call_count == 4

    # messages
    assert slack_reporter._client.chat_postMessage.call_count == 3


def test__send_success_rates_without_trends(
    mock_report_1: Report,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    mock_slack_generator: MagicMock,
    slack_reporter: SlackReporter,
    mock_trend_slack_integrator: MagicMock,
):
    slack_reporter._send_success_rates(
        report=mock_report_1,
        trends=None,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )
    # periodics
    mock_slack_generator.create_periodic_comment.assert_called_once()
    mock_trend_slack_integrator.add_periodic_trends.assert_not_called()

    # presubmits
    mock_slack_generator.create_presubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_presubmit_trends.assert_not_called()

    # postsubmits
    mock_slack_generator.create_postsubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_postsubmit_trends.assert_not_called()

    # graphs
    assert mock_plotter.create_most_failing_jobs_graph.call_count == 3
    assert mock_plotter.create_most_triggered_jobs_graph.call_count == 1
    assert slack_reporter._client.files_upload.call_count == 4

    # messages
    assert slack_reporter._client.chat_postMessage.call_count == 3


def test__send_flakiness_rates_with_flaky_jobs(
    mock_report_1: Report,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    slack_reporter: SlackReporter,
):
    slack_reporter._send_flakiness_rates(
        report=mock_report_1,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )

    mock_plotter.create_flaky_jobs_graph.assert_called_once()
    slack_reporter._client.files_upload.assert_called_once()


def test__send_flakiness_rates_without_flaky_jobs(
    mock_report_2: Report,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    slack_reporter: SlackReporter,
):
    slack_reporter._send_flakiness_rates(
        report=mock_report_2,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )

    mock_plotter.create_flaky_jobs_graph.assert_not_called()
    slack_reporter._client.files_upload.assert_not_called()


def test__send_equinix_costs_with_trends(
    mock_report_1: Report,
    mock_trends: Trends,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    mock_slack_generator: MagicMock,
    slack_reporter: SlackReporter,
    mock_trend_slack_integrator: MagicMock,
):
    slack_reporter._send_equinix_costs(
        report=mock_report_1,
        trends=mock_trends,
        feature_flags=FeatureFlags(
            success_rates=True,
            equinix_usage=True,
            equinix_cost=True,
            trends=True,
            flakiness_rates=True,
        ),
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )

    mock_slack_generator.create_equinix_message.assert_called_once()
    mock_trend_slack_integrator.add_equinix_trends.assert_called_once()
    mock_plotter.create_most_expensive_jobs_graph.assert_called_once()
    mock_plotter.create_pie_chart.call_count == 2
    slack_reporter._client.files_upload.call_count == 3
    slack_reporter._client.chat_postMessage.call_count == 1


def test__send_equinix_costs_without_trends(
    mock_report_1: Report,
    mock_trends: Trends,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    mock_slack_generator: MagicMock,
    slack_reporter: SlackReporter,
    mock_trend_slack_integrator: MagicMock,
):
    slack_reporter._send_equinix_costs(
        report=mock_report_1,
        trends=None,
        feature_flags=FeatureFlags(
            success_rates=True,
            equinix_usage=True,
            equinix_cost=True,
            trends=False,
            flakiness_rates=True,
        ),
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )

    mock_slack_generator.create_equinix_message.assert_called_once()
    mock_trend_slack_integrator.add_equinix_trends.assert_not_called()
    mock_plotter.create_most_expensive_jobs_graph.assert_called_once()
    mock_plotter.create_pie_chart.call_count == 2
    slack_reporter._client.files_upload.call_count == 3
    slack_reporter._client.chat_postMessage.call_count == 1


def test_send_report_with_all_features(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        equinix_usage=True,
        equinix_cost=True,
        trends=True,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits, equinix
    assert slack_reporter._client.chat_postMessage.call_count == 5

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, (flaky jobs) graph, 3 equinix graphs
    assert slack_reporter._client.files_upload.call_count == 8


def test_send_report_with_all_features_but_success_rate(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=False,
        equinix_usage=True,
        equinix_cost=True,
        trends=True,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, equinix
    assert slack_reporter._client.chat_postMessage.call_count == 2

    # (flaky jobs) graph, 3 equinix graphs
    assert slack_reporter._client.files_upload.call_count == 4


def test_send_report_with_all_features_but_equinix_usage(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        equinix_usage=False,
        equinix_cost=True,
        trends=True,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits, equinix (partial)
    assert slack_reporter._client.chat_postMessage.call_count == 5

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, (flaky jobs) graph, 3 equinix graphs
    assert slack_reporter._client.files_upload.call_count == 8


def test_send_report_with_all_features_but_equinix_cost(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        equinix_usage=True,
        equinix_cost=False,
        trends=True,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits, equinix (partial)
    assert slack_reporter._client.chat_postMessage.call_count == 5

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, (flaky jobs) graph
    assert slack_reporter._client.files_upload.call_count == 5


def test_send_report_with_all_features_but_trends(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        equinix_usage=True,
        equinix_cost=True,
        trends=False,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits, equinix
    assert slack_reporter._client.chat_postMessage.call_count == 5

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, (flaky jobs) graph, 3 equinix graphs
    assert slack_reporter._client.files_upload.call_count == 8


def test_send_report_with_all_features_but_flakiness_rates(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        equinix_usage=True,
        equinix_cost=True,
        trends=True,
        flakiness_rates=False,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits, equinix
    assert slack_reporter._client.chat_postMessage.call_count == 5

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, 3 equinix graphs
    assert slack_reporter._client.files_upload.call_count == 7


def test_format_cost_by_machine_type_metrics():
    machine_metrics = MachineMetrics(
        metrics={
            "c1.small.x86_64": 500,
            "c2.large.x86_64": 300,
            "m1.xlarge.x86_64": 100,
            "e1.xlarge.x86_64": 4,
            "e1.small.x86_64": 4,
            "Outbound Bandwidth": 10,
        }
    )
    slack_reporter = SlackReporter(web_client=MagicMock(), channel_id=MagicMock())
    types, costs = slack_reporter._create_cost_by_machine_type_metrics(
        machine_metrics, threshold=0.02
    )
    assert types == ["Others", "c1 small x86_64", "c2 large x86_64", "m1 xlarge x86_64"]
    assert costs == [8, 100, 300, 500]


def test_format_cost_by_job_type_metrics():
    job_type_metrics = JobTypeMetrics(
        metrics={
            "batch": 1000,
            "presubmit": 500,
            "periodic": 5,
            "postsubmit": 5,
        }
    )
    slack_reporter = SlackReporter(web_client=MagicMock(), channel_id=MagicMock())
    types, costs = slack_reporter._create_cost_by_job_type_metrics(
        job_type_metrics, threshold=0.02
    )
    assert types == ["Others", "batch", "presubmit"]
    assert costs == [10, 500, 1000]
