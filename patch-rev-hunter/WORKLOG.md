# WORKLOG — RevHunter v48 (com.hunter.net) — 999 dias

## Última atualização: 2026-10-31 ~21:45 UTC

## Estado atual
- CÉRBERO CRIADO/ATIVO: repo renomeado micsxnn/cerebro -> **micsxnn/cerbero** (GitHub não aceita acento)
  pasta patch-rev-hunter/ (WORKLOG.md, diagnostico.md, progresso.md, logs/); REGRA: TODA falha/sucesso -> commit lá
- v8 TESTADA (16:17 local): `run-as com.hunter.net id` FUNCIONA (uid 10544) = debuggable OK ✅;
  crash = MESMO padrão v7: CNFE RevHunterApp (tratadas, de com.liapp.x.getApplicationContext:1448/onCreate:410)
  + FATAL: Unable to instantiate activity LauncherActivity (CNFE) + Suppressed NCDFE BaseActivity
  → processo morre ("has died: fg TOP" + "Force finishing activity")
- PULL DO PAYLOAD FALHOU ~10x: `run-as ... sh -c 'cat $(find ...)' > arquivo` → "Error: Stream closed." → 0 B
  causa: sh -c aninhado + 14,6 MB BINÁRIOS pelo stream do terminal (aShellYou/Shizuku) + nome MUTF-8 via $()
- COMANDO CORRIGIDO (cp direto via find -exec; sem sh -c, sem cat, sem digitar nome árabe):
  `run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Download/liapp_payload.jar \;`
  fallback + análise completa: patch-rev-hunter/logs/2026-10-31_log_v8_CNFE_pull0b.md
- DIAGNÓSTICO: classloader da falha = PathClassLoader[base.apk, files/.59bca860/df2dda51/ز֯٬ڲܮ.jar]
  → LauncherActivity real não está nem nos 13 dexes visíveis (só canário MUTF-8) nem no jar montado
  → com assinatura diferente da original, o payload NÃO entrega classes reais (decifra corrompida/decoy)
- v7 TESTADA (15:47 local x2): AVANÇOU — nops no Nowin FUNCIONARAM (zero tamperProtect),
  RevHunterApp.onCreate completou, splash 3-5s (sem bolinha/"Não tenha limites") e crashou:
  ClassNotFoundException com.hunter.net.LauncherActivity + Suppressed NCDFE BaseActivity
- v8 BUILD: v7 + android:debuggable="true" (76.457.432 B) no release v1-999dias —
  objetivo era liberar run-as p/ capturar o payload (run-as OK; falta rodar o cp corrigido)

## Resultados dos testes no celular
| versão | conteúdo | resultado |
|---|---|---|
| v2 | classes13 patchado + dexes LIAPP mexidos, sem libs | crash UnsatisfiedLinkError (attachBaseContext) |
| v3 | classes13 patchado, dexes originais, sem libs | trava em loop silencioso (LIAPP captura o erro) |
| TESTE_A (testA) | tudo original só re-assinado, sem libs | trava igual v3 |
| v4 | merge python defeituoso: arsc NÃO mesclado, ~187 res faltando, libs comprimidas | NÃO instalou (provável extractNativeLibs=false + .so comprimidas → INSTALL_FAILED_INVALID_APK) |
| v5 | APKEditor merge(v3 + 3 splits), classes13 PATCHADO (crc 8d7aab13), extractNativeLibs=true | instalou ✅, crasha logo após abrir ❌ |
| v6 | idêntica à v5 mas classes13 ORIGINAL (testA) | aguardando teste |

## Diagnóstico em aberto (v5 crash)
O código do patch 999 dias NUNCA rodou de verdade (v2/v3 morriam antes). Crash da v5 pode ser:
1. Bug no patch classes13 (exception no startup) — classes13 patchado é 61KB MENOR que o original (rebuild smali)
2. Anti-tamper do LIAPP (assinatura debug ≠ Play, ou CRC de dex)
→ v6 (dexes 100% originais) decide: se v6 carregar = patch é o culpado; se v6 crashar = anti-tamper LIAPP

## Resultado v7 (2026-10-31 ~19:47 UTC)
- v7 AVANÇOU: nops no Nowin funcionaram — ZERO crash de tamperProtect; RevHunterApp.onCreate completou pela 1ª vez
- Ficou 3-5s na splash (arte do tema SEM bolinha/"Não tenha limites" = activity real nunca inflou) e fechou
- Crash novo (15:47 x2): ClassNotFoundException com.hunter.net.LauncherActivity
  + Suppressed NoClassDefFoundError com.hunter.net.activities.BaseActivity
