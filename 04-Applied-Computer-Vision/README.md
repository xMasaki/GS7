# AcessaCidade — Visão Computacional (Applied Computer Vision)

> Disciplina 4 de 7 da Global Solution 2026.2 (CitizenTech, ODS 11) — atividade **"Pitch Visão Computacional"**.
> Componente **Visão**: "enxerga o problema por imagens e transforma o que vê em informação".

O cidadão (pessoa com deficiência, cadeirante, pessoa idosa ou com mobilidade reduzida) registra no AcessaCidade
uma denúncia de problema de acessibilidade e pode anexar uma foto. Este componente:

1. **valida** a foto pelo conteúdo real (não pela extensão);
2. **protege a privacidade**: remove EXIF/GPS, reduz a resolução e borra rostos;
3. **faz a triagem automática** com OpenCV clássico (sem redes neurais), em 7 etapas visíveis;
4. **extrai dados** (brilho, contraste, nitidez, área, forma, contraste interno/externo, bordas, caixas delimitadoras);
5. **classifica de forma explicável** em `POSSIBLE_POTHOLE`, `NOT_IDENTIFIED` ou `INCONCLUSIVE`,
   com pontuação heurística (0–1, **não é probabilidade**) e frases em português explicando a decisão.

O resultado é **apoio** à equipe: a denúncia com foto vai para o status "Aguardando revisão" e uma pessoa
confirma ou descarta (`revisao_humana`). A triagem não substitui avaliação técnica.

## Estrutura

```text
04-Applied-Computer-Vision/
├── src/acessacidade_vision/      # pacote importado pelo backend (contrato, seção 5)
│   ├── __init__.py               # interface pública
│   ├── constants.py              # versão, etapas, rótulos e TODOS os limiares
│   ├── errors.py                 # VisionError(code, message)
│   ├── validation.py             # assinatura, cabeçalho, decodificação real, dimensões
│   ├── privacy.py                # sanitize_image: re-encode JPEG, redimensiona, borra rostos (Haar)
│   ├── preprocessing.py          # cinza, filtro gaussiano, qualidade, CLAHE, perspectiva (opcional)
│   ├── segmentation.py           # Otsu + limiar robusto, Canny, morfologia, contornos
│   ├── features.py               # medidas de cada região candidata
│   ├── classifier.py             # regra explicável + frases em português
│   ├── visualize.py              # contornos/caixas/rótulos e painel de etapas
│   └── pipeline.py               # analyze_image, AnalysisResult
├── scripts/
│   ├── gerar_imagens_sinteticas.py   # base SINTÉTICA (semente fixa) em data/samples/fotos/
│   ├── analisar_pasta.py             # processa uma pasta e salva etapas + dados (results/)
│   ├── avaliar_comparacao.py         # predição × rótulo manual (matriz de confusão)
│   └── sanitizar_fotos.py            # limpa fotos reais antes de versionar
├── samples/
│   ├── rotulos_manuais_sinteticas.csv    # rótulos esperados POR CONSTRUÇÃO (sintéticas)
│   └── real/                              # modelo e instruções para a coleta real
├── results/                      # saídas REAIS das execuções (etapas, CSV/JSON, relatório)
├── tests/test_vision_*.py        # testes automatizados (pytest)
└── docs/                         # documentação técnica, relatório de entrega, roteiro do vídeo
```

## Como rodar

Pré-requisito: Python 3.11 e o venv da raiz (`python -m pip install -r requirements-dev.txt`).
Os comandos abaixo são para PowerShell, **na raiz do repositório**.

```powershell
# 1) Gerar a base sintética (25 imagens, semente fixa 2026)
.\.venv\Scripts\python.exe 04-Applied-Computer-Vision\scripts\gerar_imagens_sinteticas.py

# 2) Processar a pasta: imagens das etapas + dados extraídos em 04-Applied-Computer-Vision\results\
.\.venv\Scripts\python.exe 04-Applied-Computer-Vision\scripts\analisar_pasta.py

# 3) Comparar com os rótulos manuais (matriz de confusão + relatório)
.\.venv\Scripts\python.exe 04-Applied-Computer-Vision\scripts\avaliar_comparacao.py

# 4) Testes automatizados
.\.venv\Scripts\python.exe -m pytest 04-Applied-Computer-Vision\tests
```

Uso direto em Python:

```python
from acessacidade_vision import validate_image_bytes, sanitize_image, analyze_image

data = open("data/samples/fotos/sintetica_buraco_01.jpg", "rb").read()
validate_image_bytes(data, max_bytes=5 * 1024 * 1024)   # levanta VisionError(code, message) se inválida
limpa = sanitize_image(data, max_side=1600)              # JPEG sem EXIF/GPS, rostos borrados
res = analyze_image(limpa)
print(res.classification, res.score)                     # ex.: POSSIBLE_POTHOLE 0.9354
print(res.to_dict()["explicacao"])                       # frases em português
etapas = res.encode_stages(".jpg", 85)                    # {"original": b"...", ..., "contornos": b"..."}
```

