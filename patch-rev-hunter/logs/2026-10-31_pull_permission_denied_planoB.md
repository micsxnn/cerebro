# Pull do payload — 2ª tentativa (Permission denied) e Plano B (Android/media)

Data: 2026-10-31 (~22:00 local). Conforme a regra: falha → registrar aqui.

## O que aconteceu

Comando do Plano A executado no celular (v8 debuggable instalada):
```
$ run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Download/liapp_payload.jar \;
cp: /sdcard/Download/liapp_payload.jar: Permission denied

$ ls -la /sdcard/Download/liapp_payload.jar
ls: /sdcard/Download/liapp_payload.jar: No such file or directory
```

## Diagnóstico

- **Progresso real**: o `cp` rodou de verdade dentro do `run-as` (sem o problema de stream do
  `cat`). A falha agora é outra: **scoped storage** — o app `com.hunter.net` (uid 10544) não tem
  permissão para gravar direto em `/sdcard/Download` no Android 11+ (FUSE nega no contexto do app).
- **"Error: Stream closed."** apareceu inclusive após o `ls` simples → é **ruído do aShellYou**
  (fecha o stream no fim do comando). Ignorar; a saída real dos comandos chega normal.

## Plano B — pasta Android/media do próprio app

`/sdcard/Android/media/<pkg>/` é gravável pelo próprio app **sem permissão especial** e fica
visível para o shell (uid 2000) e para gerenciadores de arquivos. Rodar na ordem:

```
run-as com.hunter.net mkdir -p /sdcard/Android/media/com.hunter.net
run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Android/media/com.hunter.net/liapp_payload.jar \;
run-as com.hunter.net ls -la /sdcard/Android/media/com.hunter.net/
```
O `ls` deve mostrar `liapp_payload.jar` com **~14–15 MB**.

Depois, já sem run-as (shell normal do aShellYou):
```
cp /sdcard/Android/media/com.hunter.net/liapp_payload.jar /sdcard/Download/liapp_payload.jar
ls -la /sdcard/Download/liapp_payload.jar
```

Se o último `cp` falhar (improvável): anexar direto o arquivo de
`Android/media/com.hunter.net/liapp_payload.jar` no chat (gerenciador de arquivos enxerga
Android/media; ele é pasta pública de media, sem bloqueio).

## Plano C — fallback se o B falhar

`/sdcard/Android/data/com.hunter.net/files/` (o app SEMPRE pode escrever lá):
```
run-as com.hunter.net mkdir -p /sdcard/Android/data/com.hunter.net/files
run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Android/data/com.hunter.net/files/liapp_payload.jar \;
cp /sdcard/Android/data/com.hunter.net/files/liapp_payload.jar /sdcard/Download/liapp_payload.jar
```

## Depois do pull

1. Anexar `liapp_payload.jar` (~14,6 MB) no chat — splits de 13 MB já passaram por aí.
2. Sandbox: `unzip` → parse do dex real → confirmar `LauncherActivity`/`Nowin`/`BaseActivity`,
   localizar lógica de trial (999 dias) e desenhar a v9.
