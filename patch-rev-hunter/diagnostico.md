# Diagnóstico atual — RevHunter 999 dias

**Atualizado:** 2026-10-31 ~19:45 UTC — status: **v7 publicada (nops no Nowin), aguardando teste**

> Regra: cada resultado (crash novo ou sucesso) gera commit aqui.

## O crash (v5 e v6, idêntico)

Buffer de crash (`logcat -d -b crash`) revelou 5 crashes:

| hora | versão | exceção |
|---|---|---|
| 12:01 | v2 (sem libs) | `UnsatisfiedLinkError` em `com.liapp.x.ز֯٬ڲܮ` — LIAPP sem lib nativa |
| 15:06 | v5 (libs + patch 999) | `RuntimeException` em `Nowin.tamperProtect` |
| 15:27 | v6 (libs, SEM patch) | `RuntimeException` em `Nowin.tamperProtect` |
| 15:28 (x2) | v6 | idem |

Stack completo do crash atual:
```
java.lang.RuntimeException: Unable to create application com.liapp.x
Caused by: java.lang.RuntimeException
  at com.kiritoprojects.ultrasshservice.util.Nowin.tamperProtect(SourceFile:139)
  at com.kiritoprojects.ultrasshservice.util.Nowin.Nextprot(SourceFile:109)
  at com.hunter.net.RevHunterApp.onCreate(SourceFile:259)
  at com.liapp.x.onCreate(ױٯز٬ۨ.java:419)
```

## Conclusões firmes

1. **NÃO é o LIAPP que mata** — o `attachBaseContext` do LIAPP passou (não há mais UnsatisfiedLinkError com as libs) e o `onCreate` dele chegou até chamar o app real. LIAPP v5.1.1.183 aceitou o APK re-assinado (pelo menos até esse ponto).
2. **NÃO é o patch dos 999 dias** — v6 tem dexes 100% originais e crasha IGUAL.
3. **O culpado é um anti-tamper do PRÓPRIO APP**: `com.kiritoprojects.ultrasshservice.util.Nowin.tamperProtect` — detecta que a assinatura não é a da Play (ou integridade do APK) e lança `RuntimeException`.

## Arquitetura descoberta (importante!)

- `com.hunter.net.RevHunterApp` e ~40 classes do app estão **estáticas no classes13.dex**
- **`Nowin` NÃO está em nenhum dos 13 dexes** — é definido no **dex escondido** que o LIAPP descriptografa em runtime e carrega no classloader dele
- `LauncherActivity/<nome ofuscado>` aparece definido 1x em CADA um dos 13 dexes (estrutura do LIAPP)
- Por isso: não dá para patchear o `Nowin` direto (está criptografado dentro do payload do LIAPP)

## Plano v7 (em execução)

1. classes13.dex tem method_ids para `Nowin->Nextprot` (mid 5177) e `Nowin->init` (mid 5178)
2. Achar os bytecodes `invoke-*` que apontam para esses mids via **scan bruto de bytes** (o walker linear se perde no dex de 1MB)
3. Substituir os 3 units de cada invoke por **nops** → Nowin nunca é chamado no startup
4. Recalcular checksum adler32 (0x08) e SHA-1 (0x0C) do dex
5. Reconstruir APK (v6 + classes13 patchado), assinar com uber, publicar como v7

## Status v7
- 2 invokes neutralizados com nops: `Nowin->init` @ 0xfd488 e `Nowin->Nextprot` @ 0xfd48e (classes13)
- APK publicado: `RevHunter_v48_999dias_v7_sem_nowin.apk` (76.457.432 B)
- Se carregar: v8 = v7 + patch 999 (re-aplicar patch no dex rebuild + nops)
- Se crashar: novo logcat -> novo alvo -> novo nop

## Plano B (se v7 continuar crashando em Nowin)

- Criar uma classe stub `Nowin` ESTÁTICA no classes13 (sombra parent-first) com métodos vazios
- Ou decriptar o payload escondido do LIAPP e patchear o Nowin dentro dele (esquema XOR já dominado: key inicial 0x6f, `key = (key ^ i) & 0x3F`)

## Riscos conhecidos

- Pode haver OUTRO check depois do `Nowin` (a classe se chama "Nextprot" — sugere cadeia de proteções). Cada um será descoberto pelo crash buffer e neutralizado na sequência.
- O LIAPP pode ter checks de runtime mais adiante (após o login) que ainda não dispararam.
