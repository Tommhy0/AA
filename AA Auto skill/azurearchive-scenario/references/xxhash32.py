# -*- coding: utf-8 -*-
"""AzureArchive 里 bgName 用的哈希：xxHash32(name, seed=0)（对 UTF-8 字节）。
用法:  python xxhash32.py BG_MainOffice
        -> BG_MainOffice 1046815759
"""
import struct, sys

P1 = 0x9E3779B1; P2 = 0x85EBCA77; P3 = 0xC2B2AE3D
P4 = 0x27D4EB2F; P5 = 0x165667B1; M = 0xFFFFFFFF

def _rotl(x, r):
    return ((x << r) | (x >> (32 - r))) & M

def xxh32(data: bytes, seed: int = 0) -> int:
    n = len(data); i = 0
    if n >= 16:
        v1 = (seed + P1 + P2) & M; v2 = (seed + P2) & M
        v3 = seed & M;             v4 = (seed - P1) & M
        def rnd(v, d):
            v = (v + d * P2) & M
            return (_rotl(v, 13) * P1) & M
        while i + 16 <= n:
            v1 = rnd(v1, struct.unpack_from('<I', data, i)[0]); i += 4
            v2 = rnd(v2, struct.unpack_from('<I', data, i)[0]); i += 4
            v3 = rnd(v3, struct.unpack_from('<I', data, i)[0]); i += 4
            v4 = rnd(v4, struct.unpack_from('<I', data, i)[0]); i += 4
        h = (_rotl(v1, 1) + _rotl(v2, 7) + _rotl(v3, 12) + _rotl(v4, 18)) & M
    else:
        h = (seed + P5) & M
    h = (h + n) & M
    while i + 4 <= n:
        h = (h + struct.unpack_from('<I', data, i)[0] * P3) & M
        h = (_rotl(h, 17) * P4) & M
        i += 4
    while i < n:
        h = (h + data[i] * P5) & M
        h = (_rotl(h, 11) * P1) & M
        i += 1
    h ^= h >> 15; h = (h * P2) & M
    h ^= h >> 13; h = (h * P3) & M
    h ^= h >> 16
    return h

def hash_name(name: str) -> int:
    """AzureArchive 写法：传入资源名（如 'BG_MainOffice'），返回 bgName 要填的 uint。"""
    return xxh32(name.encode('utf-8'))

if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(a, hash_name(a))
    if len(sys.argv) == 1:
        for k in ('BG_MainOffice', 'BG_MainOffice_Night', 'BG_Black'):
            print(k, hash_name(k))
