# Regras do pipeline AcessaCidade

Separação adotada (mesma da Aula 06): **regras técnicas** (Bronze) tornam o dado *utilizável* sem decidir nada sobre
o negócio; **regras de negócio** (Silver/Gold) aplicam o que o AcessaCidade entende por denúncia, bairro, categoria,
status e registro válido. Implementação: `src/acessacidade_pipeline/parsing.py` (técnicas), `regras.py` e
`silver.py` (negócio), `gold.py` (agregação). Cada regra é coberta por testes em `tests/test_pipeline_*.py`.

## Regras técnicas (camada Bronze)

| Código | Regra |
|---|---|
| RT-01 | **RAW fiel**: tudo `VARCHAR`, mesmas linhas da fonte, + `_source_file`, `_ingested_at`, `_row_id`, `_batch_id`. Full refresh. |
| RT-02 | **Dedup técnico**: linha 100% idêntica a outra (todas as colunas de origem) é duplicata de exportação; mantém-se a de menor `_row_id`, por fonte. |
| RT-03 | **Datas** (`parse_data_multi`): aceita ISO 8601 (com `Z`/offset ou sem), `dd/mm/aaaa [hh:mm[:ss]]`, `dd-mm-aaaa [hh:mm]` e "14 de outubro de 2026". Sem fuso → horário de Brasília (UTC−3) convertido para UTC. Data impossível (`31/09/2026`) ou texto (`ontem`) → `NULL` + `flag_data_invalida`. |
| RT-04 | **Coordenadas** (`parse_coordenada`): texto com vírgula ou ponto → `DOUBLE`. Não numérica, par incompleto ou fora de −90..90 / −180..180 → `NULL` + `flag_coordenada_invalida`. |
| RT-05 | **Booleanos** (`parse_booleano`): `true/1/sim/s/...` e `false/0/nao/...`; outro valor → `NULL`. |
| RT-06 | **Pontuação da visão**: decimal 0..1; fora disso → `NULL` + `flag_pontuacao_invalida`. |
| RT-07 | **Campos obrigatórios** vazios são sinalizados (`flag_*_ausente`, `flag_campo_obrigatorio_ausente`), não descartados. |
| RT-08 | **Minimização LGPD**: `nome_denunciante` só existe na RAW; a Bronze guarda apenas `flag_possui_nome`. Nenhuma camada posterior tem nome. |

## Regras de negócio (camada Silver e Gold)

