# 🧠 cérebro

Memória persistente do agente — o lugar onde o contexto dos chats e projetos
sobrevive à reciclagem das sandboxes. Uma pasta por projeto; a raiz tem só este README.

## Protocolo do agente (siga NA ORDEM)

1. **Puxe contexto antes de trabalhar.** Vai mexer num projeto? Procure a pasta dele
   aqui, leia o contexto (começando pelo `CONTEXTO.md`) e continue DO estado salvo —
   não refaça o que já está pronto e não invente estado. Os comandos prontos estão
   em **Como carregar o contexto**, logo abaixo.
2. **Crie a pasta ANTES de guardar.** Projeto novo = crie a pasta com o nome do
   projeto (ex.: `stream-z/`) e só ENTÃO comece a guardar arquivos dentro dela.
3. **Guarde o que importa** (dentro da pasta do projeto):
   - `CONTEXTO.md` — obrigatório: o que é o projeto, decisões tomadas, estado atual,
     links/ids importantes, como restaurar o ambiente numa sandbox nova, pendências;
   - arquivos de apoio quando valerem a pena (configs, snapshots, listas).
4. **Atualize ao fim de cada turno com progresso** e commite com mensagem clara do
   que mudou. Contexto velho é pior que contexto nenhum.
5. **Segredo NUNCA.** Nem token, nem senha, nem chave — mesmo sendo repo privado.
   Referencie ONDE o segredo vive (ex.: `.secrets/` da sandbox) e lembre o usuário
   de revogar tokens no fim do projeto.

## Como carregar o contexto

O repo é público — **ler** não exige token nem login. Do jeito mais rápido pro mais completo:

```bash
# 1. Um arquivo só (raw):
curl -fsSL https://raw.githubusercontent.com/micsxnn/cerebro/main/<projeto>/CONTEXTO.md

# 2. Listar o que tem numa pasta (API):
curl -fsSL https://api.github.com/repos/micsxnn/cerebro/contents/<projeto>

# 3. Clonar tudo (quando for trabalhar de verdade no projeto):
git clone --depth 1 https://github.com/micsxnn/cerebro
```

Ordem de leitura: `CONTEXTO.md` da pasta do projeto → arquivos de apoio que ele citar →
seção «como restaurar o ambiente» dentro dele. Se o repo voltar a ficar privado, os
mesmos comandos funcionam só acrescentando o header `Authorization: token $GH_TOKEN`
(raw e API aceitam; no clone, use o token como senha:
`git clone https://micsxnn:$GH_TOKEN@github.com/micsxnn/cerebro` — depois remova o token
do remote com `git remote set-url origin https://github.com/micsxnn/cerebro`).

## Estrutura

```
cérebro/
├── README.md          ← este protocolo
└── <projeto>/         ← uma pasta por projeto
    ├── CONTEXTO.md    ← o cérebro do projeto
    └── ...            ← apoio (snapshots, configs, logs)
```

## Projetos

| pasta | o que é |
|---|---|
| `stream-z/` | stream-z — transmissão ao vivo das falas do agente (site stream-z-ofc.vercel.app + skill «stream-z») |
| `patch-rev-hunter/` | contexto histórico do RE do RevHunter (memória original deste repo) |
| `ponte-local/` | Ponte Local — IA opera o PC do usuário pelo chat (estável público + beta privada + app desktop) |
| `agentforge/` | AgentForge — plataforma open source de agentes com IA (Next.js; repo público do lucasgabrieldevgg, colaboração do micsxnn) |
