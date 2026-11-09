import random
import uuid

from faker import Faker
from locust import HttpUser, between, task

fake = Faker("pt_BR")

PORTES = ["Pequeno", "Médio", "Grande"]


class UsuarioGestaoRacas(HttpUser):
    wait_time = between(0.5, 2)

    @task(3)
    def consultar_racas(self) -> None:
        self.client.get("/api/v1/racas", name="/api/v1/racas [GET]")

    @task
    def filtrar_racas_por_porte(self) -> None:
        self.client.get(
            "/api/v1/racas",
            params={"porte": "Grande"},
            name="/api/v1/racas?porte=Grande [GET]",
        )

    @task(1)
    def checar_saude_sistema(self) -> None:
        self.client.get("/health", name="/health [GET]")

    @task(2)
    def cadastrar_raca_sintetica(self) -> None:
        payload = {
            "nome": f"Cão {fake.first_name()} {uuid.uuid4().hex}",
            "origem": fake.country(),
            "porte": random.choice(PORTES),
            "expectativa_vida_anos": random.randint(8, 16),
            "temperamento": "Dócil, Ativo",
        }

        with self.client.post(
            "/api/v1/racas",
            json=payload,
            catch_response=True,
            name="/api/v1/racas [POST]",
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Erro inesperado: {response.status_code}")