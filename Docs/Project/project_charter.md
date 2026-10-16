# Project Charter — Radar da Transparência em Contratações Públicas

**Autor:** Caio
**Etapa:** TP3 — Múltiplas páginas, API FastAPI e preparação para LLM
**Data:** outubro/2026

---

## 1. Problema de negócio

Órgãos públicos brasileiros publicam diariamente milhares de contratações no PNCP
(Portal Nacional de Contratações Públicas) e no Portal da Transparência. Os dados são
abertos, mas ficam espalhados em APIs diferentes, com muitos registros e campos técnicos.
Na prática, quem precisa fiscalizar (cidadão, jornalista, controle interno) não consegue
olhar esse volume manualmente e acaba não identificando contratos com características
atípicas — valores muito acima do padrão do mesmo tipo de objeto, uso recorrente de
dispensa de licitação, ou concentração de contratos em poucos fornecedores.

**Problema:** falta uma ferramenta simples que reúna esses dados, destaque contratações
com padrão fora do comum e explique o achado em linguagem acessível.

### Revisão do problema à luz das novas ferramentas (TP3)

- **FastAPI:** o acesso aos dados deixou de estar dentro do app. A API passou a ser a
  camada de dados (consulta e envio de contratações, consulta de notícias) e o Streamlit
  é apenas um dos consumidores. Isso mantém o problema de negócio, mas separa a coleta
  e o armazenamento da interface e deixa os dados prontos para serem lidos pelo
  componente de LLM da próxima etapa.
- **Selenium:** avaliei as fontes do projeto e concluí que nenhuma exige scraping dinâmico
  (evidência no Data Summary Report, seção 1.1). Mantive BeautifulSoup e APIs, conforme
  a orientação do enunciado.
- **Scraper do TP2:** a listagem de notícias da CGU usada no TP2 mudou de endereço e de
  estrutura HTML, e o scraper deixou de funcionar. Atualizei o scraper e recoletei as
  notícias, agora com o texto completo, que é o insumo das tarefas de LLM.

## 2. Solução proposta

Um dashboard interativo em Python + Streamlit, apoiado por uma API FastAPI, que:

1. coleta contratações públicas via API (PNCP e Portal da Transparência);
2. complementa com dados obtidos por web scraping (BeautifulSoup) — notícias de
   fiscalização e integridade da CGU, com texto completo;
3. disponibiliza os dados por uma API (`GET`/`POST /contratacoes`, `GET /noticias`);
4. calcula indicadores descritivos e sinaliza contratos atípicos (outliers de valor,
   percentual de dispensa/inexigibilidade, concentração por fornecedor);
5. usa um LLM, via engenharia de prompt, para gerar um resumo em linguagem simples de
   cada achado sinalizado e para tarefas sobre o texto das notícias (ver
   `Docs/Model/preparacao_llm.md`).

## 3. Objetivos e metas

| # | Objetivo | Meta (indicador de sucesso) | Status (TP3) |
|---|----------|-----------------------------|---------------|
| O1 | Coletar dados de contratações públicas via API | Pipeline coletando ≥ 5.000 contratações de pelo menos 2 fontes, com execução reproduzível | Não atingido: segue com o esboço `coleta_pncp.py` e a amostra de 20 registros. Reprogramado para as etapas seguintes |
| O2 | Consolidar os dados em uma base limpa | ≥ 95% dos registros com os campos-chave preenchidos (órgão, modalidade, valor, fornecedor, data) | Amostra atual (20 registros) sem nulos nos campos-chave; a API valida os campos obrigatórios nos envios (POST) |
| O3 | Sinalizar contratações atípicas | Regra de detecção implementada e documentada; taxa de sinalização entre 1% e 5% da base | Reprogramado: depende da base real de O1. No app há apenas a sinalização manual |
| O4 | Explicar os achados com LLM | 100% dos contratos sinalizados com resumo gerado automaticamente | Dados preparados no TP3 (`corpus_llm.jsonl` e documento de preparação); implementação na próxima etapa |
| O5 | Entregar o dashboard funcional | App Streamlit rodando com filtros por órgão, período, modalidade e faixa de valor; tempo de resposta < 5s por filtro | Atingido: app multipágina com filtros por modalidade/UF/valor, cache (`st.cache_data`) e estado de sessão, agora lendo os dados pela API |
| O6 | Extrair conteúdo textual da web para enriquecer o app | Scraper com BeautifulSoup salvando CSV/TXT em `Data/raw/`, consumido pelo app | Atingido: scraper atualizado; 39 notícias da CGU com texto completo (08/07/2026 a 14/10/2026) |
| O7 | Permitir upload/download de dados complementares | Usuário envia contratações e baixa a base combinada | Atingido: formulário e CSV enviam os dados pela rota `POST /contratacoes`; download da base completa pela rota `GET /contratacoes` |
| O8 *(novo no TP3)* | Disponibilizar os dados por uma API FastAPI | ≥ 2 rotas (GET e POST) documentadas | Atingido: 3 rotas, documentação no README e em `/docs`, 7 testes automatizados |
| O9 *(novo no TP3)* | Organizar o app em múltiplas páginas com menu de navegação | Cada página com uma funcionalidade distinta | Atingido: 4 páginas com `st.navigation` (Contratações, Estatísticas e Gráficos, Notícias e Nuvem de Palavras, Upload e Download) |
| O10 *(novo no TP3)* | Preparar os dados coletados para tarefas com LLM | Corpus de texto pronto e aplicações mapeadas | Atingido: `Data/processed/corpus_llm.jsonl` (39 textos) e `Docs/Model/preparacao_llm.md` |

