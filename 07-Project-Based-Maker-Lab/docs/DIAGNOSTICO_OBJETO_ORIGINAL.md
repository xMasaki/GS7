# Diagnóstico do objeto original — placa de identificação de ponto de ônibus

> **Status:** diagnóstico **preliminar**, escrito como **HIPÓTESES a verificar no local**. Nenhuma visita,
> foto ou medição foi feita até agora. Tudo marcado com [PREENCHER] depende da equipe
> (roteiro em [`GUIA_FOTOGRAFAR_E_MEDIR.md`](GUIA_FOTOGRAFAR_E_MEDIR.md)).

## 1. Objeto escolhido

| Item | Registro |
|---|---|
| Objeto | Placa (ou totem) que identifica um ponto de ônibus, presa em poste/tubo do abrigo |
| Local (sem endereço residencial; ponto de referência público) | [PREENCHER: rua/avenida, bairro, cidade] |
| Data e horário da visita | [PREENCHER: dd/mm/aaaa hh:mm] |
| Integrantes presentes | [PREENCHER: nomes ou iniciais] |
| Fotos (link da pasta) | [PREENCHER: link para a pasta de fotos] |
| Croqui preenchido | [PREENCHER: `docs/imagens/croqui_original_preenchido.jpg`] |

## 2. Por que este objeto

O ponto de ônibus é onde a pessoa com deficiência **depende** da informação para usar o transporte público.
É também o lugar natural para **reportar** problemas de acessibilidade do entorno (calçada quebrada, obstáculo,
falta de piso tátil) — exatamente o que o AcessaCidade registra.

## 3. Falhas típicas (hipóteses) e quem é afetado

| # | Falha provável (hipótese) | Quem é afetado | Como verificar no local | Resultado observado |
|---|---|---|---|---|
| F1 | Placa instalada **alta** (borda inferior ≈ 2,2 m — estimativa) | Pessoas com baixa visão (não conseguem aproximar o rosto), cadeirantes e pessoas de baixa estatura (leitura em ângulo) | Medir piso → borda inferior e borda superior (medidas C e D do croqui) | [PREENCHER] |
| F2 | **Baixo contraste** (letras claras sobre fundo azul/cinza, desbotado ou sujo) | Pessoas com baixa visão, idosos (catarata, sensibilidade a contraste), todos à noite | Foto frontal sem flash + foto com cartão branco/preto ao lado como referência | [PREENCHER] |
| F3 | **Sem informação tátil** (sem relevo, sem Braille) | Pessoas cegas — não sabem que chegaram ao ponto, nem para que lado fica o embarque | Passar a mão (se alcançável) / fotografar a superfície | [PREENCHER] |
| F4 | **Sem canal de reporte** (nenhum QR/contato para avisar sobre calçada quebrada, piso tátil faltando, abrigo danificado) | Todos os usuários; em especial quem mais sofre com o problema | Observar se há qualquer QR, telefone ou link | [PREENCHER] |
| F5 | **Quinas vivas / fixação improvisada** (abraçadeiras metálicas, arame) | Pessoas cegas usando bengala ou mão para se orientar; crianças | Foto de detalhe da fixação; medir projeção da placa em relação ao poste (medida H) | [PREENCHER] |
| F6 | Placa **sem relação com o piso tátil** (se houver piso tátil, ele não "leva" a nenhuma informação) | Pessoas cegas | Fotografar o piso no entorno e medir distância (medida L) | [PREENCHER] |
| F7 | Desgaste/vandalismo (adesivos, pichação, desbotamento por sol) | Todos | Fotos de detalhe | [PREENCHER] |

Regra: depois da visita, **mantenha só as falhas confirmadas** e marque as demais como "não observada".
Se a placa visitada não tiver alguma das falhas, diga isso — não force o diagnóstico.

## 4. Perfis afetados (sem dados pessoais)

- Pessoa cega usuária de bengala: precisa localizar o ponto e saber o sentido de embarque pelo tato.
- Pessoa com baixa visão / idosa: precisa de letras grandes, contraste alto e leitura a curta distância.
- Cadeirante / pessoa de baixa estatura: precisa ler e alcançar o QR a uma altura menor.
- Qualquer cidadão: precisa de um canal simples para reportar problemas de acessibilidade naquele ponto.

**Não entrevistamos ninguém.** Se a equipe conversar com usuários, registre apenas falas anonimizadas e com
consentimento: [PREENCHER: relatos anonimizados, se houver].

## 5. Medidas (resumo — detalhe no croqui)

As medidas do modelo original em `cad/parametros.py` (bloco "OBJETO ORIGINAL") são **ESTIMADAS** e
`ORIGINAL_MEDIDO_EM_CAMPO = False`. Depois da visita, substitua os valores, troque para `True` e rode
`cad/gerar_todos.py` de novo.

| Medida | Estimativa usada no CAD | Medida real |
|---|---|---|
| Largura × altura da placa | 450 × 300 mm | [PREENCHER] |
| Espessura da chapa | 2 mm | [PREENCHER] |
| Altura da borda inferior ao piso | 2200 mm | [PREENCHER] |
| Diâmetro do poste | 76,2 mm | [PREENCHER] |
| Altura das letras | 40 mm | [PREENCHER] |
| Afastamento placa ↔ poste | 10 mm | [PREENCHER] |

## 6. Normas de referência a consultar (sem declarar conformidade)

- ABNT NBR 9050 — acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos (contraste,
  alturas de comunicação visual e tátil, dimensões do Braille, caracteres em relevo).
- ABNT NBR 16537 — sinalização tátil no piso (piso de alerta e direcional que conduz ao ponto).
