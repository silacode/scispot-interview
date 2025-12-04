from temporalio import activity

from models.models import AnalysisResult, ProcessedElisaData, QcMetrics


@activity.defn
async def wait_for_latest_run(experiment_id: str) -> str:
    # MOCK: pretend S3 key exists; in real world you’d poll or be signaled
    return f"s3://raw/{experiment_id}/latest.csv"


@activity.defn
async def process_elisa_plate(s3_key: str) -> ProcessedElisaData:
    # MOCK: pretend we fetched CSV and computed QC
    return ProcessedElisaData(
        s3_key=s3_key,
        qc=QcMetrics(percent_cv=5.2, control_ok=True, num_wells=96),
    )


@activity.defn
async def persist_analysis(processed: ProcessedElisaData) -> AnalysisResult:
    # MOCK: fake S3 + ES
    return AnalysisResult(
        experiment_id="exp-123",
        run_id="run-1",
        qc=processed.qc,
        summary_s3_uri="s3://processed/exp-123/run-1.json",
    )


@activity.defn
async def run_agentic_report(result: AnalysisResult) -> str:
    # MOCK: LLM call; return canned text
    return "Controls passed; signal is within expected range; proceed to next step."
