import zipfile, struct, re

def read_uleb(buf, off):
    r = 0; s = 0
    while True:
        b = buf[off]; off += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, off

def dex_info(data):
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    sis, sio = u32(0x38), u32(0x3C)
    strings = []
    for i in range(sis):
        off = u32(sio + i * 4)
        n, off = read_uleb(data, off)
        end = data.index(b'\x00', off)
        strings.append(data[off:end].decode('utf-8', 'replace'))
    return strings

z = zipfile.ZipFile('/home/z/my-project/rea-work/v6_unsigned.apk')
for dn in sorted(n for n in z.namelist() if re.match(r'classes\d*\.dex$', n)):
    d = z.read(dn)
    strs = dex_info(d)
    hits = [s for s in strs if 'kiritoprojects' in s.lower() or 'Nowin' in s or 'tamperProtect' in s or 'Nextprot' in s]
    if hits:
        print('==', dn, '(%d strings, %d MB)' % (len(strs), len(d) // 1048576))
        for h in sorted(set(hits))[:20]:
            print('   ', repr(h[:100]))
