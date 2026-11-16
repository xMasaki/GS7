# Evidências necessárias (prints, arquivos e links)

Nenhuma destas evidências foi produzida automaticamente: elas dependem do UiPath Studio, do Excel e do
AcessaCidade rodando. Salve os prints em `05-Robotic-Process-Automation/evidencias/` com os nomes
sugeridos (PNG). O relatório (`RELATORIO_RPA.md`) referencia esses nomes.

| # | Evidência | Como produzir | Nome sugerido | Usada em |
|---|---|---|---|---|
| E1 | Print da planilha de assessment (aba **Assessment**) com os valores calculados e a classificação | Abrir `spreadsheet/assessment_rpa_AcessaCidade.xlsx` no Excel (ele recalcula as fórmulas), revisar notas com a equipe, `Win + Shift + S` | `E1_assessment.png` | Relatório (obrigatório pelo PDF da GS) |
| E2 | Print da aba **Processos candidatos** | Mesmo arquivo | `E2_processos_candidatos.png` | Relatório |
| E3 | Diagramas As-Is e To-Be | Abrir os `.bpmn` em https://demo.bpmn.io → *Download as PNG/SVG* (ou usar os `.svg` já gerados em `process-mapping/`) | `E3_as_is.png`, `E3_to_be.png` | Relatório |
| E4 | Print do workflow `Main.xaml` no Studio | Studio aberto, designer com o fluxo visível (zoom para caber) | `E4_main_xaml.png` | Relatório ("print da solução") |
| E5 | Print do `ProcessarDenuncia.xaml` | Idem, mostrando Type Into/Select Item/Click | `E5_processar_denuncia.png` | Relatório |
| E6 | Print do painel **Output** com o resumo final (totais) | Após a execução | `E6_execucao_output.png` | Relatório |
| E7 | Print do navegador durante o preenchimento (selo "Canal: automação (RPA)") | Durante a execução | `E7_formulario_rpa.png` | Relatório |
| E8 | Planilha de saída preenchida | `spreadsheet/denuncias_resultado_RPA.xlsx` (gerada pelo robô) + print | arquivo + `E8_planilha_saida.png` | ZIP e relatório |
| E9 | Denúncia no AcessaCidade com **origem RPA** | `#/consultar` → buscar um protocolo da planilha de saída → print do detalhe | `E9_denuncia_origem_rpa.png` | Relatório |
| E10 | Print do Error List vazio (ou com avisos explicados) | Studio → View → Error List | `E10_error_list.png` | Relatório (transparência) |
| E11 | Link do vídeo (≤ 3 min) | `ROTEIRO_VIDEO_RPA.md` | `entrega/link_video.txt` | ZIP e relatório |
| E12 | PDF do relatório | `INSTRUCOES_ZIP_ENTREGA.md` | `entrega/RELATORIO_RPA_AcessaCidade.pdf` | ZIP |

Cuidados:

- Somente dados **simulados** na tela; nenhum token, e-mail pessoal ou dado real de cidadão.
- Se executar contra a URL pública da Azure, registre a URL no relatório como
  `[PREENCHER: URL pública]` até ela existir de fato.
- Não edite prints para "melhorar" resultados: se houver linhas `FALHA_SISTEMA`, mostre e explique.