- Padrão do stack = LauncherActivity FOI ACHADA (só pode ser no jar ز֯٬ڲܮ.jar do payload!) e falhou ao LINKAR a superclasse BaseActivity
- MEAÇÃO LOCAL (diag_v7.py): LauncherActivity real NÃO está em NENHUM dos 13 dexes (só 1 canário ofuscado por dex: Lcom/hunter/net/LauncherActivity/<MUTF-8>;) — nem no original!
- BaseActivity e RevHunterApp estão DEFINIDAS no classes13; RevHunterApp rodou MAS BaseActivity não achada → classes13 não efetivo no classloader (ou classloader do LIAPP só tem o jar)

## Payload do LIAPP (DESCOBERTA GRANDE, 2026-10-31 ~20:05 UTC)
- assets/.fxdvefvw.dex (803.322 B) = stub dex 428 B + 802.894 B CIFRADOS de um dex que declara file_size 14.640.584 B / 8.628 classes
- Header (primeiros 112 B) do payload = byte-idêntico ao classes.dex do APK (14.640.584 B); a partir de 0x70 diverge (98,69%, entropia 7.9/8 = cifra forte, NÃO é XOR simples)
- classes.dex do APK: 8.628 classes (androidx, ads SDKs); cada dex visível é camada com nomes MUTF-8 ofuscados
- O jar final (ز֯٬ڲܮ.jar, 14,6 MB) é MONTADO EM RUNTIME (libfxdvefvw.so dlopen libliapp.so) e injetado no classloader [base.apk, jar]
- LIAPP.ini: v5.1.1.183, LIAgent=0, Job-Id#=134132
- CONCLUSÃO: nomes REAIS das classes (LauncherActivity, Nowin...) só existem no payload decriptado
- Maneta: run-as exige debuggable → v8 = v7 + debuggable=true (LIAPP nem bloqueou assinatura debug, risco baixo)

## Próximos passos (v8 em execução)
1. Usuário: instalar v8 (debuggable) → abrir (vai crashar igual, tudo bem) → pegar payload:
   - `run-as com.hunter.net id` (testa)
   - `run-as com.hunter.net ls -la files/.59bca860/df2dda51/`
   - `run-as com.hunter.net sh -c 'cat files/.59bca860/df2dda51/*' > /sdcard/Download/liapp_payload.jar`
2. Usuário: logcat ART (pode revelar rejeição de dex/classes13): `logcat -c` → abrir app → fechar → `logcat -d | grep -aiE "reject|failed|not found|verif|classes13|hunter|liapp" | tail -60`
3. Sandbox: parsear liapp_payload.jar → class_defs (BaseActivity? RevHunterApp? Nowin? callsites?)
4. v9 = patch no payload (999 dias + checks) OU injeção de BaseActivity stub
5. Ao final: restaurar `settings put global verifier_verify_adb_installs 1` e `package_verifier_enable 1`

## Ferramentas
- apktool.jar 2.9.3 (baksmali embutido — classe Main AINDA A DEFINIR, `com.android.tools.smali.baksmali.Main` deu erro JavaFX)
- APKEditor.jar (merge universal — FUNCIONOU: v5/v6)
- uber.jar 1.3.0 (assinatura debug v1+v2+v3 + zipalign)
- token GitHub em rea-work/.gt ; release id 429680551; repo micsxnn/analise-revhunter-tempo-restante

## Observações técnicas
- v5/v6 manifest: extractNativeLibs="true" (APKEditor) → libs .so comprimidas OK
- v4 não instalou: merge python defeituoso — arsc do base NÃO mesclou (2.097.216 vs 2.173.532 do correto), ~187 res faltando; libs comprimidas sem ajuste de manifesto
- libfxdvefvw.so (LIAPP) empacotada: só revela "libliapp.so" (dlopen runtime)
- hidden.dex (assets/.fxdvefvw.dex) AINDA criptografado: parse dá 1 classe stub Lcom/liapp/...; 5 strings — precisa do decript XOR profundo p/ ver checks reais
- classes13 original trava baksmali do apktool 2.9.3: "bad utf-8 byte ec" (nomes ofuscados LIAPP, MUTF-8 não-estrito) — APK roda no ART mesmo assim; patch da v3 foi feito via rebuild leniente (classes13 patchado é 61KB menor, mesmo código+strings, checksum OK)
- baksmali standalone: release do smali no GitHub 404 com e sem prefixo v; jar embutido no apktool = jcommander Command sem CLI → usar mini-APK + apktool d (funciona p/ dexes que não têm nomes exóticos)
- androguard 3.3.5 instalado mas dvm sem DEX export? (instalação estranha) — parser próprio em scripts/dex_grep.py, dex_deep.py, c13_hidden_scan.py, c13_code_diff.py FUNCIONA
- Splits do celular em /sdcard/Download; cópias em upload/ (split_arm64 13.1MB, split_pt 82KB, split_xhdpi 247KB)
- merge_in/base.apk = v3.apk (base da v5); testA.apk = base original só re-assinado (dexes 100% originais)
- classes13: original 1.125.092 B crc 2b2bd529 | patchado 1.064.120 B crc 8d7aab13 (mesmo conjunto de classes/métodos/strings)
- Token GitHub em rea-work/.gt (usar Authorization: token)

