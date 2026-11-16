# AcessaCidade — Relatório de Robotic Process Automation

**FIAP Global Solution 2026.2 — CitizenTech · Disciplina 05: Robotic Process Automation**
**Atividade:** CitizenTech: Da Análise de Processos à Automação com UiPath
**Equipe:** [PREENCHER: nomes e RMs dos integrantes]
**Turma:** [PREENCHER] · **Data:** [PREENCHER]
**Link do vídeo (≤ 3 min):** [PREENCHER: link do vídeo]
**URL do AcessaCidade usada na demonstração:** [PREENCHER: URL pública da Azure ou "execução local em http://localhost:8000"]

> Fonte do PDF da entrega. Para gerar o PDF, ver `INSTRUCOES_ZIP_ENTREGA.md`. Os trechos
> `[PREENCHER: ...]` e os prints (E1–E12 de `EVIDENCIAS_NECESSARIAS.md`) devem ser completados pela equipe.
> Todos os dados de teste são **simulados**, na cidade fictícia "Cidade Exemplo".

---

## 1. Contexto

O AcessaCidade é uma plataforma web para registrar, triar por visão computacional e acompanhar denúncias
de problemas de acessibilidade em calçadas e espaços públicos (buracos, calçadas danificadas, rampas
ausentes, obstáculos), voltada a pessoas com deficiência, cadeirantes, pessoas com mobilidade reduzida e
idosos (ODS 11). Nesta disciplina, a equipe identificou um gargalo operacional da jornada do cidadão,
avaliou criticamente se RPA é a solução adequada, modelou o processo em BPMN (As-Is e To-Be) e
implementou um robô no UiPath Studio integrado ao MVP.

## 2. Escolha do processo

### 2.1 Processos candidatos

Avaliação preliminar (`spreadsheet/assessment_rpa_AcessaCidade.xlsx`, aba "Processos candidatos"; notas
de 1 a 5, 6 critérios, máximo 30):

| Processo candidato | Total | Aderência | Decisão | Motivo |
|---|---|---|---|---|
| A) Cadastro de denúncias recebidas por planilhas de parceiros / canais não digitais | 24/30 | 80 % | **Escolhido** | Repetitivo, baseado em regras, formulário com ids estáveis, ganho direto ao cidadão; os parceiros não conseguem consumir a API |
| B) Envio semanal de relatório de indicadores às associações | 19/30 | 63 % | Não escolhido | Os dados já estão na API (`/api/indicadores`) e na camada Gold do pipeline: integração nativa/BI resolve melhor; volume baixo |
| C) Revisão da triagem das fotos e mudança de status | 15/30 | 50 % | Não automatizar | Exige julgamento humano por princípio (IA responsável: pessoa no circuito) |

### 2.2 Resultado da planilha de assessment (processo A)

> **[INSERIR PRINT E1: aba Assessment aberta no Excel]**

Avaliação **PRELIMINAR da equipe — revisar com a equipe**. Pontuação ponderada = Peso × Nota; aderência =
soma ponderada ÷ (soma dos pesos × 5). Faixas: ≥ 70 % Alta aptidão; 50–70 % Média; < 50 % Baixa.

| Critério | Peso (%) | Nota (1–5) | Ponderada | Justificativa (resumo) |
|---|---|---|---|---|
| Baseado em regras | 15 | 5 | 75 | Campos fixos; tipo e impacto em listas fechadas do contrato |
| Entrada estruturada e digital | 12 | 4 | 48 | Planilha-modelo estruturada; parte ainda chega em papel/e-mail e precisa ser transcrita antes |
| Volume | 10 | 3 | 30 | Premissa: 300 denúncias/mês (a validar) |
| Frequência | 8 | 4 | 32 | Planilhas semanais (premissa); o robô pode rodar diariamente |
| Estabilidade da aplicação | 10 | 4 | 40 | `id`, `name` e `data-rpa` estáveis em contrato; risco residual de layout |
| Número de sistemas | 5 | 4 | 20 | Dois: Excel e navegador |
| Exceções | 10 | 4 | 40 | Exceções conhecidas e registradas na planilha de saída |
| Tempo manual por item | 8 | 3 | 24 | Premissa: 4 min por denúncia (a cronometrar) |
| Propensão a erro humano | 7 | 4 | 28 | Transcrição de endereço/categoria e cópia de protocolo |
| Impacto ao cidadão | 10 | 5 | 50 | Denúncias entram mais rápido e recebem protocolo |
| Ausência de API / integração nativa | 5 | 2 | 10 | O AcessaCidade **tem** API; os parceiros é que não conseguem integrar |
| **Total** | **100** | — | **397 / 500** | **Aderência 79,4 % → Alta aptidão para RPA** |

