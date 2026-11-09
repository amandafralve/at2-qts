# AGENTS.md - Regras de Contexto para Agentes de IA

## 1. Contexto do Projeto

**DogBreeds Hub** é uma aplicação web de catálogo de raças de cães, criada como Aplicação Sob Teste (SUT) da disciplina Qualidade e Teste de Software. O foco do projeto são os testes (integração, E2E, acessibilidade e carga).

## 2. Stack Obrigatória

- Python 3.12+ gerenciado com **uv** (`pyproject.toml`). Nunca use `pip install` direto nem `requirements.txt`.
- FastAPI + Pydantic v2 + Jinja2.
- Testes: `pytest`, `pytest-mock`, `pytest-playwright`, `Faker`, `axe-playwright-python`, `locust`.
- Persistência apenas em memória. Não adicionar banco de dados nem ORM.


## 3. Estrutura do Repositório

```
app/
  main.py          # rotas FastAPI
  schemas.py       # schemas Pydantic
  repository.py    # armazenamento em memória
  services.py      # VeterinaryService simulável e mockado nos testes
  templates/index.html
pages/
  racas_page.py    # Page Object Model
tests/
  conftest.py
  factories.py
  test_integracao.py
  test_e2e.py
  test_acessibilidade.py
locustfile.py
PRD.md  AGENTS.md  AI_USAGE.md  README.md  pyproject.toml
```

Não crie arquivos fora dessa estrutura sem necessidade clara.

## 4. Convenções de Código

- Type hints em todas as funções públicas. Nomes de rotas, modelos e campos seguem o PRD (em português: `racas`, `nome`, `porte`, `expectativa_vida_anos`, `temperamento`, `origem`).
- Validação de entrada **somente** via Pydantic. Não duplicar validação manualmente nas rotas.
- Erros de domínio viram `HTTPException` com os status do PRD (404, 409, 422, 503, 504). Nunca devolver 500 por entrada inválida.
- Rotas finas: regra de negócio no repositório/serviço, não na função de rota.
- Funções pequenas, sem comentários óbvios. Docstring curta só onde agrega.

## 5. Regras de Testes

### 5.1 Gerais
- Padrão **AAA** (Arrange, Act, Assert) em todo teste, com os blocos separados por linha em branco.
- Um comportamento por teste. Nomes descritivos: `test_cadastrar_raca_com_nome_duplicado_retorna_409`.
- Todo teste carrega exatamente um marker: `@pytest.mark.integration`, `@pytest.mark.e2e` ou `@pytest.mark.accessibility`. Os markers ficam declarados no `pyproject.toml`.
- Testes independentes entre si e sem ordem implícita. Nunca depender de estado deixado por outro teste.
- `uv run pytest -v` deve passar 100% sem warnings.

### 5.2 Integração
- Usar `TestClient` do FastAPI.
- Fixtures em `conftest.py` com setup e teardown via `yield`; o repositório em memória é limpo a cada teste.
- Dados de teste **sempre** via `tests/factories.py` usando `Faker("pt_BR")`. Proibido payload fixo "mágico" repetido nos testes (exceção: casos inválidos pontuais e explícitos).
- A dependência externa (`VeterinaryService`) é isolada com `mocker.patch` (pytest-mock). Cobrir sucesso, indisponibilidade (503) e timeout (504). Nenhum teste faz chamada de rede real.

### 5.3 E2E e Acessibilidade
- Todo acesso à página passa por um **Page Object** em `pages/racas_page.py`. 
- Seletores semânticos apenas: `get_by_role`, `get_by_label`, `get_by_text`. Proibido CSS, XPath e `data-testid`, salvo justificativa registrada no `AI_USAGE.md`.
- Proibido `time.sleep`. Usar as esperas automáticas e `expect(...)` do Playwright.
- O servidor para os testes E2E sobe por fixture (porta livre) e é encerrado no teardown.
- Acessibilidade: Axe-core com tags WCAG 2.1 AA e **0 violações**. Não silenciar regras do Axe para fazer o teste passar: corrigir o HTML.
- Navegação por teclado: `page.keyboard.press("Tab")` + `expect(locator).to_be_focused()`.

### 5.4 Carga
- `locustfile.py` com `HttpUser` e `@task`. Nunca incluir a rota `verificar-veterinario`.
- Usar nomes únicos no `POST` (ex.: Faker ou UUID) para não gerar 409 falsos.
- Resultados (RPS, p95, % de falhas) vão no `README.md`, medidos de verdade, nunca inventados.

## 6. HTML e Acessibilidade (frontend)

- `<html lang="pt-BR">`, um `<h1>`, landmarks `<header>/<main>/<footer>`.
- Todo campo com `<label for>`. Botões com texto visível.
- Tabela com `<caption>` e `<th scope="col">`.
- Mensagens dinâmicas em `role="status"` (sucesso) ou `role="alert"` (erro).
- Contraste mínimo 4,5:1 e foco visível. Sem CSS que remova o `outline` sem substituto.

## 7. O que a IA NÃO deve fazer

- Não alterar o `PRD.md` sem pedido explícito do autor.
- Não apagar nem enfraquecer testes (assert mais fraco, `skip`, `xfail`) para fazê-los passar.
- Não adicionar dependências, rotas ou funcionalidades fora do PRD.
- Não inventar métricas, resultados de execução ou saída de comandos.
- Não colocar segredos, chaves ou URLs privadas no código.
- Não fazer commit direto de código que não foi executado: rodar `uv run pytest -v` antes.



## 9. Comandos Úteis

```bash
uv sync
uv run playwright install chromium
uv run uvicorn app.main:app --reload
uv run pytest -v
uv run pytest -v -m integration
uv run pytest -v -m "e2e or accessibility"
uv run locust -f locustfile.py --headless -u 20 -r 5 -t 60s --host http://localhost:8000
```