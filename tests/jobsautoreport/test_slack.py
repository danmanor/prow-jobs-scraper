from unittest.mock import MagicMock

from jobsautoreport.report import Report
from jobsautoreport.slack import SlackReporter


def test_send_report_should_successfully_call_slack_api_with_expected_message_format():
    report = Report(
        number_of_e2e_or_subsystem_periodic_jobs=12,
        number_of_successful_e2e_or_subsystem_periodic_jobs=9,
        number_of_failing_e2e_or_subsystem_periodic_jobs=3,
        success_rate_for_e2e_or_subsystem_periodic_jobs=75,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[("fake-job-1", 75)],
        number_of_e2e_or_subsystem_presubmit_jobs=24,
        number_of_successful_e2e_or_subsystem_presubmit_jobs=8,
        number_of_failing_e2e_or_subsystem_presubmit_jobs=16,
        number_of_rehearsal_jobs=0,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=33.33,
        top_10_failing_e2e_or_subsystem_presubmit_jobs=[("fake-job-2", 33.33)],
        top_5_most_triggered_e2e_or_subsystem_jobs=[
            ("fake-job-2", 24),
            ("fake-job-1", 12),
        ],
        number_of_successful_machine_leases=1,
        number_of_unsuccessful_machine_leases=2,
        total_number_of_machine_leased=3,
    )

    expected_blocks_periodic = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Periodic e2e/subsystem jobs report:",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Number of e2e/subsystem periodic jobs:* \n{report.number_of_e2e_or_subsystem_periodic_jobs} - \t:slack-green: {report.number_of_successful_e2e_or_subsystem_periodic_jobs} :x: {report.number_of_failing_e2e_or_subsystem_periodic_jobs}",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Success rate for e2e/subsystem periodic jobs:* {report.success_rate_for_e2e_or_subsystem_periodic_jobs}%",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Top {min(10, len(report.top_10_failing_e2e_or_subsystem_periodic_jobs))} failed e2e/subsystem periodic jobs:*",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"•\t {report.top_10_failing_e2e_or_subsystem_periodic_jobs[0][0]}: \n{report.top_10_failing_e2e_or_subsystem_periodic_jobs[0][1]}%",
                }
            ],
        },
    ]

    expected_blocks_presubmit = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Presubmit e2e jobs report:",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Number of e2e/subsystem presubmit jobs:* {report.number_of_e2e_or_subsystem_presubmit_jobs} - \n:slack-green: {report.number_of_successful_e2e_or_subsystem_presubmit_jobs} :x: {report.number_of_failing_e2e_or_subsystem_presubmit_jobs}",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Number of rehearsal jobs:* {report.number_of_rehearsal_jobs}",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Success rate for e2e/subsystem presubmit jobs:* {report.success_rate_for_e2e_or_subsystem_presubmit_jobs}%",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Top {min(10, len(report.top_10_failing_e2e_or_subsystem_presubmit_jobs))} failed e2e/subsystem presubmit jobs:*",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"•\t {report.top_10_failing_e2e_or_subsystem_presubmit_jobs[0][0]}: \n{report.top_10_failing_e2e_or_subsystem_presubmit_jobs[0][1]}%",
                },
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Top {min(5, len(report.top_5_most_triggered_e2e_or_subsystem_jobs))} triggered e2e/subsystem jobs:*",
                },
                {
                    "type": "mrkdwn",
                    "text": f"•\t {report.top_5_most_triggered_e2e_or_subsystem_jobs[0][0]}: \t{report.top_5_most_triggered_e2e_or_subsystem_jobs[0][1]}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"•\t {report.top_5_most_triggered_e2e_or_subsystem_jobs[1][0]}: \t{report.top_5_most_triggered_e2e_or_subsystem_jobs[1][1]}",
                },
            ],
        },
    ]

    expected_blocks_equinix = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Equinix",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Number of machines leased:* {report.total_number_of_machine_leased} - \n:slack-green: {report.number_of_successful_machine_leases} :x: {report.number_of_unsuccessful_machine_leases}",
                }
            ],
        },
    ]

    test_channel = "test-channel"
    test_thread_time_stamp = {"ts": "test-thread-time_stamp"}
    web_client_mock = MagicMock()
    web_client_mock.chat_postMessage = MagicMock()
    response_mock = MagicMock()
    response_mock.validate = MagicMock()
    response_mock.validate.return_value = True
    response_mock.__getitem__.side_effect = test_thread_time_stamp.__getitem__
    web_client_mock.chat_postMessage.return_value = response_mock
    slack_reporter = SlackReporter(web_client=web_client_mock, channel_id=test_channel)
    slack_reporter.send_report(report)
    web_client_mock.chat_postMessage.assert_any_call(
        channel=test_channel, blocks=expected_blocks_periodic
    )
    web_client_mock.chat_postMessage.assert_any_call(
        channel=test_channel,
        blocks=expected_blocks_presubmit,
        thread_ts=test_thread_time_stamp["ts"],
    )
    web_client_mock.chat_postMessage.assert_any_call(
        channel=test_channel,
        blocks=expected_blocks_equinix,
        thread_ts=test_thread_time_stamp["ts"],
    )
