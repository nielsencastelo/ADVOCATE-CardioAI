import json
from schemas import PatientProfile, CheckIn, PatientAgentOut, SupervisorOut
from prompts import PATIENT_AGENT_SYSTEM, SUPERVISOR_SYSTEM

class PatientAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, profile: dict, checkin: dict, rule_risk: str, rule_reasons: list, delta_weight_kg):
        p = PatientProfile(**profile)

        user_prompt = f"""\
PATIENT:
- Name: {p.name}, Age: {p.age}
- Conditions: {p.conditions}
- Medications (list): {p.meds}

CHECK-IN TODAY (JSON):
{json.dumps(checkin, ensure_ascii=False)}

CANONICAL COMPUTED FEATURES (use these numbers exactly; do not guess):
- delta_weight_kg={delta_weight_kg}
- rule_risk={rule_risk}
- rule_reasons={rule_reasons}

Task:
Return the Patient Agent JSON (schema required).
"""
        out = self.llm.ask_json(PATIENT_AGENT_SYSTEM, user_prompt)
        return PatientAgentOut.model_validate(out).model_dump()

class SupervisorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, patient_out: dict, checkin: dict, rule_risk: str, rule_reasons: list):
        user_prompt = f"""\
Patient Agent output (JSON):
{json.dumps(patient_out, ensure_ascii=False)}

Check-in data (JSON):
{json.dumps(checkin, ensure_ascii=False)}

Rule-based risk:
{rule_risk} | {rule_reasons}
"""
        out = self.llm.ask_json(SUPERVISOR_SYSTEM, user_prompt)
        return SupervisorOut.model_validate(out).model_dump()