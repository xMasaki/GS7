# Roteiro do vídeo — RPA (até 3 minutos)

Exigência da disciplina: vídeo explicativo da solução **com a automação rodando**, com uma pessoa
explicando (não precisa aparecer o rosto). Duração máxima: **3:00**. Vale 3 pontos.

## Preparação (antes de gravar)

- [ ] AcessaCidade no ar (localhost ou URL pública Azure) e `#/registrar?canal=rpa` abrindo com o selo
      "Canal: automação (RPA)".
- [ ] Projeto aberto no UiPath Studio, sem erros no Error List; seletores validados.
- [ ] Planilha de entrada restaurada (rode `scripts/gerar_planilhas.py`) e planilha de saída apagada
      (`spreadsheet/denuncias_resultado_RPA.xlsx`), para a execução começar do zero.
- [ ] Para caber no tempo: deixe na planilha só **4 linhas** (por exemplo, 01, 02, 04 e 11 — uma com foto,
      uma sem foto, uma com foto e uma negativa). Faça isso numa **cópia** e aponte o Config para ela, ou
      acelere o trecho da execução na edição (informe "vídeo acelerado 2x" na tela).
- [ ] Excel fechado; notificações do Windows desativadas; zoom do navegador em 100 %.
- [ ] Gravador: OBS Studio, Xbox Game Bar (`Win + G`) ou Clipchamp, com microfone.
- [ ] Nenhum dado real na tela (apenas dados simulados; nada de e-mails/tokens pessoais).

## Roteiro com tempos

| Tempo | Tela | Fala (sugestão — adapte com suas palavras) |
|---|---|---|
| 0:00–0:20 | Página inicial do AcessaCidade | "Este é o AcessaCidade, plataforma para registrar e acompanhar problemas de acessibilidade em calçadas. Muitas denúncias chegam de associações em planilhas, e alguém precisa digitá-las uma a uma." |
| 0:20–0:45 | Planilha de assessment (aba Assessment) e diagrama As-Is | "Avaliamos três processos candidatos. O cadastro de denúncias de parceiros teve [PREENCHER: % final após revisão da equipe — preliminar 79,4 %], alta aptidão para RPA. No As-Is, o operador digita, confere e devolve o protocolo manualmente." |
| 0:45–1:00 | Trecho do `ANALISE_RPA_VS_API.md` ou slide | "O AcessaCidade tem API, então por que RPA? Porque os parceiros não têm TI para integrar: o robô é a ponte de transição, e a planilha-modelo já prepara a futura importação nativa." |
| 1:00–1:20 | UiPath Studio: `Main.xaml` e `ProcessarDenuncia.xaml` | "No UiPath, o Main lê a configuração e a planilha, e para cada linha, dentro de um Try/Catch, chama o ProcessarDenuncia, que preenche o formulário pelos ids estáveis e captura o protocolo." |
| 1:20–2:20 | Clicar em **Run**; navegador sendo preenchido; painel Output | "Agora o robô está rodando: abre o formulário no canal RPA, preenche endereço, tipo, impacto, anexa a foto sintética, marca o consentimento e envia. Aqui ele capturou o protocolo. Esta linha tinha descrição curta: o robô não envia e registra falha de negócio, sem parar o lote." |
| 2:20–2:45 | Planilha de saída e `#/consultar` com um protocolo | "Na planilha de saída, cada linha tem status, protocolo, mensagem e data. No AcessaCidade, a denúncia aparece com origem RPA, pronta para a triagem e revisão humana." |
| 2:45–3:00 | Diagrama To-Be | "Com o robô, o operador só trata exceções. Os números do business case são premissas que vamos validar com parceiros. Obrigado!" |

## Depois de gravar

1. Confira a duração (≤ 3:00) e o áudio.
2. Publique no YouTube como **Não listado** (ou Google Drive/OneDrive com "qualquer pessoa com o link
   pode ver").
3. Abra o link numa janela anônima para confirmar que abre sem login.
4. Cole o link em `entrega/link_video.txt` (ver `INSTRUCOES_ZIP_ENTREGA.md`) e no `RELATORIO_RPA.md`
   (`[PREENCHER: link do vídeo]`).
