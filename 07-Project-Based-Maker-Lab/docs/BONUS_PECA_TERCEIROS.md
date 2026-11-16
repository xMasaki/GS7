# Bônus (+0,5) — peça baixada integrada e creditada

Critério oficial: *"Peça baixada integrada — função real no projeto, creditada com link; a parte principal do
redesign é da equipe."*

> **Status:** nenhuma peça de terceiros foi escolhida ainda. Não indicamos um link específico porque não
> verificamos nenhum modelo — a equipe deve escolher, testar e creditar.

## 1. Onde a peça de terceiros entra

O projeto já tem um ponto de integração pensado para isso: a **fixação do suporte ao tubo**.
No projeto atual o suporte (`3d-print/suporte_tubo.stl`) tem dois túneis para abraçadeiras de nylon comuns.
A peça de terceiros pode **substituir as abraçadeiras de nylon** por uma abraçadeira/clip impresso para tubo de
25 mm, desde que passe pelos túneis do suporte ou se encaixe no berço.

Alternativas com função real (escolha UMA):
- Abraçadeira/clip para tubo de 25 mm (preferida — mesma função das abraçadeiras de nylon).
- Tampa (cap) para a ponta do tubo de PVC 25 mm (acabamento e segurança no protótipo).
- Base/pé para manter o tubo de demonstração em pé na mesa durante a apresentação.

## 2. Como escolher

1. Em https://makerworld.com, pesquise por termos como `pipe clamp 25mm`, `tube clip 25 mm`, `abraçadeira tubo 25`.
2. Filtros: licença que permita uso e remix (ex.: CC BY, CC BY-SA; se for NC, só uso não comercial e
   a publicação do conjunto precisa respeitar isso).
3. Confira as medidas no arquivo baixado (abra no fatiador ou no Onshape): diâmetro interno compatível com o
   **diâmetro medido** do tubo (`TUBO_DIAMETRO` em `cad/parametros.py`), largura da fita ≤ 5,5 mm se for
   passar pelos túneis (`SUPORTE_TUNEL_LARGURA`) e espessura ≤ 2,2 mm (`SUPORTE_TUNEL_ALTURA`).
4. Se não couber nos túneis, ajuste os parâmetros do túnel em `parametros.py` e rode `gerar_todos.py` —
   **não modifique a peça do autor sem a licença permitir** (derivados).
5. Imprima, teste a montagem e fotografe a peça em uso.

## 3. Registro de crédito (preencher)

| Campo | Valor |
|---|---|
| Nome da peça | [PREENCHER] |
| Autor(a) | [PREENCHER] |
| Link original | [PREENCHER] |
| Licença | [PREENCHER] |
| Data do download | [PREENCHER] |
| Arquivo baixado (salvar em `3d-print/terceiros/`) | [PREENCHER] |
| Escala/modificações | [PREENCHER] |
| Função no projeto | [PREENCHER] |
| Foto da peça integrada | [PREENCHER] |

O crédito precisa aparecer em três lugares: descrição do MakerWorld (e campo Remix), PDF de entrega
(`RELATORIO_ENTREGA_MAKER.md`) e README da disciplina. Deixe claro que placa, módulo tátil e suporte são
autoria da equipe.
