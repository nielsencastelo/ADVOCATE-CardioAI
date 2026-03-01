from pydantic import BaseModel, Field
from typing import Literal

class PatientProfile(BaseModel):
    patient_id: str
    name: str
    age: int
    conditions: list[str] = Field(default_factory=list)
    meds: list[str] = Field(default_factory=list)

class CheckIn(BaseModel):
    timestamp: str
    symptoms: dict
    vitals: dict
    adherence: dict
    free_text: str = ""

class PatientAgentOut(BaseModel):
    summary: str
    risk_level: Literal["stable","watch","urgent"]
    rationale: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    patient_instructions: list[str] = Field(default_factory=list)
    proposed_actions: list[dict] = Field(default_factory=list)

class SupervisorOut(BaseModel):
    decision: Literal["approve","revise","escalate_routine","escalate_urgent","block"]
    issues: list[str] = Field(default_factory=list)
    safe_revision: dict | None = None