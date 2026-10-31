# Log v8 (2026-10-31 16:17–16:18 local) — análise do crash + falha do pull do payload

Fonte: `aShellYou__20261031161811.txt` (cópia bruta em `logs/aShellYou__20261031161811.txt`).
Contexto: v8 = v7 + `android:debuggable="true"` — instalada para liberar `run-as` e capturar o
payload real do LIAPP (`ز֯٬ڲܮ.jar`) que ele monta em `files/` em runtime.

## 1. O que funcionou ✅

- **`run-as` liberado**: `run-as com.hunter.net id` → `uid=10544(u0_a544)`, grupos incluem
  `sdcard_rw(1015)` e `sdcard_r(1028)`. O `debuggable=true` da v8 fez efeito.
- **Payload localizado**: `run-as com.hunter.net find files -name "*.jar"` →
  `files/.59bca860/ز֯٬ڲܮ.jar`. O LIAPP monta o jar MESMO no APK tampered — o arquivo está lá.

## 2. Por que o arquivo veio 0 B ❌

Comando tentado (~10x):
```
run-as com.hunter.net sh -c 'cat $(find files -name "*.jar" | head -1)' > /sdcard/Download/liapp_payload.jar
```
Resultado: `Error: Stream closed.` e arquivo de 0 bytes.

Causa: `sh -c` aninhado dentro do `run-as` + **saída binária de 14,6 MB fluindo pelo stream do
terminal** (Shizuku/aShellYou) + nome MUTF-8 (ز֯٬ڲܮ) passado por `$(...)`. O aShellYou fecha o
stream antes de gravar qualquer byte. Não é problema do arquivo nem do run-as.

### Comando CORRIGIDO (cp direto, sem sh -c, sem cat, sem digitar o nome árabe)

Opção A — Download direto:
```
run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Download/liapp_payload.jar \;
```
Opção B — se der "Permission denied", usar a pasta externa do próprio app:
```
run-as com.hunter.net mkdir -p /sdcard/Android/data/com.hunter.net/files
run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Android/data/com.hunter.net/files/liapp_payload.jar \;
cp /sdcard/Android/data/com.hunter.net/files/liapp_payload.jar /sdcard/Download/liapp_payload.jar
```
Verificação:
```
run-as com.hunter.net find files -name "*.jar" -exec ls -la {} \;
ls -la /sdcard/Download/liapp_payload.jar
```
Tamanho esperado: **~14–15 MB**. Depois: anexar o arquivo no chat (splits de 13 MB já passaram por
aí) ou subir manualmente em `patch-rev-hunter/payload/` pela web do GitHub.

## 3. O crash do app no mesmo log (16:17:55–56, pid 21250)

- **Exceções TRATADAS** (W System.err, o app continuou): `ClassNotFoundException
  com.hunter.net.RevHunterApp` várias vezes, vindas de
  `com.liapp.x.getApplicationContext(ױٯز٬ۨ.java:1448)` e `com.liapp.x.onCreate(:410)`.
- **FATAL** (E AndroidRuntime): `RuntimeException: Unable to instantiate activity
  ComponentInfo{com.hunter.net/com.hunter.net.LauncherActivity}: ClassNotFoundException:
  Didn't find class "com.hunter.net.LauncherActivity"` com
  `Suppressed: NoClassDefFoundError: Failed resolution of: Lcom/hunter/net/activities/BaseActivity;`
- Classloader do lookup: `DexPathList[[base.apk, files/.59bca860/df2dda51/ز֯٬ڲܮ.jar]]`
  (subpasta `df2dda51` = variação por execução; o `find` viu o jar direto em `.59bca860/`).
- Morte do processo: `Force finishing activity com.hunter.net/.LauncherActivity` +
  `Process com.hunter.net (pid 21250) has died: fg TOP`.

## 4. Interpretação (fecha o diagnóstico)

- A `LauncherActivity` real **não existe** em nenhum dos 13 dexes visíveis do APK (só o canário
  ofuscado MUTF-8) — ela só existe no payload de 14,6 MB cifrado em `assets/.fxdvefvw.dex`.
- Em APK re-assinado, o jar montado pelo LIAPP **não entrega as classes reais** (o payload
  decifrado vira lixo/decoy quando a assinatura difere da original) → o classloader
  `[base.apk, jar]` não acha `LauncherActivity` nem resolve `BaseActivity` no lookup final → morte.
- Com a assinatura ORIGINAL o payload decifra certo (app original funciona) → **o anti-tamper do
  LIAPP é a decifragem do payload atada à assinatura**, não um `exit()` explícito.
- v7 já provou que o bytecode visível do `classes13` RODA (os nops no `Nowin.tamperProtect`
  mudaram o comportamento em runtime).
- `RevHunterApp.onCreate` completou na v7 → a cadeia Application funciona; o que falta é o
  **dex real** que só o payload tem.

## 5. Próximos passos

1. Rodar o comando corrigido no celular → `liapp_payload.jar` (~14,6 MB) → anexar aqui / subir no
   repo (`patch-rev-hunter/payload/`).
2. Sandbox: `unzip` do jar → parse do dex real (parsers próprios) → confirmar `LauncherActivity`,
   `Nowin`, `BaseActivity` e localizar a lógica de trial (999 dias) no dex REAL.
3. v9 = APK com o dex real (LIAPP removido: manifest `application` → `com.hunter.net.RevHunterApp`,
   libs próprias do app mantidas) OU patch direto no payload — decisão com o dex em mãos.
4. Ao final do projeto: restaurar `settings put global verifier_verify_adb_installs 1` e
   `package_verifier_enable 1`.
