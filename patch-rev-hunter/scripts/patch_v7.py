import struct, zipfile, shutil, hashlib, zlib

SRC_DEX = '/home/z/my-project/rea-work/orig_c13.dex'
BASE_APK = '/home/z/my-project/rea-work/v6_unsigned.apk'
OUT_DEX = '/home/z/my-project/rea-work/c13_v7.dex'
OUT_APK = '/home/z/my-project/rea-work/v7_unsigned.apk'
PATCHES = [(0xfd488, 6), (0xfd48e, 6)]
NOWIN = 'Lcom/kiritoprojects/ultrasshservice/util/Nowin;'

data = bytearray(open(SRC_DEX, 'rb').read())
u32 = lambda o: struct.unpack_from('<I', data, o)[0]
u16 = lambda o: struct.unpack_from('<H', data, o)[0]

def read_uleb(off):
    r = 0; s = 0
    while True:
        b = data[off]; off += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, off

sis, sio = u32(0x38), u32(0x3C)
strings = []
for i in range(sis):
    off = u32(sio + i * 4)
    n, off = read_uleb(off)
    end = data.index(b'\x00', off)
    strings.append(data[off:end].decode('utf-8', 'replace'))
tis, tio = u32(0x40), u32(0x44)
types = [strings[u32(tio + i * 4)] for i in range(tis)]
mis, mio = u32(0x58), u32(0x5C)
mrefs = [(types[u16(mio + i * 8)], strings[u32(mio + i * 8 + 4)]) for i in range(mis)]

# achar dono de cada patch site
cds, cdo = u32(0x60), u32(0x64)
owners = {}
for i in range(cds):
    b = cdo + i * 32
    cls = types[u32(b)]
    cda = u32(b + 24)
    if not cda:
        continue
    p, o = read_uleb(cda)
    sf, o = read_uleb(o)
    im, o = read_uleb(o)
    vm, o = read_uleb(o)
    for _ in range(p + sf):  # pula encoded fields (idx_diff + access)
        _a, o = read_uleb(o)
        _b, o = read_uleb(o)
    idx = 0
    entries = []
    try:
        for _ in range(im + vm):
            md, o = read_uleb(o)
            idx += md
            acc, o = read_uleb(o)
            co, o = read_uleb(o)
            entries.append((idx, co))
    except Exception as e:
        print('  (parse de class_data falhou em', cls, '->', e, ')')
        continue
    for midx, co in entries:
        if not co or midx >= len(mrefs):
            continue
        insns_size = u32(co + 12)
        lo, hi = co, co + 16 + insns_size * 2
        for site, _n in PATCHES:
            if lo <= site < hi:
                owners[site] = (cls, mrefs[midx][1], lo, hi)
for site, _n in PATCHES:
    found = owners.get(site)
    print('dono de 0x%08x:' % site, found if found else 'nao localizado (nao bloqueia o patch)')

# aplicar nops
for site, nb in PATCHES:
    data[site:site + nb] = b'\x00' * nb
    print('nops aplicados em 0x%08x (%d bytes)' % (site, nb))

# checksums
struct.pack_into('<I', data, 8, zlib.adler32(bytes(data[12:])) & 0xffffffff)
data[0x0C:0x20] = hashlib.sha1(bytes(data[0x20:])).digest()
open(OUT_DEX, 'wb').write(bytes(data))
print('dex patchado salvo:', OUT_DEX, len(data), 'bytes')

# rebuild APK
zin = zipfile.ZipFile(BASE_APK)
zout = zipfile.ZipFile(OUT_APK, 'w')
for it in zin.infolist():
    payload = zin.read(it.filename)
    if it.filename == 'classes13.dex':
        payload = bytes(data)
        it = zipfile.ZipInfo(it.filename, date_time=it.date_time)
        it.compress_type = it.compress_type
    zi = zipfile.ZipInfo(it.filename, date_time=it.date_time)
    zi.compress_type = it.compress_type
    zi.external_attr = it.external_attr
    zout.writestr(zi, payload)
zout.close()
print('APK v7 unsigned:', OUT_APK)
