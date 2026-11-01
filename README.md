# 🧠 cérebro

Memória persistente do agente — o lugar onde o contexto dos chats e projetos
sobrevive à reciclagem das sandboxes. Uma pasta por projeto; a raiz tem só este README.

## Protocolo do agente (siga NA ORDEM)

1. **Puxe contexto antes de trabalhar.** Vai mexer num projeto? Procure a pasta dele
   aqui, leia o contexto (começando pelo `CONTEXTO.md`) e continue DO estado salvo —
   não refaça o que já está pronto e não invente estado.
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
