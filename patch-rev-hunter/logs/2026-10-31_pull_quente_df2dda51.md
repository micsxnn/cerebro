# Pull quente do payload — descobertas (2026-10-31 ~18:40 local netbook)

Contexto: ponte-local operacional (netbook /home/msan + adb → celular ZF523XMG3M autorizado).
run_command da ponte funcionou de 1ª (`adb devices` → device).

## O que descobrimos (em 6 comandos pela ponte)
1. `adb exec-out run-as com.hunter.net tar -cf - files` → 427 KB (funciona, sem Stream closed —
   o problema era o aShellYou/Shizuku no celular, nunca o adb).
2. MAS o jar em `files/.59bca860/ز֯٬ڲܮ.jar` tem só **285.269 B** e é "data" cifrada (não é zip).
   O dex real de 14,6 MB NÃO está aí.
3. dumpsys: v8 instalada com `pkgFlags=[DEBUGGABLE ...]` ✔; celular é Moto hawaii/Android 11.
4. logcat da execução: DexPathList aponta `files/.59bca860/df2dda51/ز֯٬ڲܮ.jar` — a subpasta
   `df2dda51` é criada em runtime; logcat mostra CNFE RevHunterApp (mesmo padrão v8).
5. **Depois do crash, `df2dda51/` PERMANECE no disco (não é apagada!) — o que some é o JAR de
   dentro.** Também aparece `e345435e.dex` com **0 bytes** (artefato zerado — anti-dump do LIAPP:
   o conteúdo é entregue em memória e o arquivo fica vazio/truncado).
6. Pull em loop pelo adb (15×) não capturou: janela de vida do jar < tempo de ida-e-volta do exec-out.

## Estratégia em curso (comando #9, aguardando netbook reconectar)
Watcher DENTRO do celular (run-as) fazendo snapshot acumulativo a cada ~12-20 ms:
```
run-as com.hunter.net sh -c 'rm -rf files/snap; i=0; while [ $i -lt 4000 ]; do
  cp -r files/.59bca860/. files/snap/ 2>/dev/null; i=$((i+1)); sleep 0.012; done'
```
- `cp -r` é ACUMULATIVO: nunca apaga o que já capturou; o cp completo mais recente vence.
- Em paralelo: `am start -n com.hunter.net/.LauncherActivity` (mais rápido que monkey).
- Janela de captura: entre o write completo do jar e a deleção — detectada em ≤20 ms.
- Depois: `adb exec-out run-as com.hunter.net cat files/snap/df2dda51/*.jar > dump.jar` no netbook.

## Estado da ponte
- Comandos #2..#8 OK via netbook. Comando #9 enfileirado; agente do netbook desconectou
  (terminal fechado?) antes de executar. Religar: `cd ~/ponte-agent && nohup node agent.js
  --auto --save > ponte.log 2>&1 &` — nohup sobrevive ao fechamento do terminal.

## Lições
- aShellYou/Shizuku era o gargalo: via adb tudo flui (tar 427 KB em ~200 ms).
- monkey demora ~17 s para injetar (elapsed 17092 ms) — usar `am start` direto.
- O LIAPP v5.1.1.183: pasta runtime permanece, jar e dex são zerados/apagados → dump
  precisa ser inotify-like (loop cp interno no app, não pulls externos).
