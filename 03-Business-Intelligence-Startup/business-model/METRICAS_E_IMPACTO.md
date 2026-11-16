# Métricas e impacto — AcessaCidade

> Este documento **define** as métricas e **como medi-las**. Nenhum valor real de impacto foi medido até agora.
> Os números que aparecem no painel do MVP vêm, em grande parte, de **dados simulados** (identificados como
> `simulado=true` / `origem=SIMULADO`, cidade fictícia "Cidade Exemplo") e **não podem** ser apresentados como impacto.
> Resultados reais entram somente depois dos testes: `[PREENCHER: resultados reais]`.

## 1. Três famílias de métricas

| Família | Pergunta que responde | Quem usa |
|---|---|---|
| **Produto** | O sistema está funcionando e sendo usado como planejado? | Equipe |
| **Negócio** | A startup é sustentável? | Equipe, investidores |
| **Impacto** | A vida do cidadão melhorou? | Cidadão, cliente, banca, sociedade |

## 2. Métricas de produto e operação

Legenda de disponibilidade: **MVP** = calculável hoje com o que o MVP expõe · **Extensão** = precisa de evolução do produto.

| Métrica | Fórmula | Fonte | Disponível |
|---|---|---|---|
| Denúncias registradas | contagem de denúncias | `GET /api/indicadores` → `total` | MVP |
| % de denúncias com foto analisada | (`total` − `sem_imagem`) ÷ `total` | `GET /api/indicadores` | MVP |
| Distribuição do resultado da triagem | contagem por `visao.classificacao` | `por_resultado_visao` (API) · `resultado_visao` (Gold) | MVP |
| Tempo médio de triagem automática | `acessacidade_visao_duracao_seconds_sum` ÷ `acessacidade_visao_duracao_seconds_count` | `GET /metrics` (Prometheus/Grafana — disciplina 06) | MVP |
| % de denúncias revisadas por humano | denúncias com `revisao_humana` ≠ nulo ÷ denúncias com foto | coluna `revisao_humana` da exportação `GET /api/export/denuncias` (token do pipeline) | MVP (cálculo manual/pipeline); não aparece no painel no contrato atual |
| % de triagens confirmadas pela revisão | `revisao_humana = CONFIRMADO` ÷ revisadas, por classificação | exportação | MVP (cálculo manual) — **não é acurácia do modelo**, é concordância observada em amostra não controlada |
| Tempo até encaminhamento | data do histórico com status `ENCAMINHADA` − `criado_em` (mediana) | `historico` em `GET /api/denuncias/{ref}` | Extensão: o histórico existe por denúncia, mas não há agregado nem coluna na exportação |
| Denúncias por bairro / categoria / status / dia | contagens | `por_bairro`, `por_categoria`, `por_status`, `por_dia` (API) · Gold | MVP |
| Denúncias por origem (WEB, RPA, API, SIMULADO) | contagem por `origem` | `por_origem` (API) | MVP |
| Respostas do assistente por fonte (LLM × regras) | contagem por `fonte` | `/metrics` → `acessacidade_assistente_respostas_total` | MVP |
| Qualidade dos dados do pipeline | `percentual_registros_validos`, duplicatas, datas e coordenadas inválidas | `GET /api/indicadores/analiticos` → `qualidade` | MVP |
| Disponibilidade e latência | 4 sinais de ouro | `/metrics` + Grafana (disciplina 06) | MVP |
| Cidadãos ativos (proxy) | denúncias com `origem=WEB` por mês | API / Gold | MVP como **proxy**: o MVP não tem login (decisão de privacidade), então não conta pessoas únicas |

## 3. Métricas de negócio

| Métrica | Fórmula | Fonte |
|---|---|---|
| Clientes pagantes | contratos ativos | controle comercial (fora do MVP) |
| MRR (receita recorrente mensal) | Σ assinaturas mensais ativas | financeiro |
| Churn | contratos cancelados no período ÷ ativos no início | financeiro |
| CAC | gasto comercial ÷ novos clientes | financeiro |
| Margem de contribuição por cliente | ticket médio − custo variável por cliente | `MODELO_FINANCEIRO_HIPOTETICO.xlsx` |
| Ponto de equilíbrio | custo fixo ÷ margem de contribuição | idem (hoje: 24 municípios no cenário hipotético) |
| Conversão piloto → contrato | pilotos convertidos ÷ pilotos concluídos | controle comercial |

