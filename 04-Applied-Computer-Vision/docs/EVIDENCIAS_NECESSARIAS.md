# Evidências necessárias — Applied Computer Vision

Lista do que comprova cada entregável oficial. "Já existe" = gerado executando o código nesta entrega.
"Pendente" = só a equipe pode produzir (não pode ser inventado).

## 1. Já existe (gerado de verdade)

| Evidência | Arquivo | Como reproduzir |
|---|---|---|
| Base de teste sintética (25 imagens, semente 2026) | `data/samples/fotos/sintetica_*.jpg` + `LEIAME.txt` | `scripts/gerar_imagens_sinteticas.py` |
| Imagens intermediárias das 7 etapas, por imagem | `results/<nome>/{original,cinza,filtrada,contraste,bordas,mascara,contornos}.jpg` + `painel_etapas.jpg` | `scripts/analisar_pasta.py` |
| Dados extraídos por imagem | `results/dados_extraidos.csv`, `results/dados_extraidos.json`, `results/<nome>/resultado.json` | `scripts/analisar_pasta.py` |
| Comparação com rótulos manuais (base SINTÉTICA) | `results/comparacao_manual.csv`, `results/RELATORIO_COMPARACAO.md` (20/25 concordâncias — não é acurácia real) | `scripts/avaliar_comparacao.py` |
| Testes automatizados | `tests/test_vision_*.py` — **45 passed** (2026-11-15) | `.\.venv\Scripts\python.exe -m pytest 04-Applied-Computer-Vision/tests` |
| Documentação das transformações | `docs/DOCUMENTACAO_TECNICA_TRANSFORMACOES.md` | — |
| Fonte do PDF único | `docs/RELATORIO_ENTREGA_VISAO.md` + `docs/gerar_pdf_relatorio.py` | ver seção 3 |

## 2. Pendente (a equipe precisa produzir)

| # | Evidência | Para qual critério | Como produzir | Onde guardar / citar |
|---|---|---|---|---|
| E1 | **Vídeo** até 5 min, todos os integrantes, demo na URL pública | Vídeo (3 pts) | `docs/ROTEIRO_VIDEO_VISAO.md` | YouTube público/não listado → `docs/links_entrega.yaml` (`url_video`) |
| E2 | **URL pública** do MVP funcionando com `#/analise` e registro com foto | Automação (8 pts) | Deploy do componente 06 | `links_entrega.yaml` (`url_mvp`) |
| E3 | **Repositório público** com `results/` e `data/samples/fotos/` | Documentação (3 pts) | GitHub → Settings → visibilidade pública | `links_entrega.yaml` (`url_repositorio`) |
| E4 | Print de `#/analise` com o resultado e as 7 etapas (URL pública visível) | Automação | Navegador, Win + Shift + S | `evidencias/visao_analise_<data>.png` |
| E5 | Print de `#/denuncia/{protocolo}` com status "Aguardando revisão" e etapas salvas | Automação / integração | Registrar denúncia fictícia com foto | `evidencias/visao_denuncia_<data>.png` |
| E6 | Print de foto ruim (escura/borrada) → "Análise inconclusiva" | Explicabilidade | Enviar `sintetica_escura_01.jpg` em `#/analise` | `evidencias/visao_inconclusiva_<data>.png` |
| E7 | (Recomendado) **Fotos reais** de calçadas, autorizadas, sem pessoas/placas identificáveis, com rótulo manual | "Dados reais" do conceito da atividade | `samples/real/LEIAME_COLETA_REAL.txt` + `rotulos_manuais_reais_TEMPLATE.csv` | `samples/real/` (somente após sanitizar com `scripts/sanitizar_fotos.py`) |
| E8 | (Recomendado) Comparação com a base real | Valor demonstrado com dados reais | Rodar `analisar_pasta.py` e `avaliar_comparacao.py` na pasta real (ver PENDENCIAS) | Relatório real citado na seção 5 do `RELATORIO_ENTREGA_VISAO.md` |
| E9 | PDF único com links clicáveis | Formato de entrega | `gerar_pdf_relatorio.py --estrito` | `docs/entrega/AcessaCidade_Visao_Computacional.pdf` |
| E10 | Comprovante de envio no portal | Entrega | Portal FIAP | Guardar print fora do repositório |

## 3. Regras para as evidências

- Nada de rostos, placas de veículos, números de casas legíveis ou dados pessoais nos prints e fotos.
- Fotos reais só com autorização do local/pessoas e depois de sanitizadas (EXIF/GPS removidos).
- Sempre identificar imagens sintéticas como **sintéticas** e dados de demonstração como **simulados**.
- Não editar números dos relatórios gerados: se algo mudar, rode os scripts de novo.
- Use "Cidade Exemplo" e dados fictícios nas denúncias de demonstração.