## Integração com o backend (contrato de integração, seções 4 e 5)

O pacote é **importado** pelo backend FastAPI (`app/backend/acessacidade_api`), sem cópia de código
(`pytest.ini` e o `PYTHONPATH` do Docker já incluem `04-Applied-Computer-Vision/src`).

| Rota | O que o backend faz com este pacote |
|---|---|
| `POST /api/visao/analisar` (multipart, campo `foto`) | `validate_image_bytes` → `sanitize_image` → `analyze_image`; devolve `to_dict()` + `imagens` como `data:image/jpeg;base64,...` (de `encode_stages()`). **Não salva nada.** |
| `POST /api/denuncias` (multipart, `foto` opcional) | mesmo fluxo; grava `encode_stages()` em `DATA_DIR/uploads/<uuid>/<etapa>.jpg` (a "original" salva é a **sanitizada**), guarda `to_dict()` no campo `visao` e muda o status para `AGUARDANDO_REVISAO`. |
| `GET /api/denuncias/{id}/imagens/{etapa}` | serve as imagens das etapas `original, cinza, filtrada, contraste, bordas, mascara, contornos`. |

- `to_dict()` → `{"classificacao","rotulo","pontuacao","explicacao","metricas","deteccoes","versao_algoritmo","aviso"}`.
- `deteccoes[*]` → `{"x","y","largura","altura","area_px","area_relativa","pontuacao","tipo"}`; as coordenadas
  referem-se à imagem de análise (maior lado 800 px), a mesma das imagens das etapas.
- Erros de entrada levantam `VisionError(code, message)`; `message` já está em português para o `detail` (HTTP 422).
  Códigos: `EMPTY_IMAGE`, `FILE_TOO_LARGE`, `UNSUPPORTED_FORMAT`, `INVALID_IMAGE`, `IMAGE_TOO_SMALL`,
  `IMAGE_DIMENSIONS_TOO_LARGE`, `INVALID_INPUT`, `INVALID_POINTS`, `ENCODE_FAILED`.
- Métricas Prometheus (`acessacidade_visao_*`) são registradas pelo backend, não por este pacote.

## Resultados atuais (base SINTÉTICA)

Execução real de `avaliar_comparacao.py` em 25 imagens sintéticas: **20/25 concordâncias** com o rótulo
esperado por construção (1 falso positivo — tampa de bueiro; 1 falso negativo — buraco raso; 3 casos sem
buraco marcados como inconclusivos — sombra, mancha e poça). Detalhes: [`results/RELATORIO_COMPARACAO.md`](results/RELATORIO_COMPARACAO.md).

**Isto não é acurácia no mundo real.** As imagens são sintéticas, o gerador e a regra partem das mesmas
hipóteses e os limiares foram ajustados observando estas imagens. A avaliação com fotos reais está pendente
(ver [`PENDENCIAS_E_ACOES_MANUAIS.txt`](PENDENCIAS_E_ACOES_MANUAIS.txt)).

## Limites conhecidos

- Regra heurística sobre "região escura + rugosa + borda abrupta": **sombras, manchas, poças, tampas de bueiro,
  rachaduras largas e juntas** podem gerar falsos positivos; **buracos rasos, cheios de água ou da cor do piso**
  podem não ser detectados.
- Sombra extensa (metade da foto) altera a referência de brilho do piso; um buraco dentro dela pode passar despercebido.
- Medidas em pixels: sem referência de escala não há medida em centímetros (a correção de perspectiva é opcional e manual).
- O detector de rostos (Haar) não encontra rostos de perfil, pequenos ou parcialmente cobertos; em fotos coloridas,
  detecções sem cor (pavimento) são descartadas para não borrar o piso. Orientação ao cidadão: **não fotografar pessoas**.
- OCR não é usado: o problema é a condição física do piso; ler texto (placas, números de casas) não ajudaria a triagem e
  aumentaria o risco de coletar dado pessoal.

Documentação completa: [`docs/DOCUMENTACAO_TECNICA_TRANSFORMACOES.md`](docs/DOCUMENTACAO_TECNICA_TRANSFORMACOES.md) ·
Relatório de entrega (fonte do PDF): [`docs/RELATORIO_ENTREGA_VISAO.md`](docs/RELATORIO_ENTREGA_VISAO.md) ·
Roteiro do vídeo: [`docs/ROTEIRO_VIDEO_VISAO.md`](docs/ROTEIRO_VIDEO_VISAO.md) ·
Evidências: [`docs/EVIDENCIAS_NECESSARIAS.md`](docs/EVIDENCIAS_NECESSARIAS.md).
