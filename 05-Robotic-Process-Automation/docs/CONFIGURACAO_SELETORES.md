# Configuração e validação dos seletores (UiPath)

Os seletores do robô `AcessaCidade.RPA` seguem a seção 7 de `docs/CONTRATOS_DE_INTEGRACAO.md`.
Cada campo do formulário `#/registrar?canal=rpa` tem **três** identificadores estáveis: `id` (seletor
primário), `name` e `data-rpa` (iguais ao nome do campo na API). Isso permite um seletor principal e
dois *fallbacks* sem depender de posição, classe CSS ou texto.

> Importante: os seletores foram **escritos à mão** nos `.xaml` (não foram capturados no UiPath Studio,
> que não está disponível no ambiente onde o projeto foi gerado). Antes da primeira execução é preciso
> **validar** cada um no UI Explorer (passo a passo abaixo).

## 1. Tabela campo → seletor

Todos os seletores abaixo são **parciais** (sem a tag `<html>`), porque as atividades estão dentro de
um *Attach Browser* (`ui:BrowserScope`) que já delimita a janela do navegador.

| Campo / elemento | Atividade UiPath | Seletor primário (id) | Fallback 1 (name / data-rpa) |
|---|---|---|---|
| Formulário | Element Exists | `<webctrl id='form-denuncia' tag='FORM' />` | `<webctrl tag='FORM' parentid='...' />` (não necessário) |
| Nome | Type Into | `<webctrl id='campo-nome' tag='INPUT' />` | `<webctrl name='nome' tag='INPUT' />` |
| Logradouro | Type Into | `<webctrl id='campo-logradouro' tag='INPUT' />` | `<webctrl name='logradouro' tag='INPUT' />` |
| Número | Type Into | `<webctrl id='campo-numero' tag='INPUT' />` | `<webctrl name='numero' tag='INPUT' />` |
| Bairro | Type Into | `<webctrl id='campo-bairro' tag='INPUT' />` | `<webctrl name='bairro' tag='INPUT' />` |
| Cidade | Type Into | `<webctrl id='campo-cidade' tag='INPUT' />` | `<webctrl name='cidade' tag='INPUT' />` |
| Ponto de referência | Type Into | `<webctrl id='campo-referencia' tag='INPUT' />` | `<webctrl name='ponto_referencia' tag='INPUT' />` |
| Tipo de obstáculo | Select Item (texto visível = rótulo 3.1) | `<webctrl id='campo-tipo' tag='SELECT' />` | `<webctrl name='tipo_obstaculo' tag='SELECT' />` |
| Descrição | Type Into | `<webctrl id='campo-descricao' tag='TEXTAREA' />` | `<webctrl name='descricao' tag='TEXTAREA' />` |
| Impacto | Select Item (texto visível = rótulo 3.2) | `<webctrl id='campo-impacto' tag='SELECT' />` | `<webctrl name='impacto' tag='SELECT' />` |
| Fotografia (input file) | Click (hardware) + Type Into no diálogo, **ou** Type Into direto | `<webctrl id='campo-foto' tag='INPUT' />` | `<webctrl name='foto' tag='INPUT' />` |
| Diálogo "Abrir" do Windows — campo "Nome" | Type Into | `<wnd app='msedge.exe' cls='#32770' /><wnd ctrlid='1148' />` (montado com `NAVEGADOR`) | Reindicar (o layout varia por versão do Windows/idioma) |
| Consentimento | Check (Action = Check) | `<webctrl id='campo-consentimento' tag='INPUT' />` | `<webctrl name='consentimento' tag='INPUT' />` |
| Botão Enviar | Click | `<webctrl id='botao-enviar' />` | `<webctrl tag='BUTTON' aaname='Enviar*' />` (conferir o texto real) |
| Caixa de sucesso | Element Exists (confirmação) | `<webctrl id='resultado-envio' />` | — |
| Protocolo gerado | Get Text (`ui:GetValue`) | `<webctrl id='protocolo-gerado' />` | — |
| Caixa de erro | Get Text | `<webctrl id='erro-envio' />` | — |
| Registrar outra | Click | `<webctrl id='botao-nova-denuncia' />` | (o robô também navega de novo para a URL) |

O atributo `data-rpa` existe para ferramentas que aceitam seletores CSS (ex.: `[data-rpa="logradouro"]`);
no UiPath o caminho mais portável de fallback é `name`, que o UI Explorer reconhece nativamente.

### Observações sobre o comportamento da página

- `#resultado-envio`, `#protocolo-gerado` e `#erro-envio` **existem no HTML desde o início**, ocultos
  (atributo `hidden`). Por isso o robô **não** usa só "Element Exists" para saber se deu certo: ele faz
  *polling* (a cada 0,5 s, até `TIMEOUT_SEGUNDOS`) do **texto** de `#protocolo-gerado`, validando o formato
  do contrato `^AC-\d{4}-\d{6}$`, e do texto de `#erro-envio`. O "Element Exists" em `#resultado-envio`
  é uma confirmação adicional registrada no log.
- O formulário aberto com `?canal=rpa` mostra o selo "Canal: automação (RPA)" e envia `origem=RPA`.
  Confira esse selo no vídeo e nos prints.
