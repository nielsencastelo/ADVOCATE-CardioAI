# ADVOCATE-CardioAI

**A dual-agent, safety-supervised agentic AI prototype for cardiovascular care (CVD)** — designed to run fully locally using **Ollama** (default: **phi4**) and orchestrated with **LangGraph**.

This repository implements:
- **Patient Agent**: collects daily check-ins (symptoms/vitals/adherence), produces structured guidance and proposed actions.
- **Supervisor Agent (Safety Gate)**: reviews the Patient Agent output, enforces escalation rules, blocks unsafe content (e.g., prescribing/med changes), and triggers escalation when red flags appear.

> This is a research/prototyping system intended to validate feasibility for agentic clinical workflows. It is not a medical device and does not provide medical advice.

---

## Key Features

- ✅ Runs **100% locally** via Ollama (no external API cost)
- ✅ **Structured JSON outputs** for auditability and logging
- ✅ **Rule-based risk engine** + **LLM reasoning** (hybrid triage)
- ✅ **Supervisor safety gate** (approve / revise / escalate / block)
- ✅ Simulated “tools” (message clinical team, schedule follow-up, self-care tasks)

---

## Architecture