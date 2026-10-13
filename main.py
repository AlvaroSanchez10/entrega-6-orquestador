
from langchain_core.messages import HumanMessage

from graph import build_graph


def main():
    app = build_graph()

    pregunta = (
        "Investigá los pedidos de los clientes 102 y 205. "
        "Calculá cuánto gastó cada uno y determiná "
        "quién realizó compras por un importe mayor "
        "y cuál es la diferencia."
    )

    print("\n=== SOLICITUD ===")
    print(pregunta)

    estado_inicial = {
        "messages": [HumanMessage(content=pregunta)],
        "next_agent": "research",
        "contributions": [],
        "steps": 0,
        "task_completed": False,
        "validation_passed": False,
    }

    print("\n=== FLUJO DE DELEGACIÓN ===")

    resultado = None

    for evento in app.stream(
        estado_inicial,
        stream_mode="updates",
        config={"recursion_limit": 30},
    ):
        for nombre_nodo, actualizacion in evento.items():
            print(f"\nNodo ejecutado: {nombre_nodo}")

            if "next_agent" in actualizacion:
                print(
                    f"Próximo agente: "
                    f"{actualizacion['next_agent']}"
                )

            if "validation_passed" in actualizacion:
                print(
                    f"Validación aprobada: "
                    f"{actualizacion['validation_passed']}"
                )

            if nombre_nodo == "synthesis":
                resultado = actualizacion

    print("\n=== RESPUESTA FINAL ===")

    if resultado and resultado.get("messages"):
        print(resultado["messages"][-1].content)
    else:
        print("No se generó una respuesta final.")


if __name__ == "__main__":
    main()