- Os `<select>` têm como texto visível exatamente os rótulos do contrato (ex.: `Buraco na calçada`,
  `Risco de queda ou acidente`). A planilha de entrada usa esses mesmos textos, e o robô valida a
  linha antes de enviar (linha com rótulo diferente vira `FALHA_NEGOCIO`, sem tocar no formulário).

## 2. Pré-requisito: extensão do navegador

1. No UiPath Studio: aba **Home → Tools → UiPath Extensions**.
2. Clique em **Edge** (ou **Chrome**) e confirme. O navegador abre a página da extensão.
3. No navegador, ative a extensão "UiPath Browser Automation" (em `edge://extensions` deve aparecer
   *ativada*). Se o navegador perguntar, permita o acesso em todos os sites.
4. Reinicie o navegador.
5. Confirme no Config.xlsx: `NAVEGADOR = Edge` (ou `Chrome`) igual ao navegador com a extensão.

Sem a extensão, os seletores `webctrl` **não** funcionam (o UI Explorer só enxerga a janela).

## 3. Passo a passo: validar cada seletor no UI Explorer

1. Suba o AcessaCidade localmente (ver README da raiz) e abra `http://localhost:8000/#/registrar?canal=rpa`
   no navegador com a extensão.
2. No Studio, abra `Workflows/ProcessarDenuncia.xaml`.
3. Clique na atividade (ex.: **Type Into - #campo-logradouro**) → no painel da atividade, menu `≡`
   (ou clique direito) → **Edit Selector**.
4. Clique em **Validate**. O ícone fica **verde** se o elemento foi encontrado e **vermelho** se não.
5. Se ficar vermelho: clique em **Indicate Element** (ou "Indicate on screen"), clique no campo na página,
   e depois, no editor, deixe marcado **apenas** o atributo `id` (desmarque `css-selector`, `parentid`,
   `idx`, `aaname` gerados automaticamente). Valide novamente.
6. Para inspecionar melhor, use **Open in UI Explorer** (botão no editor de seletores): no painel
   *Selector Attributes* marque `id` e `tag`; em *Unselected Items* deixe `idx` desmarcado.
7. Repita para todos os itens da tabela da seção 1.
8. Para o `<select>`: na atividade **Select Item**, clique em **Indicate**, depois no menu suspenso, e
   confira se a lista *Items* traz os rótulos do contrato. O valor usado vem da variável `tipoObstaculo`
   / `impacto` (texto da planilha).
9. Salve (`Ctrl+S`).

## 4. Fallback por `name`

Se o `id` deixar de funcionar (por exemplo, numa versão nova do frontend), troque o seletor da atividade
pelo da coluna "Fallback 1" — basta editar o texto no **Edit Selector**. Alternativa mais robusta, sem
editar o seletor principal: envolver a atividade num **Try Catch** e, no Catch, repetir a mesma
atividade com o seletor por `name`. O projeto atual não faz isso para não poluir o fluxo; o contrato
do AcessaCidade garante `id`, `name` e `data-rpa` estáveis.

## 5. Fotografia: as duas opções

`MODO_UPLOAD_FOTO` no `Data/Config.xlsx`:

| Valor | O que o robô faz | Quando usar |
|---|---|---|
| `DIALOGO` (padrão) | **Click** com mouse real (`SimulateClick = False`) em `#campo-foto` → abre o diálogo "Abrir" do Windows → **Type Into** no campo "Nome" (`ctrlid='1148'`) com o caminho absoluto da imagem + `[k(enter)]` | Funciona em Edge/Chrome com qualquer versão da extensão. O navegador precisa estar visível (execução atendida). |
| `TYPEINTO` | **Type Into** direto no `input type=file` com o caminho | Só se o seu navegador/versão da extensão aceitar (navegadores Chromium normalmente bloqueiam valor programático em input file). **Teste antes.** |
| `IGNORAR` | Não anexa a foto (linha é cadastrada sem foto) | Demonstração rápida, ou se o diálogo não funcionar no seu Windows. |

Se o seletor do diálogo falhar: abra o diálogo manualmente (clique em "Escolher arquivo"), use
**Indicate on screen** na caixa "Nome:" e copie o seletor gerado (geralmente `<wnd app='msedge.exe'
cls='#32770' title='Abrir' /><wnd ctrlid='1148' />`; em Windows em inglês o título é "Open").

Os caminhos de imagem vêm da coluna `Caminho_Imagem` (nome do arquivo) + `PASTA_IMAGENS`
(padrão `..\..\..\data\samples\fotos`, relativo à pasta do projeto UiPath). As imagens são **sintéticas**,
geradas pela disciplina 04.

## 6. Ajustes de tempo

- `TIMEOUT_SEGUNDOS` (Config.xlsx, padrão 30) controla a espera pelo protocolo/erro após o envio.
  Contra a URL na Azure (primeiro acesso pode "acordar" o serviço), aumente para 60.
- Os `Type Into` usam `SimulateType = True` (digitação por evento, sem depender do foco do teclado) e
  `EmptyField = True` (limpa o campo antes de digitar). Se algum campo não "pegar" o valor (a SPA não
  receber o evento `input`), troque esse campo para `SimulateType = False` (digitação de hardware).
- Se o site for lento para renderizar a SPA, o robô espera `#form-denuncia` existir antes de digitar
  (Element Exists com o timeout configurado).
