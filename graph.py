from __future__ import annotations

import json
from typing import TypedDict, Any, Optional, List, Dict

from langgraph.graph import StateGraph, END

from config import Settings
from schemas import CheckIn, PatientAgentOut, SupervisorOut
from risk_engine import RiskEngine
from llm_client import LLMClient
from agents import PatientAgent, SupervisorAgent

# Se você ainda não criou tools.py, pode manter as funções de tool aqui.
# Mas o ideal é mover para advocate_cardioai/tools.py e importar.
try:
    from .tools import ToolExecutor
except Exception:  # fallback simples
    class ToolExecutor:
        def message_team(self, priority: str, summary: str, payload: dict):
            print(f"\n[TOOL] message_team | priority={priority}\n- summary: {summary}\n- payload: {json.dumps(payload, ensure_ascii=False)}")

        def schedule(self, kind: str, when: str, payload: dict):
            print(f"\n[TOOL] schedule | kind={kind} when={when}\n- payload: {json.dumps(payload, ensure_ascii=False)}")

        def self_care(self, tasks: list[str]):
            print("\n[TOOL] self_care tasks:")
            for t in tasks:
                print("-", t)


class AgentState(TypedDict):
    profile: dict
    last_checkins: list
    checkin: dict

    # computed by rules
    rule_risk: str
    rule_reasons: list
    delta_weight_kg: Optional[float]

    # llm outputs
    patient_agent_out: dict
    supervisor_out: dict


