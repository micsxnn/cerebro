# AgentForge

Plataforma open source de agentes com IA — projeto do `lucasgabrieldevgg` (amigo do usuário), com colaboração do `micsxnn`.

## Links e IDs importantes

- Repo público: https://github.com/lucasgabrieldevgg/agentforge (MIT, branch `main`)
- Demo ao vivo: https://agentforge-blue-zeta.vercel.app
- Versão: 0.22.1 (`package.json`)
- Stack: Next.js 16 (App Router/Turbopack), TypeScript 5, Tailwind CSS 4 + shadcn/ui, Prisma 6 (SQLite em dev, Postgres/Supabase em prod), Zustand, OpenRouter; CI em `.github/workflows/ci.yml`
- Push feito com token do `micsxnn` (colaborador) — NUNCA registrar o token aqui

## Estado atual (2026-11-02, fuso America/Cuiaba)

- Commit `7a5eafe` na main do agentforge: "docs: restructure README and README.pt-BR" (a partir de `046302e`), push confirmado e conteúdo verificado ao vivo (EN e PT-BR).
- `README.md` (EN) e `README.pt-BR.md` reescritos e espelhados: tom profissional, SEM emojis, header centralizado (logo `public/logo.svg` + badges CI/MIT/versão/stack/demo), ordem: Sobre → Funcionalidades → Stack → Quick start → Docker → Configuração → Uso → Deploy → Modo demo → Estrutura → CI → Contribuir → Licença → Agradecimentos.
- Correções incluídas: header duplicado no `README.pt-BR.md`; indentação quebrada na árvore de estrutura; indicadores da tabela de env viraram texto (Sim/Não); seção "Identidade — FORJA" condensada numa linha da seção Sobre; tabela de stack em formato tabela; link para `docs/DEPLOY-SUPABASE.md` adicionado.
- Cópia dos dois READMEs salva na sandbox em `/home/z/my-project/download/` (efêmera, não é backup).

## Decisões tomadas

- Badges shields.io mantidos: são imagem, não emoji — padrão em README profissional.
- Nada inventado: todo o conteúdo factual (features, env vars, comandos, limites da demo) veio dos READMEs e do código existentes.
- Seção "Projetos relacionados" citando o Cérebro: proposta ao usuário, sem resposta ainda — não incluir sem ok.

## Como restaurar o ambiente numa sandbox nova

1. Clone público: `git clone https://github.com/lucasgabrieldevgg/agentforge.git`
2. Push exige token do `micsxnn` com acesso de colaborador (usuário fornece no chat; nunca persistir em arquivo).
3. Commitar com identidade `micaelsan <167715159+micsxnn@users.noreply.github.com>`.
4. Começar daqui: não refazer o que já está pronto (ver Estado atual).

## Pendências

- [ ] Decidir com o usuário sobre a seção "Projetos relacionados" (Cérebro) nos READMEs do agentforge.
- [ ] Badge de versão é estático (0.22.1): atualizar manualmente a cada release ou migrar para badge dinâmico de releases.
- [ ] Lembrar o usuário de revogar o token da sessão (ele já foi derrubado pelo GitHub uma vez durante o uso).
