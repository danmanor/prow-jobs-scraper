import logging
import sys
from datetime import datetime, timedelta

from opensearchpy import OpenSearch
from slack_sdk import WebClient

from jobsautoreport import config
from jobsautoreport.query import Querier
from jobsautoreport.report import Reporter
from jobsautoreport.slack import SlackReporter


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=config.LOG_LEVEL)

    os_usr = config.ES_USER
    os_pwd = config.ES_PASSWORD
    os_host = config.ES_URL

    client = OpenSearch(os_host, http_auth=(os_usr, os_pwd))

    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)

    jobs_index = config.ES_JOB_INDEX + "-*"
    steps_index = config.ES_STEP_INDEX + "-*"

    querier = Querier(client, jobs_index, steps_index)
    reporter = Reporter(querier)

    report = reporter.get_report(from_date=a_week_ago, to_date=now)

    web_client = WebClient(token=config.SLACK_BOT_TOKEN)
    slack_reporter = SlackReporter(
        web_client=web_client, channel_id=config.SLACK_CHANNEL_ID
    )
    slack_reporter.send_report(report)


if __name__ == "__main__":
    main()
