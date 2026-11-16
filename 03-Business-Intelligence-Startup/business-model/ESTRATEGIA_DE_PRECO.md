# Estratégia de preço — AcessaCidade

> **Todos os valores deste documento são HIPÓTESES declaradas para validação.** Não são preços praticados,
> não foram apresentados a nenhum cliente e não se baseiam em proposta comercial real. Servem para testar se o
> modelo de negócio fecha (ver `MODELO_DE_NEGOCIO.md`, seção 8) e para orientar as entrevistas de disposição a pagar.

## 1. Princípios

1. **O cidadão nunca paga.** Registrar, consultar e usar o assistente é gratuito e sem cadastro.
2. **Paga quem tem a obrigação ou o interesse de resolver** — prefeituras, concessionárias e administradoras de áreas.
3. **Preço por faixa de população** para municípios: é um proxy simples, público e verificável do volume esperado
   de denúncias e da capacidade orçamentária. Evita cobrança por denúncia (que criaria incentivo errado: o cliente
   pagaria mais quanto mais o cidadão reclamasse).
4. **Contrato anual com cobrança mensal** (receita recorrente previsível para a startup e despesa previsível para o cliente).
5. **Piloto curto e com indicadores** como porta de entrada, para reduzir o risco percebido pelo gestor público.
6. **Transparência:** tabela pública, sem taxa escondida; dados exportáveis a qualquer momento (sem aprisionar o cliente).

## 2. Tabela de planos (HIPOTÉTICA)

| Plano | Público | Inclui | Preço hipotético | Premissa por trás do valor |
|---|---|---|---|---|
| **Piloto 90 dias** | Município, 1 a 3 bairros | Implantação simplificada, formulário, triagem, painel operacional, relatório final de indicadores | R$ 6.000 (único) | Valor baixo o bastante para caber em contratação de pequeno valor ou programa de inovação — **conferir a legislação aplicável com o jurídico do cliente** |
| **Município P** | até 50 mil hab. | Tudo do MVP: formulário, triagem, protocolo, assistente, painel operacional, área de revisão | R$ 1.200/mês | Hipótese: menor que o custo de uma pessoa dedicada à triagem manual |
| **Município M** | 50 mil a 200 mil hab. | Idem P + até 10 usuários de revisão | R$ 2.800/mês | Hipótese |
| **Município G** | 200 mil a 1 milhão hab. | Idem M + usuários ilimitados + suporte prioritário | R$ 6.500/mês | Hipótese |
| **Município GG** | acima de 1 milhão hab. | Sob medida (integração com 156/sistemas, SLA) | a partir de R$ 14.000/mês | Hipótese; sempre sob proposta |
| **Módulo Painel/BI avançado** | Qualquer plano municipal | Camada analítica do pipeline (Gold), exportação para Excel/Power BI, relatórios por bairro | + 25% da assinatura | Hipótese |
| **Implantação e treinamento** | P/M · G · GG | Configuração, treinamento de equipes, material de divulgação | R$ 5.000 · R$ 15.000 · sob proposta | Hipótese |
| **API concessionárias** | Concessionárias de serviços | Acesso às denúncias da sua área de atuação via API, por município | R$ 1.900/mês | Hipótese |
| **Grandes áreas** | Shoppings, campi, condomínios, parques | Canal próprio (QR Code), painel da área | R$ 450/mês por área | Hipótese |
| **Institucional** | ONGs e associações sem fins lucrativos | Painel e registro em lote (RPA) | R$ 0 | Custo coberto pelos clientes pagantes ou patrocínio |

## 3. Como validar os preços (roteiro para a equipe)

1. **Entrevistas de disposição a pagar** com 3 a 5 gestores públicos ou de áreas privadas
   (perguntas abertas: "como vocês recebem e triam essas reclamações hoje?", "quanto tempo/pessoas isso consome?",
   "que orçamento costuma financiar ferramentas assim?"). Não apresentar os valores logo de início.
2. **Teste de faixa de preço** (Van Westendorp simplificado): "a partir de que valor seria caro demais? barato demais para ser confiável?".
3. **Comparar com o custo da alternativa**: horas de servidores dedicadas à triagem manual (`[PREENCHER: dado obtido em entrevista]`).
4. Registrar cada evidência em `pitch/evidencias/` e atualizar o bloco "Fontes de receita" em `lean_canvas.json`.

Resultado até agora: `[PREENCHER: entrevistas de preço realizadas (quantas, com que perfil, o que mudou) — ou "nenhuma realizada"]`.

## 4. Efeito do preço no ponto de equilíbrio

Com os valores acima e as premissas de custo do `MODELO_DE_NEGOCIO.md`:

| Cenário (hipotético) | Ticket médio com BI | Ponto de equilíbrio |
|---|---|---|
| Base (mix 50% P · 35% M · 15% G; 30% com BI) | ≈ R$ 2.747/mês | 24 municípios |

Para testar outros cenários, altere a aba `Premissas` de `MODELO_FINANCEIRO_HIPOTETICO.xlsx` (preços, mix, custos,
rampa) — o ponto de equilíbrio e a projeção de 36 meses recalculam automaticamente.

## 5. O que não fazemos

- Não cobramos do cidadão nem exibimos publicidade a ele.
- Não vendemos dados pessoais. Dados abertos, quando houver, são agregados e anonimizados.
- Não cobramos por denúncia recebida (incentivo perverso).
