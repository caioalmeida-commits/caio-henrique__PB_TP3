"""
API do Radar da Transparência (FastAPI).

Uso (na raiz do projeto):
    uvicorn Code.API.main:app --reload

Documentação interativa: http://127.0.0.1:8000/docs
"""

from datetime import date
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parents[2]
CONTRATACOES_AMOSTRA = BASE_DIR / "Sample_Data" / "amostra_contratacoes.csv"
CONTRATACOES_ENVIADAS = BASE_DIR / "Data" / "processed" / "contratacoes_enviadas.csv"
NOTICIAS = BASE_DIR / "Data" / "processed" / "noticias_limpas.csv"

app = FastAPI(
    title="API do Radar da Transparência",
    description="Consulta e envio de contratações públicas e consulta das notícias da CGU coletadas.",
    version="1.0.0",
)


class Contratacao(BaseModel):
    id_contratacao: str = Field(min_length=1, examples=["PNCP-2025-000301"])
    data_publicacao: date
    orgao: str = Field(min_length=1)
    uf: str = Field(min_length=2, max_length=2, examples=["DF"])
    municipio: str = Field(min_length=1)
    modalidade: str = Field(min_length=1, examples=["Pregão Eletrônico"])
    objeto: str = Field(min_length=1)
    valor_estimado: float = Field(gt=0)
    fornecedor: str = Field(min_length=1)
    cnpj_fornecedor: str = Field(min_length=1, examples=["11.111.111/0001-11"])

    @field_validator("uf")
    @classmethod
    def uf_maiuscula(cls, valor: str) -> str:
        return valor.upper()


class Noticia(BaseModel):
    id: int
    titulo: str
    titulo_limpo: str | None = None
    data_publicacao: date
    categoria: str
    resumo: str | None = None
    url: str
    texto: str | None = None


def carregar_contratacoes() -> pd.DataFrame:
    partes = [pd.read_csv(CONTRATACOES_AMOSTRA)]
    if CONTRATACOES_ENVIADAS.exists():
        partes.append(pd.read_csv(CONTRATACOES_ENVIADAS))
    return pd.concat(partes, ignore_index=True)


def como_registros(df: pd.DataFrame) -> list[dict]:
    return df.astype(object).where(df.notna(), None).to_dict("records")


@app.get(
    "/contratacoes",
    response_model=list[Contratacao],
    summary="Consulta contratações",
    description="Retorna as contratações da amostra mais as enviadas via POST, com filtros opcionais.",
)
def listar_contratacoes(
    modalidade: str | None = Query(None, description="Modalidade (sem diferenciar maiúsculas)"),
    uf: str | None = Query(None, min_length=2, max_length=2, description="Sigla da UF"),
    valor_min: float | None = Query(None, ge=0, description="Valor estimado mínimo (R$)"),
    valor_max: float | None = Query(None, ge=0, description="Valor estimado máximo (R$)"),
    limite: int = Query(100, ge=1, le=1000, description="Máximo de registros retornados"),
):
    df = carregar_contratacoes()
    if modalidade:
        df = df[df["modalidade"].str.lower() == modalidade.lower()]
    if uf:
        df = df[df["uf"].str.upper() == uf.upper()]
    if valor_min is not None:
        df = df[df["valor_estimado"] >= valor_min]
    if valor_max is not None:
        df = df[df["valor_estimado"] <= valor_max]
    return como_registros(df.head(limite))


@app.post(
    "/contratacoes",
    response_model=Contratacao,
    status_code=201,
    summary="Envia uma nova contratação",
    description="Adiciona uma contratação à base. Retorna 409 se o id_contratacao já existir.",
)
def criar_contratacao(contratacao: Contratacao):
    if contratacao.id_contratacao in set(carregar_contratacoes()["id_contratacao"]):
        raise HTTPException(status_code=409, detail="id_contratacao já cadastrado")
    CONTRATACOES_ENVIADAS.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([contratacao.model_dump(mode="json")]).to_csv(
        CONTRATACOES_ENVIADAS, mode="a", header=not CONTRATACOES_ENVIADAS.exists(), index=False
    )
    return contratacao


@app.get(
    "/noticias",
    response_model=list[Noticia],
    response_model_exclude_none=True,
    summary="Consulta notícias da CGU",
    description="Retorna as notícias coletadas por web scraping, com filtro por categoria. "
    "O texto completo só vem com incluir_texto=true.",
)
def listar_noticias(
    categoria: str | None = Query(None, description="Categoria (sem diferenciar maiúsculas)"),
    incluir_texto: bool = Query(False, description="Inclui o texto completo de cada notícia"),
    limite: int = Query(100, ge=1, le=1000, description="Máximo de registros retornados"),
):
    if not NOTICIAS.exists():
        raise HTTPException(status_code=404, detail="Notícias ainda não coletadas")
    df = pd.read_csv(NOTICIAS)
    if categoria:
        df = df[df["categoria"].str.lower() == categoria.lower()]
    if not incluir_texto:
        df = df.drop(columns=["texto"])
    return como_registros(df.head(limite))
