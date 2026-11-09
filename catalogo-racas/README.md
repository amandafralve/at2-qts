# DogBreeds Hub

Aplicação de catálogo de raças de cães para a atividade de Qualidade e Teste de Software. A implementação usa Python 3.12+, `uv`, FastAPI, Pydantic e Jinja2; os dados ficam em memória e são reiniciados ao iniciar a aplicação.

## Requisitos

- Python 3.12 ou superior
- [`uv`](https://docs.astral.sh/uv/)

## Instalação e execução

Na pasta `catalogo-racas`:

```powershell
uv sync
uv run playwright install chromium
uv run uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000` para usar a interface. A documentação interativa da API fica em `http://127.0.0.1:8000/docs`.

## Testes

```powershell
uv run pytest -v
uv run pytest -v -m integration
uv run pytest -v -m "e2e or accessibility"
```

Os testes E2E e de acessibilidade iniciam e encerram seu próprio servidor Uvicorn. É necessário instalar o navegador Chromium uma vez com o comando acima.

## Teste de carga

Com a aplicação em execução em outro terminal:

```powershell
uv run locust -f locustfile.py --host http://127.0.0.1:8000
```

Abra `http://localhost:8089` e configure usuários e taxa de inicialização. Para execução automatizada:

```powershell
uv run locust -f locustfile.py --headless -u 20 -r 5 -t 60s --host http://127.0.0.1:8000
```

O cenário gera leituras de `/health` e `/api/v1/racas` (com e sem filtro por porte), além de cadastros com nomes sintéticos exclusivos. A rota de verificação veterinária não faz parte da carga.

### Métricas do teste de carga

Execução local em 07/11/2026, com 20 usuários, taxa de inicialização de 5 usuários/s e duração de 60 s:

| Métrica | Valor medido | Meta do PRD | Status |
|---|---:|---:|---|
| Requisições por segundo (RPS) | 15,56 | ≥ 50 | Não atingida |
| Latência p95 | 6 ms | ≤ 500 ms | Atingida |
| Taxa de falhas | 0% (0/919) | 0% | Atingida |

A meta de throughput não foi alcançada nesta execução; os demais limites foram atingidos. O teste usa o `wait_time` de 0,5 a 2 segundos definido no cenário, o que limita o número de requisições geradas por 20 usuários. Os valores são específicos deste ambiente local e não devem ser interpretados como garantia de desempenho em produção.

## Rotas principais

- `GET /health`
- `GET /api/v1/racas` (filtros opcionais `nome` e `porte`)
- `POST /api/v1/racas`
- `GET /api/v1/racas/{raca_id}`
- `POST /api/v1/racas/{raca_id}/verificar-veterinario`
- `GET /` (interface HTML com cadastro e filtros)

O serviço veterinário é uma dependência local substituível por mock nos testes; nenhuma chamada de rede externa é necessária.
