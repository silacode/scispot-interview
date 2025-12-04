from temporalio.client import Client, WorkflowExecutionDescription, WorkflowHandle
from config import get_settings
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException

from models.models import RunResponse, StatusWorkflowResponse
from workflows.workflows import ElisaAnalysisWorkflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.temporal_client = await Client.connect(settings.temporal_host)
    print("🚀 Starting Lab Workflow API...")

    yield

    # Shutdown - cleanup
    print("👋 Shutting down Lab Workflow API...")


def get_temporal_client() -> Client:
    return app.state.temporal_client


app = FastAPI(
    title="Scispot workflow service",
    description="API for lab data processing with S3, Elasticsearch, and Temporal workflows",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "lab-workflow"}


@app.post("/workflows/elisa/run", response_model=RunResponse)
async def run_elisa(req, client: Client = Depends(get_temporal_client)):
    handle = await client.start_workflow(
        ElisaAnalysisWorkflow.run,
        req,
        id=f"elisa-{req.experiment_id}",
        task_queue="elisa-task-queue",
    )
    return RunResponse(workflow_id=handle.id, run_id=handle.run_id)


@app.get("/workflows/status", response_model=StatusWorkflowResponse)
async def get_workflow_status(
    workflow_id: str, client: Client = Depends(get_temporal_client)
) -> StatusWorkflowResponse:
    handle: WorkflowHandle = await client.get_workflow_handle(workflow_id)

    try:
        desc: WorkflowExecutionDescription = await handle.describe()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StatusWorkflowResponse(
        workflow_id=handle.id, run_id=desc.run_id, status=desc.status
    )
