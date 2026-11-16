# AcessaCidade — Pitch de Negócio + MVP CitizenTech

**FIAP · Global Solution 2026.2 · CitizenTech · Engenharia de Software 4º ano (4ES)**
**Disciplina:** Business Intelligence & Startup Development — Prof. Henio Luiz Scheidt
**Equipe / startup:** [PREENCHER: nome da equipe]

| Integrante | RM | Papel na equipe |
|---|---|---|
| [PREENCHER: Integrante 1] | [PREENCHER] | [PREENCHER] |
| [PREENCHER: Integrante 2] | [PREENCHER] | [PREENCHER] |
| [PREENCHER: Integrante 3] | [PREENCHER] | [PREENCHER] |
| [PREENCHER: Integrante 4] | [PREENCHER] | [PREENCHER] |
| [PREENCHER: Integrante 5] | [PREENCHER] | [PREENCHER] |

## Links da entrega (clicáveis)

| Entregável | Link |
|---|---|
| **Vídeo-pitch** (até 5 min, demo do MVP, todos participam) | [PREENCHER: URL_VIDEO] |
| **MVP em URL pública** | [PREENCHER: URL_MVP] |
| **Repositório** (código, documentação e Ficha Técnica do MVP em `docs/FICHA_TECNICA_MVP.md`) | [PREENCHER: URL_REPOSITORIO] |

**Conteúdo deste PDF:** (1) resumo do negócio e do MVP; (2) evidências de valor entregue; (3) checklist de
verificação dos links; **Anexo A** — Lean Canvas visual (A4 paisagem); **Anexo B** — Lean Canvas consolidado com
status de validação e o que mudou desde o CP1; **Anexo C** — Modelo de negócio (proposta de valor, receitas e
preço, canais, métricas-chave, ponto de equilíbrio).

---

## 1. Resumo

**Cidadão beneficiado:** pessoas com deficiência, cadeirantes, pessoas cegas ou com baixa visão, idosos e pessoas
com mobilidade reduzida que se deslocam a pé.

**Problema, em uma frase:** barreiras nas calçadas (buracos, pisos quebrados, rampas irregulares, obstáculos)
impedem ou tornam arriscado o deslocamento dessas pessoas, e não há um jeito simples de avisar quem pode resolver
nem de acompanhar o que acontece depois.

**Território:** [PREENCHER: cidade/bairros onde a equipe observou o problema]. Dados de demonstração usam a cidade
fictícia "Cidade Exemplo" e são identificados como simulados.

**Solução (MVP):** site responsivo e acessível, sem instalar app e sem cadastro, onde o cidadão registra a barreira
com foto opcional e recebe um protocolo (`AC-AAAA-NNNNNN`). A foto passa por triagem automática com visão
computacional clássica (OpenCV), com as etapas da imagem visíveis e explicação em texto, sempre sujeita a revisão
humana. O cidadão acompanha pelo protocolo e tira dúvidas com um assistente em linguagem simples (LLM via OpenRouter,
com modo alternativo por regras). Quem resolve vê um painel com indicadores operacionais e analíticos (pipeline de
dados Raw → Bronze → Silver → Gold). Um robô RPA registra denúncias recebidas fora do site.

**Proposta de valor:** para o cidadão, registrar uma barreira em poucos minutos e saber o que aconteceu com ela;
para quem resolve, denúncias padronizadas, com foto triada e explicada, priorizáveis por impacto e visíveis em painel.

**Modelo de negócio (Anexo C):** o cidadão nunca paga. Pagam prefeituras (assinatura SaaS por faixa de população),
concessionárias (API) e administradoras de grandes áreas (assinatura por área). Valores são **hipóteses a validar**;
no cenário hipotético, o ponto de equilíbrio é de **24 municípios** com custo fixo de R$ 55 mil/mês (premissas declaradas).
Canais B2G: pilotos de 90 dias, chamamentos e programas de inovação aberta e, como caminho possível, o CPSI do Marco
Legal das Startups (LC 182/2021) — nenhum contrato existe hoje.

**Impacto e ODS:** ODS 11 (principal; metas 11.7, 11.2 e 11.3), ODS 10 (meta 10.2) e ODS 9 (meta 9.1). Indicador
central de impacto: tempo para registrar um problema no canal atual × no AcessaCidade, medido em teste com usuários.

## 2. Demonstração do MVP (no vídeo, de 1:30 a 3:00)

Fluxo central mostrado na URL pública, do primeiro clique ao resultado:

1. Acessar a URL pública → página inicial.
2. Registrar denúncia com foto → protocolo gerado.
3. Ver a triagem da foto (7 etapas: original, cinza, filtrada, contraste, bordas, máscara, contornos) e o status "Aguardando revisão".
4. Consultar a denúncia pelo protocolo.
5. Perguntar ao assistente o que significa o status.
6. Ver o painel atualizado com a nova denúncia.

## 3. Valor entregue — evidências

| Evidência | Resultado real | Onde está |
|---|---|---|
| Teste de usabilidade com o público-alvo | [PREENCHER: nº de participantes e perfil (sem nomes)] | Repositório: `03-Business-Intelligence-Startup/pitch/evidencias/testes/` |
| Tempo para registrar: canal atual × AcessaCidade | [PREENCHER: média antes (s) × depois (s)] | Planilha de registro, aba Resumo |
| Conclusão das tarefas sem ajuda | [PREENCHER: %] | Planilha de registro, aba Resumo |
| Facilidade de uso (SUS 0–100) | [PREENCHER: média] | Planilha de registro, aba SUS |
| Uso real no MVP (protocolos gerados nos testes) | [PREENCHER: lista de protocolos] | Planilha de registro |
| Prints do painel antes/depois do registro | [PREENCHER: sim/não] | `pitch/evidencias/prints/` |

> Os números do painel que vêm de dados simulados **não** são apresentados como impacto. Se algum item acima não
> tiver sido realizado até a entrega, a equipe escreve "não realizado" em vez de estimar.

## 4. Checklist de verificação antes do envio

- [ ] Os três links acima abrem em **janela anônima**, sem login, e em celular com dados móveis.
- [ ] O vídeo tem **até 5 minutos**, mostra a demo real na URL pública e **todos os integrantes** participam.
- [ ] O vídeo está como **Não listado** ou **Público** no YouTube (nunca Privado).
- [ ] O repositório está **público** e o README abre com a Ficha Técnica do MVP.
- [ ] Nenhum `[PREENCHER]` restante neste PDF (o gerador do PDF lista os restantes).
- [ ] Lean Canvas (Anexos A e B) com o status de validação de cada bloco atualizado com fatos.
- [ ] Os links continuam funcionando durante a correção (até uma semana após 19/11/2026).
- [ ] Envio feito por **um** integrante no portal da disciplina até **19/11/2026, 23h55**.
