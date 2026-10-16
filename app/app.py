"""
Radar da Transparência em Contratações Públicas — app Streamlit (TP3).

Rodar (com a API no ar):  streamlit run app/app.py
"""

import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
UTILS_DIR = str(BASE_DIR / "Code" / "Operationalization")
if UTILS_DIR not in sys.path:
    sys.path.append(UTILS_DIR)

st.set_page_config(
    page_title="Radar da Transparência em Contratações Públicas",
    page_icon="🔎",
    layout="wide",
)

st.session_state.setdefault("sinalizados", set())

menu = st.navigation(
    [
        st.Page("paginas/contratacoes.py", title="Contratações", icon="📋", default=True),
        st.Page("paginas/estatisticas.py", title="Estatísticas e Gráficos", icon="📊"),
        st.Page("paginas/noticias.py", title="Notícias e Nuvem de Palavras", icon="📰"),
        st.Page("paginas/upload_download.py", title="Upload e Download", icon="📤"),
    ]
)
st.sidebar.caption("Projeto de Bloco — TP3 | Pilar ESG: Governança | ODS 16")
menu.run()
