# Roteiro de gravação — vídeo-pitch AcessaCidade

Objetivo: um vídeo de **até 5 minutos**, com **todos os integrantes**, contendo a **demo real** do fluxo ponta a ponta
na **URL pública**, publicado no YouTube com link acessível sem login.

> Pré-requisito que depende de outro componente: a **URL pública do MVP** (disciplina 06 — Secure DevOps & Cloud).
> Enquanto ela não existir, a demo NÃO pode ser gravada (gravar em `localhost` não atende ao critério
> "fluxo central operando de verdade em URL pública"). URL: `[PREENCHER: URL pública do MVP]`.

## 1. Equipamento e programas

| Item | Recomendação | Observação |
|---|---|---|
| Gravação de tela | **OBS Studio** (gratuito, obsproject.com) | Alternativa: Barra de Jogos do Windows (Win + Alt + R) |
| Câmera | Webcam do notebook ou celular na horizontal | Luz de frente (janela ou luminária), nunca atrás |
| Microfone | Fone com microfone ou microfone de lapela de celular | Evitar o microfone embutido do notebook se houver ventoinha |
| Edição | **Clipchamp** (vem no Windows 11), DaVinci Resolve ou Shotcut | Todos gratuitos |
| Navegador | Microsoft Edge ou Chrome, janela **anônima/InPrivate**, zoom 110–125% | Sem abas pessoais, sem favoritos visíveis |

## 2. Configuração do OBS Studio (uma vez)

1. Abra o OBS → **Arquivo › Configurações › Vídeo**: Resolução base e de saída **1920×1080**, FPS **30**.
2. **Configurações › Saída**: Modo simples; Qualidade de gravação "Alta qualidade, tamanho médio"; Formato **mkv** (não perde a gravação se o programa travar). Depois use **Arquivo › Remuxar gravações** para converter em mp4.
3. **Configurações › Áudio**: selecione o microfone correto em "Áudio do microfone".
4. Em **Fontes**, clique em **+ › Captura de janela** e escolha a janela do navegador (ou **Captura de tela** para o monitor inteiro).
5. No mixer de áudio, fale normalmente e confira se o medidor fica na faixa amarela (≈ −12 dB), sem chegar ao vermelho.
6. Desative notificações do Windows: **Configurações › Sistema › Notificações › Não perturbe: Ativado**.

## 3. Preparação do MVP antes de gravar

1. Abra a URL pública em **janela anônima** e confira `/health` (`[PREENCHER: URL]/health` deve responder `"status": "ok"`).
2. Tenha a foto da demo pronta numa pasta fácil (`a2_foto_demo.jpg`, ver `LISTA_DE_CENAS.md`).
3. Defina os dados que serão digitados (anote num papel): logradouro, bairro, descrição de 1–2 frases, tipo "Buraco na calçada", impacto "Impede a passagem". **Não use nome real** no campo Nome (deixe vazio).
4. Verifique se o assistente está em modo LLM ou por regras (`/health` → `componentes.assistente`). Diga no vídeo qual é.
5. Abra o painel `#/painel` uma vez antes, para saber onde a nova denúncia vai aparecer.

## 4. Ordem de gravação (não precisa ser a ordem do vídeo)

1. **Demo de tela (B1–B6)** — primeiro, porque depende da URL pública e pode precisar de repetição.
   Grave o fluxo inteiro **em uma tomada contínua** (corta-se depois):
   1. Acessar a URL pública (mostrar a barra de endereço).
   2. Página inicial → **Registrar denúncia**.
   3. Preencher o formulário, anexar a foto, marcar o consentimento, **Enviar**.
   4. Mostrar o **protocolo gerado** (`#protocolo-gerado`).
   5. Clicar no link de acompanhamento → ver as **etapas da triagem** (original, cinza, filtrada, contraste, bordas, máscara, contornos), a explicação e o status **Aguardando revisão**.
   6. Ir a **Consultar** e buscar pelo protocolo.
   7. Ir ao **Assistente** e perguntar: "O que significa aguardando revisão no protocolo AC-...?"
   8. Ir ao **Painel** e mostrar que o total aumentou e a seção analítica do pipeline (com o aviso de dados simulados).
