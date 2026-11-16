# Relatório de comparação: triagem automática × rótulo manual

> **AVISO IMPORTANTE — BASE SINTÉTICA.** Todas as imagens avaliadas aqui foram **geradas por computador** (`scripts/gerar_imagens_sinteticas.py`) e o "rótulo manual" é o **rótulo esperado por construção** da cena. O gerador e a regra de classificação foram escritos pela mesma equipe, a partir das mesmas hipóteses físicas (buraco = região escura, rugosa e de borda abrupta), e os limiares foram ajustados observando estas mesmas imagens — então a concordância tende a ser **otimista**. Estes números **NÃO medem o desempenho no mundo real** e **não podem ser apresentados como acurácia** do AcessaCidade. Servem para verificar o funcionamento do fluxo e para discutir os tipos de erro.

- Gerado em: 2026-11-15 01:51 UTC por `scripts/avaliar_comparacao.py`
- Base: **SINTETICA**
- Predições: `dados_extraidos.csv` · Rótulos: `rotulos_manuais_sinteticas.csv`
- Imagens comparadas: **25**
- Concordância total: **20/25** (80,0%) — concordância com o rótulo esperado por construção, **não** acurácia no mundo real.

## Matriz de confusão

Linhas = rótulo manual; colunas = predição da triagem.

| Manual \ Predição | POSSÍVEL BURACO | NÃO IDENTIFICADO | INCONCLUSIVO | Total |
|---|---:|---:|---:|---:|
| **POSSÍVEL BURACO** | 8 | 1 | 0 | 9 |
| **NÃO IDENTIFICADO** | 1 | 8 | 3 | 12 |
| **INCONCLUSIVO** | 0 | 0 | 4 | 4 |

## Acertos por classe

| Classe | Imagens | Acertos | Taxa de acerto (revocação) | Precisão |
|---|---:|---:|---:|---:|
| POSSÍVEL BURACO | 9 | 8 | 88,9% | 88,9% |
| NÃO IDENTIFICADO | 12 | 8 | 66,7% | 88,9% |
| INCONCLUSIVO | 4 | 4 | 100,0% | 57,1% |

## Leitura dos erros

- **Falsos positivos** (marcado como possível buraco sem haver buraco): 1.
- **Falsos negativos** (buraco marcado como "nenhum indício"): 1.
- **Erros conservadores** (algo marcado como inconclusivo, indo para revisão humana): 3.

| Imagem | Cenário | Manual | Predição | Pontuação | Discussão |
|---|---|---|---|---:|---|
| [sintetica_buraco_raso_01.jpg](sintetica_buraco_raso_01/painel_etapas.jpg) | buraco_dificil | POSSÍVEL BURACO | NÃO IDENTIFICADO | 0.2723 | Falso negativo em buraco difícil (raso ou cheio de água): pouco contraste ou fundo liso demais. |
| [sintetica_sombra_03.jpg](sintetica_sombra_03/painel_etapas.jpg) | sombra | NÃO IDENTIFICADO | INCONCLUSIVO | 0.4628 | Sombra marcada como inconclusiva: região escura compacta com textura/borda ambíguas. Erro conservador (vai para revisão humana). |
| [sintetica_mancha_01.jpg](sintetica_mancha_01/painel_etapas.jpg) | mancha | NÃO IDENTIFICADO | INCONCLUSIVO | 0.5175 | Mancha marcada como inconclusiva: escura e compacta, mas sem a rugosidade de um buraco. Erro conservador. |
| [sintetica_tampa_bueiro_01.jpg](sintetica_tampa_bueiro_01/painel_etapas.jpg) | tampa_bueiro | NÃO IDENTIFICADO | POSSÍVEL BURACO | 0.7229 | Falso positivo em tampa de bueiro: disco escuro, com relevo (textura alta) e aro de borda abrupta — a regra não distingue objetos fabricados. |
| [sintetica_poca_01.jpg](sintetica_poca_01/painel_etapas.jpg) | poca | NÃO IDENTIFICADO | INCONCLUSIVO | 0.5928 | Poça marcada como inconclusiva: escura e com borda nítida, porém fundo liso. Erro conservador; na prática uma poça pode esconder um buraco. |

## Limitações e próximos passos

- A pontuação é **heurística** (soma ponderada de critérios), não uma probabilidade calibrada.
- Sombras, manchas, poças, tampas de bueiro e rachaduras largas podem gerar falsos positivos; buracos rasos, cheios de água ou da mesma cor do piso podem gerar falsos negativos.
- Toda triagem passa por **revisão humana** (status "Aguardando revisão").
- Próximo passo obrigatório: repetir esta comparação com **fotos reais** rotuladas manualmente (`samples/real/`, ver `PENDENCIAS_E_ACOES_MANUAIS.txt`). [PREENCHER: resultados da base real, quando existirem]

Cada imagem tem o painel com todas as etapas em `results/<nome>/painel_etapas.jpg`.
