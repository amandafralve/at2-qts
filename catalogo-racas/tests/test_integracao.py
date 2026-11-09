import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from app.main import veterinary_service
from app.services import VeterinaryServiceUnavailable, VeterinaryTimeout
from tests.factories import RacaFactory


@pytest.mark.integration
def test_healthcheck_retorna_status_e_servico(client: TestClient) -> None:
    # Arrange

    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dog-breeds-hub"}


@pytest.mark.integration
def test_cadastrar_raca_retorna_201_e_payload_com_metadados(client: TestClient) -> None:
    # Arrange
    payload = RacaFactory.criar_payload_valido()

    # Act
    response = client.post("/api/v1/racas", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == payload["nome"]
    assert data["porte"] == payload["porte"]
    assert data["expectativa_vida_anos"] == payload["expectativa_vida_anos"]
    assert data["temperamento"] == payload["temperamento"]
    assert data["origem"] == payload["origem"]
    assert isinstance(data["id"], int)
    assert "criado_em" in data


@pytest.mark.integration
def test_cadastrar_raca_com_nome_duplicado_retorna_409(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
) -> None:
    # Arrange
    payload = RacaFactory.criar_payload_valido()
    payload["nome"] = raca_pre_cadastrada["nome"]

    # Act
    response = client.post("/api/v1/racas", json=payload)

    # Assert
    assert response.status_code == 409


@pytest.mark.integration
def test_cadastrar_payload_invalido_retorna_422(client: TestClient) -> None:
    # Arrange
    payload = RacaFactory.criar_payload_invalido_sem_nome()

    # Act
    response = client.post("/api/v1/racas", json=payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.integration
def test_cadastrar_temperamento_apenas_com_espacos_retorna_422(
    client: TestClient,
) -> None:
    # Arrange
    payload = RacaFactory.criar_payload_valido()
    payload["temperamento"] = "   "

    # Act
    response = client.post("/api/v1/racas", json=payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.integration
def test_listar_racas_retorna_lista_vazia_sem_cadastros(client: TestClient) -> None:
    # Arrange

    # Act
    response = client.get("/api/v1/racas")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
def test_listar_racas_filtra_por_nome_e_porte(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
) -> None:
    # Arrange
    nome = str(raca_pre_cadastrada["nome"])
    porte = str(raca_pre_cadastrada["porte"])

    # Act
    response = client.get("/api/v1/racas", params={"nome": nome[:3], "porte": porte})

    # Assert
    assert response.status_code == 200
    assert [raca["id"] for raca in response.json()] == [raca_pre_cadastrada["id"]]


@pytest.mark.integration
def test_filtrar_racas_com_porte_invalido_retorna_422(client: TestClient) -> None:
    # Arrange

    # Act
    response = client.get("/api/v1/racas", params={"porte": "Gigante"})

    # Assert
    assert response.status_code == 422


@pytest.mark.integration
def test_obter_raca_por_id_retorna_200(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
) -> None:
    # Arrange
    raca_id = raca_pre_cadastrada["id"]

    # Act
    response = client.get(f"/api/v1/racas/{raca_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == raca_id


@pytest.mark.integration
def test_obter_raca_inexistente_retorna_404(client: TestClient) -> None:
    # Arrange

    # Act
    response = client.get("/api/v1/racas/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Raça não encontrada."


@pytest.mark.integration
def test_verificar_veterinario_com_sucesso_usa_mock(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
    mocker: MockerFixture,
) -> None:
    # Arrange
    resultado = {
        "raca_id": raca_pre_cadastrada["id"],
        "aprovada": True,
        "mensagem": "Aprovada",
    }
    verificar = mocker.patch.object(veterinary_service, "verificar", return_value=resultado)

    # Act
    response = client.post(
        f"/api/v1/racas/{raca_pre_cadastrada['id']}/verificar-veterinario"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == resultado
    verificar.assert_called_once()


@pytest.mark.integration
def test_verificar_veterinario_indisponivel_retorna_503(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
    mocker: MockerFixture,
) -> None:
    # Arrange
    mocker.patch.object(
        veterinary_service,
        "verificar",
        side_effect=VeterinaryServiceUnavailable("Serviço indisponível"),
    )

    # Act
    response = client.post(
        f"/api/v1/racas/{raca_pre_cadastrada['id']}/verificar-veterinario"
    )

    # Assert
    assert response.status_code == 503


@pytest.mark.integration
def test_verificar_veterinario_timeout_retorna_504(
    client: TestClient,
    raca_pre_cadastrada: dict[str, object],
    mocker: MockerFixture,
) -> None:
    # Arrange
    mocker.patch.object(
        veterinary_service,
        "verificar",
        side_effect=VeterinaryTimeout("Tempo limite excedido"),
    )

    # Act
    response = client.post(
        f"/api/v1/racas/{raca_pre_cadastrada['id']}/verificar-veterinario"
    )

    # Assert
    assert response.status_code == 504


@pytest.mark.integration
def test_verificar_raca_inexistente_retorna_404_sem_chamar_servico(
    client: TestClient,
    mocker: MockerFixture,
) -> None:
    # Arrange
    verificar = mocker.patch.object(veterinary_service, "verificar")

    # Act
    response = client.post("/api/v1/racas/999/verificar-veterinario")

    # Assert
    assert response.status_code == 404
    verificar.assert_not_called()
