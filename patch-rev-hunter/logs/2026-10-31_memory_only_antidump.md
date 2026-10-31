# 2026-10-31 — Payload é memory-only; LIAPP tem anti-dump

## Watcher v2 (comando #55, 133s, exitCode 0)
Loop interno 2000× (cp de `files/.59bca860/.` → `files/snap/f/` + `code_cache/` → `files/snap/c/`,
sleep 0.01) durante am start. Resultado:
- `files/snap` = 578 KB — capturados APENAS o stub `ز֯٬ڲܮ.jar` 285.269 B (2 cópias: na raiz de
  .59bca860 e dentro de df2dda51, escrita às 18:26 = durante execução).
- **`ls -la files/.59bca860/df2dda51` com o app RODANDO (t=25s): diretório VAZIO.**
- `e345435e.dex` segue 0 byte durante execução.
### Veredito
O dex real NUNCA toca o disco: **InMemoryDexClassLoader (entrega 100% em memória)**. O stub de
285 KB é gravado brevemente em df2dda51, processado e apagado; o payload real descriptografado
só existe em RAM. Watcher de disco está DESCARTADO como via de captura.

## Heap dump — bloqueado por anti-dump (comandos #56–#60)
- `am dumpheap com.hunter.net /data/data/...` → "Unable to open file" (só aceita
  /data/local/tmp — o fd é aberto pelo lado shell).
- `am dumpheap com.hunter.net /data/local/tmp/heap.hprof` (com app aberto 6s antes):
  "Waiting for dump to finish..." → agente matou em 180s; arquivo final **0 byte**;
  `pidof com.hunter.net` vazio → **o app MORREU durante o dump**.
- Probe no splash (t=2s, #60): dump pendurado de novo (resultado pendente no drain).
### Veredito
LIAPP detecta a tentativa de heap dump e **mata o próprio processo** (anti-dump clássico:
arquivo criado com 0 byte + processo desaparece + am fica pendurado esperando).

## Próximas vias (ordem avaliada)
1. **am attach-agent (JVMTI/Java agent) — Android 11, app debuggable, sem root, sem repack**
   → preserva a assinatura original (LIAPP roda normal). Agente nativo (NDK) escaneia
   /proc/self/mem por magic `dex\n0xx` e escreve o dump em files/. Sem strings "frida" nos maps
   → furtivo ao anti-frida do LIAPP. Custo: NDK/toolchain no netbook (~1 GB) OU agent.jar Java
   puro (mais frágil: achar o ByteBuffer por reflexão).
2. **Descriptografia estática** de assets/.fxdvefvw.dex (14.6 MB) — chave derivada da assinatura
   (por isso re-sign quebra). Exigiria RE do libliapp*.so (Ghidra no netbook). Plano C.
3. Watcher de disco: descartado (memory-only).
## Lição de infra
Comandos que seguram stdout aberto (loop bg do watcher) penduram o adb shell → resultado só
chega no fim; usar PONTE_WAIT_S alto + drain. `am dumpheap` pendurado também consumiu timeout
de 180s do agente (mortoPorTimeout).
