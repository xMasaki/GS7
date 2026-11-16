# Análise de alternativas e concorrência — AcessaCidade

> Análise **por categoria de alternativa**, de forma genérica. Não citamos características específicas de produtos
> comerciais, pois a equipe não as verificou. Se quiser comparar um produto concreto, pesquise o site oficial dele,
> registre a data da consulta e cite a fonte: `[PREENCHER: produto, característica, fonte, data]`.

## 1. Alternativas que o cidadão usa hoje

| Alternativa | Como funciona (genérico) | Pontos fortes | Limitações frequentes (hipótese a validar) |
|---|---|---|---|
| **Central 156 e protocolos municipais** (telefone, site ou app) | Canal oficial de solicitações da prefeitura, quando existe | Oficial; integrado à operação da prefeitura | Varia muito entre cidades; nem sempre acessível a pessoas com deficiência; foco geral, não em acessibilidade; acompanhamento pode ser difícil |
| **Ouvidorias** | Reclamação formal | Formal, gera resposta institucional | Lenta para problemas operacionais; pouca padronização |
| **Aplicativos genéricos de zeladoria** (públicos ou privados) | Registro com foto e localização de problemas urbanos variados | Foto e geolocalização; em alguns casos, painel para o gestor | Exigem instalar app/criar conta em muitos casos; acessibilidade como uma categoria entre muitas |
| **Redes sociais e imprensa local** | Publicação de foto marcando a prefeitura | Visibilidade e pressão social | Sem protocolo, sem dado estruturado, sem garantia de encaminhamento |
| **Contato com vereador/subprefeitura** | Pedido direto | Às vezes resolve rápido | Depende de relacionamento; não escala; sem dado |
| **Mapeamentos de associações** (planilhas, mutirões) | Levantamento comunitário de barreiras | Conhecimento local profundo | Trabalhoso; dados dispersos; difícil de manter |
| **Não fazer nada / mudar o trajeto** | — | — | O problema permanece e se repete para outras pessoas |

## 2. Diferenciais do AcessaCidade (o que o MVP já tem)

| Diferencial | Como aparece no MVP |
|---|---|
| **Foco em acessibilidade** | Categorias específicas (rampa, piso tátil, obstáculo fixo/temporário) e campo de **impacto** (impede passagem, risco de queda) |
| **Sem instalar app e sem cadastro** | Site responsivo; nome opcional, nunca exibido |
| **Triagem explicável da foto** | OpenCV clássico com as 7 etapas visíveis e explicação em texto; **revisão humana** sempre |
| **Transparência por protocolo** | `AC-AAAA-NNNNNN` + histórico de status + consulta pública |
| **Assistente em linguagem simples** | AcessaCidade Helper (LLM com modo alternativo por regras quando não há chave de API) |
| **Dados para gestão** | Painel operacional + camada analítica (pipeline Raw → Bronze → Silver → Gold) + exportação para Excel/Power BI |
| **Integração com o legado** | Robô RPA (UiPath) que registra denúncias pelo formulário — caminho para levar denúncias de/para sistemas sem API |
| **Privacidade desde o desenho** | Fotos sem EXIF/GPS e com rostos borrados; exportação sem nome |

## 3. Posicionamento

O AcessaCidade **não pretende substituir o 156** nem os canais oficiais. O posicionamento é ser a **camada
especializada em acessibilidade**: recebe, padroniza, tria e organiza as denúncias e as entrega ao responsável
(por integração, exportação ou RPA), com transparência para o cidadão.

## 4. Riscos competitivos

- Um município com app de zeladoria próprio pode considerar o AcessaCidade redundante → mitigação: integração, foco em acessibilidade e painel por impacto.
- Fornecedores grandes de sistemas municipais podem adicionar uma categoria de acessibilidade → mitigação: comunidade, qualidade do dado de acessibilidade e triagem explicável.
- Barreira de entrada baixa (formulários são fáceis de copiar) → a vantagem precisa vir de dados acumulados, relacionamento com associações e integração — hoje **ainda não consolidados** (ver bloco "Vantagem injusta" do Lean Canvas).
