# Radar da Transparência em Contratações Públicas

Projeto de Bloco — **TP3**
Pilar ESG: **Governança** | **ODS 16** — Paz, Justiça e Instituições Eficazes

Repositório no GitHub: **https://github.com/caioalmeida-commits/caio-henrique__PB_TP3**

## Entregas do TP3

- Aplicação Streamlit com 4 páginas e menu de navegação (`st.navigation`), em [`app/`](app/)
- API FastAPI com rotas GET e POST, consumida pelo app — [`Code/API/main.py`](Code/API/main.py)
- Scraper das notícias da CGU atualizado (BeautifulSoup): 39 notícias com texto completo em `Data/raw/`
- Avaliação do Selenium: não foi necessário (justificativa no [Data Summary Report](Docs/DataReport/data_summary_report.md), seção 1.1)
- [Project Charter](Docs/Project/project_charter.md) e [Data Summary Report](Docs/DataReport/data_summary_report.md) revisados
- Preparação para LLM: [`Docs/Model/preparacao_llm.md`](Docs/Model/preparacao_llm.md) e `Data/processed/corpus_llm.jsonl`

## Estrutura

```
├── Code/
│   ├── API/                 # API FastAPI
│   ├── DataAcquisition/     # scraping (BeautifulSoup) e esboço da coleta PNCP
│   ├── DataPrep/            # limpeza das notícias e corpus para LLM
│   ├── Modeling/
│   └── Operationalization/  # acesso do app à API (utils.py)
├── Data/                    # raw, interim, processed
├── Docs/                    # Project, DataReport, Model
├── Sample_Data/             # amostra de contratações e exemplo de upload
├── app/                     # app Streamlit (app.py + paginas/)
├── tests/                   # testes da API
├── requirements.txt
└── README.md
```

## Ambiente

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Executar

A API precisa estar no ar antes do app. Em dois terminais, na raiz do projeto:

```bash
uvicorn Code.API.main:app --reload
```

```bash
streamlit run app/app.py
```

- App: http://localhost:8501
- Documentação interativa da API (Swagger): http://127.0.0.1:8000/docs

Páginas do app (menu lateral):

| Página | Função |
|--------|--------|
| Contratações | Tabela com filtros, sinalização para revisão (estado de sessão) e download |
| Estatísticas e Gráficos | Indicadores e gráficos interativos (Altair) |
| Notícias e Nuvem de Palavras | Notícias da CGU, filtros, gráfico por categoria e nuvem de palavras |
| Upload e Download | Envio de contratação por formulário ou CSV (POST) e download da base |

## API

| Método | Rota | Função |
|--------|------|--------|
| GET | `/contratacoes` | Lista contratações (amostra + enviadas). Filtros opcionais: `modalidade`, `uf`, `valor_min`, `valor_max`, `limite` (padrão 100, máximo 1000) |
| POST | `/contratacoes` | Adiciona uma contratação. Retorna `201` com o registro, `409` se o `id_contratacao` já existir e `422` se os dados forem inválidos |
| GET | `/noticias` | Lista as notícias da CGU coletadas. Filtros opcionais: `categoria`, `limite`; `incluir_texto=true` inclui o texto completo |

Exemplos:

```bash
curl "http://127.0.0.1:8000/contratacoes?uf=DF&modalidade=Dispensa&valor_min=500000"
```

```bash
curl -X POST http://127.0.0.1:8000/contratacoes -H "Content-Type: application/json" -d '{"id_contratacao":"PNCP-2025-000301","data_publicacao":"2025-03-01","orgao":"Ministério da Saúde","uf":"DF","municipio":"Brasília","modalidade":"Dispensa","objeto":"Aquisição de insumos","valor_estimado":150000.0,"fornecedor":"Fornecedor Exemplo Ltda","cnpj_fornecedor":"12.345.678/0001-90"}'
```

```bash
curl "http://127.0.0.1:8000/noticias?categoria=INVESTIGA%C3%87%C3%83O&incluir_texto=true&limite=3"
```

As contratações enviadas por POST são gravadas em `Data/processed/contratacoes_enviadas.csv` (fora do versionamento).

## Coleta e preparação dos dados

```bash
python Code/DataAcquisition/scraping_noticias_cgu.py   # -> Data/raw/noticias_cgu.csv, .txt
python Code/DataPrep/preparar_noticias.py              # -> Data/processed/
```

## Testes

```bash
pytest
```

## Uso de IA

Ferramenta: Claude (Anthropic), modelo Claude Sonnet 5.5, via Claude Code.

Uso neste trabalho: escrita do código do scraper, da API FastAPI, das páginas do Streamlit e dos testes; redação e atualização da documentação; verificação das páginas e das APIs usadas na coleta.

Páginas e APIs consultadas durante a verificação:
- https://www.gov.br/cgu/pt-br e https://www.gov.br/cgu/pt-br/assuntos/noticias/2026/defeso-eleitoral (listagem e páginas das notícias)
- https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao
- https://portaldatransparencia.gov.br/sancoes/ceis
