import struct

def read_uleb(buf, off):
    r = 0; s = 0
    while True:
        b = buf[off]; off += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, off

def method_code_map(data):
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    u16 = lambda o: struct.unpack_from('<H', data, o)[0]
    sis, sio = u32(0x38), u32(0x3C)
    strings = []
    for i in range(sis):
        off = u32(sio + i * 4)
        n, off = read_uleb(data, off)
        end = data.index(b'\x00', off)
        strings.append(data[off:end].decode('utf-8', 'replace'))
    tis, tio = u32(0x40), u32(0x44)
    types = [strings[u32(tio + i * 4)] for i in range(tis)]
    pis, pio = u32(0x48), u32(0x4C)
    protos = []
    for i in range(pis):
        base = pio + i * 12
        protos.append(u32(base + 4))  # return_type_idx
    cds, cdo = u32(0x60), u32(0x64)
    out = {}
    for i in range(cds):
        base = cdo + i * 32
        cls = types[u32(base)]
        cdo_off = u32(base + 24)
        if cdo_off == 0:
            continue
        p, o = read_uleb(data, cdo_off)
        sf, o = read_uleb(data, o)
        im, o = read_uleb(data, o)
        vm, o = read_uleb(data, o)
        idx = 0
        for _ in range(im + vm):
            mdiff, o = read_uleb(data, o)
            idx += mdiff
            acc, o = read_uleb(data, o)
            code_off, o = read_uleb(data, o)
            if code_off:
                name = strings[u32(data.index(b'\x00', 0) if False else 0)] if False else None
                out.setdefault(cls, []).append((idx, code_off))
        # resolver nomes precisa method_ids; faremos fora
    mis, mio = u32(0x58), u32(0x5C)
    mnames = {}
    for i in range(mis):
        b = mio + i * 8
        mnames[i] = (types[u16(b)], strings[u32(b + 4)])
    res = {}
    for cls, lst in out.items():
        for midx, coff in lst:
            key = (cls,) + mnames.get(midx, ('?', '?'))
            if coff + 16 > len(data):
                continue
            insns_size = u32(coff + 12)
            insns = data[coff + 16: coff + 16 + insns_size * 2]
            res[key] = (coff, insns_size, insns)
    return res

o = method_code_map(open('/home/z/my-project/rea-work/orig_c13.dex', 'rb').read())
p = method_code_map(open('/home/z/my-project/rea-work/v3_dexes/classes13.dex', 'rb').read())
print('metodos com codigo  orig=%d patch=%d' % (len(o), len(p)))
common = set(o) & set(p)
diff = [k for k in common if o[k][1:3] != p[k][1:3]]
print('metodos com bytecode diferente:', len(diff))
for k in sorted(diff):
    print()
    print('### ', ' -> '.join(k))
    co, so, io = o[k]
    cp, sp, ip = p[k]
    print('  orig : insns_size=%d (%d B)' % (so, so * 2))
    print('  patch: insns_size=%d (%d B)' % (sp, sp * 2))
    a, b = io, ip
    n = min(len(a), len(b))
    first = next((i for i in range(n) if a[i] != b[i]), n)
    print('  primeiro byte divergente em offset', first)
    print('  orig  [0:96]:', a[:96].hex())
    print('  patch [0:96]:', b[:96].hex())
    print('  orig  tail[-64:]:', a[-64:].hex())
    print('  patch tail[-64:]:', b[-64:].hex())
only_o = set(o) - set(p)
only_p = set(p) - set(o)
for k in sorted(only_o)[:10]:
    print('so orig:', ' -> '.join(k))
for k in sorted(only_p)[:10]:
    print('so patch:', ' -> '.join(k))
