import random
from typing import Any

from faker import Faker

fake = Faker("pt_BR")

PORTES_DISPONIVEIS = ["Pequeno", "Médio", "Grande"]
PAISES = ["Alemanha", "Escócia", "Inglaterra", "França", "Japão", "Brasil", "Canadá"]
ADJETIVOS_TEMPERAMENTO = [
    "Amigável", "Inteligente", "Dócil", "Protetor", "Alerta", "Ativo", "Calmo",
]


class RacaFactory:
    """Fábrica de dados sintéticos para o domínio de Raças de Cães."""

    @staticmethod
    def criar_payload_valido() -> dict[str, Any]:
        nome_unico = f"Raça {fake.unique.first_name()}"
        temperamentos = random.sample(ADJETIVOS_TEMPERAMENTO, k=3)

        return {
            "nome": nome_unico,
            "origem": random.choice(PAISES),
            "porte": random.choice(PORTES_DISPONIVEIS),
            "expectativa_vida_anos": random.randint(8, 18),
            "temperamento": ", ".join(temperamentos),
        }

    @staticmethod
    def criar_payload_invalido_sem_nome() -> dict[str, Any]:
        payload = RacaFactory.criar_payload_valido()
        payload["nome"] = ""
        return payload