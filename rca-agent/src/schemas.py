from pydantic import BaseModel, Field
from typing import List

class RootCauseAnalysis(BaseModel):
    root_cause_summary: str = Field(description="A precise technical explanation of what caused the failure based on the provided logs.")
    confidence_level: float = Field(description="Confidence score of the diagnosis between 0.0 and 1.0.", ge=0.0, le=1.0)
    remediation_steps: List[str] = Field(description="Actionable bash commands or configuration steps to resolve the issue.")