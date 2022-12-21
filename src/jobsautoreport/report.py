from datetime import datetime
from typing import Any, Callable

from pydantic import BaseModel

from jobsautoreport.models import JobState, JobType, StepState
from jobsautoreport.query import Querier
from prowjobsscraper.event import JobDetails, StepEvent


class Report(BaseModel):

    number_of_e2e_or_subsystem_periodic_jobs: int
    number_of_successful_e2e_or_subsystem_periodic_jobs: int
    number_of_failing_e2e_or_subsystem_periodic_jobs: int
    success_rate_for_e2e_or_subsystem_periodic_jobs: float
    top_10_failing_e2e_or_subsystem_periodic_jobs: list[tuple[str, float]]
    number_of_e2e_or_subsystem_presubmit_jobs: int
    number_of_successful_e2e_or_subsystem_presubmit_jobs: int
    number_of_failing_e2e_or_subsystem_presubmit_jobs: int
    number_of_rehearsal_jobs: int
    success_rate_for_e2e_or_subsystem_presubmit_jobs: float
    top_10_failing_e2e_or_subsystem_presubmit_jobs: list[tuple[str, float]]
    top_5_most_triggered_e2e_or_subsystem_jobs: list[tuple[str, int]]
    number_of_successful_machine_leases: int
    number_of_unsuccessful_machine_leases: int
    total_number_of_machine_leased: int

    def __str__(self) -> str:
        return (
            f"number_of_e2e_or_subsystem_periodic_jobs_triggered: {self.number_of_e2e_or_subsystem_periodic_jobs}\n"
            f"number_of_successful_e2e_or_subsystem_periodic_jobs_triggered: {self.number_of_successful_e2e_or_subsystem_periodic_jobs}\n"
            f"number_of_failures_e2e_or_subsystem_periodic_jobs_triggered: {self.number_of_failing_e2e_or_subsystem_periodic_jobs}\n"
            f"success_rate_for_e2e_or_subsystem_periodic_jobs: {self.success_rate_for_e2e_or_subsystem_periodic_jobs}\n"
            f"top_10_failed_e2e_or_subsystem_periodic_jobs: {self.top_10_failing_e2e_or_subsystem_periodic_jobs}\n"
            f"number_of_e2e_or_subsystem_presubmit_jobs_triggered: {self.number_of_e2e_or_subsystem_presubmit_jobs}\n"
            f"number_of_successful_e2e_or_subsystem_presubmit_jobs_triggered: {self.number_of_successful_e2e_or_subsystem_presubmit_jobs}\n"
            f"number_of_failures_e2e_or_subsystem_pre_submit_jobs_triggered: {self.number_of_failing_e2e_or_subsystem_presubmit_jobs}\n"
            f"number_of_rehearsal_jobs_triggered: {self.number_of_rehearsal_jobs}\n"
            f"success_rate_for_e2e_or_subsystem_presubmit_jobs: {self.success_rate_for_e2e_or_subsystem_presubmit_jobs}\n"
            f"top_10_failed_e2e_or_subsystem_presubmit_jobs: {self.top_10_failing_e2e_or_subsystem_presubmit_jobs}\n"
            f"top_5_most_triggered_e2e_or_subsystem_jobs: {self.top_5_most_triggered_e2e_or_subsystem_jobs}\n"
            f"number_of_successful_machine_leases: {self.number_of_successful_machine_leases}\n"
            f"number_of_unsuccessful_machine_leases: {self.number_of_unsuccessful_machine_leases}\n"
            f"total_number_of_machine_leased: {self.total_number_of_machine_leased}\n"
        )


