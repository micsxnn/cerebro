# Diagnóstico atual — RevHunter 999 dias

**Atualizado:** 2026-10-31 ~20:15 UTC — status: **v8 publicada (debuggable) para capturar o payload real do LIAPP**

> Regra: cada resultado (crash novo ou sucesso) gera commit aqui.

## Linha do tempo de crashes

| hora (local) | versão | exceção |
|---|---|---|
| 12:01 | v2 (sem libs) | `UnsatisfiedLinkError` no attachBaseContext do LIAPP |
| 15:06 / 15:27 / 15:28 (x3) | v5 / v6 | `RuntimeException` em `Nowin.tamperProtect` |
| **15:47 (x2)** | **v7 (nops no Nowin)** | **`ClassNotFoundException: com.hunter.net.LauncherActivity`** |

## Resultado v7 — AVANÇO IMPORTANTE

Comportamento no celular: fica 3-5s na splash (só a arte do tema: escudo + astronauta, SEM a
bolinha rosa e o texto "Não tenha limites" — que é conteúdo da activity real que nunca inflou) e fecha.

1. **NOPS FUNCIONARAM**: ZERO crash de `Nowin.tamperProtect`. `RevHunterApp.onCreate` completou pela 1ª vez. O anti-tamper do próprio app está neutralizado.
2. O app avançou até instanciar a `LauncherActivity` — mais longe que nunca.

### Anatomia do crash v7
```
ClassNotFoundException: Didn't find class "com.hunter.net.LauncherActivity"
  on path: DexPathList[[zip base.apk, zip files/.59bca860/df2dda51/ز֯٬ڲܮ.jar]]
Suppressed: NoClassDefFoundError: Lcom/hunter/net/activities/BaseActivity;
Caused by: ClassNotFoundException: com.hunter.net.activities.BaseActivity
```
O padrão (CNFE da classe + Suppressed NCDFE da superclasse) significa: **a LauncherActivity FOI
ENCONTRADA (só pode estar no jar do payload!) e falhou ao LINKAR porque a BaseActivity não estava
disponível no classloader.**

### Fatos medidos no sandbox (scripts/diag_v7.py)
- `Lcom/hunter/net/LauncherActivity;` NÃO está definida em NENHUM dos 13 dexes — nem no ORIGINAL!
  Em cada dex existe 1 canário: `Lcom/hunter/net/LauncherActivity/<nome MUTF-8 ofuscado>;`
  → **a LauncherActivity real só existe no payload que o LIAPP decripta em runtime** (jar ز֯٬ڲܮ.jar).
- `Lcom/hunter/net/activities/BaseActivity;` e `Lcom/hunter/net/RevHunterApp;` estão DEFINIDAS no classes13.
- Contradição central: RevHunterApp (classes13) RODOU (nops!) MAS BaseActivity (MESMO dex) deu CNFE
  → o classes13 não está efetivo no classpath da v7, ou o classloader do LIAPP só expõe o jar
  (base.apk como elemento "fantasma" no DexPathList).

## Estrutura do payload do LIAPP (DESCOBERTA GRANDE)

- `assets/.fxdvefvw.dex` (803.322 B) = **stub dex de 428 B + 802.894 B CIFRADOS** de um dex que
  declara `file_size = 14.640.584 B` com **8.628 classes**
- O header (primeiros 112 B) desse payload é **byte-idêntico ao `classes.dex` do APK** (14.640.584 B);
  a partir de 0x70 diverge: 98,69% dos bytes, entropia 7.9/8 → **cifra forte, NÃO é XOR simples**
- `classes.dex` do APK: 8.628 classes (androidx, SDKs de anúncio...); os 13 dexes visíveis são
  camadas com nomes MUTF-8 ofuscados — **os NOMES REAIS estão só na string pool do payload**
- O jar final (ز֯٬ڲܮ.jar, 14,6 MB) é **montado em runtime** (libfxdvefvw.so → dlopen libliapp.so)
  e injetado no classloader da app
- `LIAPP.ini`: v5.1.1.183, LIAgent=0, Job-Id#=134132
- O LIAPP **não bloqueou**: APK re-assinado (v5/v6/v7), dexes alterados (v7: classes13 com 32 bytes
  de nops), e nem checa assinatura — quem checa é o `Nowin` do próprio app (já noped)

## v8 — capturar o payload real (em execução)

A v7 não é debuggable → `run-as` falha. **v8 = v7 + `android:debuggable="true"`** (AXML rebuildado
com APKEditor d/b, round-trip verificado, mesmo resto). Publicada como
`RevHunter_v48_999dias_v8_debuggable.apk`. O LIAPP nem bloqueou assinatura debug, risco baixo.

No celular (aShellYou + Shizuku):
```
run-as com.hunter.net id
run-as com.hunter.net ls -la files/.59bca860/df2dda51/
run-as com.hunter.net sh -c 'cat files/.59bca860/df2dda51/*' > /sdcard/Download/liapp_payload.jar
```

E o logcat principal (pode revelar rejeição de dex pelo ART):
```
logcat -c   → abrir o app → deixar fechar →
logcat -d | grep -aiE "reject|failed|not found|verif|classes13|hunter|liapp" | tail -60
```

### Com o payload em mãos (v9)
1. Parsear class_defs: o payload define BaseActivity? RevHunterApp? Nowin? quem chama o Nowin?
2. Entender por que os dexes visíveis ficam inefetivos (e se dá pra reverter)
3. Aplicar patch 999 dias + neutralizar checks DIRETO no payload (nomes reais!)
4. Re-criptografar? NÃO dá (cifra forte) — mas o jar é montado em runtime a partir do asset...
   → alternativa: injetar `BaseActivity` stub ou fazer o payload "enxergar" os dexes visíveis