## 4. Métricas de impacto no cidadão — e como medir antes/depois

| Indicador de impacto | Antes (linha de base) | Depois | Método |
|---|---|---|---|
| **Tempo para registrar um problema** | Tempo no canal que a pessoa usa hoje (156, site/app da prefeitura, rede social) | Tempo no AcessaCidade, da página inicial até o protocolo | Teste de usabilidade cronometrado (`pitch/ROTEIRO_TESTE_USABILIDADE.md`), mesma pessoa, mesmo problema descrito |
| **Etapas até registrar** | Nº de telas/ligações/perguntas no canal atual | Nº de telas no AcessaCidade | Observação no teste |
| **Conclusão sem ajuda** | — | % de participantes que concluem cada tarefa sem ajuda | Teste de usabilidade |
| **Facilidade percebida (SUS)** | — | Pontuação SUS 0–100 | Questionário após o teste |
| **Saber o andamento** | A pessoa sabe o que aconteceu com a última reclamação que fez? (sim/não) | Consegue ver o status pelo protocolo? (sim/não) | Pergunta no teste |
| **Tempo até encaminhamento** (piloto real) | Tempo médio informado pelo município antes do piloto | Mediana medida no AcessaCidade | Piloto com cliente (futuro) |
| **Barreiras resolvidas por bairro** (piloto real) | Contagem antes do piloto | Contagem registrada ao fim | Piloto com cliente (futuro) — "Resolvida" é registro da equipe, não confirmação oficial |

Cuidados de método (obrigatórios):

- **Não enviar denúncias falsas a canais oficiais** para medir o "antes". Cronometrar até a etapa anterior ao envio,
  ou usar um problema real observado pela própria pessoa, com autorização dela.
- Registrar **quantas pessoas** participaram e **qual o perfil** (sem nomes). Amostra pequena é aceitável no MVP,
  mas deve ser declarada ("5 participantes, não representativos").
- Testes com colegas ou membros da equipe **não** contam como testes com o público-alvo — marcar na planilha.
- Registro em `pitch/registro_testes_usuarios_TEMPLATE.xlsx` (salvar uma cópia preenchida, por exemplo
  `pitch/evidencias/registro_testes_usuarios.xlsx`, **sem dados pessoais**).

Resultados medidos: `[PREENCHER: tempo médio antes × depois, taxa de conclusão, SUS médio, nº e perfil dos participantes]`.

## 5. Como o impacto escala

- Cada município novo multiplica a base de barreiras mapeadas e os dados para planejamento (ODS 11.3 e 11.7).
- Dados agregados e anonimizados por bairro podem orientar orçamento de calçadas e rotas acessíveis.
- O mesmo fluxo atende outras categorias de zeladoria, ampliando o público beneficiado.

## 6. Ligação com os ODS

| ODS / meta | Como a métrica evidencia a contribuição |
|---|---|
| **ODS 11 — meta 11.7** (acesso universal a espaços públicos seguros, inclusivos e acessíveis, em particular para idosos e pessoas com deficiência) | Barreiras registradas, triadas e acompanhadas por bairro; tempo até encaminhamento |
| **ODS 11 — meta 11.2** (transporte seguro e acessível, com atenção às pessoas com deficiência e idosos) | Barreiras em rotas a pé até pontos de transporte (campo ponto de referência) |
| **ODS 11 — meta 11.3** (urbanização inclusiva e planejamento participativo) | Denúncias como participação cidadã; painel por bairro para planejamento |
| **ODS 10 — meta 10.2** (inclusão social independentemente de deficiência ou idade) | Conclusão sem ajuda e SUS de pessoas com deficiência e idosos no teste |
| **ODS 9 — meta 9.1** (infraestrutura de qualidade, confiável e acessível para todos) | Denúncias por categoria de infraestrutura (calçada, rampa, piso tátil) e evolução no tempo |
