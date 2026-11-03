# AgentForge

Plataforma open source de agentes com IA — projeto do `lucasgabrieldevgg` (amigo do usuário), com colaboração do `micsxnn`. Coordenação numa "Sala de Agentes" (saladeagentes.vercel.app/?s=AG-KMN3T7): líder Z.ai + Agente 1 (Z, eu).

## Links e IDs importantes

- Repo público: https://github.com/lucasgabrieldevgg/agentforge (MIT, branch `main`)
- Branch de trabalho do app local: `feat/local-v0.1-appimage` (daemon Bun + supervisor + tools + AppImage)
- Minha branch (F5): **`feat/agente1-search`** (commit `da90c2b`)
- Demo web: https://agentforge-blue-zeta.vercel.app · App local: daemon na :3199, AppImage 48MB
- Sala: AG-KMN3T7 (Firebase RTDB por trás; reporta-se por TAREFA/FEITO/BLOQUEIO/DECISÃO)
- Plano v0.2 (contrato de divisão): doc `07-plano-v02.md` anexado na sala
- Push com token do `micsxnn` (colaborador) — NUNCA registrar o token aqui

## Estado atual (2026-11-02/03, fuso America/Cuiaba)

### Sessão A — READMEs do agentforge (fechada)
- Commit `7a5eafe` na main: README.md + README.pt-BR.md reescritos (profissional, sem emojis, header com logo/badges). Corrigidos: header duplicado no PT-BR, árvore quebrada, flags na tabela de env.

### Sessão B — Sala de agentes: tarefa F5 (fechada com ressalva de canal)
- Onboarding recebido da líder (doc 07-plano-v02.md): escopo Agente 1 = SÓ `local/src/tools/search.ts`, `search-impl.ts`, `search.test.ts`.
- **F5 ENTREGUE**: 8 tools de busca (web_search DDG Lite c/ POST+fallback GET+detecção de bloqueio; arxiv_search; openalex_search; hn_search; stack_search; github_search; weather_lookup c/ geocoding; gdelt_search c/ timeout 20s justificado) + wikipedia_search mantida como referência. Zero deps, zero keys, timeout 10s, saída 12KB. PT-BR, Conventional Commits.
- **Testes**: `bun test src/tools/search.test.ts` = 19 pass / 3 skip / 0 fail (22 testes; skips só por ambiente de datacenter: DDG egress instável, OpenAlex cota de IP, GDELT throttle — pré-voo documentado no arquivo).
- **Job real no daemon (aceite 4.4-2)**: job `done` em 3 iterações — web_search com resultados REAIS do DuckDuckGo (1. Bun — bun.sh), wikipedia_search de 2ª fonte, declare_done com as fontes. LLM via AGENTFORGE_MOCK_SCRIPT (mecanismo do daemon p/ testes); as tools rodaram rede de verdade.
- **Push**: branch `feat/agente1-search` no repo público (da90c2b) ✓
- **BLOQUEIO DE CANAL (não é do trabalho)**: desde ~04:05 (hora da sala) TODA escrita no Firebase da sala virou PERMISSION_DENIED (site mostra "não foi: set"; probes diretos em msgs/ e fora da sala idem; leitura OK; o app nem carrega firebase-auth). Meus relatos de 02:59 (BLOQUEIO/onboarding) e 03:44 (TAREFA/assumi F5) passaram — as rules mudaram no servidor no intervalo, perto do FEITO da líder às 04:01 (provavelmente via helper room.py com acesso elevado). Resultado: o FEITO do F5 não pôde ser postado na sala; a prova está no repo público.

## Como restaurar o ambiente numa sandbox nova

1. `git clone -b feat/local-v0.1-appimage https://github.com/lucasgabrieldevgg/agentforge agentforge-local && cd agentforge-local/local`
2. Bun já no PATH do sandbox; `bun test src/tools/search.test.ts` (verde esperado; skips dependem da rede)
3. Job real: script `/home/z/my-project/scripts/f5_real_job.sh` (sandbox efêmera — recriar se preciso)
4. Sala: entrar com nome "Z" (identidade persiste em localStorage do agent-browser; pode sumir com a sandbox)
5. Commitar com identidade `micaelsan <167715159+micsxnn@users.noreply.github.com>`

## Pendências

- [ ] Postar o FEITO do F5 na sala quando a escrita voltar (texto pronto; ou o dono/líder relata via room.py) + líder revisar e integrar na branch principal.
- [ ] Descobrir/reverter a mudança de rules do Firebase da sala (o dono é quem administra o projeto).
- [ ] F4/F2 são da líder (browser do agente, providers diretos); minha próxima fatia: aguardar divisão.
- [ ] Badge de versão do README é estático (0.22.1) — atualizar por release.
- [ ] Lembrar o usuário de revogar o token usado nas sessões.
