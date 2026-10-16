import streamlit as st
from utils import carregar_contratacoes, exigir_api

exigir_api()

st.title("🔎 Radar da Transparência em Contratações Públicas")
st.caption("Contratações consultadas na API (GET /contratacoes).")

df = carregar_contratacoes()

st.sidebar.header("Filtros")
modalidades = st.sidebar.multiselect(
    "Modalidade", options=sorted(df["modalidade"].unique()), default=sorted(df["modalidade"].unique())
)
ufs = st.sidebar.multiselect("UF", options=sorted(df["uf"].unique()), default=sorted(df["uf"].unique()))
valor_min, valor_max = float(df["valor_estimado"].min()), float(df["valor_estimado"].max())
faixa_valor = st.sidebar.slider(
    "Valor estimado (R$)", min_value=valor_min, max_value=valor_max, value=(valor_min, valor_max)
)

df_filtrado = df[
    df["modalidade"].isin(modalidades) & df["uf"].isin(ufs) & df["valor_estimado"].between(*faixa_valor)
]

c1, c2, c3 = st.columns(3)
c1.metric("Contratações (filtro atual)", len(df_filtrado))
c2.metric("Órgãos distintos", df_filtrado["orgao"].nunique())
c3.metric("Valor total (R$)", f"{df_filtrado['valor_estimado'].sum():,.2f}")

st.subheader("Contratações")
st.caption("Marque **sinalizar** para separar contratações para revisão manual (guardado no estado de sessão).")

df_tabela = df_filtrado.copy()
df_tabela.insert(0, "sinalizar", df_tabela["id_contratacao"].isin(st.session_state["sinalizados"]))

edicao = st.data_editor(
    df_tabela,
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in df_tabela.columns if c != "sinalizar"],
    column_config={
        "data_publicacao": st.column_config.DateColumn("Data de publicação", format="DD/MM/YYYY"),
        "valor_estimado": st.column_config.NumberColumn("Valor estimado (R$)", format="%.2f"),
        "sinalizar": st.column_config.CheckboxColumn("Sinalizar"),
    },
    key="editor_contratacoes",
)

novos_sinalizados = set(edicao.loc[edicao["sinalizar"], "id_contratacao"])
fora_do_filtro = st.session_state["sinalizados"] - set(df_tabela["id_contratacao"])
st.session_state["sinalizados"] = novos_sinalizados | fora_do_filtro

if st.session_state["sinalizados"]:
    st.write(f"**{len(st.session_state['sinalizados'])} contratação(ões) sinalizada(s)** para revisão.")

st.download_button(
    "⬇️ Baixar contratações filtradas (CSV)",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="contratacoes_filtradas.csv",
    mime="text/csv",
)
