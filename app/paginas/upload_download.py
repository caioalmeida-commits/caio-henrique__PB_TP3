import json
from datetime import date

import pandas as pd
import streamlit as st
from utils import (
    COLUNAS_CONTRATACOES,
    EXEMPLO_UPLOAD_PATH,
    carregar_contratacoes,
    enviar_contratacao,
    exigir_api,
)

exigir_api()

st.title("📤 Upload e Download de Dados")
st.caption("Os envios usam a rota POST /contratacoes da API; o download usa GET /contratacoes.")

st.subheader("Enviar uma contratação")
with st.form("form_contratacao", clear_on_submit=True):
    c1, c2 = st.columns(2)
    id_contratacao = c1.text_input("ID da contratação")
    data_publicacao = c2.date_input("Data de publicação", value=date.today())
    orgao = c1.text_input("Órgão")
    modalidade = c2.text_input("Modalidade")
    uf = c1.text_input("UF", max_chars=2)
    municipio = c2.text_input("Município")
    objeto = st.text_input("Objeto")
    valor_estimado = c1.number_input("Valor estimado (R$)", min_value=0.0, step=1000.0, format="%.2f")
    fornecedor = c2.text_input("Fornecedor")
    cnpj_fornecedor = c1.text_input("CNPJ do fornecedor")
    enviado = st.form_submit_button("Enviar para a API")

if enviado:
    resposta = enviar_contratacao(
        {
            "id_contratacao": id_contratacao,
            "data_publicacao": data_publicacao.isoformat(),
            "orgao": orgao,
            "uf": uf,
            "municipio": municipio,
            "modalidade": modalidade,
            "objeto": objeto,
            "valor_estimado": valor_estimado,
            "fornecedor": fornecedor,
            "cnpj_fornecedor": cnpj_fornecedor,
        }
    )
    if resposta.status_code == 201:
        st.success("Contratação enviada.")
    elif resposta.status_code == 409:
        st.error("Já existe uma contratação com esse ID.")
    else:
        st.error("Dados inválidos: preencha todos os campos e use um valor maior que zero.")

st.divider()
st.subheader("Enviar um CSV de contratações")
with open(EXEMPLO_UPLOAD_PATH, "rb") as f:
    st.download_button(
        "⬇️ Baixar CSV de exemplo",
        data=f.read(),
        file_name="exemplo_upload_contratacoes.csv",
        mime="text/csv",
    )

arquivo = st.file_uploader("Arquivo CSV", type="csv")
if arquivo is not None:
    try:
        df_novo = pd.read_csv(arquivo)
    except Exception as erro:
        st.error(f"Não foi possível ler o CSV: {erro}")
    else:
        faltando = set(COLUNAS_CONTRATACOES) - set(df_novo.columns)
        if faltando:
            st.error(f"Faltam colunas no arquivo: {', '.join(sorted(faltando))}")
        else:
            df_novo["data_publicacao"] = pd.to_datetime(df_novo["data_publicacao"]).dt.strftime("%Y-%m-%d")
            st.dataframe(df_novo, use_container_width=True, hide_index=True)
            if st.button("Enviar linhas para a API"):
                contagem = {201: 0, 409: 0, "erro": 0}
                for registro in json.loads(df_novo[COLUNAS_CONTRATACOES].to_json(orient="records")):
                    codigo = enviar_contratacao(registro).status_code
                    contagem[codigo if codigo in contagem else "erro"] += 1
                st.success(
                    f"{contagem[201]} enviadas, {contagem[409]} já existentes, {contagem['erro']} com erro."
                )

st.divider()
st.subheader("Baixar a base atual")
df_atual = carregar_contratacoes()
st.write(f"{len(df_atual)} contratações na base (amostra + enviadas).")
st.download_button(
    "⬇️ Baixar base completa (CSV)",
    data=df_atual.to_csv(index=False).encode("utf-8"),
    file_name="contratacoes_base_completa.csv",
    mime="text/csv",
)
