import io

import matplotlib.pyplot as plt
import streamlit as st
from utils import carregar_noticias, exigir_api
from wordcloud import WordCloud

exigir_api()

st.title("📰 Notícias e Nuvem de Palavras")
st.caption(
    "Notícias da CGU coletadas com BeautifulSoup (`Code/DataAcquisition/scraping_noticias_cgu.py`) "
    "e consultadas na API (GET /noticias)."
)

df = carregar_noticias()

st.sidebar.header("Filtros de notícias")
categorias = st.sidebar.multiselect(
    "Categoria", options=sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique())
)
periodo = st.sidebar.date_input(
    "Período", value=(df["data_publicacao"].min().date(), df["data_publicacao"].max().date())
)

df_filtrado = df[df["categoria"].isin(categorias)]
if len(periodo) == 2:
    inicio, fim = periodo
    df_filtrado = df_filtrado[
        (df_filtrado["data_publicacao"].dt.date >= inicio) & (df_filtrado["data_publicacao"].dt.date <= fim)
    ]

c1, c2, c3 = st.columns(3)
c1.metric("Notícias no filtro", len(df_filtrado))
c2.metric("Categorias distintas", df_filtrado["categoria"].nunique())
if len(df_filtrado) > 0:
    c3.metric(
        "Período",
        f"{df_filtrado['data_publicacao'].min().strftime('%d/%m')} a "
        f"{df_filtrado['data_publicacao'].max().strftime('%d/%m')}",
    )

st.subheader("Notícias por categoria")
st.bar_chart(df_filtrado["categoria"].value_counts())

st.subheader("Nuvem de palavras (títulos)")


@st.cache_data(show_spinner=False)
def gerar_nuvem(texto: str) -> bytes:
    nuvem = WordCloud(width=1000, height=450, background_color="white", collocations=False).generate(texto)
    buffer = io.BytesIO()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.imshow(nuvem, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout(pad=0)
    fig.savefig(buffer, format="png")
    plt.close(fig)
    return buffer.getvalue()


texto = " ".join(df_filtrado["titulo_limpo"].fillna(""))
if texto.strip():
    st.image(gerar_nuvem(texto), use_column_width=True)
else:
    st.warning("Sem texto suficiente para gerar a nuvem de palavras.")

st.subheader("Tabela de notícias")
st.dataframe(
    df_filtrado[["titulo", "data_publicacao", "categoria", "resumo", "url"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "data_publicacao": st.column_config.DateColumn("Data de publicação", format="DD/MM/YYYY"),
        "url": st.column_config.LinkColumn("Link"),
    },
)
