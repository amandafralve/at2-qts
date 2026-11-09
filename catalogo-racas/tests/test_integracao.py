import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from app.main import veterinary_service
from app.services import VeterinaryServiceUnavailable, VeterinaryTimeout
from tests.factories import RacaFactory


@pytest.mark.integration
def test_rotas_basicas_de_racas(client: TestClient) -> None:
    payload = RacaFactory.criar_payload_valido()

    health = client.get("/health")
    vazio = client.get("/api/v1/racas")
    criada = client.post("/api/v1/racas", json=payload)
    lista = client.get("/api/v1/racas")
    consulta = client.get(f"/api/v1/racas/{criada.json()['id']}")
    inexistente = client.get("/api/v1/racas/999")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert vazio.status_code == 200
    assert vazio.json() == []
    assert criada.status_code == 201
    assert criada.json()["nome"] == payload["nome"]
    assert lista.json()[0]["id"] == criada.json()["id"]
    assert consulta.status_code == 200
    assert consulta.json()["id"] == criada.json()["id"]
    assert inexistente.status_code == 404


@pytest.mark.integration
def test_cadastro_e_filtros_rejeitam_dados_invalidos(client: TestClient) -> None:
    payload = RacaFactory.criar_payload_valido()
    payload_invalido = RacaFactory.criar_payload_invalido_sem_nome()
    payload_temperamento_invalido = RacaFactory.criar_payload_valido()
    payload_temperamento_invalido["temperamento"] = "   "

    criada = client.post("/api/v1/racas", json=payload)
    duplicada = client.post("/api/v1/racas", json=payload)
    nome_invalido = client.post("/api/v1/racas", json=payload_invalido)
    temperamento_invalido = client.post(
        "/api/v1/racas",
        json=payload_temperamento_invalido,
    )
    filtrada = client.get(
        "/api/v1/racas",
        params={"nome": payload["nome"][:3], "porte": payload["porte"]},
    )
    porte_invalido = client.get("/api/v1/racas", params={"porte": "Gigante"})

    assert criada.status_code == 201
    assert duplicada.status_code == 409
    assert nome_invalido.status_code == 422
    assert temperamento_invalido.status_code == 422
    assert [raca["id"] for raca in filtrada.json()] == [criada.json()["id"]]
    assert porte_invalido.status_code == 422


@pytest.mark.integration
def test_verificacao_veterinaria_com_sucesso_e_falhas(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
    mocker: MockerFixture,
) -> None:
    raca_id = raca_pre_cadastrada["id"]
    resultado = {"raca_id": raca_id, "aprovada": True, "mensagem": "Aprovada"}
    verificar = mocker.patch.object(
        veterinary_service,
        "verificar",
        side_effect=[
            resultado,
            VeterinaryServiceUnavailable("Serviço indisponível"),
            VeterinaryTimeout("Tempo limite excedido"),
        ],
    )

    sucesso = client.post(f"/api/v1/racas/{raca_id}/verificar-veterinario")
    indisponivel = client.post(f"/api/v1/racas/{raca_id}/verificar-veterinario")
    timeout = client.post(f"/api/v1/racas/{raca_id}/verificar-veterinario")
    inexistente = client.post("/api/v1/racas/999/verificar-veterinario")

    assert sucesso.status_code == 200
    assert sucesso.json() == resultado
    assert indisponivel.status_code == 503
    assert timeout.status_code == 504
    assert inexistente.status_code == 404
    assert verificar.call_count == 3
