# Instruções — PDF, link do vídeo e ZIP de entrega (Teams)

Formato oficial (PDF da GS, disciplina 05): **arquivo PDF + arquivos da automação + link do vídeo**, numa
**pasta compactada .zip**, entregue pela abertura da atividade no **Microsoft Teams** até
**19/11/2026 às 23h55** — **um envio por equipe**.

## 1. Completar o relatório

1. Abra `docs/RELATORIO_RPA.md` e substitua todos os `[PREENCHER: ...]` (equipe, RMs, link do vídeo,
   URL usada, resultados reais da execução, conclusão).
2. Coloque os prints em `evidencias/` (nomes em `EVIDENCIAS_NECESSARIAS.md`) e troque cada bloco
   `> **[INSERIR PRINT ...]**` por uma imagem Markdown, por exemplo:
   `![Planilha de assessment](../evidencias/E1_assessment.png)`.

## 2. Gerar o PDF

Opção A — script (usa o Edge/Chrome instalado; não precisa de internet):

```powershell
cd C:\Users\masak\Desktop\GS7-4ESPR
.\.venv\Scripts\python.exe 05-Robotic-Process-Automation\scripts\gerar_pdf_relatorio.py
```

Saída: `05-Robotic-Process-Automation\entrega\RELATORIO_RPA_AcessaCidade.pdf`. O script avisa quantos
`[PREENCHER]` ainda existem. Abra o PDF e confira imagens, tabelas e acentos.

Opção B — manual: abra o `.md` no VS Code → *Markdown: Open Preview* → copie para o Word/Google Docs →
*Arquivo → Salvar como PDF*.

## 3. Link do vídeo

1. Publique o vídeo (≤ 3 min) — ver `ROTEIRO_VIDEO_RPA.md`.
2. Crie `05-Robotic-Process-Automation\entrega\link_video.txt` com **uma linha** contendo o link
   (`https://...`). Teste o link numa janela anônima.

## 4. Gerar o ZIP

```powershell
cd C:\Users\masak\Desktop\GS7-4ESPR
powershell -ExecutionPolicy Bypass -File .\05-Robotic-Process-Automation\scripts\gerar_zip_entrega.ps1
```

- Sem o PDF ou sem um link válido em `link_video.txt`, o script **não gera** o ZIP (código de saída 2) e
  lista o que falta. Para um ZIP de conferência: acrescente `-PermitirIncompleto`.
- Também avisa (sem bloquear) se a planilha de saída do robô ou os prints ainda não existem.
- Saída: `05-Robotic-Process-Automation\entrega\AcessaCidade_RPA_entrega.zip`.

Conteúdo do ZIP:

```text
RELATORIO_RPA_AcessaCidade.pdf
link_video.txt
UiPath/AcessaCidade.RPA/      (project.json, Main.xaml, Workflows/*.xaml, Data/Config.xlsx, .gitignore)
planilhas/                    (assessment, entrada simulada, denuncias_resultado_RPA.xlsx se existir)
process-mapping/              (.bpmn e .svg As-Is/To-Be)
evidencias/                   (prints, se existirem)
```

As pastas locais do Studio (`.local`, `.objects`, `.project`, `.screenshots`, `.tmh`) e arquivos
temporários do Excel (`~$*.xlsx`) ficam de fora.

## 5. Conferir e entregar

1. Extraia o ZIP numa pasta temporária e abra o `project.json` no UiPath Studio para garantir que o projeto
   do ZIP abre (não só o do repositório).
2. Confira o PDF (links clicáveis, prints legíveis) e o link do vídeo.
3. No Teams: equipe da turma → **Tarefas/Atividades** → atividade da GS de RPA → **Adicionar trabalho** →
   *Carregar deste dispositivo* → selecione o ZIP → **Entregar**. Um integrante entrega pela equipe.
4. Tire um print da confirmação de entrega (comprovante) antes de 19/11/2026 23h55.
