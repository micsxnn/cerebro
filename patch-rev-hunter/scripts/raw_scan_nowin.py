"""Scan BRUTO de bytes: procura invokes (0x6e-0x72, 0x74-0x78) cujo method_idx
seja 5177 ou 5178 (Nowin->Nextprot / Nowin->init) em classes13 inteiro."""
import struct

DEX = '/home/z/my-project/rea-work/orig_c13.dex'
data = open(DEX, 'rb').read()
targets = {5177: 'Nextprot', 5178: 'init'}
n = len(data)
hits = []
for p in range(4, n - 6):
    op = data[p]
    if (0x6e <= op <= 0x72) or (0x74 <= op <= 0x78):
        mid = data[p + 2] | (data[p + 3] << 8)
        if mid in targets:
            hits.append((p, op, mid))
print('hits brutos:', len(hits))
for p, op, mid in hits:
    print('  offset=0x%08x  op=0x%02x  mid=%d (%s)  bytes: %s' % (
        p, op, mid, targets[mid], data[p - 6: p + 8].hex()))
