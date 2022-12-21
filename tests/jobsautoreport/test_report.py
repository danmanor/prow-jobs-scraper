from datetime import datetime, timedelta
from unittest.mock import MagicMock

from jobsautoreport.report import Report, Reporter
from prowjobsscraper.event import JobDetails, JobRefs, StepDetails, StepEvent

valid_queried_jobs = [
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="periodic",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="periodic",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="periodic",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-1",
        refs=JobRefs(base_ref="test", org="not-openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="periodic",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-1",
        refs=JobRefs(base_ref="test", org="openshift", repo="not-assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="periodic",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-subsystem-metal-assisted-3",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-subsystem-metal-assisted-3",
        refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="presubmit",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-20",
        refs=JobRefs(base_ref="test", org="openshift", repo="not-assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="pull-ci-openshift-assisted-service-master-edge-metal-assisted-40",
        refs=JobRefs(base_ref="test", org="openshift", repo="not-assisted-installer"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
    ),
]

valid_queried_step_events = [
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="pull-ci-openshift-assisted-service-master-edge-metal-assisted-41",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-1", state="success"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="pull-ci-openshift-assisted-service-master-edge-metal-assisted-42",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-2", state="failure"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="pull-ci-openshift-assisted-service-master-edge-metal-assisted-43",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-3", state="failure"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="pull-ci-openshift-assisted-service-master-edge-metal-assisted-44",
            refs=JobRefs(
                base_ref="test", org="openshift", repo="non-assisted-installer"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-3", state="success"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="pull-ci-openshift-assisted-service-master-edge-metal-assisted-45",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-4", state="success"
        ),
    ),
]

expected_report = Report(
    number_of_e2e_or_subsystem_periodic_jobs=3,
    number_of_successful_e2e_or_subsystem_periodic_jobs=2,
    number_of_failing_e2e_or_subsystem_periodic_jobs=1,
    success_rate_for_e2e_or_subsystem_periodic_jobs=66.67,
    top_10_failing_e2e_or_subsystem_periodic_jobs=[
        ("pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-0", 66.67)
    ],
    number_of_e2e_or_subsystem_presubmit_jobs=4,
    number_of_successful_e2e_or_subsystem_presubmit_jobs=3,
    number_of_failing_e2e_or_subsystem_presubmit_jobs=1,
    number_of_rehearsal_jobs=0,
    success_rate_for_e2e_or_subsystem_presubmit_jobs=75.0,
    top_10_failing_e2e_or_subsystem_presubmit_jobs=[
        (
            "pull-ci-openshift-assisted-service-master-edge-subsystem-metal-assisted-3",
            50.0,
        ),
        ("pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-2", 100.0),
    ],
    top_5_most_triggered_e2e_or_subsystem_jobs=[
        ("pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-0", 3),
        (
            "pull-ci-openshift-assisted-service-master-edge-subsystem-metal-assisted-3",
            2,
        ),
        ("pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted-2", 2),
    ],
    number_of_successful_machine_leases=3,
    number_of_unsuccessful_machine_leases=2,
    total_number_of_machine_leased=5,
)


def test_get_report_should_successfully_create_report_from_queried_jobs():
    querier_mock = MagicMock()
    querier_mock.query_jobs = MagicMock()
    querier_mock.query_step_events = MagicMock()
    querier_mock.query_jobs.return_value = valid_queried_jobs
    querier_mock.query_step_events.return_value = valid_queried_step_events
    reporter = Reporter(querier=querier_mock)
    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)
    report = reporter.get_report(from_date=a_week_ago, to_date=now)
    assert report == expected_report
