# Modelo de negócio — AcessaCidade

> **Natureza deste documento.** Os valores de preço, custo, mix de clientes e rampa de vendas são **hipóteses
> declaradas** pela equipe para mostrar que "a conta fecha" sob premissas explícitas. Nenhum valor aqui foi validado
> com cliente e nenhuma parceria ou contrato existe. Quando a equipe obtiver evidência (CP1, entrevistas, testes),
> atualize o texto e o status no Lean Canvas (`lean_canvas.json`).
>
> Documentos complementares: `LEAN_CANVAS.md` (9 blocos e status de validação), `ESTRATEGIA_DE_PRECO.md`
> (planos e lógica de preço), `METRICAS_E_IMPACTO.md` (métricas e medição antes/depois),
> `MODELO_FINANCEIRO_HIPOTETICO.xlsx` (todas as contas em fórmulas do Excel).

---

## 1. Resumo em uma frase

O AcessaCidade é uma plataforma de zeladoria colaborativa focada em acessibilidade: **o cidadão registra
gratuitamente** uma barreira na calçada (com foto opcional) e acompanha pelo protocolo; **quem precisa resolver**
(prefeituras, concessionárias e administradoras de grandes áreas) **paga uma assinatura** para receber essas
denúncias padronizadas, triadas por visão computacional, revisadas por pessoas e organizadas em painel.

## 2. Quem usa × quem paga

| Papel | Quem é | O que ganha | Paga? |
|---|---|---|---|
| **Usuário final** | Pessoas com deficiência, cadeirantes, pessoas cegas ou com baixa visão, idosos, pessoas com mobilidade reduzida, cuidadores | Registrar o problema em poucos minutos, de qualquer celular, sem instalar app, e acompanhar pelo protocolo; assistente em linguagem simples | **Nunca** |
| **Cliente pagante B2G** | Prefeituras — secretarias de zeladoria/serviços urbanos, obras, mobilidade, pessoa com deficiência | Denúncias padronizadas e priorizáveis por impacto, foto triada e explicada, painel por bairro e categoria, exportação de dados | Sim (assinatura SaaS) |
| **Cliente pagante B2B** | Concessionárias de serviços (água, energia, gás, telecom) que intervêm nas calçadas | Saber onde suas obras deixaram barreiras; integração via API | Sim (assinatura por volume) |
| **Cliente pagante B2B** | Administradoras de grandes áreas (shoppings, campi universitários, condomínios, parques) | Canal de acessibilidade para o público da área, com painel próprio | Sim (assinatura por área) |
| **Parceiro social** | ONGs e associações de pessoas com deficiência | Ferramenta para organizar o mapeamento que já fazem à mão e cobrar soluções com dados | Plano institucional simbólico ou patrocinado |

Princípio inegociável: **o cidadão nunca paga** e nunca precisa criar conta. O nome é opcional e nunca é exibido nem exportado.

## 3. Proposta de valor por segmento

| Segmento | Dor (hipótese) | Ganho entregue pelo MVP | Funcionalidade que comprova |
|---|---|---|---|
| Cidadão PcD / idoso | Canal atual demorado, pouco acessível, sem retorno | Registro rápido com protocolo; acompanhamento com histórico; explicação em linguagem simples | `#/registrar`, `#/denuncia/{protocolo}`, `#/consultar`, `#/assistente` |
| Prefeitura (zeladoria) | Denúncias sem padrão, sem foto organizada, triagem manual | Campos padronizados (tipo, impacto, bairro), triagem automática da foto com etapas visíveis e revisão humana | `POST /api/denuncias`, triagem OpenCV, `#/revisao` |
| Prefeitura (gestão/planejamento) | Falta de dados para priorizar bairros e orçar | Painel operacional e analítico (pipeline Raw → Bronze → Silver → Gold) | `#/painel`, `GET /api/indicadores`, `GET /api/indicadores/analiticos` |
| Concessionárias | Não sabem onde deixaram calçadas danificadas | Denúncias por localização e categoria; exportação para integração | `GET /api/export/denuncias` (token) — base para a futura API comercial |
| Administradoras de grandes áreas | Reclamações dispersas (SAC, redes sociais) | Canal único de acessibilidade com QR Code no local (a testar) e painel | Mesmo fluxo do cidadão + painel |
| ONGs e associações | Mapeamento manual em planilhas | Registro padronizado e dados agregados para incidência política | Formulário + robô RPA que lança denúncias de planilhas |