Os valores acima foram recalculados em Python (`scripts/gerar_planilhas.py`) e conferidos por teste
automatizado (`tests/test_rpa_planilhas.py`); no Excel, as fórmulas da planilha produzem o mesmo resultado
ao abrir o arquivo. Após a revisão da equipe: [PREENCHER: resultado final revisado, se mudar].

## 3. Mapeamento do processo (BPMN)

Arquivos: `process-mapping/AS-IS_cadastro_denuncias.bpmn` e `TO-BE_cadastro_denuncias.bpmn` (BPMN 2.0 com
diagrama, abríveis em demo.bpmn.io ou Camunda Modeler), versões SVG e Mermaid, e narrativa completa em
`process-mapping/MAPEAMENTO_PROCESSOS.md`.

### 3.1 As-Is (cadastro manual)

> **[INSERIR IMAGEM E3: As-Is]**

Raias: Cidadão/Associação, Operador AcessaCidade, AcessaCidade (web). A associação reúne relatos em papel,
planilha ou e-mail; o operador abre o material, padroniza endereço/categoria, pede complemento quando falta
dado, digita campo a campo, confere, copia o protocolo e devolve por e-mail.

Gargalos: (1) fila dependente da agenda do operador; (2) digitação de ~10 campos por denúncia, com erro de
endereço/categoria; (3) cópia manual do protocolo; (4) nenhum registro de quais linhas já foram cadastradas.

### 3.2 To-Be (robô + operador tratando exceções)

> **[INSERIR IMAGEM E3: To-Be]**

Raias: Cidadão/Associação, Operador, Robô UiPath, AcessaCidade. A associação preenche a planilha-modelo;
o robô lê a planilha, valida cada linha, cadastra no formulário `#/registrar?canal=rpa`, captura o
protocolo e registra o resultado; o operador só trata linhas com `FALHA_NEGOCIO`/`FALHA_SISTEMA` e devolve
a planilha de saída (com protocolos) ao parceiro.

## 4. Diagnóstico: RPA ou integração nativa/API?

Resumo de `docs/ANALISE_RPA_VS_API.md`:

- O AcessaCidade **tem API** (`POST /api/denuncias`). Para parceiros com TI, **integração por API é a
  melhor escolha** (mais rápida, sem seletores frágeis, com validação e erros estruturados).
- O RPA faz sentido **neste cenário específico** porque os parceiros (associações, ONGs, agentes
  comunitários) trabalham com planilhas e não têm capacidade técnica para integrar; o robô usa o mesmo
  formulário validado pelo cidadão, marca a origem `RPA` e devolve rastreabilidade (planilha de saída).
- Riscos assumidos: seletores frágeis (mitigados por ids estáveis em contrato), dependência de licença,
  execução atendida por causa do diálogo de arquivo.
- Recomendação: RPA como **solução de transição**; evoluir para importação nativa de planilha no
  AcessaCidade quando o volume crescer ou a manutenção ficar cara.

| Critério | RPA (UiPath) | API / integração nativa |
|---|---|---|
| Exige TI no parceiro | Não | Sim |
| Tempo para colocar no ar | Curto | Médio |
| Robustez a mudanças de tela | Baixa/média | Alta |
| Velocidade por registro | Segundos | Milissegundos |
| Custo recorrente | Licença + manutenção de seletores | Manutenção de código |

## 5. Business Case

Resumo de `docs/BUSINESS_CASE.md` (**premissas a validar**, não medições):

| Item | Valor |
|---|---|
| Volume (premissa) | 300 denúncias/mês |
| Tempo manual (premissa) | 4 min/denúncia → 20 h/mês |
| Horas humanas no To-Be (exceções 10 % + supervisão + manutenção) | 7 h/mês |
| Horas liberadas | 13 h/mês (65 %) |
| Valor (premissa R$ 35/h) | R$ 455/mês |
| Ponto de equilíbrio | ≈ 83 denúncias/mês |
| Licença em produção | Não estimada — [PREENCHER: cotação oficial] |

