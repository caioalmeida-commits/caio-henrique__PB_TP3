import pandas as pd
import pytest
from fastapi.testclient import TestClient

from Code.API import main

NOVA = {
    "id_contratacao": "PNCP-2025-000999",
    "data_publicacao": "2025-03-01",
    "orgao": "Órgão de Teste",
    "uf": "df",
    "municipio": "Brasília",
    "modalidade": "Dispensa",
    "objeto": "Serviço de teste",
    "valor_estimado": 1000.5,
    "fornecedor": "Fornecedor Teste Ltda",
    "cnpj_fornecedor": "00.000.000/0001-00",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    noticias = tmp_path / "noticias.csv"
    pd.DataFrame(
        [
            {"id": 1, "titulo": "A", "data_publicacao": "2026-07-10", "categoria": "Integridade",
             "resumo": "r1", "url": "http://x/1", "texto": "texto 1", "titulo_limpo": "a"},
            {"id": 2, "titulo": "B", "data_publicacao": "2026-07-11", "categoria": "Ouvidoria",
             "resumo": None, "url": "http://x/2", "texto": "texto 2", "titulo_limpo": "b"},
        ]
    ).to_csv(noticias, index=False)
    monkeypatch.setattr(main, "CONTRATACOES_ENVIADAS", tmp_path / "enviadas.csv")
    monkeypatch.setattr(main, "NOTICIAS", noticias)
    return TestClient(main.app)


def test_get_contratacoes_retorna_amostra(client):
    resposta = client.get("/contratacoes")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 20


def test_get_contratacoes_filtros(client):
    dados = client.get("/contratacoes", params={"uf": "df", "modalidade": "dispensa", "valor_min": 500000}).json()
    assert dados and all(
        c["uf"] == "DF" and c["modalidade"] == "Dispensa" and c["valor_estimado"] >= 500000 for c in dados
    )
    assert len(client.get("/contratacoes", params={"limite": 3}).json()) == 3


def test_post_contratacao_e_consulta(client):
    resposta = client.post("/contratacoes", json=NOVA)
    assert resposta.status_code == 201
    assert resposta.json()["uf"] == "DF"
    ids = [c["id_contratacao"] for c in client.get("/contratacoes").json()]
    assert "PNCP-2025-000999" in ids and len(ids) == 21


def test_post_contratacao_duplicada(client):
    assert client.post("/contratacoes", json=NOVA).status_code == 201
    assert client.post("/contratacoes", json=NOVA).status_code == 409


def test_post_contratacao_invalida(client):
    assert client.post("/contratacoes", json={**NOVA, "valor_estimado": -1}).status_code == 422
    assert client.post("/contratacoes", json={**NOVA, "uf": "DFX"}).status_code == 422


def test_get_noticias(client):
    dados = client.get("/noticias").json()
    assert len(dados) == 2 and all("texto" not in n for n in dados)
    assert "resumo" not in dados[1]
    assert client.get("/noticias", params={"incluir_texto": True}).json()[0]["texto"] == "texto 1"
    filtradas = client.get("/noticias", params={"categoria": "ouvidoria"}).json()
    assert [n["id"] for n in filtradas] == [2]


def test_get_noticias_sem_arquivo(client, tmp_path, monkeypatch):
    monkeypatch.setattr(main, "NOTICIAS", tmp_path / "inexistente.csv")
    assert client.get("/noticias").status_code == 404