## 4. Canais de aquisição

### 4.1 Usuários (cidadãos)

- **Associações e coletivos de pessoas com deficiência** — principal canal hipotético; também fonte de usuários para testes.
- **QR Code em pontos de grande circulação** (pontos de ônibus, entradas de shopping/campus) — a testar.
- **Redes sociais e imprensa local**; boca a boca entre cuidadores e familiares.
- **O próprio site** é o canal: funciona em celulares de entrada, sem instalar aplicativo.

### 4.2 Pagantes B2G (prefeituras)

- **Chamamentos públicos e programas de inovação aberta** de municípios e estados — caminho mais comum para startups chegarem ao setor público.
- **CPSI — Contrato Público para Solução Inovadora**, previsto no Marco Legal das Startups
  (**Lei Complementar nº 182/2021**), que permite à administração pública testar soluções inovadoras com
  contratação simplificada. É um **caminho possível**, não um contrato existente: a equipe não tem nenhum CPSI firmado.
- **Licitação/contratação regular** (Lei nº 14.133/2021) após um piloto com indicadores.
- **Eventos de cidades inteligentes e gestão pública**; apresentação a secretarias da pessoa com deficiência.
- **Piloto de 90 dias com indicadores** (ver plano Piloto em `ESTRATEGIA_DE_PRECO.md`) como porta de entrada.

### 4.3 Pagantes B2B

- **Venda consultiva** a concessionárias e administradoras (contato direto com áreas de relacionamento, sustentabilidade, ESG e acessibilidade).
- **Indicação** de clientes municipais (concessionárias que atuam no mesmo município).

## 5. Fontes de receita

| Fonte | Como funciona | Status |
|---|---|---|
| **Assinatura SaaS municipal** | Valor mensal (contrato anual) por município, por **faixa de população** | Hipótese |
| **Módulo Painel/BI avançado** | Acréscimo sobre a assinatura: painel analítico, exportação para BI, relatórios por bairro | Hipótese |
| **Implantação e treinamento** | Pagamento único: configuração, treinamento das equipes, divulgação inicial | Hipótese |
| **API para concessionárias** | Assinatura mensal por concessionária e por município atendido | Hipótese |
| **Plano grandes áreas** | Assinatura mensal por área (shopping, campus, condomínio) | Hipótese |
| **Plano institucional (ONGs)** | Gratuito ou simbólico; custo coberto por patrocínio ou pelos clientes pagantes | Hipótese |

O cidadão **nunca** é fonte de receita. Venda de dados pessoais **não** é fonte de receita (LGPD e confiança):
dados abertos, quando houver, são **agregados e anonimizados**.

## 6. Estratégia de preço (resumo — detalhes em `ESTRATEGIA_DE_PRECO.md`)

**Todos os valores abaixo são HIPOTÉTICOS, a validar com clientes.** Lógica: preço por faixa de população
(proxy de volume de denúncias e de capacidade orçamentária), contrato anual, piloto como porta de entrada.

| Plano (HIPOTÉTICO) | Para quem | Preço hipotético |
|---|---|---|
| Piloto 90 dias | Município, 1 a 3 bairros | R$ 6.000 (pagamento único) |
| Município P | até 50 mil habitantes | R$ 1.200/mês |
| Município M | 50 mil a 200 mil habitantes | R$ 2.800/mês |
| Município G | 200 mil a 1 milhão de habitantes | R$ 6.500/mês |
| Município GG | acima de 1 milhão de habitantes | sob proposta (a partir de R$ 14.000/mês) |
| Módulo Painel/BI avançado | qualquer plano municipal | + 25% da assinatura |
| Implantação e treinamento | P e M / G / GG | R$ 5.000 / R$ 15.000 / sob proposta |
| API concessionárias | por concessionária e município | R$ 1.900/mês |
| Grandes áreas | por área | R$ 450/mês |
| Institucional (ONGs) | associações sem fins lucrativos | R$ 0 |

## 7. Estrutura de custos estimada (premissas)

