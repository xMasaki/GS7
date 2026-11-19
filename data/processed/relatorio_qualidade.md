# Relatório de qualidade — pipeline AcessaCidade

- Execução: `scheduled__2026-11-18T03:00:00+00:00`
- Gerado em (UTC): 2026-11-19T19:58:32Z
- Situação: **APROVADO**
- Dados: fonte SIMULADA (Cidade Exemplo, fictícia); exportação da API não carregada nesta execução

## Contagens por camada

| Camada | Tabela | Linhas |
|---|---|---:|
| raw | raw.denuncias_simuladas | 271 |
| raw | raw.denuncias_app | 0 |
| bronze | bronze.denuncias | 260 |
| silver | silver.denuncias | 250 |
| silver | silver.denuncias_duplicadas | 10 |
| gold | gold.denuncias_por_bairro | 9 |
| gold | gold.denuncias_por_categoria | 8 |
| gold | gold.denuncias_por_periodo | 19 |
| gold | gold.denuncias_por_status | 5 |
| gold | gold.resultado_visao | 4 |
| gold | gold.qualidade_registros | 10 |

## Indicadores (contrato 4.8, campo `qualidade`)

| Indicador | Valor |
|---|---:|
| linhas_raw | 271 |
| linhas_bronze | 260 |
| duplicatas_removidas | 11 |
| datas_invalidas | 12 |
| coordenadas_invalidas | 11 |
| campos_obrigatorios_ausentes | 25 |
| percentual_registros_validos | 84.4 |
| linhas_silver | 250 |
| duplicatas_negocio_removidas | 10 |
| registros_validos | 211 |

## Flags da Bronze (problemas técnicos sinalizados)

| Flag | Registros |
|---|---:|
| flag_possui_nome | 155 |
| flag_data_ausente | 1 |
| flag_data_invalida | 11 |
| flag_coordenada_ausente | 116 |
| flag_coordenada_invalida | 8 |
| flag_pontuacao_invalida | 3 |
| flag_logradouro_ausente | 5 |
| flag_bairro_ausente | 3 |
| flag_tipo_ausente | 2 |
| flag_descricao_ausente | 2 |
| flag_impacto_ausente | 14 |
| flag_campo_obrigatorio_ausente | 25 |

## Flags da Silver (regras de negócio)

| Flag | Registros |
|---|---:|
| flag_bairro_nao_padronizado | 3 |
| flag_tipo_nao_reconhecido | 2 |
| flag_impacto_nao_reconhecido | 1 |
| flag_status_inferido | 16 |
| flag_visao_inconsistente | 1 |
| flag_coordenada_fora_area | 3 |
| flag_data_invalida | 12 |

## Motivos de invalidade (RN-12)

| Motivo | Registros |
|---|---:|
| impacto ausente ou não reconhecido | 15 |
| data de registro ausente ou inválida | 12 |
| descrição ausente ou com menos de 10 caracteres | 7 |
| logradouro ausente | 5 |
| bairro ausente | 3 |
| tipo de obstáculo ausente | 2 |

## Bairros fora do dicionário oficial (mantidos com grafia limpa)

- Recanto Verde

## Verificações automáticas

| Verificação | Resultado | Detalhe |
|---|---|---|
| RAW não vazia | OK | 271 linhas na RAW |
| RAW fiel à fonte simulada | OK | arquivo=271 raw=271 |
| BRONZE ≤ RAW | OK | 260 ≤ 271 |
| SILVER + duplicadas = BRONZE | OK | 260 = 260 |
| Sem coluna de nome fora da RAW | OK | nenhuma |
| Arquivos Gold sem dados pessoais | OK | nenhum |
| Snapshot no formato do contrato 4.8 | OK | ok |
| Chaves Gold pertencem ao contrato (seção 3) | OK | ok |
| Agregados Gold somam os registros válidos | OK | válidos=211 somas={'por_bairro': 211, 'por_categoria': 211, 'por_periodo_mensal': 211, 'por_status': 211, 'resultado_visao': 211} |
| Percentual de válidos entre 0 e 100 | OK | 84.4% |
