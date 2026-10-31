# Estado da ponte-local (2026-10-31 ~22:50 UTC)

## O que está pronto
- Relay Next.js completo no sandbox (`ponte-relay/`): painel (`/`) + APIs `/api/ponte/{status,poll,result,cmd,results,download}`.
- Tokens gerados (`PONTE_AGENT_TOKEN` / `PONTE_ADMIN_TOKEN`, arquivo `.ponte_tokens` chmod 600, nunca versionado).
- `agent.js` servido pela rota `/api/ponte/download` — instalação do agente é 2 comandos.
- Validação LOCAL: `GET /api/ponte/status` → `{"ok":true,"connected":false,...}` ✅

## Por que ainda não está no ar (extremo a extremo)
- URL pública alvo `https://preview-chat-a1260866-8acd-4bef-af97-e877a8e52dc6.space-z.ai/` → **502 persistente**
  (o gateway da plataforma não provisionou o upstream desta sessão; a página é placeholder com retry).
- Túneis (cloudflared/ngrok) **bloqueados por política no sandbox** → não há como expor o relay daqui.
- Limitação adicional: processos do sandbox não sobrevivem entre comandos/mensagens → a operação da
  ponte seria em "turnos" (1 comando Bash longo que sobe relay + enfileira + lê resultado).

## Decisão prática
Pull do payload **manual via adb no netbook** (guia: `2026-10-31_planoB_falhou_migracao_adb.md`):
```
sudo pacman -S --needed android-tools
adb devices                                  # aceitar RSA no celular
adb exec-out run-as com.hunter.net tar -cf - files > payload.tar
mkdir -p payload && tar -xf payload.tar -C payload
find payload -name "*.jar" -exec ls -la {} \;    # esperado ~14–15 MB
```
Entrega: anexar o `.jar` no chat (navegador do netbook) OU subir pela web em
`github.com/micsxnn/cerebro` → `patch-rev-hunter/` → Add file → Upload (15 MB entra).

## Opção futura — ponte 2.0 leve (automação total dos ciclos v9→teste→log)
Relay em node puro rodando no PRÓPRIO netbook (sem npm install) + túnel cloudflared no netbook
(túnel na máquina do usuário é permitido; a IA só faz curl de saída para a URL do túnel).
Agente no netbook polla `localhost:3000`. A IA comanda via `https://<trycloudflare>/api/ponte/cmd`.
Para ativar: usuário só pede.
