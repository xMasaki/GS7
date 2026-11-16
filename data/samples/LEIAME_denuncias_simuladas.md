# LEIAME — `denuncias_simuladas.csv` (fonte SIMULADA do pipeline de dados)

> **Todos os dados deste arquivo são SIMULADOS (sintéticos).** Não há denúncias reais, pessoas
> reais nem ruas reais. A cidade é a fictícia **"Cidade Exemplo"**; os nomes de denunciantes são
> marcadores do tipo `Pessoa Simulada 017`. Toda linha tem `origem_dado=SIMULADO`.

## Por que existe

O AcessaCidade é um MVP novo: ainda não existe histórico real de denúncias de acessibilidade.
Para que o pipeline ELT (disciplina 02 — Big Data Architecture & Data Integration) tenha o que
tratar — e para mostrar o que cada camada raw → bronze → silver → gold resolve — geramos uma
exportação "bagunçada" de um **sistema legado fictício** da prefeitura fictícia da Cidade Exemplo,
reproduzindo problemas típicos de cadastros reais. A segunda fonte do pipeline é a exportação da
própria API do AcessaCidade (`GET /api/export/denuncias?formato=csv`), já limpa.

## Como foi gerado

- Script: `02-Big-Data-Architecture/src/acessacidade_pipeline/simulate.py`
- Comando (na raiz do repositório, com o `.venv` ativo):
  ```powershell
  $env:PYTHONPATH = "02-Big-Data-Architecture/src"
  .\.venv\Scripts\python.exe -m acessacidade_pipeline.simulate
  ```
- Semente fixa `20261114` → o arquivo é **sempre idêntico** (verificado: duas gerações com o mesmo
  hash MD5 `e1792546864d085d8d49cbf1c3d31e1f`).
- Se o arquivo não existir, o próprio pipeline o gera na etapa de extração.

## Conteúdo

- **271 linhas** + cabeçalho, UTF-8, separador vírgula.
- Colunas: as 21 da exportação da API (contrato 4.7: `id, protocolo, criado_em, atualizado_em,
  logradouro, numero, bairro, cidade, ponto_referencia, tipo_obstaculo, descricao, impacto, latitude,
  longitude, status, origem, simulado, possui_imagem, visao_classificacao, visao_pontuacao,
  revisao_humana`) **mais** `nome_denunciante` e `origem_dado`.
- Composição: 250 denúncias-base + 10 quase-duplicatas + 11 duplicatas exatas (≈4%).
- Datas de registro entre **2026-08-01 e 2026-11-13** (horário local).
- Protocolos no formato `SIM-2026-000123` (prefixo `SIM` deixa claro que não são protocolos do app).

## Problemas inseridos de propósito (e qual camada trata)

| Problema | Exemplo | Tratado em |
|---|---|---|
| Duplicatas exatas (linha repetida campo a campo) | 11 linhas | Bronze (dedup técnico) |
| Datas em vários formatos | `2026-10-27T22:11:20Z`, `12/08/2026`, `08-08-2026 00:24`, `14 de outubro de 2026` | Bronze (`parse_data_multi`) |
| Datas inválidas/irreconhecíveis | `31/09/2026`, `2026-13-05`, `ontem`, `sem data`, vazio | Bronze (flag) + Silver (RN-09) |
| Coordenadas como texto, vírgula ou ponto, espaços | `"-48,322707"`, `" -10.157506 "` | Bronze (`parse_coordenada`) |
| Coordenadas inválidas, fora do Brasil ou vazias | `abc`, `-10.18.2`, latitude `-123.4`, `0,0`, pontos fora do Brasil (ex.: `38,722300 / -9,139300`), vazio | Bronze (flag) + Silver (RN-10) |
| Bairro com grafias diferentes (42 variações para 9 bairros) | `Jd das Flores`, `CENTRO`, ` Centro `, `Bela  Vista`, `SAO JOSE` | Silver (RN-01) |
| Bairro fora do dicionário | `Recanto Verde` | Silver (mantido, `flag_bairro_nao_padronizado`) |
| Tipo de obstáculo em texto livre (38 variações) | `buraco`, `Buraco na calcada`, `BURACO_CALCADA`, `piso solto na calçada` | Silver (RN-04) |
| Impacto em texto livre | `impede`, `risco acidente`, `DIFICULTA_PASSAGEM` | Silver (RN-05) |
| Status com variações (nunca `ENCAMINHADA`/`RESOLVIDA`) | `Em Analise`, ` RECEBIDA`, `aguardando revisao`, vazio | Silver (RN-06) |
| Classificação da visão em vários formatos, incl. vazio | `possible_pothole`, `Análise inconclusiva`, vazio | Silver (RN-07) |
| Booleanos em vários formatos | `1`, `true`, `TRUE` | Bronze |
| Campos obrigatórios ausentes | logradouro, bairro, tipo, impacto ou descrição vazios | Bronze (flag) + Silver (RN-12) |
| Quase-duplicatas (mesma ocorrência registrada 2x no mesmo dia, outra grafia) | 10 linhas | Silver (RN-11) |
| Dado pessoal (`nome_denunciante`) em 161 linhas | `Pessoa Simulada 060` | Fica só na RAW; Bronze guarda apenas `flag_possui_nome` (LGPD) |

## Uso e limites

- Serve **apenas** para demonstrar e testar o pipeline. Os números da camada Gold calculados a
  partir dele **não** representam nenhuma cidade real e não devem ser apresentados como dados reais.
- O snapshot publicado traz `"inclui_simulados": true` e a fonte `denuncias_simuladas.csv`.
