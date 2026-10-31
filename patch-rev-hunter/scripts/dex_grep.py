#!/usr/bin/env python3
"""Search string pools of all dexes in an APK for patterns."""
import sys, zipfile, re, struct

def read_uleb(buf, off):
    r = 0; s = 0
    while True:
        b = buf[off]; off += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, off

def dex_strings(data):
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    sis, sio = u32(0x38), u32(0x3C)
    out = []
    for i in range(sis):
        off = u32(sio + i * 4)
        n, off = read_uleb(data, off)
        end = data.index(b'\x00', off)
        out.append(data[off:end].decode('utf-8', 'replace'))
    return out

pats = [p.lower() for p in sys.argv[2:]]
with zipfile.ZipFile(sys.argv[1]) as z:
    for dn in sorted(n for n in z.namelist() if re.match(r'classes\d*\.dex$', n)):
        data = z.read(dn)
        try:
            strs = dex_strings(data)
        except Exception as e:
            print(dn, 'parse error', e); continue
        hits = []
        for s in strs:
            sl = s.lower()
            for p in pats:
                if p in sl:
                    hits.append(s)
                    break
        if hits:
            print(f"== {dn} ==")
            for h in sorted(set(hits))[:15]:
                print(f"   {h!r}")
