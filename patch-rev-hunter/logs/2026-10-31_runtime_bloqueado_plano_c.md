# 2026-10-31 (noite) — Injeção em runtime: TODAS as vias bloqueadas neste ROM

## O que foi testado (celular moto e32 "hawaii", Android 11, SDK 30, targetSdk 37, DEBUGGABLE)
1. **JVMTI nativo via `am attach-agent`** (agente .so 6.160 B, NDK r27c, aarch64):
   - de `files/` (app_data_file): sem efeito — W^X do Android 10+ nega dlopen de app_data_file
     para targetSdk ≥ 29 (o .so tem que ser somente-leitura; files/ é rw).
   - de `/data/local/tmp` (shell_data_file): sem efeito — SELinux nega execute para untrusted_app.
2. **Agente JAVA (.jar, 3.063 B, javac 17 --release 8, Agent-Class+agentmain)** via attach-agent
   de `files/`: sem efeito (jar não sofre W^X — só precisaria de leitura; nem chegou a carregar).
3. **`wrap.com.hunter.net` + LD_PRELOAD**: `setprop` NEGADO no user build ("Failed to set
   property", SELinux).
4. **`am dumpheap`**: LIAPP anti-dump — app morre, arquivo fica 0 byte (v. doc anterior).

## Evidência-chave
- `ls /apex/com.android.art/lib64/` → `libjdwp.so` e `libopenjdkjvmti.so` EXISTEM no ROM.
- **`am attach-agent com.hunter.net /nao/existe.so` → exit=0, app continua vivo (PID igual),
  nenhum log** — no AOSP isso abortaria o processo. Conclusão: o attach-agent é **no-op
  castrado no firmware** (Unisoc/Moto). Logcat anterior: "Not starting debugger since process
  cannot load the jdwp agent" coerente com runtime de agentes desativado.
- Logcat de testes só mostra ruído de SurfaceFlinger/Chrome; nada de art/agent.

## Inventário do que temos (tudo em mãos)
- APK original (assinado) com `assets/.fxdvefvw.dex` (14.6 MB, payload cifrado) — no sandbox.
- Stub LIAPP `ز֯٬ڲܮ.jar` (285.269 B) capturado no snap do celular — puxável via run-as cat.
- Toolchains: NDK r27c (clang aarch64) e JDK 17 (Temurin) instalados no sandbox.
- Infra ponte 100% estável; transferências netbook↔sandbox↔celular funcionando (md5 ok).

## Caminhos restantes
1. **ROOT no celular** (desbloqueio Motorola + Magisk — apaga dados): libera frida-server ou
   leitura direta de /proc/<pid>/mem → dump do dex em minutos. Depende de decisão do usuário.
2. **Descriptografia estática** (plano C): RE do libliapp*.so (do stub e/ou do APK) no Ghidra
   headless do sandbox; reproduzir KDF (chave ligada à assinatura) e decifrar .fxdvefvw.dex
   offline. Sem ação do usuário, porém trabalhoso.
3. Emulador rooted: descartado por custo/risco (x86 netbook fraco, sandbox sem KVM).
