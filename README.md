# ADVOCATE-CardioAI

## Dual-Agent Supervisory Agentic AI Prototype for Safe Cardiovascular Care (CVD)

A research-grade, local-first prototype implementing a **dual-agent architecture** for cardiovascular disease management aligned with ADVOCATE-style principles:

- 🫀 Patient-Facing Clinical Agent  
- 🛡️ Supervisory Safety & Governance Agent  
- 📊 Deterministic Risk Engine Baseline  
- 🧪 Strict JSON Outputs for Auditability & Evaluation  

> **Disclaimer**: This repository is a research prototype for simulation and evaluation.  
> It is **not** a medical device and **not** a substitute for licensed clinical judgment.

---

## Why this project

Cardiovascular conditions (e.g., heart failure and post–myocardial infarction follow-up) require continuous monitoring, early detection of deterioration, and safe escalation pathways.  
This project explores a governed **agentic clinical AI** workflow using:

1) a **patient-facing agent** that produces structured triage outputs, and  
2) a **supervisory agent** that enforces safety policies and prevents unsafe actions.

---

## Architecture (High-level)

**Pipeline**
1. Patient submits a daily check-in (symptoms / vitals / adherence).
2. A **rule-based risk engine** computes canonical features (e.g., `delta_weight_kg`) and baseline risk.
3. The **Patient Agent** generates strict JSON:
   - summary, risk label, rationale
   - clarifying questions
   - safe patient instructions
   - proposed actions (tools)
4. The **Supervisor Agent** audits the Patient Agent output and applies governance:
   - blocks medication/dose changes and definitive diagnosis
   - enforces escalation policies (routine vs urgent)
   - revises unsafe instructions
5. Tool actions are executed (currently simulated; replaceable with integrations).

---

## Key Features (MVP)

### ✅ Patient Agent (LLM)
- Produces **strict JSON** outputs for deterministic parsing
- Risk levels: `stable | watch | urgent`
- Proposes actions (tools): `message_team`, `schedule`, `self_care`, `none`

### ✅ Supervisor Agent (LLM Guardrail)
- Enforces escalation policies and safety constraints
- Revises or blocks unsafe outputs
- Ensures urgent cases prioritize immediate emergency evaluation steps

### ✅ Risk Engine Baseline (Rules)
- Red flags: chest pain, dyspnea at rest, syncope, acute neuro symptoms → `urgent`
- Worsening signals: edema + dyspnea + weight trend → `watch`
- Stable otherwise → `stable`

---

## Tech Stack

- **Ollama** (local LLM runtime)
- **Phi-4** (default model)
- Optional: **Meditron** (medical-tuned model; free via Ollama)
- **LangGraph** (graph-based agent orchestration)
- **LangChain** (Ollama connector)
- **Pydantic** (schemas)

---

## Quickstart (Notebook)

### 1) Install Ollama
https://github.com/ollama/ollama

### 2) Pull a model
```bash
ollama pull phi4
# optional medical model
ollama pull meditron
```

### 3) Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4) Run the notebook
Open `main.ipynb` and execute cells sequentially.

---

## Configuration

In the notebook:
```python
MODEL = "phi4"        # or "meditron"
TEMPERATURE = 0.2
BASE_URL = "http://localhost:11434"
```

---

## Safety & Governance Principles

This prototype is intentionally conservative:
- **No prescribing**
- **No medication or dose changes**
- **No definitive diagnosis**
- **Urgent red flags trigger escalation**
- **Deterministic action gating** (avoid spam, avoid empty actions, avoid TBD scheduling in urgent)
- **Strict JSON schema** for audits and evaluation
- Supervisor agent gates patient-facing content and tool actions

---

## Evaluation Ideas

Metrics you can compute immediately:
- Escalation rate by risk level (`stable/watch/urgent`)
- Supervisor interventions (approve vs revise vs block)
- Rule/LLM agreement
- Unsafe output attempts (med/dose advice)
- Stress tests for false negatives using synthetic check-ins

---

## Roadmap

- Longitudinal memory (7–14 days) and trends
- Synthetic cohort simulator (100–1,000 patients)
- Triage dashboard (alert queue)
- Replace simulated tools with real integrations (FHIR/EHR, scheduling, messaging)
- Automated evaluation harness + regression tests

---

## References

- Ollama: https://github.com/ollama/ollama  
- Phi-4 (Ollama library): https://ollama.com/library/phi4  
- Meditron (Ollama library): https://ollama.com/library/meditron  
- LangGraph: https://www.langchain.com/langgraph  
