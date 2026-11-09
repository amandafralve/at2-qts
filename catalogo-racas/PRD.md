# PRD: DogBreeds Hub (Gestão de Raças de Cães)

## 1. Visão Geral e Objetivos

O **DogBreeds Hub** é um sistema web em Python 3.12+ com FastAPI, Pydantic v2 e interface HTML para cadastro e consulta de raças de cães.

O projeto serve como Aplicação Sob Teste (SUT) para demonstrar os níveis intermediário e superior da Pirâmide de Testes (integração, E2E e acessibilidade) e a validação automatizada de requisitos não funcionais segundo a **ISO/IEC 25010**.


---

## 2. Stack e Arquitetura

| Camada | Tecnologia |
|---|---|
| Linguagem / projeto | Python 3.12+, `uv` (`pyproject.toml`) |
| Backend | FastAPI + Pydantic v2 |
| Frontend | HTML5 semântico com Jinja2 e formulário nativo |
| Persistência | Repositório em memória (lista/dicionário), reiniciado a cada execução |
| Integração | `pytest`, `TestClient`, fixtures com `yield`, `pytest-mock`, `Faker("pt_BR")` (padrão Factory) |
| E2E | `pytest-playwright`, Page Object Model, seletores semânticos |
| Acessibilidade | `axe-playwright-python` (WCAG 2.1 AA) + navegação por teclado |
| Carga | `locust` (`HttpUser`, `@task`) |

**Estrutura:** `app/main.py` define as rotas, `app/repository.py` mantém os dados em memória, `app/services.py` simula a dependência veterinária e `app/schemas.py` valida os dados com Pydantic.

**Markers pytest:** `integration`, `e2e`, `accessibility`.

---

## 3. Modelo de Dados

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Gerado pelo sistema, sequencial |
| `nome` | string | Obrigatório, 2 a 100 caracteres |
| `porte` | enum | `Pequeno`, `Médio` ou `Grande` |
| `expectativa_vida_anos` | inteiro | Entre 1 e 25 |
| `temperamento` | string | Obrigatório, 3 a 200 caracteres |
| `origem` | string | Opcional, até 100 caracteres |
| `criado_em` | datetime (ISO 8601) | Gerado pelo sistema |

**Regra de negócio:** o `nome` é único, sem diferenciar maiúsculas de minúsculas. Cadastro duplicado retorna `409 Conflict`.

---

## 4. Rotas da API

### 4.1 Healthcheck
- `GET /health` → `200` com `{"status": "ok", "service": "dog-breeds-hub"}`

### 4.2 Listar e filtrar raças
- `GET /api/v1/racas`
- Query params opcionais: `nome` (busca parcial, sem diferenciar maiúsculas) e `porte` (`Pequeno`, `Médio`, `Grande`).
- `200`: lista de raças (vazia quando não há resultados).
- `422`: `porte` fora do enum.

### 4.3 Consultar por ID
- `GET /api/v1/racas/{raca_id}`
- `200`: dados da raça.
- `404`: `{"detail": "Raça não encontrada."}`

### 4.4 Cadastrar raça
- `POST /api/v1/racas`
- Payload de exemplo:

```json
{
  "nome": "Golden Retriever",
  "porte": "Grande",
  "expectativa_vida_anos": 12,
  "temperamento": "Dócil, inteligente, amigável",
  "origem": "Escócia"
}
```

- `201`: raça criada, com `id` e `criado_em`.
- `409`: nome já cadastrado.
- `422`: violação do schema.

### 4.5 Verificar raça com serviço veterinário externo (dependência mockada)
- `POST /api/v1/racas/{raca_id}/verificar-veterinario`
- Chama `VeterinaryService.verificar(raca)` (`services.py`), que simula uma API externa de controle veterinário.
- `200`: `{"raca_id": 1, "aprovada": true, "mensagem": "..."}`
- `404`: raça inexistente (o serviço externo não é chamado).
- `503`: serviço externo indisponível.
- `504`: tempo limite excedido no serviço externo.
- **Nos testes**, o serviço é isolado com `mocker.patch`, cobrindo sucesso, indisponibilidade e timeout. Em execução normal, o cliente usa uma implementação simulada local, sem chamada de rede real.

---

## 5. Interface Web

**Página principal: `GET /`** (HTML renderizado com Jinja2). Idioma declarado (`<html lang="pt-BR">`), um único `<h1>`, landmarks `<header>`, `<main>` e `<footer>`.

### 5.1 Formulário de cadastro
- Campos com `<label for>` vinculado: **Nome**, **Porte** (`<select>`), **Expectativa de vida (anos)**, **Temperamento**, **Origem**.
- Botão **Cadastrar raça**.
- Mensagem de sucesso ou erro em região `role="status"` / `role="alert"`, para ser anunciada por leitores de tela.

