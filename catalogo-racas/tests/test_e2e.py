import pytest
from playwright.sync_api import Page

from pages.racas_page import RacasPage
from tests.factories import RacaFactory


@pytest.mark.e2e
def test_fluxo_completo_cadastro_raca_via_interface(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    payload = RacaFactory.criar_payload_valido()

    # Act
    racas_page.navegar(server_url)
    racas_page.cadastrar_raca_completo(
        nome=payload["nome"],
        origem=payload["origem"],
        porte=payload["porte"],
        expectativa=payload["expectativa_vida_anos"],
        temperamento=payload["temperamento"],
    )

    # Assert
    racas_page.validar_sucesso(payload["nome"])
    racas_page.validar_raca_na_tabela(payload["nome"])


@pytest.mark.e2e
def test_filtrar_racas_por_nome_e_porte(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    payload = RacaFactory.criar_payload_valido()

    # Act
    racas_page.navegar(server_url)
    racas_page.cadastrar_raca_completo(
        nome=payload["nome"],
        origem=payload["origem"],
        porte=payload["porte"],
        expectativa=payload["expectativa_vida_anos"],
        temperamento=payload["temperamento"],
    )
    racas_page.filtrar_racas(nome=payload["nome"][:4], porte=payload["porte"])

    # Assert
    racas_page.validar_raca_na_tabela(payload["nome"])


@pytest.mark.e2e
def test_estado_vazio_aparece_sem_racas(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)

    # Act
    racas_page.navegar(server_url)

    # Assert
    racas_page.validar_estado_vazio()


@pytest.mark.e2e
def test_formulario_invalido_exibe_mensagem_de_erro(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    racas_page.navegar(server_url)

    # Act
    racas_page.submeter_formulario()

    # Assert
    racas_page.validar_erro()