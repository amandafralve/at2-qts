import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from fastapi.testclient import TestClient

from app.main import app, repository
from tests.factories import RacaFactory


@pytest.fixture
def client() -> Iterator[TestClient]:
    repository.limpar()
    with TestClient(app) as test_client:
        yield test_client
    repository.limpar()


@pytest.fixture
def raca_pre_cadastrada(client: TestClient) -> dict[str, object]:
    response = client.post("/api/v1/racas", json=RacaFactory.criar_payload_valido())
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def server_url() -> Iterator[str]:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 15
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                error = process.stderr.read() if process.stderr else ""
                raise RuntimeError(f"Uvicorn encerrou durante a inicialização: {error}")
            try:
                with urlopen(f"{url}/health", timeout=0.5):
                    break
            except (OSError, URLError):
                threading.Event().wait(0.1)
        else:
            raise RuntimeError("Uvicorn não iniciou no prazo de 15 segundos.")
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.stderr:
            process.stderr.close()
