from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.repository import RacaRepository
from app.schemas import PorteCachorro, RacaCreate, RacaResponse
from app.services import VeterinaryService, VeterinaryServiceUnavailable, VeterinaryTimeout

app = FastAPI(
    title="DogBreeds Hub",
    description="Catálogo de raças de cães para testes de qualidade.",
    version="1.0.0",
)
repository = RacaRepository()
veterinary_service = VeterinaryService()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "dog-breeds-hub"}


@app.post(
    "/api/v1/racas",
    response_model=RacaResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_raca(payload: RacaCreate) -> RacaResponse:
    try:
        return repository.criar(payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.get("/api/v1/racas", response_model=list[RacaResponse])
def listar_racas(
    nome: str | None = Query(default=None, description="Busca parcial por nome"),
    porte: PorteCachorro | None = Query(default=None),
) -> list[RacaResponse]:
    return repository.listar(nome=nome, porte=porte)


@app.get("/api/v1/racas/{raca_id}", response_model=RacaResponse)
def obter_raca(raca_id: int) -> RacaResponse:
    raca = repository.obter(raca_id)
    if raca is None:
        raise HTTPException(status_code=404, detail="Raça não encontrada.")
    return raca


@app.post("/api/v1/racas/{raca_id}/verificar-veterinario")
def verificar_veterinario(raca_id: int) -> dict[str, int | bool | str]:
    raca = repository.obter(raca_id)
    if raca is None:
        raise HTTPException(status_code=404, detail="Raça não encontrada.")
    try:
        return veterinary_service.verificar(raca)
    except VeterinaryServiceUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except VeterinaryTimeout as error:
        raise HTTPException(status_code=504, detail=str(error)) from error


def _render_pagina(
    request: Request,
    *,
    cadastrado: bool = False,
    erro: str | None = None,
    valores: dict[str, str] | None = None,
    filtro_nome: str = "",
    filtro_porte: str = "",
) -> HTMLResponse:
    porte = PorteCachorro(filtro_porte) if filtro_porte else None
    racas = repository.listar(nome=filtro_nome or None, porte=porte)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "cadastrado": cadastrado,
            "erro": erro,
            "valores": valores or {},
            "filtro_nome": filtro_nome,
            "filtro_porte": filtro_porte,
            "portes": [porte.value for porte in PorteCachorro],
            "racas": racas,
        },
    )


@app.get("/", response_class=HTMLResponse)
def pagina_inicial(
    request: Request,
    nome: str = "",
    porte: PorteCachorro | None = None,
) -> HTMLResponse:
    return _render_pagina(
        request,
        filtro_nome=nome,
        filtro_porte=porte.value if porte else "",
    )


@app.post("/", response_class=HTMLResponse)
def cadastrar_pela_interface(
    request: Request,
    nome: str = Form(default=""),
    porte: str = Form(default=""),
    expectativa_vida_anos: str = Form(default=""),
    temperamento: str = Form(default=""),
    origem: str = Form(default=""),
) -> HTMLResponse:
    valores = {
        "nome": nome,
        "porte": porte,
        "expectativa_vida_anos": expectativa_vida_anos,
        "temperamento": temperamento,
        "origem": origem,
    }
    try:
        payload = RacaCreate.model_validate(
            {
                **valores,
                "origem": origem or None,
            }
        )
        repository.criar(payload)
    except ValidationError:
        return _render_pagina(
            request,
            erro="Dados inválidos. Verifique os campos e tente novamente.",
            valores=valores,
        )
    except ValueError as error:
        return _render_pagina(request, erro=str(error), valores=valores)
    return _render_pagina(request, cadastrado=True)