class Reporter:
    def __init__(self, querier: Querier):
        self._querier = querier

    @staticmethod
    def _get_job_triggers_count(job_name: str, jobs: list[JobDetails]) -> int:
        return sum(1 for job in jobs if job.name == job_name)

    @classmethod
    def _get_job_success_rate(cls, job_name: str, jobs: list[JobDetails]) -> float:
        job_by_name = [job for job in jobs if job.name == job_name]
        return cls._get_success_rate(job_by_name)

    @staticmethod
    def _get_number_of_jobs_by_state(
        jobs: list[JobDetails], job_state: JobState
    ) -> int:
        return len([job for job in jobs if job.state == job_state.value])

    @classmethod
    def _get_success_rate(cls, jobs: list[JobDetails]) -> float:
        total_jobs_number = len(jobs)
        successful_jobs_number = cls._get_number_of_jobs_by_state(
            jobs, JobState.SUCCESS
        )
        return (
            0
            if total_jobs_number == 0
            else float(round((successful_jobs_number / total_jobs_number) * 100, 2))
        )

    @staticmethod
    def _get_top_n_jobs(
        jobs: list[JobDetails],
        computation_func: Callable[[str, list[JobDetails]], Any],
        n: int,
        is_reverse: bool = False,
    ):
        distinct_jobs = {job.name for job in jobs}
        res = [
            (job_name, computation_func(job_name, jobs)) for job_name in distinct_jobs
        ]
        res = sorted(res, key=lambda job: (job[1], job[0]), reverse=is_reverse)
        return res[0 : min(len(res), n)]

    @staticmethod
    def _is_rehearsal(job: JobDetails) -> bool:
        return (
            "rehearse" in job.name
            and job.type == "presubmit"
            and job.refs.repo == "release"
            and job.refs.org == "openshift"
        )

    @staticmethod
    def _is_assisted_repository(job: JobDetails) -> bool:
        return (
            job.refs.repo
            in [
                "assisted-service",
                "assisted-installer",
                "assisted-installer-agent",
                "assisted-image-service",
                "assisted-test-infra",
                "cluster-api-provider-agent",
            ]
            and job.refs.org == "openshift"
        )

    @staticmethod
    def _is_e2e_or_subsystem_class(job: JobDetails) -> bool:
        return "e2e" in job.name or "subsystem" in job.name

    def get_report(self, from_date: datetime, to_date: datetime) -> Report:
        jobs = self._querier.query_jobs(from_date, to_date)
        step_events = self._querier.query_step_events(from_date, to_date)
        rehearsal_jobs = [job for job in jobs if self._is_rehearsal(job)]
        subsystem_and_e2e_jobs = [
            job
            for job in jobs
            if self._is_assisted_repository(job)
            and self._is_e2e_or_subsystem_class(job)
        ]
        periodic_subsystem_and_e2e_jobs = [
            job for job in subsystem_and_e2e_jobs if job.type == JobType.PERIODIC.value
        ]
        presubmit_subsystem_and_e2e_jobs = [
            job for job in subsystem_and_e2e_jobs if job.type == JobType.PRESUBMIT.value
        ]

        return Report(
            number_of_e2e_or_subsystem_periodic_jobs=len(
                periodic_subsystem_and_e2e_jobs
            ),
            number_of_successful_e2e_or_subsystem_periodic_jobs=self._get_number_of_jobs_by_state(
                periodic_subsystem_and_e2e_jobs, JobState.SUCCESS
            ),
            number_of_failing_e2e_or_subsystem_periodic_jobs=self._get_number_of_jobs_by_state(
                periodic_subsystem_and_e2e_jobs, JobState.FAILURE
            ),
            success_rate_for_e2e_or_subsystem_periodic_jobs=self._get_success_rate(
                periodic_subsystem_and_e2e_jobs
            ),
            top_10_failing_e2e_or_subsystem_periodic_jobs=self._get_top_n_jobs(
                periodic_subsystem_and_e2e_jobs, self._get_job_success_rate, 10, False
            ),
            number_of_e2e_or_subsystem_presubmit_jobs=len(
                presubmit_subsystem_and_e2e_jobs
            ),
            number_of_successful_e2e_or_subsystem_presubmit_jobs=self._get_number_of_jobs_by_state(
                presubmit_subsystem_and_e2e_jobs, JobState.SUCCESS
            ),
            number_of_failing_e2e_or_subsystem_presubmit_jobs=self._get_number_of_jobs_by_state(
                presubmit_subsystem_and_e2e_jobs, JobState.FAILURE
            ),
            number_of_rehearsal_jobs=len(rehearsal_jobs),
            success_rate_for_e2e_or_subsystem_presubmit_jobs=self._get_success_rate(
                presubmit_subsystem_and_e2e_jobs
            ),
            top_10_failing_e2e_or_subsystem_presubmit_jobs=self._get_top_n_jobs(
                presubmit_subsystem_and_e2e_jobs, self._get_job_success_rate, 10, False
            ),
            top_5_most_triggered_e2e_or_subsystem_jobs=self._get_top_n_jobs(
                subsystem_and_e2e_jobs, self._get_job_triggers_count, 5, True
            ),
            number_of_successful_machine_leases=len(
                [
                    step_event
                    for step_event in step_events
                    if step_event.step.state == StepState.SUCCESS.value
                ]
            ),
            number_of_unsuccessful_machine_leases=len(
                [
                    step_event
                    for step_event in step_events
                    if step_event.step.state == StepState.FAILURE.value
                ]
            ),
            total_number_of_machine_leased=len(step_events),
        )