2. **Narração da demo (C3)** — grave o áudio assistindo à gravação de tela, seguindo o bloco 3 do `ROTEIRO_PITCH.md`.
3. **Falas na câmera (C1, C2, C4, C5)** — cada integrante, no mesmo enquadramento (peito para cima, olhos no terço superior).
4. **Apresentação do time (C6)** — cada um diz nome e papel em uma frase.
5. **Captação no território (A1–A3)** — se ainda não feita.
6. **Lean Canvas (B8)** — `LEAN_CANVAS.html` no navegador, rolando devagar.

## 5. Dicas de áudio

- Ambiente pequeno, com cortinas/roupas/sofá (absorvem eco). Evite cozinha e banheiro.
- Celular em modo avião durante a gravação.
- Microfone a ~15–20 cm da boca, levemente de lado (evita "estalos" de P e B).
- Grave 5 segundos de silêncio no começo (ajuda a remover ruído na edição).
- Fale ~10% mais devagar que numa conversa; pausa curta entre os blocos.
- Se errar, pare, respire, e **repita a frase inteira** — é mais fácil cortar depois.

## 6. Edição

1. Monte na ordem do `STORYBOARD.md`. Linha do tempo: vídeo da câmera/tela na faixa 1, narração na faixa de áudio 1, trilha na faixa 2 (−25 dB).
2. Na demo, **corte esperas** (upload, carregamento), mas **não altere a sequência nem o resultado** exibido. Nada de tela simulada.
3. Aplique **zoom** (1,3×–1,5×) no protocolo, nas etapas da triagem e nos números do painel.
4. Adicione **legendas** em português (o Clipchamp gera legendas automáticas: revise palavra por palavra).
5. Coloque cartelas (D1–D7). Dados públicos sempre com a fonte na tela; preços com "valores hipotéticos".
6. Confira a duração final: **≤ 5:00** (ideal 4:45–4:55).
7. Exporte em **1080p, MP4 (H.264)**.

## 7. Publicação no YouTube

1. Acesse **studio.youtube.com** com a conta da equipe → **Criar › Enviar vídeos** → selecione o MP4.
2. Título: `AcessaCidade — Pitch + MVP | FIAP Global Solution 2026.2 CitizenTech` (ajuste se quiser).
3. Descrição: resumo de 2 linhas + links do MVP e do repositório (`[PREENCHER]`).
4. **Público-alvo**: "Não, não é conteúdo para crianças".
5. **Visibilidade**: **Não listado** (qualquer pessoa com o link assiste) **ou Público**. **Nunca "Privado"** — a banca não consegue abrir.
6. Aguarde o processamento em HD terminar antes de copiar o link.
7. Copie o link `https://youtu.be/...` e cole em:
   - `03-Business-Intelligence-Startup/docs/links_entrega.yaml` (campo `url_video`);
   - `docs/FICHA_TECNICA_MVP.md` e no README da raiz (se houver campo de vídeo).

## 8. Checagem do link (obrigatória)

1. Abra uma **janela anônima** (Ctrl + Shift + N no Edge/Chrome), **sem login** em conta Google.
2. Cole o link do vídeo → o vídeo deve tocar inteiro, em 1080p, com áudio.
3. Repita em um **celular com dados móveis** (fora do Wi-Fi da equipe).
4. Faça o mesmo para a **URL do MVP** e o **repositório** (deve abrir sem login no GitHub).
5. Tire um print de cada teste (vai para `pitch/evidencias/`).
6. **Mantenha tudo público até o fim da correção** (até uma semana após 19/11/2026, conforme regras da GS).
