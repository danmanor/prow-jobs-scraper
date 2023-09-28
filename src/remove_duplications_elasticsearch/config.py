import os

ES_URL = os.environ.get("ES_URL")
ES_USER = os.environ.get("ES_USER")
ES_PASSWORD = os.environ.get("ES_PASSWORD")
ES_INDEX = os.environ.get("INDEX")
DOCUMENT_COMPARISON_FIELD = os.environ.get("DOCUMENT_COMPARISON_FIELD")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DRY_RUN = os.environ.get("DRY_RUN", "false")
