---
name: espelho
description: Espelho ao vivo — streama TODAS as falas do agente (incluindo narrativas intermediárias entre tool calls) para um site que o usuário acompanha em tempo real, ANTES de aparecerem no chat, com marcador «fim» no fim de cada turno. Use SEMPRE que o usuário pedir para trabalhar "com o espelho ligado", "no espelho", "me mostrando ao vivo", "streama pro site", "quero ver você trabalhando" ou qualquer acompanhamento em tempo real; também use para montar o ambiente do zero (gist + viewer + push) ou para reconectar/recuperar um espelho que parou de atualizar. Não serve para tarefas rápidas em que ninguém está assistindo — aí o uso é opcional.
---

# Espelho ao vivo (arquitetura stream-z)

O usuário acompanha seu trabalho em tempo real num site estático que lê um feed JSON.
Você transmite cada fala para o feed ANTES de escrevê-la no chat — mesmo quando a
plataforma travar, o espelho continua mostrando o que você está fazendo.

## Arquitetura

```
sandbox (você)                      GitHub (gist SECRETO = banco do feed)
mirror_push.py  ── PATCH ──────▶   feed.json = {"updated","items":[{t,k,x}]}
                                        │ GET autenticado
                                        ▼
                        proxy serverless /api/feed  (o token NUNCA vai ao navegador)
                                        │ no-store, sem cache
                                        ▼
                        viewer estático (poll 2,5 s, agrupa emissores, marca «F I M»)
```

Por que um gist e não um banco? Zero infraestrutura, versionamento de graça e a API
aceita PATCH num único arquivo. Por que um proxy? O CDN do gist cacheia a resposta —
sem o `/api/feed` autenticado o viewer mostra feed velho.

## A REGRA DE OURO — operar vem antes de montar

Se o espelho já existe (`.secrets/mirror.json` com `gist_id`, ou o usuário informou
o site/token), PULE a configuração e vá direto para "Operação".

1. **Todo texto que você falar no chat vai PRIMEIRO pro espelho, verbatim, e DEPOIS
   aparece no chat.** Inclui narrativas intermediárias entre tool calls ("vou checar…",
   "agora vou montar…"). Se um turno tem 6 falas, o espelho recebe as 6.
2. **Ao TERMINAR cada turno**: `--kind fim --text "fim"` — desenha o marcador «F I M»
   que separa os turnos no site.
3. **Mensagens do USUÁRIO nunca vão pro espelho** (privacidade).
4. Push falhou? Repita. O viewer mostra banner "sem sinal" após 3 polls sem update —
   isso quase sempre significa que VOCÊ parou de transmitir.

### Operação (a cada fala)

```bash
set -a && source /home/z/my-project/.secrets/tokens.env && set +a
python3 /home/z/my-project/skills/espelho/scripts/mirror_push.py --kind agent --text "<sua fala EXATA>"
```

| kind | quando usar |
|---|---|
| `agent` | qualquer texto seu que aparecerá no chat (narrativas incluídas) |
| `status` | estados do trabalho ("deployando…", "pronto") |
| `tool` | avisos de ferramenta, se quiser marcar |
| `fim` | UMA vez, no fim de cada turno |

O agrupamento de falas consecutivas do mesmo emissor é automático no viewer — o
símbolo «z» não se repete a cada parágrafo. É feature, não bug; não tente "corrigir".

## Configuração (montar do zero)

**PASSO 1 — pergunte ao usuário onde o viewer vai morar** (use exatamente esta pergunta):

> Onde você quer ver o espelho: **(A) na Vercel** — link fixo, tipo
> `espelho-z.vercel.app`, sobrevive a tudo — **ou (B) no preview da plataforma** —
> mais rápido de subir, mas o link é gigante e muda a cada sessão?

- Resposta **A → leia `reference/vercel.md`** e siga o passo a passo completo
  (inclui orientar o usuário a criar o token Vercel com escopo **Full Account**).
- Resposta **B → leia `reference/preview.md`** e siga o passo a passo completo
  (inclui ENCURTAR o link do preview com is.gd antes de entregá-lo ao usuário).

Pré-requisitos dos dois caminhos (recolha tudo antes de começar):

- **Token GitHub** com escopo `gist` — o usuário cria em github.com → Settings →
  Developer settings → Personal access tokens (clássico) e te manda no chat.
- Os arquivos prontos estão nesta skill: `assets/viewer.html` (o site), `assets/feed.js`
  (o proxy de leitura) e `scripts/mirror_push.py` (a transmissão). **Copie, não
  reimagine** — eles já implementam agrupamento, «F I M», skeleton e truncagem.

## Segurança

- Tokens morrem em `.secrets/` (pasta 700, arquivos 600), FORA de qualquer git.
- Em toda chamada Bash que usa token: `set -a && source .secrets/tokens.env && set +a`.
- O token NUNCA vai ao navegador — o viewer só conversa com o proxy.
- No fim do projeto, lembre o usuário de REVOGAR os tokens (GitHub e Vercel).

## Troubleshooting

- **Feed velho no site** → o viewer deve ler `/api/feed` (proxy no-store), nunca
  `gist.githubusercontent.com` direto (o CDN do gist cacheia).
- **Feed cresce sem parar** → `mirror_push.py` trunca sozinho (400 itens / 400 KB).
- **401 no push** → token girou/revogou; peça um novo ao usuário e atualize
  `.secrets/tokens.env`.
- **Preview fora do ar** → o preview vive enquanto a sessão vive; suba de novo e
  re-encurte o link — o feed está no gist, nada se perde.
