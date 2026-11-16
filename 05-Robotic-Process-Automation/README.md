# 05 — Robotic Process Automation · AcessaCidade

**Atividade:** CitizenTech: Da Análise de Processos à Automação com UiPath (14 pontos: 3 documentação,
3 vídeo, 8 automação no UiPath) · **Entrega:** ZIP no Teams até 19/11/2026 23h55, um envio por equipe.

**Papel no MVP:** o robô que executa de ponta a ponta um processo hoje manual — cadastrar no AcessaCidade
as denúncias de acessibilidade que chegam de associações, ONGs e agentes comunitários em **planilhas**,
capturar o protocolo e devolver o resultado linha a linha. O operador passa a tratar só as exceções.

> Dados exclusivamente **simulados** (cidade fictícia "Cidade Exemplo", nomes "Robô Teste NN", imagens
> sintéticas). Os números do business case são **premissas** a validar.

## Estrutura

```text
05-Robotic-Process-Automation/
├── UiPath/AcessaCidade.RPA/          # projeto UiPath (Windows, VB.NET)
│   ├── project.json
│   ├── Main.xaml                     # orquestração + Try/Catch por linha + resumo
│   ├── Workflows/CarregarConfiguracao.xaml
│   ├── Workflows/ProcessarDenuncia.xaml
│   ├── Workflows/RegistrarResultado.xaml
│   └── Data/Config.xlsx              # URL, caminhos, timeout, navegador, modo de upload
├── spreadsheet/
│   ├── denuncias_para_cadastro_SIMULADAS.xlsx   # entrada do robô (12 linhas: 10 válidas + 2 negativas)
│   └── assessment_rpa_AcessaCidade.xlsx         # assessment (preliminar) + modelo em branco + candidatos
├── process-mapping/                  # BPMN 2.0 As-Is/To-Be (+ SVG) e MAPEAMENTO_PROCESSOS.md (Mermaid + narrativa)
├── docs/
│   ├── RELATORIO_RPA.md              # fonte do PDF da entrega
│   ├── ANALISE_RPA_VS_API.md         # diagnóstico RPA vs integração nativa/API
│   ├── BUSINESS_CASE.md
│   ├── CONFIGURACAO_SELETORES.md
│   ├── INSTRUCOES_UIPATH_STUDIO.md
│   ├── ROTEIRO_VIDEO_RPA.md
│   ├── EVIDENCIAS_NECESSARIAS.md
│   └── INSTRUCOES_ZIP_ENTREGA.md
├── scripts/
│   ├── gerar_planilhas.py            # gera as 3 planilhas (openpyxl)
│   ├── gerar_bpmn.py                 # gera os .bpmn e .svg
│   ├── gerar_pdf_relatorio.py        # RELATORIO_RPA.md -> PDF (Edge/Chrome headless)
│   └── gerar_zip_entrega.ps1         # monta o ZIP de entrega
├── tests/test_rpa_*.py               # validações estruturais (pytest)
├── entrega/                          # PDF, link_video.txt e ZIP (produzidos pela equipe)
├── evidencias/                       # prints (produzidos pela equipe)
└── PENDENCIAS_E_ACOES_MANUAIS.txt    # o que falta fazer manualmente, passo a passo
```

## Como o robô funciona

1. `CarregarConfiguracao.xaml` lê `Data/Config.xlsx` (aba `Settings`, `Nome`/`Valor`).
2. `Main.xaml` lê a planilha de entrada (Read Range), confere as colunas e abre o navegador.
3. Para cada linha (For Each Row, com Try/Catch por linha), `ProcessarDenuncia.xaml`:
   valida a linha → abre `{URL_ACESSACIDADE}/#/registrar?canal=rpa` (origem `RPA`) → preenche os campos
   pelos ids do contrato (`campo-logradouro`, `campo-tipo`, ...) → seleciona tipo e impacto pelo texto
   visível (rótulos do contrato) → anexa a foto (opcional) → marca `#campo-consentimento` → clica
   `#botao-enviar` → aguarda `#protocolo-gerado` (`AC-AAAA-NNNNNN`) ou `#erro-envio` → clica
   `#botao-nova-denuncia`.
4. `RegistrarResultado.xaml` grava `Status_Robo` (`SUCESSO` / `FALHA_NEGOCIO` / `FALHA_SISTEMA`),
   `Protocolo`, `Mensagem` e `Data_Hora_Processamento` em `spreadsheet/denuncias_resultado_RPA.xlsx`.
5. No final, o log mostra o resumo com os totais. Linhas já com `SUCESSO` são ignoradas ao reprocessar.

## Comandos

```powershell
cd C:\Users\masak\Desktop\GS7-4ESPR
# regenerar planilhas (entrada, assessment, Config.xlsx)
.\.venv\Scripts\python.exe 05-Robotic-Process-Automation\scripts\gerar_planilhas.py
# regenerar BPMN/SVG
.\.venv\Scripts\python.exe 05-Robotic-Process-Automation\scripts\gerar_bpmn.py
# testes da disciplina
.\.venv\Scripts\python.exe -m pytest 05-Robotic-Process-Automation\tests
# PDF do relatório e ZIP de entrega (depois de preencher o relatório e gravar o vídeo)
.\.venv\Scripts\python.exe 05-Robotic-Process-Automation\scripts\gerar_pdf_relatorio.py
powershell -ExecutionPolicy Bypass -File .\05-Robotic-Process-Automation\scripts\gerar_zip_entrega.ps1
```

## Estado e limitações (honesto)

- O projeto UiPath foi escrito **fora do UiPath Studio**. Os testes garantem XML bem-formado, namespaces,
  argumentos coerentes entre workflows, seletores com os ids do contrato e IdRefs únicos — **não**
  garantem que o Studio abre sem avisos nem que o robô roda. Abrir, corrigir, validar seletores e executar
  no Studio é tarefa manual (ver `docs/INSTRUCOES_UIPATH_STUDIO.md` e `PENDENCIAS_E_ACOES_MANUAIS.txt`).
- Versões de pacotes no `project.json` são de referência para o Studio 2023.10; o Studio pode pedir para
  atualizá-las.
- A execução contra a URL pública depende do deploy da disciplina 06 (`[PREENCHER: URL pública]`).
- O resultado do assessment (79,4 % — Alta aptidão) é uma avaliação **preliminar** a revisar com a equipe.