| Código | Regra | Exemplo |
|---|---|---|
| RN-01 | **Bairro**: normaliza (sem acento, minúsculas, espaços únicos), expande abreviações (`jd/jdm/jard`→jardim, `v/vl`→vila, `s`→são, `sto/sta`→santo/santa, `pq/pque/prq`→parque, `res`→residencial, `conj/cj`→conjunto) e consulta o dicionário de bairros fictícios da Cidade Exemplo (Centro, Jardim das Flores, Vila Nova, São José, Bela Vista, Parque das Árvores, Santa Luzia, Nova Esperança). Fora do dicionário: mantém em "Formato Título" e marca `flag_bairro_nao_padronizado`. | `Jd das Flores`, `JARDIM DAS FLORES ` → `Jardim das Flores`; `recanto verde` → `Recanto Verde` (flag) |
| RN-02 | **Cidade**: variações de "Cidade Exemplo" (`cid. exemplo`, `CIDADE EXEMPLO`) → `Cidade Exemplo`; vazio → `Não informada`. | |
| RN-03 | **Endereço normalizado**: logradouro sem acento/minúsculo com o tipo expandido (`r`→rua, `av`→avenida, `tv`→travessa, `pc/pça`→praça...); número `S/N`/`sn` → `S/N`, demais compactados em maiúsculas. | `AV CENTRAL` ≡ `Avenida Central` |
| RN-04 | **Tipo de obstáculo** → chave do contrato 3.1: (1) chave exata ou rótulo exato (sem acento/caixa); (2) palavras-chave em ordem: `tatil`→PISO_TATIL; `rampa`→RAMPA_IRREGULAR; `buraco`+(`via/rua/travessia/asfalto/pista/faixa`)→BURACO_VIA; `buraco`→BURACO_CALCADA; `quebrada/desnivel/danificada/rachada/solto/irregular`→CALCADA_DANIFICADA; `poste/lixeira/placa/orelhao/hidrante`→OBSTACULO_FIXO; `entulho/veiculo/carro/obra/tapume/cacamba`→OBSTACULO_TEMPORARIO; `outro(s)`→OUTRO. Sem correspondência → `NULL` + `flag_tipo_nao_reconhecido`. | `buraco`, `BURACO_CALCADA`, `Buraco na calcada` → `BURACO_CALCADA` |
| RN-05 | **Impacto** → contrato 3.2: chave/rótulo exatos ou palavras (`impede/bloqueia/intransitavel`→IMPEDE_PASSAGEM; `dificulta/atrapalha`→DIFICULTA_PASSAGEM; `risco/queda/acidente/perigo`→RISCO_QUEDA; `baixo/leve/pequeno`→BAIXO_IMPACTO). Sem correspondência → `NULL` + flag. | `risco acidente` → `RISCO_QUEDA` |
| RN-06 | **Status** → contrato 3.3 (chave, rótulo e sinônimos como `em analise`, `aguardando revisao`). Ausente ou irreconhecível → `RECEBIDA` (status inicial do contrato) + `flag_status_inferido`. A fonte simulada nunca contém `ENCAMINHADA`/`RESOLVIDA`. | `Em Analise` → `EM_ANALISE`; `pendente` → `RECEBIDA` (flag) |
| RN-07 | **Visão computacional** → contrato 3.4 (`POSSIBLE_POTHOLE`, `NOT_IDENTIFIED`, `INCONCLUSIVE`; sinônimos e rótulos aceitos). Sem fotografia → classificação e pontuação `NULL` ("Sem fotografia (não analisada)"). `possui_imagem` ausente é deduzido da existência de classificação; classificação com `possui_imagem=false` é descartada e marcada `flag_visao_inconsistente`. | |
| RN-08 | **Origem e dado simulado**: origem → `WEB`/`RPA`/`SIMULADO`/`API` (contrato 3.5). `dado_simulado = simulado OR origem_dado='SIMULADO' OR origem='SIMULADO'`. | |
| RN-09 | **Data plausível**: válida se reconhecida e entre 2020-01-01 e (instante da execução + 1 dia). `data_registro` = data local (UTC−3) usada nos períodos. | |
| RN-10 | **Área de atendimento**: coordenada válida só dentro da caixa envolvente aproximada do Brasil (lat −33,8..5,3; lon −74,0..−28,8). Fora → latitude/longitude `NULL` + `flag_coordenada_fora_area`. Coordenada ausente **não** invalida a denúncia (o cidadão pode não compartilhar a localização). | `0,0`, `38.72/−9.14` → fora |
| RN-11 | **Dedup de negócio** (quase-duplicata): mesma ocorrência = mesmo endereço normalizado (RN-03) + mesmo tipo (RN-04) + mesma `data_registro`. Mantém o registro válido, depois o mais antigo; os demais vão para `silver.denuncias_duplicadas` com `chave_denuncia_mantida`. Registros sem endereço/tipo/data não são agrupados. | |
| RN-12 | **Registro válido**: data válida (RN-09), logradouro com ≥ 3 caracteres, bairro, tipo de obstáculo reconhecido, impacto reconhecido e descrição com ≥ 10 caracteres. Os motivos de falha ficam em `motivos_invalidade`. | |
| RN-13 | **Gold**: agrega somente `registro_valido = true`; não contém nome, descrição, logradouro nem coordenadas; categorias e status aparecem todos (inclusive com zero) para manter a legenda estável no dashboard. | |

## Indicadores de qualidade (contrato 4.8, campo `qualidade`)

| Métrica | Definição |
|---|---|
| linhas_raw | linhas na RAW (todas as fontes) |
| linhas_bronze | linhas após o dedup técnico (RT-02) |
| duplicatas_removidas | `linhas_raw − linhas_bronze` |
| datas_invalidas | denúncias (Bronze) com data ausente, irreconhecível ou implausível (RN-09) |
| coordenadas_invalidas | coordenada informada inválida (RT-04) ou fora do Brasil (RN-10) |
| campos_obrigatorios_ausentes | denúncias com algum obrigatório vazio (RT-07) |
| percentual_registros_validos | válidos (RN-12) / denúncias únicas da Silver × 100, 1 casa |

## Verificações automáticas (tarefa `quality_report`)

RAW não vazia; RAW fiel à fonte simulada (contagem igual ao arquivo); BRONZE ≤ RAW; SILVER + duplicadas = BRONZE;
nenhuma coluna de nome fora da RAW; arquivos Gold sem o marcador de dado pessoal; snapshot com as chaves do
contrato 4.8; chaves Gold pertencentes às enumerações do contrato; agregados somando o total de válidos; percentual
entre 0 e 100. Qualquer falha → situação `REPROVADO` e a tarefa falha (o snapshot não é publicado).
