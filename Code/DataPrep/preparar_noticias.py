"""
Limpeza e estatísticas das notícias de Data/raw/noticias_cgu.csv.

Uso:
    python Code/DataPrep/preparar_noticias.py

Saída:
    Data/processed/noticias_limpas.csv       (dados tratados, servidos pela API)
    Data/processed/estatisticas_noticias.csv (notícias por categoria)
    Data/processed/corpus_llm.jsonl          (uma notícia por linha, para uso com LLM)
"""

import re
from collections import Counter
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATH = BASE_DIR / "Data" / "raw" / "noticias_cgu.csv"
PROCESSED_DIR = BASE_DIR / "Data" / "processed"

STOPWORDS_PT = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "e", "é", "ao", "aos", "à", "às", "um", "uma", "uns", "umas", "para", "por", "com",
    "sem", "sobre", "entre", "que", "se", "sua", "seu", "suas", "seus", "como", "mais",
    "menos", "ou", "após", "até", "cgu", "pf", "mpf",
}


def limpar_titulo(titulo: str) -> str:
    titulo = titulo.lower()
    titulo = re.sub(r"[^a-zà-ú0-9\s]", " ", titulo)
    palavras = [p for p in titulo.split() if p not in STOPWORDS_PT and len(p) > 2]
    return " ".join(palavras)


def main() -> None:
    df = pd.read_csv(RAW_PATH, parse_dates=["data_publicacao"])
    df = df.sort_values("data_publicacao", ascending=False).reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df["titulo_limpo"] = df["titulo"].apply(limpar_titulo)
    df["categoria"] = df["categoria"].fillna("Sem categoria")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "noticias_limpas.csv", index=False)

    contagem_categoria = df["categoria"].value_counts().rename_axis("categoria").reset_index(name="quantidade")
    contagem_categoria.to_csv(PROCESSED_DIR / "estatisticas_noticias.csv", index=False)

    corpus = df.loc[df["texto"].notna(), ["id", "titulo", "data_publicacao", "categoria", "url", "texto"]].copy()
    corpus["data_publicacao"] = corpus["data_publicacao"].dt.strftime("%Y-%m-%d")
    corpus.to_json(PROCESSED_DIR / "corpus_llm.jsonl", orient="records", lines=True, force_ascii=False)

    top10 = Counter(" ".join(df["titulo_limpo"]).split()).most_common(10)
    print(f"{len(df)} notícias processadas, {len(corpus)} no corpus para LLM")
    print(f"Período: {df['data_publicacao'].min().date()} a {df['data_publicacao'].max().date()}")
    print(f"Categorias distintas: {df['categoria'].nunique()}")
    print("Top 10 palavras:", top10)


if __name__ == "__main__":
    main()
