# Data Summary Report

**Projeto:** Radar da Transparência em Contratações Públicas
**Etapa:** TP3
**Status:** amostra de contratações (fictícia/ilustrativa, herdada do TP1) e notícias da CGU
recoletadas por web scraping, agora com o texto completo. Os dados são servidos por uma API
FastAPI. A coleta em massa via API do PNCP não foi feita neste TP (ver Project Charter, O1).

---

## 1. Fontes de dados

| # | Fonte | Forma de acesso | Tipo de dado | Objetivo de uso no projeto | Status |
|---|-------|-----------------|--------------|----------------------------|--------|
| F1 | PNCP — Portal Nacional de Contratações Públicas (`pncp.gov.br/api/consulta`) | API REST pública, JSON, sem autenticação | Estruturado: contratações por data de publicação (órgão, modalidade, objeto, valor estimado, situação) | Base principal do dashboard: volume, valores e modalidades das contratações | Esboço do coletor pronto (`Code/DataAcquisition/coleta_pncp.py`). Testada no TP3: resposta HTTP 200 com paginação (11.003 registros da modalidade 6 entre 01/09/2026 e 10/09/2026). Coleta em massa ainda não realizada |
| F2 | Portal da Transparência do Governo Federal (`api.portaldatransparencia.gov.br`) | API REST, JSON, requer chave de API gratuita | Estruturado: contratos, licitações, fornecedores, órgãos | Complementar F1 com dados de execução e de fornecedor (CNPJ, situação) | Planejado |
| F3 | Dados Abertos Compras.gov.br (`dadosabertos.compras.gov.br`) | API REST, JSON | Estruturado: itens de contratação, catálogo de materiais/serviços | Padronizar o objeto contratado para comparar preços entre contratos semelhantes | Planejado |
| F4 | **CGU — Notícias** (`gov.br/cgu/pt-br/assuntos/noticias/2026/defeso-eleitoral`) | Web scraping (BeautifulSoup + requests), com paginação e leitura de cada notícia | Semiestruturado: HTML → título, data, categoria, resumo, URL e texto completo | Contexto qualitativo (nuvem de palavras, contagem por categoria, tabela no app) e corpus para as tarefas de LLM | **Recoletado no TP3** — 39 notícias em `Data/raw/noticias_cgu.csv` e `Data/raw/noticias_cgu.txt` |
| F5 | IBGE — Localidades (`servicodados.ibge.gov.br/api/v1/localidades`) | API REST, JSON | Estruturado: municípios, UFs, códigos | Enriquecer os registros com UF/região para os filtros geográficos | Planejado |
| F6 | Envios do usuário (formulário e CSV) | `POST /contratacoes` da API FastAPI, a partir da página Upload e Download | Estruturado: mesmo esquema da amostra de contratações | Permitir que o usuário complemente a base com dados próprios | **Implementado no TP3** — gravados em `Data/processed/contratacoes_enviadas.csv` |
| F7 | LLM (API de modelo de linguagem) | API, engenharia de prompt | Texto gerado | Resumo, classificação de sentimento, perguntas e respostas e geração de texto | Dados preparados no TP3 (`Docs/Model/preparacao_llm.md`); integração na próxima etapa |

### 1.1 Avaliação de scraping dinâmico (Selenium)

Testei com requests (HTML estático) e com Selenium (Chrome headless, HTML renderizado) as
páginas que o projeto usa ou poderia usar:

| Página | HTML estático | HTML renderizado (Selenium) | Conclusão |
|--------|---------------|-----------------------------|-----------|
| Listagem de notícias da CGU (`/assuntos/noticias/2026/defeso-eleitoral`) | 30 links de notícia; paginação por `?b_start:int=30` no HTML | 30 links de notícia; mesma paginação | Conteúdo estático: Selenium não é necessário |
| Notícia da CGU (página individual) | Texto completo em `#parent-fieldname-text` | — | Conteúdo estático |
| PNCP (`/api/consulta/v1/contratacoes/publicacao`) | API JSON, HTTP 200 | — | Coleta por API |
| Portal da Transparência (`/sancoes/ceis`) | Requisição direta retornou HTTP 405 e a página referencia captcha | — | Não usada |

Como nenhuma fonte exige interação com elementos dinâmicos, mantive BeautifulSoup e APIs,
conforme a observação do enunciado.

Outra constatação da avaliação: a listagem usada no TP2 (`/assuntos/noticias`) passou a
redirecionar (HTTP 302) para uma tela de login, e as notícias passaram a ficar em
`/assuntos/noticias/2026/defeso-eleitoral`, com outra estrutura HTML. O scraper foi
atualizado para essa estrutura.

## 2. Campos-chave

**Contratações (F1/F2/F3/F6 — `Sample_Data/amostra_contratacoes.csv`)**

| Campo | Tipo | Uso |
|-------|------|-----|
| `id_contratacao` | texto | Chave do registro (a API rejeita repetidos com HTTP 409) |
| `orgao` | texto | Filtro e agregação por órgão |
| `uf` / `municipio` | texto | Filtro geográfico (a API converte a UF para maiúsculas) |
| `modalidade` | categórico | Análise de dispensa/inexigibilidade |
| `objeto` | texto | Agrupar contratos comparáveis |
| `valor_estimado` | numérico | Indicadores e detecção de outliers (a API exige valor maior que zero) |
| `fornecedor` / `cnpj_fornecedor` | texto | Concentração de contratos |
| `data_publicacao` | data | Séries temporais e filtro de período |

