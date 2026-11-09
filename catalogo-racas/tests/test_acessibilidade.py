import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

from pages.racas_page import RacasPage
from tests.factories import RacaFactory

TAGS_WCAG_21_AA = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]


@pytest.mark.accessibility
def test_auditoria_wcag_21_aa_com_axe_core(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    racas_page.navegar(server_url)

    # Act
    results = Axe().run(
        page,
        options={"runOnly": {"type": "tag", "values": TAGS_WCAG_21_AA}},
    )

    # Assert
    assert results.violations_count == 0, results.generate_report()


@pytest.mark.accessibility
def test_navegacao_por_teclado_e_foco(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    racas_page.navegar(server_url)

    # Act and assert: Tab follows the expected form order.
    page.keyboard.press("Tab")
    expect(racas_page.input_nome).to_be_focused()

    page.keyboard.press("Tab")
    expect(racas_page.select_porte).to_be_focused()

    page.keyboard.press("Tab")
    expect(racas_page.input_expectativa).to_be_focused()

    page.keyboard.press("Tab")
    expect(racas_page.input_temperamento).to_be_focused()

    page.keyboard.press("Tab")
    expect(racas_page.input_origem).to_be_focused()

    page.keyboard.press("Tab")
    expect(racas_page.btn_cadastrar).to_be_focused()


@pytest.mark.accessibility
def test_estado_de_erro_nao_tem_violacoes_wcag(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    racas_page.navegar(server_url)
    racas_page.submeter_formulario()
    racas_page.validar_erro()

    # Act
    results = Axe().run(
        page,
        options={"runOnly": {"type": "tag", "values": TAGS_WCAG_21_AA}},
    )

    # Assert
    assert results.violations_count == 0, results.generate_report()


@pytest.mark.accessibility
def test_tabela_com_dados_nao_tem_violacoes_wcag(page: Page, server_url: str) -> None:
    # Arrange
    racas_page = RacasPage(page)
    payload = RacaFactory.criar_payload_valido()
    racas_page.navegar(server_url)
    racas_page.cadastrar_raca_completo(
        nome=payload["nome"],
        origem=payload["origem"] or "",
        porte=payload["porte"],
        expectativa=payload["expectativa_vida_anos"],
        temperamento=payload["temperamento"],
    )
    racas_page.validar_raca_na_tabela(payload["nome"])

    # Act
    results = Axe().run(
        page,
        options={"runOnly": {"type": "tag", "values": TAGS_WCAG_21_AA}},
    )

    # Assert
    assert results.violations_count == 0, results.generate_report()