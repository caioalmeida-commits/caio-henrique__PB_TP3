# Preparação para uso de LLM

## 1. Dados disponíveis

| Dado | Origem | Volume | Tipo | Acesso |
|------|--------|--------|------|--------|
| Notícias da CGU (título, resumo, texto, data, categoria, URL) | Scraping (F4) | 39 notícias, 10.873 palavras de texto | Texto não estruturado + metadados | `Data/processed/corpus_llm.jsonl` e `GET /noticias?incluir_texto=true` |
| Contratações (órgão, modalidade, objeto, valor, fornecedor, data) | Amostra de 20 registros + envios do usuário | 20 registros | Estruturado, com o campo `objeto` em texto curto | `GET /contratacoes` |
| Estatísticas das contratações | Calculadas no app (página Estatísticas e Gráficos) | — | Números agregados | Dados de `GET /contratacoes` |

`corpus_llm.jsonl` tem uma notícia por linha, com os campos `id`, `titulo`, `data_publicacao`,
`categoria`, `url` e `texto`.

## 2. Aplicações com LLM

| Tarefa | Dados de entrada | Saída esperada | Observações |
|--------|------------------|----------------|-------------|
| Resumo automático | `texto` das notícias (1.083 a 3.202 caracteres) | Resumo curto em linguagem simples | O campo `resumo` coletado do site serve de referência para comparar os resumos gerados |
| Classificação de sentimento | `titulo` + `texto` | positivo, negativo ou neutro, com justificativa curta | Não há rótulos prévios; a avaliação depende de uma amostra rotulada manualmente. O conjunto trata em grande parte de operações de fiscalização, então a distribuição tende a ser enviesada para negativo |
| Perguntas e respostas | Corpus de notícias; contratações via API para perguntas numéricas | Resposta com citação da `url` da notícia usada | O modelo só deve responder com base no texto fornecido |
| Geração de texto | Indicadores e estatísticas das contratações | Relatório descritivo em texto corrido | Os números vêm do cálculo do app, e o LLM apenas redige |

## 3. Pontos de integração já prontos

- A API entrega notícias e contratações em JSON, então o componente de LLM pode consumir
  `GET /noticias?incluir_texto=true` e `GET /contratacoes` sem ler arquivos.
- O corpus em JSONL pode ser carregado diretamente em lotes.
- O app é multipágina (`app/paginas/`): uma nova página pode ser registrada em `app/app.py`
  com `st.Page`.
- Os módulos da etapa ficam em `Code/Modeling/` (prompts e chamadas ao modelo).

## 4. Cuidados

- O app sinaliza padrão atípico, não irregularidade: os textos gerados não devem afirmar
  ilegalidade (Project Charter, seção 6).
- As contratações da amostra são ilustrativas; resultados de LLM sobre elas servem apenas
  como demonstração até a coleta real.
- Custo e limite de uso: gerar sob demanda e guardar os resultados para não repetir chamadas.
- Respostas de LLM podem ser imprecisas ou enviesadas e devem ser conferidas com a fonte
  (`url` da notícia ou dado da API).
