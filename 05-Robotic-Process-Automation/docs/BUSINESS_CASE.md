# Business Case — robô de cadastro de denúncias recebidas de parceiros (AcessaCidade)

> Todos os números deste documento são **premissas (hipóteses de trabalho)**, não medições. Eles servem
> para dimensionar a ordem de grandeza do ganho e devem ser **validados com a equipe e com parceiros**
> antes de qualquer decisão. Onde houver `[PREENCHER: ...]`, a equipe deve substituir pelo dado real.
> A disciplina não exige cálculo de ROI; ele é apresentado de forma simples e opcional.

## 1. Problema

Parte das denúncias de acessibilidade não chega pelo formulário web: associações de pessoas com
deficiência, ONGs e agentes comunitários coletam relatos **em papel, por telefone ou em planilhas** e os
enviam por e-mail. Hoje (cenário As-Is), um operador precisa **digitar cada denúncia** no AcessaCidade,
conferir, copiar o protocolo e devolvê-lo ao parceiro. Consequências:

- **Atraso**: a denúncia só entra na fila de triagem quando alguém tem tempo de digitar.
- **Erro de transcrição**: endereço trocado, categoria errada, descrição truncada.
- **Falta de retorno ao cidadão**: o parceiro raramente recebe o protocolo de volta, então o cidadão não
  consegue acompanhar.
- **Uso ruim de tempo qualificado**: a equipe deveria revisar fotos e encaminhar ocorrências, não digitar.

Público afetado: pessoas com deficiência, cadeirantes, pessoas com mobilidade reduzida e idosos —
exatamente quem mais depende de canais assistidos (associações) e de resposta rápida. Alinhamento com
o **ODS 11** (cidades inclusivas, seguras e acessíveis).

## 2. Solução proposta

Robô UiPath (`UiPath/AcessaCidade.RPA`) que lê a planilha-modelo enviada pelo parceiro, valida cada linha
com as mesmas regras da API, cadastra no formulário `#/registrar?canal=rpa` (origem `RPA`), captura o
protocolo e grava uma **planilha de saída** com `Status_Robo`, `Protocolo`, `Mensagem` e
`Data_Hora_Processamento`. O operador passa a tratar **apenas as exceções** (linhas `FALHA_NEGOCIO` ou
`FALHA_SISTEMA`). Fluxos As-Is/To-Be em `process-mapping/`.

## 3. Benefícios esperados

| Benefício | Como aparece | Tipo |
|---|---|---|
| Menos tempo de digitação | Operador só trata exceções | Quantitativo (ver seção 5) |
| Padronização | Mesmos rótulos do contrato; validação antes do envio | Qualidade |
| Rastreabilidade | Origem `RPA` no AcessaCidade + planilha de saída com protocolo por linha | Governança |
| Retorno ao parceiro/cidadão | A planilha de saída volta para a associação com os protocolos | Impacto social |
| Escala sob demanda | O robô processa lotes fora do horário comercial (execução atendida/agendada) | Operacional |
| Base para evolução | A planilha-modelo vira o formato de uma futura importação nativa/API | Estratégico |

## 4. Premissas (HIPÓTESES a validar)

| # | Premissa | Valor adotado | Como validar |
|---|---|---|---|
| P1 | Volume mensal de denúncias vindas de parceiros (fase piloto) | 300 / mês | [PREENCHER: levantar com associações parceiras] |
| P2 | Tempo manual por denúncia (abrir planilha, digitar ~10 campos, anexar foto, copiar protocolo, responder) | 4 min | [PREENCHER: cronometrar 10 cadastros manuais] |
| P3 | Custo da hora de um operador administrativo (salário + encargos) | R$ 35,00 / h | [PREENCHER: referência salarial da região/organização] |
| P4 | Percentual de linhas com exceção que exigem tratamento humano | 10 % | [PREENCHER: medir na primeira execução real] |
| P5 | Tempo humano por exceção | 4 min | igual a P2 |
| P6 | Supervisão do robô (iniciar, conferir resumo, enviar planilha de saída) | 2 h / mês | [PREENCHER] |
| P7 | Manutenção de seletores e do projeto | 3 h / mês (média) | [PREENCHER] |
| P8 | Licenciamento | UiPath Studio Community no piloto acadêmico; em produção, licença de robô atendido/não atendido | [PREENCHER: cotação oficial UiPath — não estimada aqui] |
| P9 | Implantação inicial (desenvolvimento, testes, documentação) | 24 h | horas reais da equipe [PREENCHER] |

## 5. Cálculo simples (ilustrativo, com as premissas acima)

