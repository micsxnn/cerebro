import zipfile, struct, re

def read_uleb(buf, off):
    r = 0; s = 0
    while True:
        b = buf[off]; off += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, off

def class_defs(data):
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    sis, sio = u32(0x38), u32(0x3C)
    strings = []
    for i in range(sis):
        off = u32(sio + i * 4)
        n, off = read_uleb(data, off)
        end = data.index(b'\x00', off)
        strings.append(data[off:end].decode('utf-8', 'replace'))
    tis, tio = u32(0x40), u32(0x44)
    types = [strings[u32(tio + i * 4)] for i in range(tis)]
    cds, cdo = u32(0x60), u32(0x64)
    return [types[u32(cdo + i * 32)] for i in range(cds)]

z = zipfile.ZipFile('/home/z/my-project/rea-work/v6_unsigned.apk')
alvo = re.compile(r'Lcom/(hunter/net|kiritoprojects)/')
tot = 0
for dn in sorted(n for n in z.namelist() if re.match(r'classes\d*\.dex$', n)):
    d = z.read(dn)
    cds = class_defs(d)
    hits = [c for c in cds if alvo.match(c)]
    kit = [c for c in hits if 'kiritoprojects' in c]
    hun = [c for c in hits if 'hunter/net' in c]
    print('== %s: %d classes definidas | kiritoprojects: %d | hunter.net: %d' % (dn, len(cds), len(kit), len(hun)))
    for c in kit[:6]:
        print('     kit:', c)
    for c in hun[:6]:
        print('     hun:', c)
    tot += len(hits)
print('TOTAL definidas:', tot)
