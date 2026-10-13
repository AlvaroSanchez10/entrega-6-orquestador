
import json

from tools import buscar_pedidos, analizar_pedidos


def test_investigacion_y_analisis():
    # El Investigador consulta los pedidos reales.
    pedidos_102 = json.loads(
        buscar_pedidos.invoke({"cliente_id": 102})
    )

    pedidos_205 = json.loads(
        buscar_pedidos.invoke({"cliente_id": 205})
    )

    assert len(pedidos_102) == 3
    assert len(pedidos_205) == 2

    # El Analista procesa los importes obtenidos.
    resultado_102 = analizar_pedidos.invoke({
        "importes": [
            pedido["total"] for pedido in pedidos_102
        ]
    })

    resultado_205 = analizar_pedidos.invoke({
        "importes": [
            pedido["total"] for pedido in pedidos_205
        ]
    })

    assert resultado_102["total"] == 14500
    assert resultado_205["total"] == 11000

    diferencia = resultado_102["total"] - resultado_205["total"]

    assert diferencia == 3500