## Resultado v6 (2026-10-31 ~19:50 UTC)
- v6 crashou IGUAL a v5 (buffer de crash: `logcat -d -b crash` — 5 crashes registrados)
- Stack: `Nowin.tamperProtect(SourceFile:139)` <- `Nowin.Nextprot(109)` <- `RevHunterApp.onCreate(259)` <- `com.liapp.x.onCreate`
- CONCLUSAO: LIAPP aceitou o APK re-assinado (passou attachBaseContext e onCreate); patch 999 inocente (v6 sem patch crasha igual)
- Culpado real: anti-tamper do PROPRIO APP, classe `com.kiritoprojects.ultrasshservice.util.Nowin`
- Nowin NAO esta em nenhum dos 13 dexes (definido no payload escondido do LIAPP, descriptografado em runtime)
- classes13 tem method_ids: Nowin->Nextprot (mid 5177) e Nowin->init (mid 5178)

## v7 (2026-10-31 ~19:45 UTC) — PUBLICADA
- Scan BRUTO de bytes achou 2 invokes: `invoke-static Nowin->init` @ 0xfd488 e `invoke-static Nowin->Nextprot` @ 0xfd48e (adjacentes, seguidos de `const/4 v1, 1`)
- Patch: 12 bytes -> nops (00) nos 2 invokes + recalc adler32(0x08) e SHA-1(0x0C)
- Diff vs classes13 original: apenas 32 bytes (checksums + nops) — confirmado
- v7 = v6 com classes13 patchado (nops nowin), assinada, publicada como RevHunter_v48_999dias_v7_sem_nowin.apk
- URL: https://github.com/micsxnn/analise-revhunter-tempo-restante/releases/download/v1-999dias/RevHunter_v48_999dias_v7_sem_nowin.apk
- AGUARDANDO TESTE: se carregar -> v8 = v7 + patch 999 re-aplicado; se crashar noutro lugar -> logcat e proximo nop

## Log v8 (2026-10-31 16:17–16:18 local) — análise completa
Fonte: aShellYou__20261031161811.txt (anexo do usuário; cópia em patch-rev-hunter/logs/)
1. run-as OK: `run-as com.hunter.net id` → uid=10544(u0_a544), grupos com sdcard_rw(1015)/sdcard_r(1028) — debuggable=true FUNCIONOU
2. Payload montado: `find files -name "*.jar"` → `files/.59bca860/ز֯٬ڲܮ.jar` (o LIAPP monta o jar MESMO no APK tampered)
3. Pull falhou: `run-as com.hunter.net sh -c 'cat $(find files -name "*.jar" | head -1)' > /sdcard/Download/liapp_payload.jar` → "Error: Stream closed." (2x no log; ~10x segundo o usuário) → 0 B
   → causa: sh -c aninhado + saída binária de 14,6 MB pelo stream do terminal Shizuku + nome MUTF-8 por $(...) — o aShellYou fecha o stream antes de gravar
4. Crash (16:17:55–56, pid 21250):
   - W System.err TRATADAS: CNFE com.hunter.net.RevHunterApp — de com.liapp.x.getApplicationContext(ױٯز٬ۨ.java:1448) e com.liapp.x.onCreate(:410), várias vezes
   - FATAL: RuntimeException Unable to instantiate activity ComponentInfo{com.hunter.net/com.hunter.net.LauncherActivity}: CNFE LauncherActivity; Suppressed: NoClassDefFoundError Failed resolution of Lcom/hunter/net/activities/BaseActivity;
   - DexPathList do lookup: [base.apk, files/.59bca860/df2dda51/ز֯٬ڲܮ.jar] (subpasta df2dda51 = por-execução; find viu direto em .59bca860)
   - Morte: "Force finishing activity com.hunter.net/.LauncherActivity" + "Process com.hunter.net (pid 21250) has died: fg TOP"
5. Interpretação: fecha o diagnóstico — em APK re-assinado, o jar montado a partir do payload cifrado NÃO entrega as classes reais (LauncherActivity etc. só existem no payload de 14,6 MB); com assinatura original ele entrega (app original funciona). RevHunterApp/BaseActivity existem no classes13 visível, mas o lookup final também falha → LIAPP controla o classloader pós-attach (v7 provou que o bytecode do classes13 visível RODA: os nops no Nowin mudaram o comportamento)
6. AVANÇO CHAVE: agora o payload está ALCANÇÁVEL via run-as (v8 debuggable) — falta só o cp corrigido:
   `run-as com.hunter.net find files -name "*.jar" -exec cp {} /sdcard/Download/liapp_payload.jar \;`
   (fallback: /sdcard/Android/data/com.hunter.net/files/ — ver docs do cerbero)