| Item | Premissa mensal | Observação |
|---|---|---|
| Equipe | R$ 48.000 | 4 pessoas × R$ 12.000 de custo total com encargos (premissa) |
| Nuvem e monitoramento — base | R$ 2.000 | Container, registro de imagens, armazenamento, monitoramento. **Conferir na calculadora de preços do provedor** (o PDF da disciplina 06 traz a estimativa de custo da infraestrutura do MVP: `[PREENCHER: valor da estimativa de custo da disciplina 06]`) |
| Jurídico, contabilidade, LGPD, ferramentas | R$ 3.000 | Premissa |
| Comercial, eventos e deslocamentos | R$ 2.000 | Premissa |
| **Custo fixo total** | **R$ 55.000** | |
| Nuvem variável por cliente | R$ 120 | Fotos e processamento (premissa) |
| LLM por cliente | R$ 60 | Assistente via OpenRouter (modelo padrão configurável `openai/gpt-4o-mini`); o modo por regras funciona sem custo de API (premissa) |
| Suporte por cliente | R$ 270 | Premissa |
| **Custo variável por cliente** | **R$ 450** | |

## 8. A conta fecha? (ponto de equilíbrio com premissas declaradas)

Premissas adicionais (hipóteses): mix de clientes municipais 50% P, 35% M, 15% G; 30% contratam o módulo
Painel/BI (+25%); receita de implantação **não** entra no cálculo (visão conservadora); primeiro contrato no
mês 6 e 2 novos municípios por mês depois disso.

| Passo | Conta | Resultado |
|---|---|---|
| Ticket médio sem BI | 0,50 × 1.200 + 0,35 × 2.800 + 0,15 × 6.500 | R$ 2.555/mês |
| Ticket médio com BI | 2.555 × (1 + 0,30 × 0,25) | ≈ R$ 2.747/mês |
| Margem de contribuição por cliente | 2.747 − 450 | ≈ R$ 2.297/mês |
| **Ponto de equilíbrio** | 55.000 ÷ 2.297 | **24 municípios** (arredondado para cima) |
| Mês em que o resultado mensal fica positivo | rampa: 2 novos/mês a partir do mês 6 | mês 17 |
| Necessidade de caixa até o equilíbrio | soma dos resultados negativos | ≈ R$ 577 mil |
| Caixa acumulado volta a ficar positivo | projeção de 36 meses | mês 33 |

Leitura honesta:

- **24 municípios** equivalem a cerca de 0,4% dos **5.570 municípios brasileiros** (IBGE — conferir a fonte antes de usar no pitch).
  O número é alcançável em tese, mas o **ciclo de venda pública é longo**: por isso a rampa só começa no mês 6.
- Clientes B2B (concessionárias a R$ 1.900/mês, grandes áreas a R$ 450/mês) e implantações reduzem o número de municípios necessários.
- A necessidade de caixa (≈ R$ 577 mil) indica que o negócio precisa de **investimento-anjo, programa de aceleração
  ou edital de inovação** até o equilíbrio — isso entra no "pedido" do pitch.
- Os números foram gerados por `scripts/gerar_planilhas.py` e conferidos com as fórmulas do Excel
  (`MODELO_FINANCEIRO_HIPOTETICO.xlsx`, abas `Ponto_de_equilibrio` e `Projecao_36_meses`). Mude qualquer premissa
  na aba `Premissas` e tudo recalcula.

## 9. Métricas-chave (resumo — definições completas em `METRICAS_E_IMPACTO.md`)

| Tipo | Métrica | Fonte no MVP |
|---|---|---|
| Produto | Tempo médio de triagem automática da foto | `/metrics` → `acessacidade_visao_duracao_seconds` (soma ÷ contagem) |
| Produto | % de denúncias com foto analisada | `GET /api/indicadores`: (total − sem_imagem) ÷ total |
| Produto | % de denúncias revisadas por humano | campo `revisao_humana` não nulo (exportação para o pipeline) |
| Operação | Tempo até encaminhamento | histórico de status: data de `ENCAMINHADA` − `criado_em` |
| Operação | Denúncias por bairro e por categoria | `por_bairro`, `por_categoria` (API) e Gold |
| Cidadão | Tempo para registrar um problema (antes × depois) | teste de usabilidade (`pitch/registro_testes_usuarios_TEMPLATE.xlsx`) |
| Cidadão | Cidadãos ativos (proxy) | denúncias com `origem=WEB` por mês (o MVP não tem login, por desenho de privacidade) |
| Negócio | Clientes pagantes, MRR, churn, CAC | CRM/financeiro da startup (fora do MVP) |

