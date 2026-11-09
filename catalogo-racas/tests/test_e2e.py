import pytest
from playwright.sync_api import Page

from pages.racas_page import RacasPage
from tests.factories import RacaFactory


@pytest.mark.e2e
def test_cadastrar_e_filtrar_raca(page: Page, server_url: str) -> None:
    racas_page = RacasPage(page)
    payload = RacaFactory.criar_payload_valido()

    racas_page.navegar(server_url)
    racas_page.cadastrar_raca_completo(
        nome=payload["nome"],
        origem=payload["origem"],
        porte=payload["porte"],
        expectativa=payload["expectativa_vida_anos"],
        temperamento=payload["temperamento"],
    )
    racas_page.validar_sucesso(payload["nome"])
    racas_page.filtrar_racas(nome=payload["nome"][:4], porte=payload["porte"])

    racas_page.validar_raca_na_tabela(payload["nome"])


@pytest.mark.e2e
def test_pagina_vazia_e_mensagem_de_erro(page: Page, server_url: str) -> None:
    racas_page = RacasPage(page)

    racas_page.navegar(server_url)
    racas_page.validar_estado_vazio()
    racas_page.submeter_formulario()

    racas_page.validar_erro()
