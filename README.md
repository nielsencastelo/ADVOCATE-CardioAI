# ADVOCATE-CardioAI

**Dual-Agent Supervisory Agentic AI Prototype for Safe Cardiovascular Care (CVD)**  
Local-first, notebook-friendly, built to validate an ARPA-H ADVOCATE-style architecture: **Patient Agent + Safety Supervisor Agent**.

> This repository is a research prototype for simulating agentic cardiovascular care workflows (heart failure & post-MI follow-up).  
> It is **not** a medical device and **not** a substitute for clinical judgment.

---

## Why this project

The ARPA-H ADVOCATE program emphasizes:
- a **patient-facing clinical agent**
- a **supervisory safety agent**
- a plan for **workflow integration and consistent safety**

This repo implements that core architecture in a minimal, testable form.

---

## What it does (MVP)

### ✅ Patient Agent (LLM)
- Summarizes the patient’s daily check-in (symptoms/vitals/adherence)
- Classifies risk: `stable | watch | urgent`
- Produces safe, structured outputs in **strict JSON**
- Proposes actions (simulated tools): message clinical team, schedule follow-up, self-care tasks

### ✅ Supervisor Agent (LLM Guardrail)
- Reviews Patient Agent output for unsafe content
- Enforces escalation policies (routine vs urgent)
- Blocks or revises content if it suggests medication changes, dosing, or definitive diagnosis
- Outputs a final safe JSON to be delivered to the patient + clinical workflow

### ✅ Rule-Based Risk Engine (MVP baseline)
- Simple “red flag” rules (e.g., chest pain + severe dyspnea => urgent)
- “Watch” triggers (e.g., edema + weight gain trend)

---

## Tech Stack

- **Ollama** (local LLM runtime)
- **Phi-4** (default local model)
- Optional: **Meditron** (medical-tuned model; free to download in Ollama)
- **LangGraph** (agent orchestration via graph)
- **LangChain** (Ollama chat connector)

---

## Quickstart (Notebook)

### 1) Install Ollama
Follow the official instructions: https://github.com/ollama/ollama

### 2) Pull a model
```bash
ollama pull phi4
# optional medical model
ollama pull meditron