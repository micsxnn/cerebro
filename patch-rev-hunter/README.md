# 🧠 patch-rev-hunter — Cérebro do projeto

Memória oficial do projeto **RevHunter v48 — patch 999 dias** (app `com.hunter.net`, Android).

## Regra de ouro
**TODA vez que algo der certo ou falhar, atualiza este repositório** (commit nesta pasta).

## Estrutura
| arquivo | conteúdo |
|---|---|
| `README.md` | este índice |
| `progresso.md` | linha do tempo completa: versões, testes, descobertas |
| `diagnostico.md` | diagnóstico técnico atual (onde está travando e por quê) |
| `logs/` | logcats e evidências de crash enviadas pelo celular |
| `scripts/` | ferramentas python de análise de dex/APK usadas no sandbox |

## Ferramentas em uso
- APKEditor.jar — merge universal dos splits (base + arm64 + pt + xhdpi)
- uber-apk-signer 1.3.0 — assinatura debug (v1+v2+v3) + zipalign
- apktool 2.9.3 — decode/build (limitação: trava em nomes MUTF-8 exóticos do LIAPP)
- parser próprio de dex em python (strings, class_defs, method_ids, invokes, scan bruto)
- GitHub como transporte de APKs (release `v1-999dias` no repo analise-revhunter-tempo-restante)
- aShellYou + Shizuku no celular (uid 2000) para logcat e comandos

## Links rápidos
- Release dos APKs: https://github.com/micsxnn/analise-revhunter-tempo-restante/releases/tag/v1-999dias
- v7 atual: https://github.com/micsxnn/analise-revhunter-tempo-restante/releases/download/v1-999dias/RevHunter_v48_999dias_v7_sem_nowin.apk