def build_app(settings: Settings):
    """
    Build & compile LangGraph app.

    Implements the pipeline described in README:
    - rule-based risk engine computes canonical features (delta_weight_kg) and baseline risk
    - Patient Agent outputs strict JSON
    - Supervisor Agent audits/revises/blocks and enforces safety policies
    - Tool actions executed (simulated) with deterministic gating
    """
    # Engines / tools
    risk_engine = RiskEngine()
    tools = ToolExecutor()

    # LLM clients
    patient_llm = LLMClient(
        model=settings.patient_model,
        base_url=settings.base_url,
        temperature=settings.temperature,
        options=settings.ollama_options,
        format_json=getattr(settings, "format_json", False),
    )
    supervisor_llm = LLMClient(
        model=settings.supervisor_model,
        base_url=settings.base_url,
        temperature=max(0.1, settings.temperature),  # supervisor mais determinístico
        options=settings.ollama_options,
        format_json=getattr(settings, "format_json", False),
    )

    patient_agent = PatientAgent(patient_llm)
    supervisor_agent = SupervisorAgent(supervisor_llm)

    # ------------------------- NODES -------------------------

    def node_rule_risk(state: AgentState) -> AgentState:
        c = CheckIn(**state["checkin"])
        last = [CheckIn(**x) for x in state.get("last_checkins", [])]

        risk, reasons, delta_w = risk_engine.evaluate(c, last)

        state["rule_risk"] = risk
        state["rule_reasons"] = reasons
        state["delta_weight_kg"] = delta_w
        return state

    def node_patient_agent(state: AgentState) -> AgentState:
        out = patient_agent.run(
            profile=state["profile"],
            checkin=state["checkin"],
            rule_risk=state["rule_risk"],
            rule_reasons=state["rule_reasons"],
            delta_weight_kg=state.get("delta_weight_kg"),
        )

        # valida de novo aqui (redundante, mas protege o grafo)
        out = PatientAgentOut.model_validate(out).model_dump()
        state["patient_agent_out"] = out
        return state

    def node_supervisor(state: AgentState) -> AgentState:
        """
        Supervisor é a parte mais crítica para evitar que o grafo quebre
        (ex.: KeyError decision). Se falhar, aplica fallback determinístico
        baseado no rule_risk.
        """
        try:
            sup = supervisor_agent.run(
                patient_out=state["patient_agent_out"],
                checkin=state["checkin"],
                rule_risk=state["rule_risk"],
                rule_reasons=state["rule_reasons"],
            )
            sup = SupervisorOut.model_validate(sup).model_dump()
        except Exception as e:
            rr = state.get("rule_risk", "stable")

            if rr == "urgent":
                sup = {
                    "decision": "escalate_urgent",
                    "issues": [f"Supervisor invalid output; fallback to rule_risk=urgent ({type(e).__name__})."],
                    "safe_revision": None,
                }
            elif rr == "watch":
                sup = {
                    "decision": "escalate_routine",
                    "issues": [f"Supervisor invalid output; fallback to rule_risk=watch ({type(e).__name__})."],
                    "safe_revision": None,
                }
            else:
                sup = {
                    "decision": "approve",
                    "issues": [f"Supervisor invalid output; fallback approve ({type(e).__name__})."],
                    "safe_revision": None,
                }

        state["supervisor_out"] = sup
        return state

    def node_act(state: AgentState) -> AgentState:
        decision = (state.get("supervisor_out") or {}).get("decision", "block")
        agent_out = state.get("patient_agent_out") or {}

        # If supervisor revised the output, use safe_revision
        if decision == "revise":
            safe_rev = (state["supervisor_out"] or {}).get("safe_revision")
            if isinstance(safe_rev, dict) and safe_rev:
                agent_out = safe_rev

        # ---- HARD GATING (deterministic safety & ops) ----
        risk = agent_out.get("risk_level", "stable")

        filtered_actions = []
        for a in agent_out.get("proposed_actions", []) or []:
            t = (a or {}).get("type", "none")
            payload = (a or {}).get("payload", {}) or {}

            # 1) Never notify clinical team if stable (avoid spam)
            if risk == "stable" and t == "message_team":
                continue

            # 2) For urgent: prefer emergency escalation, not schedule TBD
            if risk == "urgent" and t == "schedule":
                when = (payload.get("when") or "").strip()
                if when.lower() in ["", "tbd", "none", "null"]:
                    continue

            # 3) Self-care must include non-empty tasks
            if t == "self_care":
                tasks = payload.get("tasks", [])
                if not isinstance(tasks, list) or len(tasks) == 0:
                    continue

            filtered_actions.append(a)

        agent_out["proposed_actions"] = filtered_actions

        # ---- Execute simulated tool actions ----
        for a in agent_out.get("proposed_actions", []) or []:
            t = (a or {}).get("type", "none")
            payload = (a or {}).get("payload", {}) or {}

            if t == "message_team":
                priority = "urgent" if agent_out.get("risk_level") == "urgent" else "routine"
                default_msg = "Routine clinical review requested due to worsening symptoms."
                msg = payload.get("message") or payload.get("content") or default_msg

                tools.message_team(
                    priority=priority,
                    summary=agent_out.get("summary", ""),
                    payload={"message": msg},
                )

            elif t == "schedule":
                tools.schedule(
                    kind=payload.get("kind", "follow_up"),
                    when=payload.get("when", "TBD"),
                    payload=payload,
                )

            elif t == "self_care":
                tools.self_care(payload.get("tasks", []))

        # ---- Print safe patient-facing message ----
        print("\n=== SAFE PATIENT MESSAGE ===")
        print("Summary:", agent_out.get("summary", ""))
        print("Risk:", agent_out.get("risk_level", ""))
        print("Rationale:", " | ".join(agent_out.get("rationale", []) or []))

        qs = agent_out.get("questions") or []
        if qs:
            print("\nQuick questions:")
            for q in qs:
                print("-", q)

        instr = agent_out.get("patient_instructions") or []
        if instr:
            print("\nInstructions:")
            for i in instr:
                print("-", i)

        # Persist final output if you want
        state["patient_agent_out"] = agent_out
        return state

    def route_after_supervisor(state: AgentState) -> str:
        d = (state.get("supervisor_out") or {}).get("decision", "block")
        if d == "block":
            return "end"
        return "act"

    # ------------------------- GRAPH -------------------------

    g = StateGraph(AgentState)
    g.add_node("rule_risk", node_rule_risk)
    g.add_node("patient_agent", node_patient_agent)
    g.add_node("supervisor", node_supervisor)
    g.add_node("act", node_act)

    g.set_entry_point("rule_risk")
    g.add_edge("rule_risk", "patient_agent")
    g.add_edge("patient_agent", "supervisor")
    g.add_conditional_edges("supervisor", route_after_supervisor, {"act": "act", "end": END})
    g.add_edge("act", END)

    return g.compile()