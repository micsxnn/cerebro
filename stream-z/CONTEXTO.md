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
  (o id já é público no feed.js do repo; escrever no feed exige token — que NUNCA
  fica salvo aqui)
- Skill local: /home/z/my-project/skills/stream-z — snapshot em ./skill/

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

## Como restaurar em sandbox nova
1. Clone este cérebro e o repo stream-z.
2. Tokens NUNCA estão salvos — peça ao usuário: GitHub (escopo gist) e, se for
   redeploy, Vercel (Full Account). Salve em /home/z/my-project/.secrets/tokens.env
   (chmod 600) e crie .secrets/mirror.json = {"gist_id": "<id acima>"}.
3. Carregue a skill de skills/stream-z (ou restaure o snapshot ./skill/).
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
