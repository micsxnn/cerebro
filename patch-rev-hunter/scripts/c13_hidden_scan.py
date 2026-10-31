import struct

def read_uleb(buf, off):
    r = 0; s = 0
    while True:
        b = buf[off]; off += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, off

def dex_parse(data):
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
    mis, mio = u32(0x58), u32(0x5C)
    methods = set()
    for i in range(mis):
        base = mio + i * 8
        methods.add((types[u16(base)], strings[u32(base + 4)], strings[u32(base + 8) if False else 0]) if False else None)
    # refaz method ids corretamente: proto_idx u16 em +2
    methods = set()
    for i in range(mis):
        base = mio + i * 8
        cls = types[u16(base)]
        name = strings[u32(base + 4)]
        methods.add((cls, name))
    cds, cdo = u32(0x60), u32(0x64)
    classes = []
    for i in range(cds):
        base = cdo + i * 32
        classes.append(types[u32(base)])
    return strings, methods, classes

# ---------- PARTE A: hidden.dex ----------
print('================ hidden.dex: strings de verificação ================')
hdata = open('/home/z/my-project/rea-work/hidden.dex', 'rb').read()
hs, hm, hc = dex_parse(hdata)
print('strings:', len(hs), '| metodos:', len(hm), '| classes:', len(hc))
KW = ['signature', 'getpackageinfo', 'get_sign', 'getsign', 'messagedigest', 'sha', 'md5',
      'getpackagecodepath', 'getpackageresourcepath', 'classes', '.apk', '.dex', 'crc',
      'verify', 'checksig', 'tamper', 'zipfile', 'exit', 'signature', 'packageinfo',
      ' abdominals', 'liapp', 'hash', 'android.content.pm']
seen = set()
for s in hs:
    sl = s.lower()
    for k in KW:
        if k in sl and s not in seen:
            seen.add(s)
            print('  ', repr(s[:130]))
            break

print()
print('========== classes do hidden.dex ==========')
for c in sorted(hc)[:40]:
    print('  ', c)

# ---------- PARTE B: diff classes13 ----------
print()
print('================ DIFF classes13: original vs patch 999 ================')
o = dex_parse(open('/home/z/my-project/rea-work/orig_c13.dex', 'rb').read())
p = dex_parse(open('/home/z/my-project/rea-work/v3_dexes/classes13.dex', 'rb').read())
os_, om, oc = set(o[0]), o[1], set(o[2])
ps_, pm, pc = set(p[0]), p[1], set(p[2])
print('classes so no original (%d):' % len(oc - pc))
for c in sorted(oc - pc)[:12]:
    print('   -', c)
print('classes so no patch (%d):' % len(pc - oc))
for c in sorted(pc - oc)[:12]:
    print('   +', c)
rm = om - pm
ad = pm - om
print('metodos removidos (%d):' % len(rm))
for c, n in sorted(rm)[:15]:
    print('   -', c, '->', n)
print('metodos adicionados (%d):' % len(ad))
for c, n in sorted(ad)[:15]:
    print('   +', c, '->', n)
rst = os_ - ps_
ast = ps_ - os_
print('strings removidas (%d) [amostra]:' % len(rst))
for s in sorted(rst)[:25]:
    print('   -', repr(s[:110]))
print('strings adicionadas (%d) [amostra]:' % len(ast))
for s in sorted(ast)[:25]:
    print('   +', repr(s[:110]))
