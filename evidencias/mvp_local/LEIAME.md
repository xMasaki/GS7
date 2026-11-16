# Evidências locais do MVP (execução automatizada)

**Atenção:** as imagens desta pasta são capturas de uma execução **LOCAL** e **automatizada** do
AcessaCidade (backend FastAPI real + frontend), feita em **15/11/2026 às 03:52 (horário de Brasília)**
no computador de desenvolvimento, com o navegador Microsoft Edge em modo headless controlado pelo Playwright.

- Os dados exibidos são **SIMULADOS**: são as 28 denúncias de demonstração do seed (cidade fictícia
  "Cidade Exemplo") mais 2 denúncias de teste criadas pelo próprio script (AC-2026-000029, com foto
  sintética, e AC-2026-000030, sem foto, enviada por `#/registrar?canal=rpa`). As fotos são
  **sintéticas** (`data/samples/fotos`). Nenhuma pessoa real, endereço real ou foto real aparece.
- O assistente funcionou em **modo básico** (`fonte: fallback`, sem chave de IA configurada).
- A seção analítica do painel mostra um snapshot Gold gerado nessa mesma execução pelo pipeline
  `02-Big-Data-Architecture` (fonte simulada `denuncias_simuladas.csv` + exportação da API local),
  gravado só em uma pasta temporária.
- O endereço usado foi `http://127.0.0.1:8012` (máquina local). **Estas capturas não substituem as
  evidências da URL pública** exigidas na entrega: [PREENCHER: URL pública e prints/vídeo da aplicação implantada].

## Como foi gerado

1. Backend real iniciado em uma pasta de dados temporária (fora do repositório), com `SEED_DEMO_DATA=true`
   e tokens `ADMIN_TOKEN`/`PIPELINE_TOKEN` gerados na hora (`secrets.token_urlsafe`) só como variáveis de
   ambiente do processo (nenhum token foi gravado em arquivo):

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn acessacidade_api.main:app --app-dir app/backend --host 127.0.0.1 --port 8012
   ```

2. Pipeline de dados executado contra essa API (`python -m acessacidade_pipeline`, com `ACESSACIDADE_API_URL`
   e `PIPELINE_TOKEN` no ambiente e `PIPELINE_DATA_DIR` temporário).
3. Teste ponta a ponta (com o token da equipe apenas na variável `ACESSACIDADE_E2E_ADMIN_TOKEN`):

   ```powershell
   .\.venv\Scripts\python.exe app/frontend/tests_e2e/e2e_acessacidade.py --url http://127.0.0.1:8012 --shots evidencias/mvp_local
   ```

   Resultado real: `RESULTADO: 199/199 verificações OK; 0 falha(s).` (duração ~31 s). Servidor parado ao final.

## Arquivos

| Arquivo | O que mostra |
|---|---|
| `01_inicio_desktop.png` | Início com indicadores, ocorrências recentes, ODS 11 e aviso de serviço não oficial (1280 px) |
| `02a_registrar_validacao_desktop.png` | Formulário enviado vazio: resumo de erros e mensagens junto aos campos |
| `02b_registrar_preenchido_desktop.png` | Formulário preenchido com foto sintética e prévia |
| `02c_registrar_protocolo_desktop.png` | Sucesso: protocolo em `#protocolo-gerado` e resumo da triagem |
| `03_registrar_rpa_sem_foto_desktop.png` | Registro sem foto pelo canal `?canal=rpa` (origem RPA) |
| `04_detalhe_etapas_desktop.png` | Detalhe com status, histórico, resultado, métricas e as 7 etapas da imagem |
| `05_detalhe_simulado_desktop.png` | Detalhe de denúncia do seed com selo SIMULADO |
| `06a_consultar_protocolo_desktop.png` | Busca por protocolo levando ao detalhe |
| `06_consultar_filtros_desktop.png` | Consulta com filtros (status, sem simulados) |
| `07_analise_avulsa_desktop.png` | Testar análise de foto (nada é gravado) |
| `08_assistente_desktop.png` | Assistente em modo básico explicando o resultado e citando o protocolo |
| `09_painel_desktop.png`, `09b_painel_analitico_desktop.png` | Painel operacional e seção analítica (camada Gold) |
| `10_revisao_status_alterado_desktop.png` | Área da equipe: status alterado para "Em análise" com token |
| `11_sobre_desktop.png` | Sobre, privacidade/LGPD, limites da triagem |
| `12_404_desktop.png` | Página não encontrada |
| `21_` a `29_..._mobile.png` | As mesmas telas em largura de celular (390 px) e o menu móvel |
