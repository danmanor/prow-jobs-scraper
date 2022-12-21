from enum import Enum
from typing import NewType


class JobType(Enum):
    PRESUBMIT = "presubmit"
    POSTSUBMIT = "postsubmit"
    PERIODIC = "periodic"
    BATCH = "batch"


class JobState(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


StepState = NewType("StepState", JobState)(JobState)
