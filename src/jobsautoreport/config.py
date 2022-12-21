import os

ES_URL = os.environ["ES_URL"]
ES_USER = os.environ["ES_USER"]
ES_PASSWORD = os.environ["ES_PASSWORD"]
ES_JOB_INDEX = os.environ["ES_JOB_INDEX"]
ES_STEP_INDEX = os.environ["ES_STEP_INDEX"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
