# Instruções — abrir, configurar, executar e depurar no UiPath Studio

> **Transparência:** o projeto `UiPath/AcessaCidade.RPA` foi escrito fora do UiPath Studio (o Studio
> não estava disponível no ambiente de geração). Os `.xaml` são XML bem-formado, com namespaces do
> Workflow Foundation/UiPath, variáveis, argumentos e anotações — validados por testes automatizados
> (`tests/test_rpa_artefatos.py`). **Não** foram abertos nem executados no Studio. Espere que o Studio
> peça para restaurar/atualizar pacotes e, eventualmente, mostre avisos que precisam de correção manual.
> Este guia diz como resolver cada caso.

## 1. Instalar o UiPath Studio (Community)

1. Acesse o site oficial da UiPath, crie uma conta gratuita (Automation Cloud — plano *Community*/*Free*)
   e baixe o instalador do **UiPath Studio** (Studio Community). Verifique os termos de licença da edição
   Community para uso acadêmico.
2. Instale com as opções padrão e faça login com a conta criada (o Studio conecta ao Orchestrator da
   conta Community — isso é necessário apenas para ativar a licença).
3. No primeiro início, escolha o perfil **UiPath Studio** (não o StudioX).
4. Versões de referência para este projeto: **Studio 2023.10** ou **2024.10** (o `project.json` declara
   `studioVersion 23.10.0.0`). Versões mais novas abrem o projeto e podem oferecer conversão — aceite.

## 2. Instalar a extensão do navegador

`Home → Tools → UiPath Extensions → Edge` (ou `Chrome`). Ative a extensão no navegador e reinicie-o.
Detalhes em `CONFIGURACAO_SELETORES.md`, seção 2.

## 3. Abrir o projeto

1. Copie a pasta inteira do repositório (ou clone) para o computador com o Studio. **Mantenha a estrutura
   de pastas**: o `Data/Config.xlsx` usa caminhos relativos (`..\..\spreadsheet\...` e
   `..\..\..\data\samples\fotos`).
2. Studio → **Open** (ou *Open a Local Project*) → selecione
   `05-Robotic-Process-Automation\UiPath\AcessaCidade.RPA\project.json`.
3. Se aparecer *"Project is from an older version / convert"*: aceite.
4. O Studio restaura os pacotes. Se aparecer erro de dependência ("Package not found" / "Unresolved"):
   - `Design → Manage Packages → Project Dependencies`;
   - para cada pacote com aviso (`UiPath.System.Activities`, `UiPath.UIAutomation.Activities`,
     `UiPath.Excel.Activities`), clique e escolha a **versão estável mais próxima** disponível no feed
     oficial (as versões do `project.json` — 23.10.x / 23.10.x / 2.22.x — são de referência para o
     Studio 2023.10; o feed pode ter apenas revisões como `.2`, `.3`...). Clique **Save**.
5. Abra o painel **Error List** (`View → Error List`) e corrija o que aparecer (seção 6).
6. Salve tudo (`Ctrl+Shift+S`). O Studio completa automaticamente o *ViewState* (posições no designer).

Arquivos do projeto:

| Arquivo | Papel |
|---|---|
| `Main.xaml` | Orquestra: carregar config → ler planilha → abrir navegador → For Each Row (Try/Catch por linha) → `ProcessarDenuncia` → `RegistrarResultado` → log → resumo |
| `Workflows/CarregarConfiguracao.xaml` | Lê `Data/Config.xlsx` (aba `Settings`, colunas `Nome`/`Valor`) para `Dictionary(Of String, Object)` |
| `Workflows/ProcessarDenuncia.xaml` | Valida a linha, abre `#/registrar?canal=rpa`, preenche pelos ids, anexa foto (opcional), marca consentimento, envia, captura `#protocolo-gerado` ou `#erro-envio` |
| `Workflows/RegistrarResultado.xaml` | Escreve `Status_Robo`, `Protocolo`, `Mensagem`, `Data_Hora_Processamento` e grava a planilha de saída |
| `Data/Config.xlsx` | Configuração (gerada por `scripts/gerar_planilhas.py`) |

## 4. Configurar `Data/Config.xlsx`

Abra no Excel, aba **Settings**:

| Nome | Valor padrão | Quando mudar |
|---|---|---|
| `URL_ACESSACIDADE` | `http://localhost:8000` | Para a apresentação/vídeo, troque pela URL pública da Azure **[PREENCHER: URL pública — depende da disciplina 06]** (sem `/` no final) |
| `CAMINHO_PLANILHA_ENTRADA` | `..\..\spreadsheet\denuncias_para_cadastro_SIMULADAS.xlsx` | Se usar outra planilha |
| `CAMINHO_PLANILHA_SAIDA` | `..\..\spreadsheet\denuncias_resultado_RPA.xlsx` | Criada pelo robô |
| `PASTA_IMAGENS` | `..\..\..\data\samples\fotos` | Se as imagens estiverem em outro lugar |
| `TIMEOUT_SEGUNDOS` | `30` | 60 contra a Azure |
| `NAVEGADOR` | `Edge` | `Chrome` se for o navegador com a extensão |
| `ABA_ENTRADA` / `ABA_SAIDA` | `Denuncias` / `Resultado` | — |
| `MODO_UPLOAD_FOTO` | `DIALOGO` | `TYPEINTO` ou `IGNORAR` (ver `CONFIGURACAO_SELETORES.md`, seção 5) |

**Feche o Excel** antes de executar o robô (Read/Write Range falham com o arquivo aberto e bloqueado).
Para regenerar as planilhas originais: `python 05-Robotic-Process-Automation\scripts\gerar_planilhas.py`.

## 5. Executar

### 5.1 Contra o ambiente local (teste)

1. Na raiz do repositório, suba o AcessaCidade (conforme README da raiz — ex.:
   `.\.venv\Scripts\python.exe -m uvicorn ...` ou `docker compose up`) e confirme que
   `http://localhost:8000/#/registrar?canal=rpa` abre e mostra o selo "Canal: automação (RPA)".
2. `URL_ACESSACIDADE = http://localhost:8000` no Config.xlsx.
3. No Studio, com `Main.xaml` aberto: **Debug File → Run File** (`Ctrl+F6`) ou **Run** (`F5`) para o projeto.
4. Não use mouse/teclado durante a execução (o modo `DIALOGO` da foto usa clique real).
5. Acompanhe o painel **Output**: uma linha de log por denúncia e, no final, o resumo
   (`sucesso`, `falha de negócio`, `falha de sistema`, `ignoradas`).
6. Abra `spreadsheet\denuncias_resultado_RPA.xlsx`, aba `Resultado`: as linhas 1–10 devem ter
   `Status_Robo = SUCESSO` e protocolo `AC-AAAA-NNNNNN`; as linhas 11 e 12 (cenários negativos de propósito)
   devem ter `FALHA_NEGOCIO` com a mensagem do motivo.
7. No AcessaCidade, abra `#/consultar`, busque um protocolo da planilha e confira que a denúncia aparece
   com **origem RPA**.

### 5.2 Contra a URL pública na Azure (apresentação)

1. Pré-requisito: a disciplina 06 publicou o AcessaCidade e a URL está acessível.
2. Troque `URL_ACESSACIDADE` e aumente `TIMEOUT_SEGUNDOS` para 60.
3. Execute como em 5.1. Os registros criados são **de teste** (descrições começam com
   `[TESTE SIMULADO RPA]`); combine com a equipe se devem permanecer no ambiente público.

### 5.3 Reprocessar sem duplicar

O robô ignora linhas cuja coluna `Status_Robo` já seja `SUCESSO`. Para retomar uma execução
interrompida, aponte `CAMINHO_PLANILHA_ENTRADA` para a planilha de saída e `ABA_ENTRADA = Resultado`.

## 6. Depurar e corrigir avisos comuns

| Sintoma | Causa provável | Correção |
|---|---|---|
| Atividade com ícone vermelho "Unresolved activity" | Pacote ausente ou versão diferente | Manage Packages → instalar/atualizar o pacote; reabrir o arquivo |
| `Compiler error(s): 'Regex' is not declared` / `'Path' is not declared` | Import ausente | Painel **Imports** (rodapé do designer) → adicionar `System.Text.RegularExpressions` / `System.IO` |
| `'BusinessRuleException' is not defined` | Import ausente | Imports → `UiPath.Core.Activities` |
| Erro de propriedade desconhecida ao abrir (ex.: atributo que a versão do pacote não tem) | Diferença de versão do pacote | Abra o `.xaml` num editor de texto, remova o atributo citado na mensagem, salve e reabra no Studio |
| "Cannot find the UI element corresponding to this selector" | Seletor não confere com a página | `CONFIGURACAO_SELETORES.md`, seção 3 (Validate/Indicate) |
| Selo "Canal: automação (RPA)" não aparece | URL sem `?canal=rpa` | Confira `URL_ACESSACIDADE` (sem barra final) |
| Planilha "being used by another process" | Excel aberto | Feche o Excel |
| Linhas válidas viram `FALHA_SISTEMA` com `TimeoutException` | AcessaCidade lento ou fora do ar | Aumente `TIMEOUT_SEGUNDOS`; confira `GET /health` |
| Foto não é anexada | Diálogo "Abrir" com outro layout/idioma | Reindique a caixa "Nome:" ou use `MODO_UPLOAD_FOTO = IGNORAR` |

Ferramentas úteis: **breakpoints** (`F9`) na atividade "Invoke - ProcessarDenuncia.xaml"; **Step Into**
(`F11`); painel **Locals** para ver `row`, `protocolo`, `mensagemErro`; **Highlight Elements** no modo
depuração para ver cada seletor sendo encontrado; **Slow Step** para gravar o vídeo com ritmo legível.

Se alguma atividade não puder ser corrigida, a alternativa é **recriá-la** no designer arrastando a
atividade equivalente (Type Into, Select Item, Click, Check, Get Text, Element Exists) e colando o seletor
da tabela de `CONFIGURACAO_SELETORES.md` — as anotações de cada atividade explicam o que ela deve fazer.

## 7. Publicar (opcional)

Não é exigido pela disciplina. Se quiser: **Design → Publish** → destino *Orchestrator Tenant Processes
Feed* (conta Community) ou *Custom* (pasta local, gera um `.nupkg`). No Orchestrator, crie um *Process*
a partir do pacote e execute com um robô atendido. Não publique dados reais.

## 8. Prints para o relatório

Ver `EVIDENCIAS_NECESSARIAS.md`.
