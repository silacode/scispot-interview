from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

from activities.activities import (
    persist_analysis,
    process_elisa_plate,
    run_agentic_report,
    wait_for_latest_run,
)
from models.models import AnalysisResult, ElisaRunRequest


retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=1),
    maximum_attempts=3,
)


@workflow.defn
class ElisaAnalysisWorkflow:
    def __init__(self):
        self._current_step = "pending"
        self._is_approved = False
        self._approval_notes: str | None = None

    # QUERY - let external code read workflow state
    @workflow.query
    def current_step(self) -> str:
        return self._current_step

    # SIGNAL - let external code modify running workflow
    @workflow.signal
    async def approve_qc(self, notes: str = ""):
        self._is_approved = True
        self._approval_notes = notes

    @workflow.run
    async def run(self, req: ElisaRunRequest) -> AnalysisResult:
        # 1) wait for data to land in S3 (long-running)
        s3_key = await workflow.execute_activity(
            wait_for_latest_run,
            req.experiment_id,
            schedule_to_close_timeout=timedelta(hours=1),
            retry_policy=retry_policy,
        )

        # 2) fetch + process + QC
        processed = await workflow.execute_activity(
            process_elisa_plate,
            s3_key,
            schedule_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        # 3) write processed result + index in ES
        result = await workflow.execute_activity(
            persist_analysis,
            processed,
            schedule_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy,
        )

        # 4) run LLM agentic report
        report = await workflow.execute_activity(
            run_agentic_report,
            result,
            schedule_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy,
        )

        # merge report into result and return
        return AnalysisResult(**result.model_dump(), report=report)
