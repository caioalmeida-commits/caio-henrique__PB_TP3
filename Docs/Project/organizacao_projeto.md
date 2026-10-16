# Organização do Projeto — CRISP-DM e TDSP

## 1. Por que os dois métodos

O CRISP-DM organiza **o que precisa ser feito** em cada fase analítica do projeto.
O TDSP organiza **como o time trabalha**: quais papéis existem, quais artefatos cada
estágio precisa entregar e como o código e os dados ficam versionados. Neste projeto
uso o CRISP-DM para guiar o raciocínio analítico e o TDSP para a estrutura de pastas,
artefatos e ciclo de vida. Como o projeto é individual, acumulo os quatro papéis do
TDSP (Project Lead, Data Scientist, Project Manager e Solution Architect).

## 2. Ciclo de vida TDSP aplicado ao projeto

| Estágio TDSP | O que farei | Artefatos | Entrega | Status |
|--------------|-------------|-----------|---------|--------|
| **Business Understanding** | Definir o problema de transparência em contratações, metas, indicadores de sucesso, ODS 16 e público-alvo | `Docs/Project/project_charter.md`, repositório estruturado | TP1 | Concluído (charter revisado no TP3) |
| **Data Acquisition & Understanding** | Coletar via API do PNCP, Portal da Transparência e Compras.gov.br; complementar com scraping (BeautifulSoup); explorar e avaliar qualidade | `Docs/DataReport/data_summary_report.md`, `Code/DataAcquisition`, `Code/DataPrep`, `Data/raw`, `Data/processed` | TP1 (esboço) → TP3 | Notícias da CGU recoletadas com texto completo no TP3; Selenium avaliado e não necessário; coleta em massa da API do PNCP segue pendente |
| **Modeling** | Feature engineering (valor por unidade, share do fornecedor, frequência de dispensa) e regra/modelo de detecção de contratos atípicos; prompts do LLM | `Docs/Model/preparacao_llm.md`, `Code/Modeling` | Próxima etapa | Dados preparados para LLM no TP3; implementação planejada |
| **Deployment** | Publicar o dashboard Streamlit, monitorar erros de coleta e tempo de resposta | `app/`, `Code/API`, `Code/Operationalization`, dashboard | TP4 (demo evoluída desde o TP1) | Em andamento — app multipágina com menu de navegação, cache e estado de sessão, consumindo uma API FastAPI |
| **Acceptance** | Revisar contra os critérios do charter, documentar e apresentar | `Docs/Project/project_final_report.md` | Etapas finais | Planejado |

Os papéis do diagrama TDSP, neste projeto individual, ficam assim:
- **Project Lead:** cria o repositório a partir do template e faz os checkpoints de cada entrega.
- **Project Manager:** mantém o Project Charter e a documentação final.
- **Data Scientist:** coleta, explora, faz feature engineering e o modelo/regra de detecção.
- **Solution Architect:** define a arquitetura (coleta → tratamento → API → app) e o pipeline de dados.

## 3. Correspondência com o CRISP-DM

| CRISP-DM | Estágio TDSP correspondente | Situação no TP3 |
|----------|-----------------------------|-----------------|
| Business Understanding | Business Understanding | Concluído (problema e metas revistos à luz do FastAPI e da avaliação do Selenium) |
| Data Understanding | Data Acquisition & Understanding | Data Summary Report atualizado com a nova coleta de notícias e a avaliação de scraping dinâmico |
| Data Preparation | Data Acquisition & Understanding / Modeling | Limpeza das notícias e geração do corpus para LLM em `Code/DataPrep/preparar_noticias.py`; preparação da base de contratações segue pendente |
| Modeling | Modeling | Planejado (próxima etapa, com LLM) |
| Evaluation | Modeling / Acceptance | Planejado |
| Deployment | Deployment | App Streamlit multipágina (`st.navigation`) integrado à API FastAPI (`Code/API/main.py`), com cache (`st.cache_data`), estado de sessão (`st.session_state`) e testes da API |

O CRISP-DM é iterativo: se a exploração dos dados mostrar que o campo de valor tem
qualidade ruim, volto para a fase de entendimento dos dados e ajusto os indicadores
definidos no charter.

## 4. Ambiente de desenvolvimento (TP3)

- Controle de versão com **Git**, repositório versionado e preparado para publicação
  no GitHub (ver `README.md` para o link do repositório).
- `.gitignore` cobre ambiente virtual, cache do Python e os subdiretórios de `Data/` que
  não devem ser versionados por completo (apenas a amostra, as notícias coletadas e os
  arquivos processados delas ficam versionados como evidência da coleta; as contratações
  enviadas por POST ficam fora).
- `requirements.txt` fixa as versões das bibliotecas usadas (Streamlit, pandas, requests,
  BeautifulSoup, WordCloud, matplotlib, Altair, FastAPI, Uvicorn, pytest).

## 5. Estrutura de diretórios

```
TP3-Projeto-de-Bloco/
├── Code/
│   ├── API/                 # API FastAPI (consulta e envio de dados)
│   ├── DataAcquisition/     # coleta via API (PNCP, esboço) e web scraping (BeautifulSoup)
│   ├── DataPrep/            # limpeza e estatísticas das notícias; corpus para LLM
│   ├── Modeling/            # features, detecção de atípicos e prompts do LLM
│   └── Operationalization/  # acesso do app à API (cache de carregamento)
├── Data/
│   ├── raw/                 # dados como vieram da fonte (notícias CGU versionadas)
│   ├── interim/             # dados em tratamento
│   └── processed/           # base tratada servida pela API
├── Docs/
│   ├── Project/             # project_charter.md, organizacao_projeto.md
│   ├── DataReport/          # data_summary_report.md
│   └── Model/               # preparacao_llm.md
├── Sample_Data/             # amostra de contratações + exemplo de upload
├── app/                     # aplicação Streamlit (app.py + paginas/)
├── notebooks/               # exploração (EDA)
├── tests/                   # testes da API
├── requirements.txt
└── README.md
```
