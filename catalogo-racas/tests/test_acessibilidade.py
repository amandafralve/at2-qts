import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

from pages.racas_page import RacasPage
from tests.factories import RacaFactory

TAGS_WCAG_21_AA = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]


@pytest.mark.accessibility
def test_wcag_21_aa_em_todos_os_estados_da_pagina(
    page: Page,
    server_url: str,
) -> None:
    racas_page = RacasPage(page)
    axe = Axe()
    options = {"runOnly": {"type": "tag", "values": TAGS_WCAG_21_AA}}

    racas_page.navegar(server_url)
    vazio = axe.run(page, options=options)
    racas_page.submeter_formulario()
    racas_page.validar_erro()
    erro = axe.run(page, options=options)

    payload = RacaFactory.criar_payload_valido()
    racas_page.cadastrar_raca_completo(
        nome=payload["nome"],
        origem=payload["origem"],
        porte=payload["porte"],
        expectativa=payload["expectativa_vida_anos"],
        temperamento=payload["temperamento"],
    )
    racas_page.validar_raca_na_tabela(payload["nome"])
    com_dados = axe.run(page, options=options)

    assert vazio.violations_count == 0, vazio.generate_report()
    assert erro.violations_count == 0, erro.generate_report()
    assert com_dados.violations_count == 0, com_dados.generate_report()


@pytest.mark.accessibility
def test_navegacao_por_teclado(page: Page, server_url: str) -> None:
    racas_page = RacasPage(page)
    racas_page.navegar(server_url)

    for locator in (
        racas_page.input_nome,
        racas_page.select_porte,
        racas_page.input_expectativa,
        racas_page.input_temperamento,
        racas_page.input_origem,
        racas_page.btn_cadastrar,
    ):
        page.keyboard.press("Tab")
        expect(locator).to_be_focused()