Principais ganhos não financeiros: denúncia registrada no mesmo dia em que o parceiro envia, protocolo
devolvido ao cidadão, padronização e rastreabilidade. KPIs: taxa de sucesso do robô, taxa de exceção,
falhas de sistema, tempo por registro, tempo até devolução do protocolo.

## 6. A automação no UiPath Studio

> **[INSERIR PRINTS E4 e E5: Main.xaml e ProcessarDenuncia.xaml]**

Projeto `UiPath/AcessaCidade.RPA` (Windows, VB.NET; pacotes UiPath.System.Activities,
UiPath.UIAutomation.Activities, UiPath.Excel.Activities).

| Workflow | O que faz |
|---|---|
| `Main.xaml` | Carrega a configuração, lê a planilha de entrada (Read Range), confere colunas, abre o navegador, percorre as linhas (For Each Row) com Try/Catch por linha, invoca `ProcessarDenuncia` e `RegistrarResultado`, registra log e exibe resumo com totais |
| `Workflows/CarregarConfiguracao.xaml` | Lê `Data/Config.xlsx` (aba `Settings`, `Nome`/`Valor`) para um `Dictionary(Of String, Object)` e valida chaves obrigatórias |
| `Workflows/ProcessarDenuncia.xaml` | Valida a linha (mesmas regras da API e rótulos do contrato), navega para `#/registrar?canal=rpa`, preenche os campos pelos ids (`campo-logradouro`, `campo-tipo`...), seleciona tipo/impacto pelo texto visível, anexa a foto (diálogo do Windows ou Type Into), marca `#campo-consentimento`, clica `#botao-enviar`, aguarda `#protocolo-gerado` (formato `AC-AAAA-NNNNNN`) ou `#erro-envio`, e clica `#botao-nova-denuncia` |
| `Workflows/RegistrarResultado.xaml` | Grava `Status_Robo`, `Protocolo`, `Mensagem` e `Data_Hora_Processamento` e salva a planilha de saída a cada linha (resiliência a interrupções) |

Resiliência:

- **Exceção de negócio** (`BusinessRuleException`): dados inválidos na planilha ou recusa do AcessaCidade
  → `FALHA_NEGOCIO` com a mensagem; o lote continua.
- **Exceção de sistema** (timeout, seletor, navegador) → `FALHA_SISTEMA`; o lote continua.
- **Idempotência**: linhas com `Status_Robo = SUCESSO` são ignoradas ao reprocessar.
- Configuração externa (URL, caminhos, timeout, navegador, modo de upload) sem alterar o código.

Planilha de entrada: `spreadsheet/denuncias_para_cadastro_SIMULADAS.xlsx` — 12 linhas **simuladas**
(10 válidas e 2 negativas de propósito, para demonstrar o tratamento de exceção).

### 6.1 Resultado da execução

> **[INSERIR PRINTS E6, E7, E8 e E9]**

| Indicador | Valor |
|---|---|
| Linhas processadas | [PREENCHER] |
| SUCESSO | [PREENCHER] |
| FALHA_NEGOCIO | [PREENCHER] (esperado: 2, linhas 11 e 12) |
| FALHA_SISTEMA | [PREENCHER] |
| Duração total da execução | [PREENCHER] |
| Exemplo de protocolo gerado (origem RPA) | [PREENCHER] |

Observações e ajustes feitos no Studio (seletores reindicados, pacotes atualizados, avisos corrigidos):
[PREENCHER].

## 7. Limitações

- O projeto foi estruturado fora do Studio e precisou ser aberto, revisado e testado no Studio pela equipe
  ([PREENCHER: o que precisou ser ajustado]).
- O anexo da foto pelo diálogo do Windows exige execução atendida (navegador visível).
- Premissas do business case não foram medidas em campo.
- Dados exclusivamente simulados; nenhuma parceria real foi firmada.

## 8. Conclusão

[PREENCHER: conclusão da equipe — ex.: o RPA reduziu o trabalho manual ao tratamento de exceções no
cenário de parceiros sem integração, como etapa de transição para uma importação nativa.]

## Anexos

- Projeto UiPath (`.xaml`, `project.json`, `Data/Config.xlsx`)
- Planilhas: assessment, entrada simulada, saída gerada pelo robô
- BPMN As-Is e To-Be
- Link do vídeo: [PREENCHER: link do vídeo]
