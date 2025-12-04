from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from temporalio.common import WorkflowExecutionStatus


class WorkflowStep(BaseModel):
    name: str
    type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str
    steps: List[WorkflowStep]


class CreateWorkflowResponse(BaseModel):
    template_id: str
    name: str
    description: str


class WorkflowTemplate(BaseModel):
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]


class UpdateWorkflowRequest(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[WorkflowStep]] = None


class UpdateWorkflowResponse(CreateWorkflowResponse):
    pass


class StatusWorkflowResponse(BaseModel):
    workflow_id: str
    run_id: Optional[str]
    status: WorkflowExecutionStatus


class RunResponse(BaseModel):
    workflow_id: str
    run_id: str


class ElisaRunRequest(BaseModel):
    experiment_id: str
    plate_id: str | None = None
    assay_type: str | None = None


class QcMetrics(BaseModel):
    percent_cv: float
    control_ok: bool
    num_wells: int


class AnalysisResult(BaseModel):
    experiment_id: str
    run_id: str
    qc: QcMetrics
    summary_s3_uri: str
    report: str | None = None


class ProcessedElisaData(BaseModel):
    s3_key: str
    qc: "QcMetrics"
    raw_values: list[float] = []