### 5.2 Busca e filtro
- Campo **Buscar por nome**, `<select>` **Filtrar por porte** e botão **Filtrar**.

### 5.3 Listagem
- Tabela com `<caption>` e `<th scope="col">`: Nome, Porte, Expectativa de vida, Temperamento, Origem.
- Estado vazio: texto "Nenhuma raça encontrada."

### 5.4 Requisitos de interface
- Todo o fluxo (preencher, cadastrar, filtrar) deve funcionar apenas com teclado, com ordem de Tab lógica e foco visível.
- Contraste mínimo de 4,5:1 para texto normal.
- Nenhuma informação transmitida só por cor.

---

## 6. Requisitos Não Funcionais (ISO/IEC 25010)

| ID | Característica ISO 25010 | Requisito | Verificação |
|---|---|---|---|
| RNF-01 | Adequação funcional | Rotas retornam os status HTTP e payloads do contrato | Testes de integração (`@pytest.mark.integration`) |
| RNF-02 | Confiabilidade / Tolerância a falhas | Falhas do serviço externo retornam 503/504 sem derrubar a API | Testes com `mocker.patch` (sucesso e falha) |
| RNF-03 | Usabilidade / Acessibilidade | 0 violações WCAG 2.1 AA (tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`) | Axe-core (`@pytest.mark.accessibility`) |
| RNF-04 | Usabilidade / Operabilidade | Fluxo completo operável só por teclado | Playwright: `keyboard.press("Tab")` + `to_be_focused()` |
| RNF-05 | Eficiência de desempenho | p95 ≤ 500 ms e RPS ≥ 50 nas rotas locais com 20 usuários concorrentes | Locust, registrado no `README.md` |
| RNF-06 | Confiabilidade / Maturidade | 0% de falhas no teste de carga | Locust |
| RNF-07 | Manutenibilidade / Testabilidade | Testes isolados e repetíveis (banco reiniciado por fixture, dados via Factory) | Fixtures com `yield` |
| RNF-08 | Segurança (validação de entrada) | Entradas inválidas rejeitadas com 422, sem erro 500 | Testes de integração |

---

## 7. Estratégia de Testes

### 7.1 Integração (`tests/integration/`)
- Padrão AAA (Arrange, Act, Assert) com `TestClient`.
- `conftest.py`: fixture `client` e fixture que limpa o repositório (setup antes, teardown depois do `yield`).
- `factories.py`: `BreedFactory` com `Faker("pt_BR")`, gerando payload válido e inválido.
- Casos mínimos: listagem (vazia, com dados, filtros), consulta (200/404), cadastro (201/409/422 com vários campos inválidos) e verificação veterinária (200/404/503/504 com mock).

### 7.2 E2E (`tests/e2e/`)
- Page Object `BreedsPage` (`tests/e2e/pages/`) encapsula `get_by_role`, `get_by_label` e `get_by_text`, sem seletores CSS nos testes.
- Fixture de sessão sobe o servidor uvicorn em porta livre e o encerra no teardown.
- Cenários: cadastrar raça válida e vê-la na tabela; erro de validação na tela; filtrar por nome e por porte; estado vazio.

### 7.3 Acessibilidade
- Axe-core executado na página inicial em estado vazio, com dados e com mensagem de erro visível.
- Navegação por teclado: Tab percorre os campos na ordem esperada, e Enter no botão envia o formulário.

### 7.4 Carga (`locustfile.py`)
- `HttpUser` com `wait_time = between(0.5, 2)`.
- Tarefas: `GET /health`, `GET /api/v1/racas` (peso maior), `GET /api/v1/racas?porte=Grande`, `POST /api/v1/racas` (nome único por requisição).
- A rota `verificar-veterinario` **não** entra no teste de carga.
- Execução de referência: 20 usuários, spawn rate 5/s, 60 s, em modo headless. Os resultados (RPS, p95, % de falhas) vão no `README.md`.

---

## 8. Critérios de Aceite

- [ ] `uv run pytest -v` passa 100% (integração, E2E e acessibilidade).
- [ ] Axe-core reporta 0 violações WCAG 2.1 AA.
- [ ] Locust atinge as metas do RNF-05 e RNF-06, com métricas no `README.md`.
- [ ] `README.md` explica a execução via `uv` (instalação, `playwright install chromium`, pytest, uvicorn, locust).
- [ ] Arquivos de governança presentes: `AGENTS.md` e `AI_USAGE.md`.

---

## 9. Governança de IA

- Regras de contexto para a IA em `AGENTS.md` (stack, padrões de teste, proibições).
- Uso e auditoria da IA registrados em `AI_USAGE.md`: ferramenta utilizada, o que foi gerado, o que foi revisado e corrigido manualmente.