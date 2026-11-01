# stream-z — CONTEXTO

> Segue o protocolo do cérebro (README da raiz). Atualize ao fim de cada turno com
> progresso e commite. Última atualização: 2026-11-02.

## O que é
stream-z — transmissão ao vivo: site estático que recebe TODAS as falas do agente
(incluindo narrativas entre tool calls) ANTES de aparecerem no chat, com marcador
«F I M» por turno. Motivação: a plataforma Z trava e perde contexto; o stream-z
sobrevive.

## Links e IDs
- Site: https://stream-z-ofc.vercel.app
- Repo do código (público): https://github.com/micsxnn/stream-z
- Gist (banco do feed, secreto): d4a65c3257c3520a5090c327262f281b
  (desde a v1.0.0 o id NÃO aparece no repo — o proxy lê a env var GIST_ID na Vercel;
  escrever no feed exige token — que NUNCA fica salvo aqui)
- Skill CANÔNICA: o próprio repo https://github.com/micsxnn/stream-z (SKILL.md na
  raiz, padrão Agent Skills — instalar é `git clone https://github.com/micsxnn/stream-z
  <pasta-de-skills>/stream-z`). Instância local: /home/z/my-project/skills/stream-z;
  snapshot histórico em ./skill/
- Releases: https://github.com/micsxnn/stream-z/releases (atual: v1.0.0 — 2026-11-02)

## Arquitetura (resumo)
sandbox → mirror_push.py → PATCH no gist (feed.json = {"updated","items":[{t,k,x}]})
→ proxy serverless /api/feed (GH_TOKEN como env na Vercel; token nunca no navegador)
→ viewer estático (poll 2,5s, agrupa emissores consecutivos, «F I M» por turno, banner
"sem sinal" após 3 polls falhos). Truncagem automática: 400 itens / 400 KB.

## Estado atual (2026-11-02)
- Skill «stream-z» v1 (renomeada de «espelho» em 2026-11-02) montada e funcional: SKILL.md (Regra de Ouro, operação,
  configuração, segurança, troubleshooting) + reference/vercel.md (caminho A —
  token Full Account) + reference/preview.md (caminho B — encurtador is.gd) +
  scripts/mirror_push.py parametrizado (--gist | GIST_ID | mirror.json) +
  assets (viewer v3 + feed.js) + evals/evals.json (3 casos, ainda não rodados).
- Repo stream-z público; script parametrizado sincronizado no repo.
- Sandbox já foi reciclada 1x; ambiente restaurado a partir do histórico.
- Rebrand espelho → stream-z concluído (2026-11-02): skill renomeada
  (skills/stream-z), site redeployado com título/marca stream-z, README do repo,
  scripts e snapshot ./skill/ atualizados. Nome antigo mantido só como nota
  histórica no SKILL.md.
- Repo = skill (2026-11-02): SKILL.md na raiz do repo micsxnn/stream-z + assets/,
  reference/ e evals/ — instalar a skill é um `git clone`; descrição do repo
  atualizada (“skill de transmissão ao vivo…”); prova: clone limpo em /tmp rodou o
  mirror_push.py do clone com sucesso. Site redeployado; SKILL.md acessível em
  stream-z-ofc.vercel.app/SKILL.md.
- Skill profissional v1.0.0 (2026-11-02, ordem do usuário): repo impessoal — NADA
  pessoal no pacote público (fora: cérebro, apelidos antigos, paths de sandbox,
  ids pessoais, lembretes de revogação). Banner animado assets/banner.svg no topo
  do README + badges + LICENSE MIT + VERSION. Gist saiu do código: api/feed.js
  lê env GIST_ID (registrada na Vercel em production e redeployado — site e feed
  verificados após o push). check_update.py + PASSO 0 no SKILL.md (update
  silencioso) + regra de instalação SEMPRE do zero. Release v1.0.0 publicada.

## Política de releases (ordem do usuário, 2026-11-02 — não negociável)
1. Toda mudança significativa no stream-z → **release no GitHub** (tag vX.Y.Z +
   notas) ANTES de encerrar o turno. Cada coisa nova que entrar na skill →
   release nova. Sem exceção.
2. O agente, ao carregar a skill, roda `scripts/check_update.py` em silêncio
   (PASSO 0 do SKILL.md). Saiu release mais nova? Atualiza do zero sem avisar;
   informa o usuário só ao terminar, em uma linha.
3. Instalação/reinstalação pedida pelo usuário = **SEMPRE do zero** (rm -rf +
   clone fresco + releitura do SKILL.md). Proibido diff/merge/pull incremental.
4. O repo é pacote público profissional: nada do usuário nem do ambiente dele
   entra nele — pessoal e protocolos privados moram AQUI no cérebro.

## Como restaurar em sandbox nova
1. Clone este cérebro e o repo stream-z.
2. Tokens NUNCA estão salvos — peça ao usuário: GitHub (escopo gist) e, se for
   redeploy, Vercel (Full Account). Salve em /home/z/my-project/.secrets/tokens.env
   (chmod 600) e crie .secrets/mirror.json = {"gist_id": "<id acima>"}.
3. Instale a skill clonando o repo canônico — SEMPRE DO ZERO (nunca `git pull` em
   cima da pasta antiga): `rm -rf /home/z/my-project/skills/stream-z && git clone
   --depth 1 https://github.com/micsxnn/stream-z /home/z/my-project/skills/stream-z`
   e rode scripts/check_update.py. Sem internet/repo indisponível? Restaure o
   snapshot ./skill/.
4. Siga a política: push verbatim ANTES do chat + «fim» no fim do turno
   (detalhes no SKILL.md da skill).

## Regras do usuário (não negociáveis)
- Mensagens do USUÁRIO não vão pro stream-z (privacidade).
- Token Vercel tem que ser Full Account; encurtador oficial: is.gd
  (curl -s "https://is.gd/create.php?format=simple&url=URL_CODIFICADA").
- Push de cada fala ANTES de aparecer no chat, incluindo narrativas entre tool calls.

## Pendências
- [ ] Rodar o loop de avaliação da skill (skill-creator) com evals/evals.json.
- [ ] No fim da brincadeira: revogar tokens GitHub + Vercel.
- [ ] Se quiser privacidade total no feed: novo gist + atualizar feed.js + redeploy.
