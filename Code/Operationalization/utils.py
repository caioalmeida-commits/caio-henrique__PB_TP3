"""Acesso do app Streamlit à API FastAPI (com cache)."""

import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
EXEMPLO_UPLOAD_PATH = BASE_DIR / "Sample_Data" / "exemplo_upload_contratacoes.csv"
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

COLUNAS_CONTRATACOES = [
    "id_contratacao",
    "data_publicacao",
    "orgao",
    "uf",
    "municipio",
    "modalidade",
    "objeto",
    "valor_estimado",
    "fornecedor",
    "cnpj_fornecedor",
]


def exigir_api() -> None:
    try:
        requests.get(f"{API_URL}/contratacoes", params={"limite": 1}, timeout=3).raise_for_status()
    except requests.RequestException:
        st.error(
            f"API indisponível em {API_URL}. Inicie com `uvicorn Code.API.main:app` "
            "na raiz do projeto e recarregue a página."
        )
        st.stop()


@st.cache_data(ttl=30, show_spinner=False)
def carregar_contratacoes() -> pd.DataFrame:
    resposta = requests.get(f"{API_URL}/contratacoes", params={"limite": 1000}, timeout=30)
    resposta.raise_for_status()
    df = pd.DataFrame(resposta.json(), columns=COLUNAS_CONTRATACOES)
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
    return df


@st.cache_data(ttl=30, show_spinner=False)
def carregar_noticias() -> pd.DataFrame:
    resposta = requests.get(f"{API_URL}/noticias", params={"limite": 1000}, timeout=30)
    resposta.raise_for_status()
    df = pd.DataFrame(resposta.json())
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
    return df


def enviar_contratacao(contratacao: dict) -> requests.Response:
    resposta = requests.post(f"{API_URL}/contratacoes", json=contratacao, timeout=30)
    if resposta.status_code == 201:
        carregar_contratacoes.clear()
    return resposta