## 10. Impacto e como medir antes/depois

Ver `METRICAS_E_IMPACTO.md`. Resumo: (1) **tempo para registrar** uma barreira no canal atual × no AcessaCidade,
medido em teste de usabilidade com o público-alvo; (2) **taxa de conclusão** das tarefas sem ajuda e nota **SUS**;
(3) em um piloto real, **tempo até encaminhamento** e **% de denúncias com foto analisada e revisada**, comparados
com a linha de base do município antes do piloto. Nenhum valor de impacto foi medido até agora:
`[PREENCHER: resultados reais dos testes, quando houver]`.

## 11. Possibilidades de escala

1. **Outros municípios** — o produto é multi-cidade por configuração (`CIDADE_PADRAO`, campo `cidade`); um container por cliente ou instância compartilhada.
2. **Outros tipos de zeladoria** — iluminação, sinalização, poda, lixo: o mesmo fluxo (foto + triagem + protocolo + painel) com novas categorias e novos classificadores.
3. **Integração com o 156 e sistemas municipais** — via API ou, quando não houver API, via **RPA** (o robô UiPath da disciplina 05 já registra denúncias pelo formulário).
4. **Dados abertos** — publicação agregada e anonimizada (por bairro e categoria) a partir da camada Gold.
5. **Rotas acessíveis** — com volume de dados, sugerir trajetos que evitem barreiras registradas.
6. **Grandes áreas privadas** — shoppings, campi e condomínios como mercado B2B com ciclo de venda mais curto.

## 12. Riscos e mitigação

| Risco | Probabilidade (hipótese) | Mitigação |
|---|---|---|
| Ciclo de venda pública longo | Alta | Piloto de 90 dias; CPSI como caminho possível; foco inicial em grandes áreas privadas (B2B) |
| Prefeitura não agir sobre as denúncias (frustração do cidadão) | Média | Status honestos ("Resolvida" é registro da equipe, não confirmação oficial); painel público por bairro como pressão social; parceria com associações |
| Triagem automática errar | Média | Triagem é apoio, nunca decisão; revisão humana obrigatória; etapas da imagem visíveis e explicação em texto |
| Fotos com rostos ou placas (LGPD) | Média | Remoção de metadados EXIF/GPS, rostos borrados, termo de consentimento no formulário |
| Denúncias falsas ou duplicadas | Média | Revisão humana; deduplicação no pipeline; limite de requisições por IP |
| Custo de LLM crescer | Baixa | Modelo configurável; modo por regras sem custo de API; limite de histórico |
| Concorrência de soluções existentes (156, apps de zeladoria) | Alta | Foco em acessibilidade + integração (inclusive por RPA) em vez de substituir o 156 |
| Dependência de uma pessoa-chave na equipe | Média | Documentação, contratos de integração e testes automatizados |

## 13. Contexto de mercado (dados públicos — conferir a fonte antes de usar no pitch)

- **Pessoas com deficiência no Brasil:** a PNAD Contínua 2022 (IBGE, módulo sobre pessoas com deficiência,
  divulgado em 2023) estimou cerca de **18,6 milhões de pessoas de 2 anos ou mais com deficiência (8,9%)**.
  _Conferir a fonte antes de usar no pitch._
- **População idosa:** `[PREENCHER: número de pessoas com 60 anos ou mais — Censo 2022/IBGE — com link da fonte]`.
- **Municípios brasileiros:** 5.570 (IBGE). _Conferir a fonte antes de usar no pitch._
- **Distribuição dos municípios por faixa de população:** `[PREENCHER: dado + fonte (IBGE, estimativas populacionais)]`.
- **Base legal da acessibilidade:** Lei Brasileira de Inclusão (Lei nº 13.146/2015), Lei nº 10.098/2000 e norma
  ABNT NBR 9050 (acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos).
- **Território observado pela equipe:** `[PREENCHER: cidade/bairros onde a equipe observou o problema, com fotos próprias]`.
