import altair as alt
import streamlit as st
from utils import carregar_contratacoes, exigir_api

exigir_api()

st.title("📊 Estatísticas e Gráficos")
st.caption("Indicadores calculados a partir das contratações da API.")

df = carregar_contratacoes()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Contratações", len(df))
c2.metric("Valor total (R$)", f"{df['valor_estimado'].sum():,.2f}")
c3.metric("Valor médio (R$)", f"{df['valor_estimado'].mean():,.2f}")
c4.metric("Valor mediano (R$)", f"{df['valor_estimado'].median():,.2f}")

st.subheader("Valor ou quantidade por categoria")
col_a, col_b = st.columns(2)
dimensao = col_a.selectbox("Agrupar por", ["modalidade", "uf", "orgao", "fornecedor"])
metrica = col_b.radio("Métrica", ["Valor total (R$)", "Quantidade"], horizontal=True)

if metrica == "Quantidade":
    agrupado = df.groupby(dimensao).size().reset_index(name="valor")
else:
    agrupado = df.groupby(dimensao)["valor_estimado"].sum().reset_index(name="valor")
agrupado = agrupado.sort_values("valor", ascending=False).head(15)

st.altair_chart(
    alt.Chart(agrupado)
    .mark_bar()
    .encode(
        x=alt.X("valor:Q", title=metrica),
        y=alt.Y(f"{dimensao}:N", sort="-x", title=dimensao),
        tooltip=[dimensao, alt.Tooltip("valor:Q", title=metrica, format=",.2f")],
    )
    .interactive(),
    use_container_width=True,
)

st.subheader("Valor estimado por data de publicação")
por_dia = df.groupby("data_publicacao")["valor_estimado"].sum().reset_index()
st.altair_chart(
    alt.Chart(por_dia)
    .mark_line(point=True)
    .encode(
        x=alt.X("data_publicacao:T", title="Data de publicação"),
        y=alt.Y("valor_estimado:Q", title="Valor total (R$)"),
        tooltip=[
            alt.Tooltip("data_publicacao:T", title="Data"),
            alt.Tooltip("valor_estimado:Q", title="Valor total (R$)", format=",.2f"),
        ],
    )
    .interactive(),
    use_container_width=True,
)

st.subheader("Distribuição dos valores")
st.altair_chart(
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("valor_estimado:Q", bin=alt.Bin(maxbins=15), title="Valor estimado (R$)"),
        y=alt.Y("count()", title="Contratações"),
        tooltip=[alt.Tooltip("count()", title="Contratações")],
    ),
    use_container_width=True,
)

st.subheader("Estatísticas descritivas do valor estimado")
st.dataframe(df["valor_estimado"].describe().rename("valor_estimado").to_frame(), use_container_width=True)
