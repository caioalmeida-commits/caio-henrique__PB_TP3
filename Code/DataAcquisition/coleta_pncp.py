"""
Esboço do coletor de contratações do PNCP (coleta em massa ainda não realizada).

Uso:
    python Code/DataAcquisition/coleta_pncp.py --inicio 20250101 --fim 20250131
"""

import argparse
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
RAW_DIR = Path(__file__).resolve().parents[2] / "Data" / "raw"


def consultar_pagina(data_inicial: str, data_final: str, modalidade: int, pagina: int) -> dict:
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": modalidade,
        "pagina": pagina,
        "tamanhoPagina": 50,
    }
    resposta = requests.get(BASE_URL, params=params, timeout=60)
    resposta.raise_for_status()
    return resposta.json()


def coletar(data_inicial: str, data_final: str, modalidade: int = 6) -> pd.DataFrame:
    registros, pagina = [], 1
    while True:
        dados = consultar_pagina(data_inicial, data_final, modalidade, pagina)
        itens = dados.get("data", [])
        if not itens:
            break
        registros.extend(itens)
        if pagina >= dados.get("totalPaginas", 1):
            break
        pagina += 1
    return pd.DataFrame(registros)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inicio", required=True, help="AAAAMMDD")
    parser.add_argument("--fim", required=True, help="AAAAMMDD")
    parser.add_argument("--modalidade", type=int, default=6)
    args = parser.parse_args()

    df = coletar(args.inicio, args.fim, args.modalidade)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    destino = RAW_DIR / f"pncp_{args.inicio}_{args.fim}.csv"
    df.to_csv(destino, index=False)
    print(f"{len(df)} registros salvos em {destino}")


if __name__ == "__main__":
    main()
