# 2026-10-31 (noite 2) — RE estática: avanços no libfxdvefvw.so

## Estrutura do payload (assets/.fxdvefvw.dex, 803.322 B) — CASCATA
- **Dex-casca externo** ("dex\n035", 428 B): header válido mas file_size=428; o corpo real
  está na seção LINK (link_off=0x1ac, link_size=0xc404e).
- **Dex-casca interno** @428: "dex\n037" com header em claro e **file_size = 14.640.584
  (0xdf65c8) = os 14.6MB misteriosos!** map_off coerente (0xdf64ec). Campos de índices
  plausíveis (65.791 strings, 63.869 métodos) → é um dex real grande.
- Corpo: ~802.894 B com entropia 7.95-7.98 uniforme = **CIFRADO de verdade** (zlib testado e
  descartado; magics de compressão = coincidência). Header em claro + corpo cifrado.
- Marcadores ASCII no campo SHA-1: casca "3abf2ed602be307b4ca3", interno "3c28cc019af06f7a2e7b".
- Cert original extraído (863 B DER): SHA1 5d08264b44e0e53fbccc70b4f016474cc6c5ab5c.

## libfxdvefvw.so (657.452 B, arm64) — características
- **Section headers FALSOS** (readelf: "no .dynamic section in the dynamic segment") — armadilha
  p/ ferramentas; PT_LOADs são íntegros e offset==vaddr.
- Entropia 6.0-6.6 = código real (não cifrado), mas **OLLVM control-flow flattening** pesado.
- Tabelas em claro: **AES S-box @0x8fb40, AES inverse S-box @0x8fc50, SHA-256 K @0x8e630,
  CRC32 @0x8e430** → cifra = AES (com direção inversa presente → dá pra re-cifrar pro v9!),
  KDF provavelmente SHA-256.
- `.text` real = 180 B; o código mora num segmento de 472 KB; `.lisec.dynamic` = marcador LIAPP.
- INIT_ARRAY: 2 construtores reais via relocações RELATIVE (0xc920, 0xd538); strings ofuscadas
  por XOR por-byte decodificadas em stack ("Android", "/system"...).

## Infra de RE montada no sandbox
- Ghidra 11.2.1 headless + JDK 21 (Temurin) instalados (gproj2/LIAPP_RAW).
- **Técnica-chave: import como RAW BINARY** (BinaryLoader, base 0, processor AARCH64:LE:64:v8A,
  cspec **default**) — o import ELF do Ghidra confia nos section headers falsos e PERDE os bytes
  (findBytes não achava as tabelas; raw achou tudo).
- 586 funções identificadas na import raw (vs 241 na import ELF quebrada).

## Funções identificadas até agora
- FUN_00043d18 = **transform de blocos SHA-256** (schedule σ0/σ1, estado @+0x88 do ctx).
- FUN_0007d5c0 = função gigante achatada, chamada com (caminho, 4) — **patcher de .so**
  (proteção de libs nativas do LIAPP), NÃO é o decrypt do payload.
- FUN_00128f48 (import ELF; equiv. ~0x28f48 raw) = anti-tamper CRC32 do próprio código.
- Desofuscação de strings: XOR simples por-byte, decodificadas no stack.

## Próximos passos
1. Dump completo das 586 funções do projeto RAW → procurar RegisterNatives (vtable JNI +0x6b8)
   e o fluxo do método nativo (nome árabe MUTF-8) até o decrypt do dex interno.
2. Rastrear origem da chave AES (SHA-256 de quê? assinatura? package? fixa?).
3. Se KDF for da assinatura: reproduzir em Python com o cert original e decifrar o corpo;
   validar magic no início do plaintext.
4. Com o dex real: achar trial → 999 dias; re-cifrar (AES inverso) com chave da NOVA
   assinatura; montar v9.

## Nota de processo
- Custos de disco: NDK removido após uso; intermediários antigos (v2-v7, ~1.3 GB) limpos.
- Ghidra exige JDK 21 na 11.2.x (17 não serve); cspec de AARCH64 = "default" (não "gcc").
