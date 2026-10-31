#!/usr/bin/env python3
"""Deep dex scan: find classes extending android.app.Application and
exact com/liapp/* method references in each dex."""
import sys, zipfile, re, struct

def read_uleb(buf, off):
    result = 0; shift = 0
    while True:
        b = buf[off]; off += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return result, off

def analyze(data, dexname):
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    u16 = lambda o: struct.unpack_from('<H', data, o)[0]
    str_ids_size, str_ids_off = u32(0x38), u32(0x3C)
    strings = []
    for i in range(str_ids_size):
        off = u32(str_ids_off + i * 4)
        n, off = read_uleb(data, off)
        end = data.index(b'\x00', off)
        strings.append(data[off:end].decode('utf-8', 'replace'))
    type_ids_size, type_ids_off = u32(0x40), u32(0x44)
    types = [strings[u32(type_ids_off + i * 4)] for i in range(type_ids_size)]
    # class defs: find superclass == Application
    cd_size, cd_off = u32(0x60), u32(0x64)
    apps = []
    for i in range(cd_size):
        base = cd_off + i * 32
        cls_idx = u32(base)
        cls = types[cls_idx] if cls_idx < len(types) else '?'
        sup_idx = u32(base + 8)
        sup = types[sup_idx] if sup_idx != 0xFFFFFFFF else None
        if sup == 'Landroid/app/Application;':
            apps.append(cls)
    # method ids referencing com/liapp classes
    m_size, m_off = u32(0x58), u32(0x5C)
    liapp_calls = {}
    tsize = type_ids_size
    for i in range(m_size):
        base = m_off + i * 8
        cls_idx = u16(base); name_idx = u32(base + 4)
        cls = types[cls_idx] if cls_idx < tsize else '?'
        if cls.startswith('Lcom/liapp'):
            liapp_calls.setdefault(cls, set()).add(strings[name_idx])
    print(f"== {dexname} ==")
    for a in sorted(apps):
        if a not in ('Landroid/app/Application;',):
            print(f"   EXTENDS-APPLICATION: {a}")
    for cls, names in sorted(liapp_calls.items()):
        print(f"   CALLS {cls}: {sorted(names)}")

def main():
    apk = sys.argv[1]
    with zipfile.ZipFile(apk) as z:
        for dn in sorted(n for n in z.namelist() if re.match(r'classes\d*\.dex$', n)):
            try:
                analyze(z.read(dn), dn)
            except Exception as e:
                print(f"== {dn} == ERROR {e}")

main()
