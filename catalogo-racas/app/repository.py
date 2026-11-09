from datetime import datetime, timezone

from app.schemas import PorteCachorro, RacaCreate, RacaResponse


class RacaRepository:
    def __init__(self) -> None:
        self._racas: dict[int, RacaResponse] = {}
        self._next_id = 1

    def limpar(self) -> None:
        self._racas.clear()
        self._next_id = 1

    def criar(self, payload: RacaCreate) -> RacaResponse:
        nome_normalizado = payload.nome.casefold()
        if any(raca.nome.casefold() == nome_normalizado for raca in self._racas.values()):
            raise ValueError(f"A raça '{payload.nome}' já está cadastrada.")

        raca = RacaResponse(
            id=self._next_id,
            criado_em=datetime.now(timezone.utc),
            **payload.model_dump(),
        )
        self._racas[raca.id] = raca
        self._next_id += 1
        return raca

    def listar(
        self,
        *,
        nome: str | None = None,
        porte: PorteCachorro | None = None,
    ) -> list[RacaResponse]:
        racas = list(self._racas.values())
        if nome:
            termo = nome.casefold()
            racas = [raca for raca in racas if termo in raca.nome.casefold()]
        if porte is not None:
            racas = [raca for raca in racas if raca.porte == porte]
        return racas

    def obter(self, raca_id: int) -> RacaResponse | None:
        return self._racas.get(raca_id)
