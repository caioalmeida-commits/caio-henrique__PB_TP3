"""
Scraper das notícias da CGU (BeautifulSoup + requests).

Uso:
    python Code/DataAcquisition/scraping_noticias_cgu.py

Saída:
    Data/raw/noticias_cgu.csv  (titulo, data_publicacao, categoria, resumo, url, texto)
    Data/raw/noticias_cgu.txt  (título e texto completo de cada notícia)
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL_LISTAGEM = "https://www.gov.br/cgu/pt-br/assuntos/noticias/2026/defeso-eleitoral"
RAW_DIR = Path(__file__).resolve().parents[2] / "Data" / "raw"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; coletor-tp3-faculdade/1.0)"}
NOTICIAS_POR_PAGINA = 30
MAX_PAGINAS = 4
PAUSA_SEGUNDOS = 1.0


def baixar_html(url: str, params: dict | None = None) -> str:
    resposta = requests.get(url, params=params, headers=HEADERS, timeout=30)
    resposta.raise_for_status()
    resposta.encoding = "utf-8"
    return resposta.text


def extrair_listagem(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    noticias = []
    for item in soup.select("ul.listagem-noticias-com-foto li"):
        link = item.select_one("h2.titulo a[href]")
        if link is None:
            continue
        data_tag = item.select_one("span.data")
        descricao_tag = item.select_one("span.descricao")
        categoria_tag = item.select_one(".subtitulo-noticia")
        resumo = descricao_tag.get_text(" ", strip=True) if descricao_tag else ""
        resumo = re.sub(r"^\d{2}/\d{2}/\d{4}\s*-\s*", "", resumo)
        noticias.append(
            {
                "titulo": link.get_text(strip=True),
                "data_publicacao": data_tag.get_text(strip=True) if data_tag else None,
                "categoria": categoria_tag.get_text(strip=True) if categoria_tag else None,
                "resumo": resumo or None,
                "url": link["href"],
            }
        )
    return noticias


def extrair_texto(html: str) -> str | None:
    corpo = BeautifulSoup(html, "html.parser").select_one("#parent-fieldname-text")
    if corpo is None:
        return None
    paragrafos = [p.get_text(" ", strip=True) for p in corpo.find_all("p")]
    return "\n".join(p for p in paragrafos if p) or None


def coletar() -> list[dict]:
    noticias, urls_vistas = [], set()
    for pagina in range(MAX_PAGINAS):
        params = {"b_start:int": pagina * NOTICIAS_POR_PAGINA} if pagina else None
        itens = extrair_listagem(baixar_html(URL_LISTAGEM, params))
        novos = [n for n in itens if n["url"] not in urls_vistas]
        if not novos:
            break
        urls_vistas.update(n["url"] for n in novos)
        noticias.extend(novos)
        time.sleep(PAUSA_SEGUNDOS)

    for i, noticia in enumerate(noticias, start=1):
        try:
            noticia["texto"] = extrair_texto(baixar_html(noticia["url"]))
        except requests.RequestException as erro:
            noticia["texto"] = None
            print(f"Falha ao baixar {noticia['url']}: {erro}")
        print(f"[{i}/{len(noticias)}] {noticia['titulo'][:70]}")
        time.sleep(PAUSA_SEGUNDOS)
    return noticias


def salvar(noticias: list[dict]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(noticias)
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], format="%d/%m/%Y").dt.date
    df.to_csv(RAW_DIR / "noticias_cgu.csv", index=False)

    with open(RAW_DIR / "noticias_cgu.txt", "w", encoding="utf-8") as f:
        f.write(f"FONTE: {URL_LISTAGEM}\n")
        f.write(f"COLETADO EM: {time.strftime('%Y-%m-%d')}\n")
        f.write("=" * 65 + "\n\n")
        for _, linha in df.iterrows():
            f.write(f"{linha['titulo']}\n{linha['texto'] or ''}\n\n")

    print(f"{len(df)} notícias salvas em {RAW_DIR}")


def main() -> None:
    noticias = coletar()
    if not noticias:
        raise SystemExit("Nenhuma notícia encontrada: revise os seletores em extrair_listagem().")
    salvar(noticias)


if __name__ == "__main__":
    main()
