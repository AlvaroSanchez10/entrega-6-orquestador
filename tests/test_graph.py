
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from graph import build_graph


def test_flujo_completo():
    """Comprueba la delegación y validación del grafo."""

    llamadas = []

    def supervisor_falso(state):
        agentes = [
            item["agent"]
            for item in state.get("contributions", [])
        ]

        if "research" not in agentes:
            siguiente = "research"
        elif "analyst" not in agentes:
            siguiente = "analyst"
        else:
            siguiente = "validation"

        return {
            "next_agent": siguiente,
            "task_completed": False,
        }

    def investigador_falso(state):
        llamadas.append("buscar_pedidos")

        return {
            "messages": [
                AIMessage(
                    content="Cliente 102: [4500, 6000, 4000]. "
                            "Cliente 205: [7000, 4000].",
                    name="research",
                )
            ],
            "contributions": [
                {
                    "agent": "research",
                    "content": (
                        '{"response": "Datos obtenidos", '
                        '"tools_executed": ["buscar_pedidos"]}'
                    ),
                }
            ],
            "steps": state.get("steps", 0) + 1,
        }

    def analista_falso(state):
        llamadas.append("analizar_pedidos")

        return {
            "messages": [
                AIMessage(
                    content="Cliente 102: 14500. "
                            "Cliente 205: 11000. Diferencia: 3500.",
                    name="analyst",
                )
            ],
            "contributions": [
                {
                    "agent": "analyst",
                    "content": (
                        '{"response": "Totales calculados", '
                        '"tools_executed": ["analizar_pedidos"]}'
                    ),
                }
            ],
            "steps": state.get("steps", 0) + 1,
        }

    def sintesis_falsa(state):
        return {
            "messages": [
                AIMessage(
                    content="Ana gastó $3500 más que Carlos.",
                    name="synthesis",
                )
            ],
            "task_completed": True,
        }

    with (
        patch("graph.supervisor_node", supervisor_falso),
        patch("graph.research_node", investigador_falso),
        patch("graph.analyst_node", analista_falso),
        patch("graph.synthesis_node", sintesis_falsa),
    ):
        app = build_graph()

    resultado = app.invoke({
        "messages": [
            HumanMessage(
                content="Investigá y compará los clientes 102 y 205."
            )
        ],
        "next_agent": "research",
        "contributions": [],
        "steps": 0,
        "task_completed": False,
        "validation_passed": False,
    })

    assert llamadas == ["buscar_pedidos", "analizar_pedidos"]
    assert resultado["validation_passed"] is True
    assert resultado["task_completed"] is True
    assert resultado["messages"][-1].name == "synthesis"
