import logging
from typing import Any

from slack_sdk import WebClient

from jobsautoreport.models import JobType
from jobsautoreport.report import Report

logger = logging.getLogger(__name__)


class SlackReporter:
    def __init__(self, web_client: WebClient, channel_id: str) -> None:
        self._client = web_client
        self._channel_id = channel_id

    def send_report(self, report: Report) -> None:
        blocks = self._format_message(report)
        logger.debug("Message format finished successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks
        )
        response.validate()
        logger.info("Message sent successfully")

        time_stamp = response["ts"]
        blocks = self._format_presubmit_comment(report)
        logger.debug("comment format finished successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks, thread_ts=time_stamp
        )
        response.validate()
        logger.info("Presubmit comment sent successfully")
        blocks = self._format_equinix_comment(report)
        logger.debug("comment format finished successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks, thread_ts=time_stamp
        )
        response.validate()
        logger.info("Equinix comment sent successfully")

    @classmethod
    def _format_message(cls, report: Report) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = [
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
        ]

        cls._build_top_failing_jobs(
            report.top_10_failing_e2e_or_subsystem_periodic_jobs,
            result,
            JobType.PERIODIC,
        )

        return result

    @classmethod
    def _format_presubmit_comment(cls, report: Report) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = [
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
        ]

        cls._build_top_failing_jobs(
            report.top_10_failing_e2e_or_subsystem_presubmit_jobs,
            result,
            JobType.PRESUBMIT,
        )

        result.append(
            {
                "type": "section",
                "fields": cls._build_top_triggered_jobs(
                    report.top_5_most_triggered_e2e_or_subsystem_jobs
                ),
            }
        )

        return result

    @staticmethod
    def _format_equinix_comment(report: Report) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = [
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

        return result

    @staticmethod
    def _build_top_failing_jobs(
        top_jobs: list[tuple[str, Any]], result: list[dict[str, Any]], job_type: JobType
    ) -> None:

        if len(result) == 0:
            return

        result.append(
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Top {min(10, len(top_jobs))} failed e2e/subsystem {job_type.value} jobs:*",
                    }
                ],
            }
        )

        for i in range(0, len(top_jobs), 2):
            left_job = top_jobs[i]
            if i + 1 < len(top_jobs):
                right_job = top_jobs[i + 1]
                result.append(
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"•\t {left_job[0]}: \n{left_job[1]}%",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"•\t {right_job[0]}: \n{right_job[1]}%",
                            },
                        ],
                    }
                )
            else:
                result.append(
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"•\t {left_job[0]}: \n{left_job[1]}%",
                            }
                        ],
                    }
                )

    @staticmethod
    def _build_top_triggered_jobs(
        top_jobs: list[tuple[str, Any]]
    ) -> list[dict[str, Any]]:
        if len(top_jobs) == 0:
            return []
        res = [
            {
                "type": "mrkdwn",
                "text": f"*Top {min(5, len(top_jobs))} triggered e2e/subsystem jobs:*",
            }
        ]

        for job in top_jobs:
            res.append(
                {
                    "type": "mrkdwn",
                    "text": f"•\t {job[0]}: \t{job[1]}",
                }
            )

        return res
