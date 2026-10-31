# Plano B falhou (app sem storage) → migração para ADB no netbook (CachyOS)

Data: 2026-10-31 (~22:15 local). Regra: falha → registrar.

## Evidência (saída do usuário)

```
$ run-as com.hunter.net mkdir -p /sdcard/Android/media/com.hunter.net
mkdir: '/sdcard/Android': Permission denied

$ run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Android/media/com.hunter.net/liapp_payload.jar \;
cp: /sdcard/Android/media/com.hunter.net/liapp_payload.jar: Permission denied

$ run-as com.hunter.net ls -la /sdcard/Android/media/com.hunter.net/
ls: /sdcard/Android/media/com.hunter.net/: Permission denied
```

## Diagnóstico

- O app `com.hunter.net` não declara nenhuma permissão de armazenamento → no Android 11+ o FUSE
  nega **todo** `/sdcard` ao contexto do app (não só Download/Android/media — nem `mkdir` em
  `/sdcard/Android` passa).
- `run-as` executa com a identidade do app → herda as mesmas negações. Shizuku/aShellYou não
  contornam: só o root (ou um PC via adb) acessa o `files/` do app e tira o payload de lá.
- Conclusão: pull do payload **só via ADB** (ou root). Celular não tem root.

## Solução escolhida: netbook do usuário com CachyOS (Arch) + adb

Pentium N3710 (4× Apollo Lake) — adb é leve, aguenta de boa.

### Passo 1 — instalar adb (Arch)
```
sudo pacman -S --needed android-tools
```

### Passo 2 — celular
- Ativar **Opções do desenvolvedor → Depuração USB**.
- Conectar no netbook por cabo USB e **aceitar a impressão digital RSA** no popup do celular.

### Passo 3 — conferir
```
adb devices
```
(deve listar `xxxxxxxx  device`)

### Passo 4 — pull do payload (à prova de bala)
`exec-out` é o canal binário cru do adb via USB — sem terminal-app, sem stream quebrado, sem
scoped storage. O `tar` evita digitar o nome MUTF-8 do jar e pega tudo de `files/`:
```
adb exec-out run-as com.hunter.net tar -cf - files > payload.tar
mkdir -p payload && tar -xf payload.tar -C payload
find payload -name "*.jar" -exec ls -la {} \;
```
Esperado: um `.jar` de **~14–15 MB** (o `ز֯٬ڲܮ.jar` do LIAPP).

Alternativa pontual (se preferir só o jar):
```
adb exec-out run-as com.hunter.net cat files/.59bca860/ز֯٬ڲܮ.jar > liapp_payload.jar
```

### Passo 5 — entrega
- Anexar o `.jar` aqui no chat (do netbook), **ou**
- subir em `patch-rev-hunter/payload/` pela web do GitHub, **ou**
- instalar a **ponte-local** no netbook: aí a IA opera o adb sozinha (pull, `adb install -r`
  das próximas versões, logcat limpo) sem o usuário digitar nada.

## Bônus do adb no PC

- `adb install -r v9.apk` — instalação direta da próxima versão.
- `adb logcat -d -b crash` — crash buffer limpo para os próximos testes.
- `adb shell am force-stop com.hunter.net` — reset limpo entre testes.
