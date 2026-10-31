# Ponte: skill desatualizada → v1.8.0 (micsxnn/ponte-local)

**Data:** 2026-10-31 · **Lane:** netbook · **Status:** compatibilidade confirmada, aguardando usuário atualizar

## Contexto
- Usuário: "a skill que você mandou eu instalar está totalmente desatualizada. Pega ela ATUALIZADA por aqui. micsxnn/ponte-local."
- Reclamação de visibilidade: com `nohup ... > ponte.log 2>&1 &` o terminal fica mudo — usuário não vê nada do que a IA faz.

## Descobertas (repo público micsxnn/ponte-local, branch main)
- **Agente v1.8.0** (`agente/agent.js`, 70 KB): leitura universal read_text/read_binary com
  **offset + maxBytes → proximoOffset** (arquivos grandes em pedaços!), write_binary até 8 MB,
  **god_mode** (ativação conversacional, sem flag CLI), **skill auto-atualizada** a cada 60 s do
  repo → `~/ponte-agent/SKILL.md` (fim do problema de skill velha), relatório de tarefa (task_done).
- **Operador** (`operador/ponte.py`): idêntico ao já instalado no sandbox em `scripts/ponte.py`
  (diff vazio). Tem `pegar`/`enviar` (transferência de arquivos), `--drain`, `--status`, lanes.
- **Relay do repo** usa os mesmos endpoints `/api/ponte/{poll,result,cmd,results,status,download}`
  → relay do sandbox (v1.3.1, com lanes) é **100% compatível** com o agente v1.8.0. Nada a migrar.
- Repo é **público**: netbook baixa com curl puro, sem token.

## Estado no momento
- Agente antigo **v1.3.0** ainda conectado (lane netbook, lastSeen 0 s, modo autônomo, msan-cachyos).
- **Watcher TOTAL (resultado #52): FALHOU** — `adb: no devices/emulators found` (celular saiu da
  USB / autorização perdida antes do comando rodar). Nada foi capturado.

## Comando enviado ao usuário (netbook, atualizar + rodar em PRIMEIRO PLANO)
```bash
mkdir -p ~/ponte-update && cd ~/ponte-update
curl -sL -O https://raw.githubusercontent.com/micsxnn/ponte-local/main/agente/agent.js
curl -sL -O https://raw.githubusercontent.com/micsxnn/ponte-local/main/agente/atualizar.sh
bash atualizar.sh
# depois, na pasta que o atualizar.sh indicar (normalmente ~/ponte-agent):
cd ~/ponte-agent && node agent.js --auto --save
```
Foreground resolve a visibilidade: o terminal passa a mostrar conexão, cada comando e resultado
com timestamp. `--auto` mantém run_command sem s/N (sem god_mode preciso).

## Próximos passos
1. Usuário roda o bloco acima → agente v1.8.0 conecta em foreground.
2. **Reconectar o celular na USB** (watcher falhou por adb sem device) + verificar autorização.
3. Retomar captura: `adb devices` → Watcher TOTAL de novo (am start + cp acumulado em files/snap).
4. Payload ~14.6 MB → `read_binary` em pedaços (offset/maxBytes) via `pegar`, direto pro sandbox.