## 4. ODS atendido

**ODS 16 — Paz, Justiça e Instituições Eficazes.**

Justificativa: a meta 16.5 trata de reduzir substancialmente a corrupção e o suborno,
a meta 16.6 de desenvolver instituições eficazes, responsáveis e transparentes, e a
meta 16.10 de assegurar o acesso público à informação. O projeto atua exatamente nesse
ponto: pega dado público que já existe mas é pouco utilizável, transforma em informação
navegável e ajuda no controle social do gasto público. As notícias da CGU coletadas no
TP3 tratam de operações de fiscalização com a Polícia Federal (apuração de suspeitas de
fraude e desvio de recursos públicos, por exemplo), o que reforça esse recorte.

**ODS secundário: ODS 12 — Consumo e Produção Responsáveis**, meta 12.7 (promover
práticas de compras públicas sustentáveis), já que a base permite analisar o perfil das
compras dos órgãos.

**Pilar ESG:** Governança (G).

## 5. Público-alvo

- **Primário:** cidadãos, jornalistas de dados e organizações de controle social que
  querem acompanhar gastos públicos sem precisar programar.
- **Secundário:** servidores de controle interno e auditoria, que podem usar a
  sinalização como triagem inicial.
- **Terciário:** estudantes e pesquisadores de dados abertos governamentais.

## 6. Escopo

**Dentro do escopo**
- Contratações publicadas no PNCP a partir de 2023.
- Coleta via API, tratamento, indicadores descritivos, detecção estatística de outliers.
- Notícias de integridade/fiscalização (CGU) coletadas via web scraping, com texto
  completo, para contexto qualitativo (nuvem de palavras, estatísticas por categoria) e
  para as tarefas de LLM.
- API FastAPI para consulta e envio de dados.
- Dashboard Streamlit multipágina com filtros, estado de sessão e upload/download de dados.

**Fora do escopo**
- Afirmar que um contrato é irregular ou fraudulento (o app sinaliza padrão atípico, não ilegalidade).
- Dados de estados/municípios que não publicam no PNCP.
- Modelo supervisionado de fraude (não há base rotulada disponível).

## 7. Stakeholders

| Stakeholder | Papel | Interesse |
|-------------|-------|-----------|
| Caio (aluno) | Project Lead, Data Scientist, Solution Architect | Desenvolver e entregar o projeto |
| Professor/orientador | Sponsor e avaliador | Avaliar o cumprimento dos requisitos das entregas |
| Usuário final (cidadão/jornalista) | Usuário | Consultar e entender os gastos públicos |
| PNCP / Portal da Transparência / CGU | Provedores de dados | Disponibilizar as APIs e páginas públicas usadas na coleta |

## 8. Riscos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Instabilidade ou limite de requisições nas APIs públicas | Alto | Cache local dos dados em `Data/raw`, coleta paginada com retry |
| Campos ausentes ou inconsistentes entre fontes | Médio | Etapa de padronização em `Code/DataPrep` e relatório de qualidade |
| Mudança de endereço ou de layout das páginas raspadas *(ocorreu no TP3: a listagem da CGU do TP2 deixou de funcionar)* | Médio | Scraper atualizado com seletores da estrutura atual, pausa entre requisições, aviso de erro quando nenhuma notícia é encontrada e dados coletados versionados em `Data/raw/` |
| App depende da API local estar no ar | Médio | O app verifica a API ao abrir cada página e mostra o comando para iniciá-la |
| Custo/limite de uso do LLM | Médio | Gerar resumo só sob demanda, apenas para contratos sinalizados |
| Interpretação equivocada dos achados pelo usuário | Alto | Aviso explícito no app de que sinalização ≠ irregularidade |

## 9. Cronograma por entrega

| Entrega | Foco | Estágio TDSP | Status |
|---------|------|--------------|--------|
| TP1 | Proposta, charter, estrutura de diretórios, demo Streamlit | Business Understanding / início de Data Acquisition | Concluído |
| TP2 | Ambiente de dev, interface interativa, scraping com BeautifulSoup, cache/estado de sessão, upload/download, Data Summary Report | Data Acquisition & Understanding | Concluído |
| TP3 | App multipágina com menu, API FastAPI, scraper atualizado, revisão da documentação e preparação para LLM | Data Acquisition & Understanding / Deployment | Concluído |
| TP4 | Integração com LLM (resumo, classificação de sentimento, perguntas e respostas ou geração de texto) | Modeling | Planejado |
| Etapas seguintes | Coleta em massa via API do PNCP e detecção de outliers (O1 e O3); dashboard final e apresentação | Modeling / Deployment / Acceptance | Planejado |

## 10. Critério de aceite

O projeto é considerado bem-sucedido se, ao final, o dashboard permitir que um usuário
sem conhecimento técnico filtre contratações públicas, visualize os indicadores, leia
uma explicação automática dos contratos sinalizados como atípicos, acompanhe notícias
relacionadas ao tema e complemente a base com seus próprios dados, tudo servido por uma
API documentada.
