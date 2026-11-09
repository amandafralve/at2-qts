from playwright.sync_api import Page, expect


class RacasPage:
    """Page Object para a tela de gestão de raças de cães."""

    def __init__(self, page: Page) -> None:
        self.page = page

        # Mapeamento com seletores semânticos (WCAG / Acessibilidade)
        self.input_nome = page.get_by_label("Nome da Raça")
        self.input_origem = page.get_by_label("País de Origem")
        self.select_porte = page.get_by_label("Porte do Cão")
        self.input_expectativa = page.get_by_label("Expectativa de vida (anos)")
        self.input_temperamento = page.get_by_label("Temperamento")
        self.btn_cadastrar = page.get_by_role("button", name="Cadastrar raça")
        self.input_busca = page.get_by_label("Buscar por nome")
        self.select_filtrar_porte = page.get_by_label("Filtrar por porte")
        self.btn_filtrar = page.get_by_role("button", name="Filtrar")

        self.mensagem_status = page.get_by_role("status")
        self.mensagem_erro = page.get_by_role("alert")
        self.tabela_racas = page.get_by_role("table")
        self.estado_vazio = page.get_by_text("Nenhuma raça encontrada.")

    def navegar(self, url_base: str) -> None:
        self.page.goto(url_base)

    def preencher_formulario(
        self,
        nome: str,
        origem: str,
        porte: str,
        expectativa: int,
        temperamento: str,
    ) -> None:
        self.input_nome.fill(nome)
        self.input_origem.fill(origem)
        self.select_porte.select_option(porte)
        self.input_expectativa.fill(str(expectativa))
        self.input_temperamento.fill(temperamento)

    def submeter_formulario(self) -> None:
        self.btn_cadastrar.click()

    def cadastrar_raca_completo(
        self,
        nome: str,
        origem: str,
        porte: str,
        expectativa: int,
        temperamento: str,
    ) -> None:
        self.preencher_formulario(nome, origem, porte, expectativa, temperamento)
        self.submeter_formulario()

    def validar_sucesso(self, nome_raca: str) -> None:
        expect(self.mensagem_status).to_contain_text("Raça cadastrada com sucesso.")

    def validar_raca_na_tabela(self, nome_raca: str) -> None:
        expect(self.tabela_racas).to_contain_text(nome_raca)

    def filtrar_racas(self, nome: str = "", porte: str = "") -> None:
        self.input_busca.fill(nome)
        if porte:
            self.select_filtrar_porte.select_option(porte)
        self.btn_filtrar.click()

    def validar_erro(self) -> None:
        expect(self.mensagem_erro).to_contain_text("Dados inválidos")

    def validar_estado_vazio(self) -> None:
        expect(self.estado_vazio).to_be_visible()