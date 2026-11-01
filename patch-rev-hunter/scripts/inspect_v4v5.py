import zipfile, zlib, sys

def brief(name, show_dex_crc=True):
    z = zipfile.ZipFile(name)
    inf = z.infolist()
    print('==', name, '| entries:', len(inf))
    so = [i for i in inf if i.filename.startswith('lib/') and i.filename.endswith('.so')]
    print('  .so:', len(so))
    for i in so[:4]:
        print('    ', i.filename.split('/')[-1], 'ct=', i.compress_type, 'sz=', i.file_size, 'off=', i.header_offset, 'align4096=', i.header_offset % 4096)
    dex = sorted([i for i in inf if i.filename.startswith('classes') and i.filename.endswith('.dex')], key=lambda x: x.filename)
    for i in dex:
        print('    ', i.filename, 'sz=', i.file_size, 'ct=', i.compress_type, 'date=', i.date_time, 'crc=%08x' % i.CRC)
    mi = [i for i in inf if i.filename.startswith('META-INF/') and (i.filename.endswith('.SF') or i.filename.endswith('.RSA') or 'vending' in i.filename or 'stamp' in i.filename or 'pin' in i.filename)]
    for i in mi:
        print('    META:', i.filename, 'sz=', i.file_size, 'date=', i.date_time)
    if 'resources.arsc' in z.namelist():
        a = z.getinfo('resources.arsc')
        print('    arsc: ct=', a.compress_type, 'sz=', a.file_size, 'align4096=', a.header_offset % 4096)
    fx = [i for i in inf if '.fxdvefvw' in i.filename]
    for i in fx:
        print('    LIAPP:', i.filename, 'sz=', i.file_size, 'crc=%08x' % i.CRC)
    tot = sum(i.file_size for i in inf)
    big = sorted(inf, key=lambda x: -x.file_size)[:6]
    for i in big:
        print('    BIG:', i.filename[:70], 'sz=', i.file_size, 'ct=', i.compress_type)
    print('  total uncompressed MB:', round(tot/1e6, 1))
    print()
    return {i.filename: i.CRC for i in inf}

crcs = {}
for n in sys.argv[1:]:
    try:
        crcs[n] = brief(n)
    except Exception as e:
        print('ERRO', n, e)

patched = '/home/z/my-project/rea-work/v3_dexes/classes13.dex'
pc = zlib.crc32(open(patched, 'rb').read()) & 0xffffffff
print('PATCHED classes13 (v3_dexes) crc = %08x' % pc)
for n, c in crcs.items():
    v = c.get('classes13.dex')
    if v is not None:
        print('   ', n, 'classes13 %08x' % v, '=> PATCHED' if v == pc else '=> original/other')
