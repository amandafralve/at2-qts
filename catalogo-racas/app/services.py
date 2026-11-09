from app.schemas import RacaResponse


class VeterinaryServiceUnavailable(Exception):
    pass


class VeterinaryTimeout(Exception):
    pass


class VeterinaryService:
    def verificar(self, raca: RacaResponse) -> dict[str, int | bool | str]:
        return {
            "raca_id": raca.id,
            "aprovada": True,
            "mensagem": "Raça aprovada na verificação veterinária.",
        }
