from datetime import datetime, timedelta
from typing import Optional

from jobsautoreport.query import Querier


class Reporter:
    def __init__(self, querier: Querier):
        self._querier = querier

    def get_success_rate(self, from_date: datetime, to_date: datetime) -> str:
        successful_jobs_list = self._querier.query_successful_jobs(from_date, to_date)
        unsuccessful_jobs_list = self._querier.query_successful_jobs(from_date, to_date)
        if len(successful_jobs_list) == 0:
            return "0"
        return f"{(len(successful_jobs_list) / (len(unsuccessful_jobs_list) + len(successful_jobs_list))) * 100}%"

    def get_number_of_jobs_triggered(
        self, from_date: datetime, to_date: datetime
    ) -> int:
        jobs_list = self._querier.query_number_of_jobs_triggered(from_date, to_date)
        return len(jobs_list)

    def get_average_duration_of_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> Optional[timedelta]:
        jobs_list = self._querier.query_number_of_jobs_triggered(from_date, to_date)
        if len(jobs_list) == 0:
            return None
        avg = int(sum([job.duration for job in jobs_list]) / len(jobs_list))
        return timedelta(seconds=avg)
    

    class JobData:
        def __init__(self, success_count: int, failed_count: int, success_rate: float) -> None:
            self.success_count = success_count
            self.failed_count = failed_count
            self.success_rate = success_rate
    
    class JobAggregator:
        def __init__(self, querier: Querier) -> None:
            self._querier = querier
        
        def by_job_type(self, type: str) -> JobData:
            
