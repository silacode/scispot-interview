from workflows.workflows import ElisaAnalysisWorkflow
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from activities.activities import (
    persist_analysis,
    process_elisa_plate,
    run_agentic_report,
    wait_for_latest_run,
)
from config import get_settings
from activities import greet


async def main():
    settings = get_settings()
    client = await Client.connect(settings.temporal_host)
    worker = Worker(
        client,
        task_queue=settings.task_queue,
        workflows=[ElisaAnalysisWorkflow],
        activities=[
            wait_for_latest_run,
            process_elisa_plate,
            persist_analysis,
            run_agentic_report,
        ],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