| Item | Fórmula | Resultado |
|---|---|---|
| Horas manuais/mês (As-Is) | P1 × P2 = 300 × 4 min | **20,0 h** |
| Horas humanas/mês (To-Be) | P1 × P4 × P5 + P6 + P7 = 300 × 10 % × 4 min + 2 h + 3 h | 2,0 + 2 + 3 = **7,0 h** |
| Horas liberadas/mês | 20,0 − 7,0 | **13,0 h** (65 %) |
| Valor das horas liberadas/mês | 13,0 h × R$ 35,00 | **R$ 455,00** |
| Custo de implantação | P9 × P3 = 24 h × R$ 35,00 | R$ 840,00 |
| Retorno da implantação (sem licença) | 840 / 455 | **≈ 1,8 mês** |

Leitura honesta:

- Em volume baixo (P1 = 50/mês) as horas liberadas ficam em ≈ −2,0 h — 3,3 h manuais contra 5,3 h de exceções, supervisão e manutenção (o robô **não compensa**: a
  manutenção supera a digitação). O ponto de equilíbrio, com estas premissas, é ≈ **83 denúncias/mês**
  (`(P6 + P7) / (P2 × (1 − P4))` = 5 h / 3,6 min ≈ 83).
- O custo de **licença em produção não foi estimado** (P8) — ele pode mudar completamente a conclusão;
  por isso o relatório recomenda RPA como **solução de transição** e a evolução para importação nativa/API
  (ver `ANALISE_RPA_VS_API.md`).
- O principal ganho não é financeiro: é **tempo de resposta ao cidadão** (denúncia registrada no mesmo dia
  em que o parceiro envia) e **retorno do protocolo**.

O mesmo cálculo pode ser refeito trocando as premissas; a planilha de assessment
(`spreadsheet/assessment_rpa_AcessaCidade.xlsx`) registra as notas de volume e tempo baseadas nelas.

## 6. Riscos e mitigação

| Risco | Probabilidade / impacto | Mitigação |
|---|---|---|
| Mudança no formulário quebra seletores | Média / alto | Contrato com `id`, `name`, `data-rpa` estáveis; testes do contrato; fallback por `name` |
| Planilha do parceiro fora do modelo | Alta / médio | Validação de colunas e regras antes do envio; linha inválida vira `FALHA_NEGOCIO` com motivo |
| Denúncia duplicada ao reprocessar | Média / médio | Idempotência: linha com `Status_Robo = SUCESSO` é ignorada |
| Dados pessoais na planilha | Média / alto (LGPD) | Nome é opcional e nunca exposto pela API; planilha-modelo orienta a não incluir dados sensíveis; ambiente de teste só com dados **simulados** |
| Aplicação lenta/fora do ar | Baixa / médio | Timeout configurável; `FALHA_SISTEMA` não interrompe o lote |
| Dependência de licença/ferramenta proprietária | Média / médio | Planilha-modelo e API permitem migrar para importação nativa |
| Robô usado como substituto da revisão humana | Baixa / alto | O robô só **cadastra**; triagem de fotos e mudança de status continuam humanas (processo C do assessment foi **descartado** para RPA) |

## 7. KPIs

| KPI | Fórmula | Meta inicial (hipótese) | Fonte |
|---|---|---|---|
| Taxa de sucesso do robô | linhas `SUCESSO` / linhas processadas | ≥ 90 % das linhas válidas | Planilha de saída / log |
| Taxa de exceção | (`FALHA_NEGOCIO` + `FALHA_SISTEMA`) / processadas | ≤ 10 % | Planilha de saída |
| Falhas de sistema | `FALHA_SISTEMA` / processadas | ≤ 2 % | Log do robô |
| Tempo médio por registro (robô) | duração da execução / linhas | [PREENCHER: medir na execução real] | Log (início/fim) |
| Tempo entre recebimento da planilha e protocolo devolvido | data de devolução − data de recebimento | ≤ 1 dia útil | Controle do operador |
| Denúncias com origem RPA | contagem no AcessaCidade (`origem = RPA`) | acompanhar mensalmente | `GET /api/denuncias` / painel |
| Horas humanas no processo | horas registradas pelo operador | ≤ 7 h/mês (premissa) | Apontamento da equipe |

## 8. Decisão recomendada

Implantar o robô como **piloto** para o processo de cadastro de denúncias de parceiros, por 1 a 3 meses,
medindo os KPIs acima, e reavaliar: se o volume ficar abaixo do ponto de equilíbrio ou a manutenção de
seletores for alta, substituir por **importação nativa de planilha** no AcessaCidade (usando a mesma
lógica da API `POST /api/denuncias`).
