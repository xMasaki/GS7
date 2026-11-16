# Exemplos com o LLM real — como gerar

Esta pasta guarda **somente** respostas reais do modelo de linguagem, geradas pelo script
`examples/gerar_exemplos_llm.py` com a chave da própria equipe. **Nenhuma resposta de LLM foi
escrita à mão nem inventada.** Enquanto não houver arquivos `respostas_llm_*.json` aqui, ainda
não existem exemplos reais com LLM nesta entrega.

O teste `tests/test_helper_cli_e_exemplos.py::test_nenhum_exemplo_llm_inventado` confere que todo
arquivo `respostas_llm_*.json` desta pasta tem metadados de geração e a `fonte` registrada.

## Pré-requisitos

1. Conta no OpenRouter (https://openrouter.ai) com créditos e uma chave de API criada
   (passo a passo em `../../PENDENCIAS_E_ACOES_MANUAIS.txt`, seção D).
2. **Limite de gasto** definido na chave (sugestão: US$ 1 — os 20 casos custam centavos, ver
   README da disciplina, seção 6).
3. Arquivo `.env` na raiz do repositório (copiado de `.env.example`, nunca versionado) com:
   - `OPENROUTER_API_KEY=` a chave da equipe
   - `OPENROUTER_MODEL=openai/gpt-4o-mini` (ou outro modelo do catálogo)

## Como gerar (PowerShell, na raiz do repositório)

```powershell
.\.venv\Scripts\python.exe 01-Generative-AI-Engineering/examples/gerar_exemplos_llm.py
# somente alguns casos:
.\.venv\Scripts\python.exe 01-Generative-AI-Engineering/examples/gerar_exemplos_llm.py --casos 01_como_registrar 05_consultar_protocolo_inexistente
```

Saídas: `respostas_llm_<AAAAMMDD-HHMMSS>.json` e `.md` nesta pasta, com data/hora (UTC), modelo,
fonte (`llm` ou `fallback`), avisos e tokens informados pelo provedor. Se algum caso cair no modo
básico (erro da API, guardrail), ele fica marcado como `fallback` — **não apague nem edite**:
isso também é evidência do comportamento real.

## Depois de gerar

1. Confira se nenhum arquivo contém a chave (`gitleaks` no CI; a chave nunca é gravada pelo script).
2. Compare as respostas com as do modo básico (`../fallback/exemplos_fallback.md`).
3. Registre o custo observado no painel *Activity* do OpenRouter em
   `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md` e no README (seção 6).
4. Faça um print da tela `#/assistente` com `fonte = llm` para as evidências.