**Notícias (F4 — `Data/raw/noticias_cgu.csv` → `Data/processed/noticias_limpas.csv`)**

| Campo | Tipo | Uso |
|-------|------|-----|
| `id` | inteiro | Identificador gerado em `Code/DataPrep/preparar_noticias.py` (ordem da data mais recente para a mais antiga) |
| `titulo` | texto | Exibição na tabela |
| `titulo_limpo` | texto | Título sem stopwords/pontuação, usado na nuvem de palavras |
| `data_publicacao` | data | Filtro de período |
| `categoria` | categórico | "Chapéu" exibido acima do título; em muitas notícias é o nome da operação (ex.: OPERAÇÃO RES PUBLICA). Valores ausentes viram "Sem categoria" |
| `resumo` | texto | Linha de apoio exibida na listagem |
| `url` | texto (link) | Acesso à notícia original e citação de fonte |
| `texto` | texto | Texto completo da notícia, insumo das tarefas de LLM |

## 3. Qualidade dos dados

**Amostra de contratações** (`Sample_Data/amostra_contratacoes.csv`, 20 registros, dados
fictícios/ilustrativos com o mesmo esquema que a coleta real via API terá):

- 0% de valores nulos em qualquer campo-chave (`orgao`, `modalidade`, `valor_estimado`,
  `fornecedor`, `data_publicacao`) — 100% de preenchimento, acima da meta de 95% do charter.
- Período coberto: 06/01/2025 a 17/01/2025 (12 dias).
- 8 órgãos distintos, 8 UFs distintas (BA, CE, DF, MG, PR, RJ, RS, SP).
- Nenhuma duplicidade de `id_contratacao`.
- Ponto de atenção para a coleta real: duplicidade de registros entre PNCP e Portal da
  Transparência, padronização de nomes de órgãos e fornecedores, e datas fora do período
  consultado.

**Notícias CGU** (`Data/raw/noticias_cgu.csv`, 39 registros, coleta real via scraping em
16/10/2026):

- 0% de nulos em `titulo`, `data_publicacao`, `resumo`, `url` e `texto`; 1 nulo em
  `categoria` (2,6%), tratado como "Sem categoria".
- Período coberto: 08/07/2026 a 14/10/2026 (99 dias), com 9 notícias em julho, 9 em
  agosto, 12 em setembro e 9 em outubro.
- A coleta cobre toda a listagem disponível no momento (2 páginas: 30 + 9 notícias).
- 32 categorias distintas no dado bruto (33 no processado, com "Sem categoria"), sem
  concentração forte: a mais frequente é INVESTIGAÇÃO, com 6 notícias.
- Nenhuma URL duplicada.
- Limitação: `categoria` é o chapéu da notícia, e não uma classificação temática; por isso
  há muitas categorias com uma única notícia.

## 4. Estatísticas descritivas

**Contratações**

| Métrica | Valor |
|---|---|
| Registros | 20 |
| Valor total estimado | R$ 25.184.200,50 |
| Valor médio | R$ 1.259.210,03 |
| Valor mediano | R$ 739.250,00 |
| Valor mínimo / máximo | R$ 45.300,50 / R$ 5.400.000,00 |
| Modalidade mais frequente | Pregão Eletrônico (10 de 20 registros) |
| Distribuição por modalidade | Pregão Eletrônico: 10, Dispensa: 6, Inexigibilidade: 2, Concorrência: 2 |

**Notícias CGU**

| Métrica | Valor |
|---|---|
| Registros | 39 |
| Categorias distintas (processado) | 33 |
| Categoria mais frequente | INVESTIGAÇÃO (6 de 39 notícias) |
| Texto das notícias | 10.873 palavras no total; média de 278 palavras (1.854 caracteres) por notícia; mínimo de 1.083 e máximo de 3.202 caracteres |
| Palavras mais frequentes nos títulos (top 7, sem stopwords) | apuram (17), recursos (15), públicos (13), suspeitas (11), investigam (10), fraudes (10), desvio (10) |

As tabelas acima também estão calculadas em `Data/processed/estatisticas_noticias.csv`
(contagem por categoria) e são recalculadas dinamicamente no app a partir dos filtros
escolhidos pelo usuário (páginas Estatísticas e Gráficos e Notícias e Nuvem de Palavras).

## 5. Pipeline de dados (TP3)

```
Code/DataAcquisition/scraping_noticias_cgu.py  →  Data/raw/noticias_cgu.csv, .txt
Code/DataPrep/preparar_noticias.py             →  Data/processed/noticias_limpas.csv,
                                                  estatisticas_noticias.csv, corpus_llm.jsonl

Sample_Data/amostra_contratacoes.csv  ┐
Data/processed/noticias_limpas.csv    ├→  Code/API/main.py (FastAPI)  →  app/ (Streamlit)
Data/processed/contratacoes_enviadas.csv ┘            ↑
                                            POST /contratacoes (formulário e CSV do app)
```

Os scripts de coleta e preparação rodam separadamente (fora do Streamlit). O app não lê
os arquivos diretamente: consulta e envia dados pela API.
