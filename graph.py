
from typing import Literal

from langgraph.graph import StateGraph, START, END

from state import AgentState
from supervisor import supervisor_node
from nodes import research_node, analyst_node
from validation import validation_node
from synthesis import synthesis_node


def route_supervisor(
    state: AgentState,
) -> Literal["research", "analyst", "validation"]:
    """Envía el trabajo al nodo elegido por el Supervisor."""
    return state["next_agent"]


def route_validation(
    state: AgentState,
) -> Literal["supervisor", "synthesis"]:
    """Permite corregir resultados o finalizar el proceso."""
    if state.get("validation_passed", False):
        return "synthesis"

    if state.get("steps", 0) >= 6:
        return "synthesis"

    return "supervisor"


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("synthesis", synthesis_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "research": "research",
            "analyst": "analyst",
            "validation": "validation",
        },
    )

    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analyst", "supervisor")

    workflow.add_conditional_edges(
        "validation",
        route_validation,
        {
            "supervisor": "supervisor",
            "synthesis": "synthesis",
        },
    )

    workflow.add_edge("synthesis", END)

    return workflow.compile()
