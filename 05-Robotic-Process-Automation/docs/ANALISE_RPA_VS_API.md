# Diagnóstico crítico: RPA ou integração nativa/API?

## 1. O fato que não podemos esconder

O AcessaCidade **tem API REST**. A rota `POST /api/denuncias` (multipart, contrato seção 4.2) recebe exatamente os
mesmos campos do formulário, inclusive `origem=RPA`/`API` e a foto. Documentação interativa em `/docs`.

Portanto, **do lado do AcessaCidade, RPA não é necessário**: qualquer sistema capaz de fazer uma requisição HTTP pode
cadastrar denúncias de forma mais rápida, mais estável e mais barata do que um robô que clica na tela.

A pergunta certa não é "o AcessaCidade precisa de RPA?", e sim: **"quem está do outro lado consegue usar a API?"**

## 2. Quando a integração nativa/API é a melhor escolha

| Situação | Por que API é melhor |
|---|---|
| Parceiro tem sistema próprio com equipe de TI (ex.: prefeitura com sistema de ouvidoria) | Integração sistema-a-sistema, sem tela no meio; volume alto sem custo de licença de robô |
| Volume alto (milhares/mês) ou necessidade de tempo real | O robô processa uma linha por vez, na velocidade da interface; a API processa em paralelo |
| Dados já estão em banco ou em outro serviço | Exportar/consumir via API ou pipeline de dados (como o da disciplina 02) é mais simples |
| Mudanças frequentes no layout do formulário | API é um contrato versionado; seletores de tela quebram |
| Necessidade de autenticação/assinatura forte de cada requisição | Melhor resolvido por API com tokens do que por interface gráfica |

**Exemplo do próprio projeto:** o processo candidato B ("enviar indicadores semanais às associações") foi descartado
para RPA justamente porque `/api/indicadores` e a camada Gold do pipeline já entregam os dados — a solução certa ali é
integração/BI, não robô (`spreadsheet/assessment_rpa_AcessaCidade.xlsx`, aba "Processos candidatos").

## 3. Por que RPA ainda faz sentido neste cenário

1. **Parceiros sem capacidade técnica.** Associações de pessoas com deficiência, ONGs de bairro e agentes comunitários
   trabalham com Excel e e-mail. Eles não vão escrever código para chamar uma API multipart. A planilha é a
   "interface" que eles dominam.
2. **Sistemas legados e canais não digitais.** Relatos em papel, ligações e listas de reuniões comunitárias viram
   planilhas. O gargalo está na **transcrição** para o sistema, que é exatamente o que o RPA resolve.
3. **Transição sem esperar desenvolvimento.** O robô entrega valor já, enquanto uma eventual "importação de planilha"
   nativa no AcessaCidade não existe. RPA funciona como ponte (tactical automation), não como arquitetura final.
4. **Mesmas regras do canal web.** O robô usa o formulário público com `canal=rpa`: passa pelas mesmas validações,
   rate limit, sanitização de foto e triagem de visão computacional que o cidadão. Não há "porta dos fundos".
5. **Rastreabilidade para o parceiro.** A planilha de saída devolve à associação status, mensagem e protocolo por
   linha, no formato que ela já usa.
6. **Exigência pedagógica.** A disciplina pede o robô no UiPath; este diagnóstico registra que a escolha foi
   consciente e com prazo de validade.

## 4. Riscos do RPA e mitigação

| Risco | Impacto | Mitigação adotada |
|---|---|---|
| **Seletores frágeis** (mudança de layout quebra o robô) | Alto | Seletores pelos `id` estáveis definidos em contrato (seção 7), com `name`/`data-rpa` como alternativa; qualquer mudança de id exige mudar primeiro o contrato |
| Lentidão/indisponibilidade da aplicação | Médio | `TIMEOUT_SEGUNDOS` configurável; falha vira `FALHA_SISTEMA` na linha e o robô segue para a próxima |
| Dados inválidos na planilha | Médio | Validação prévia com as regras do contrato → `FALHA_NEGOCIO` sem enviar nada |
| Duplicidade ao reprocessar | Médio | Linhas com `Status_Robo = SUCESSO` são ignoradas numa nova execução |
| Upload de foto pelo diálogo do Windows | Médio | Dois modos (`DIALOGO`/`TYPEINTO`) + `IGNORAR`; a foto é opcional no AcessaCidade |
| Planilha aberta no Excel durante a execução | Baixo | Gravação em Try/Catch; erro registrado no log |
| Rate limit (`RATE_LIMIT_PER_MINUTE`) | Baixo | Volume da demonstração (12 linhas) é baixo; para lotes grandes, aumentar o limite no ambiente ou espaçar o envio |
| Dados pessoais | Médio | Planilha usa identificação fictícia; o nome é opcional e a API nunca o devolve; nada de senha/token no `Config.xlsx` |
| Licenciamento e máquina dedicada | Médio | Studio Community para o MVP; para produção, avaliar licenças e um Robot não assistido (ver Business Case) |

## 5. Tabela comparativa

| Critério | RPA (UiPath + formulário web) | Integração nativa (API `POST /api/denuncias`) | Importação de planilha nativa (futuro) |
|---|---|---|---|
| Esforço para o parceiro | Baixo (preenche planilha) | Alto (precisa programar) | Baixo |
| Esforço para a equipe AcessaCidade | Médio (robô + manutenção de seletores) | Baixo (API já existe) | Médio (desenvolver tela de importação) |
| Disponível hoje | Sim | Sim (para quem programa) | Não |
| Estabilidade | Média (depende da interface) | Alta (contrato versionado) | Alta |
| Velocidade | Baixa (segundos por linha) | Alta | Alta |
| Custo recorrente | Licença/máquina do robô em produção | Praticamente zero | Zero |
| Mesmas validações do cidadão | Sim | Sim | Sim |
| Rastreabilidade por linha | Sim (planilha de saída) | Depende do cliente | Sim |
| Indicado para | Transição, parceiros sem TI, volume baixo/médio | Parceiros com TI, volume alto | Solução definitiva para planilhas |

## 6. Conclusão

- **Decisão:** usar RPA para o processo "cadastro de denúncias recebidas por planilhas de parceiros" **como ponte**,
  com seletores ancorados no contrato e tratamento de exceções por linha.
- **Recomendação de evolução:** quando o volume crescer ou a manutenção de seletores ficar cara, substituir o robô por
  uma tela de importação de planilha no próprio AcessaCidade (que chamaria a mesma lógica da API) ou por integração
  direta via API com os parceiros que tiverem TI. A planilha-modelo e a planilha de saída continuam válidas nesse futuro.
- A nota baixa do critério "Ausência de API" no assessment (2 de 5) registra exatamente esse ponto; mesmo assim, o
  processo obteve **79,4%** (Alta aptidão) na avaliação preliminar da equipe — a revisar com a equipe.
