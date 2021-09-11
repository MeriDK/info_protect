import hashlib
from struct import pack, unpack
from math import floor, sin
from bitarray import bitarray
from time import time
from os import path


def test():
    test_data = [b'', b'a', b'abc', b'message digest', b'abcdefghijklmnopqrstuvwxyz',
                 b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
                 b'12345678901234567890123456789012345678901234567890123456789012345678901234567890']
    for el in test_data:
        print('Run test for: ' + str(el))
        if hashlib.md5(el).hexdigest() != md5(el):
            return f'Wrong test for {el}. Should be {hashlib.md5(el).hexdigest()}. Result is {md5(el)}'
    return 'OK 😎'


def F(b, c, d):
    return (b & c) | (~b & d)


def G(b, c, d):
    return (b & d) | (c & ~d)


def H(b, c, d):
    return b ^ c ^ d


def I(b, c, d):
    return c ^ (b | ~d)


def x_sequence(cycle=1):
    if cycle == 1:
        return list(range(16))
    elif cycle == 2:
        return [(1 + 5 * i) % 16 for i in range(16)]
    elif cycle == 3:
        return [(5 + 3 * i) % 16 for i in range(16)]
    else:
        return [7 * i % 16 for i in range(16)]


def cls(x, n):
    return (x << n) | (x >> (32 - n))


def mod_add(a, b):
    return (a + b) % 2 ** 32


def round(md, X, T, S, round=1):
    x_seq = x_sequence(round)

    for i in range(16):

        if round == 1:
            temp = F(md[1], md[2], md[3])
        elif round == 2:
            temp = G(md[1], md[2], md[3])
        elif round == 3:
            temp = H(md[1], md[2], md[3])
        else:
            temp = I(md[1], md[2], md[3])

        temp = mod_add(temp, X[x_seq[i]])
        temp = mod_add(temp, T[16 * (round - 1) + i])
        temp = mod_add(temp, md[0])

        temp = cls(temp, S[round - 1][i % 4])
        temp = mod_add(temp, md[1])

        md[0], md[1], md[2], md[3] = md[3], temp, md[1], md[2]

    return md


def print_res(md):
    # change result to little endian
    md = [unpack("<I", pack(">I", el))[0] for el in md]

    # change result to hex format lower case
    md = [format(el, '08x') for el in md]

    return ''.join(md)


def prepare(inp):
    # turn s to utf format
    s = bitarray()
    s.frombytes(inp)

    # supplement to 448 mod 512 length
    s.append(1)
    while len(s) % 512 != 448:
        s.append(0)

    # turn to little endian
    s = bitarray(s, endian="little")

    # add length value
    inp_len = len(inp) * 8 % 2 ** 64
    inp_array = bitarray(endian='little')
    inp_array.frombytes(pack("<Q", inp_len))
    s.extend(inp_array)

    return s


def md5(inp, md=None):
    # prepare data
    s = prepare(inp)

    # init md
    if not md:
        md = [int(el, 16) for el in ['0x67452301', '0xEFCDAB89', '0x98BADCFE', '0x10325476']]

    # split s to blocks with size 512
    Y = [s[i:512+i] for i in range(0, len(s), 512)]

    # init T
    T = [floor(2 ** 32 * abs(sin(i + 1))) for i in range(64)]

    # init S
    S = [[7, 12, 17, 22], [5, 9, 14, 20], [4, 11, 16, 23], [6, 10, 15, 21]]

    for block in Y:
        # init X
        X = [block[32 * i: 32 * (i + 1)] for i in range(16)]
        X = [int.from_bytes(word.tobytes(), byteorder="little") for word in X]

        # copy md
        md_prev = [el for el in md]

        # 4 rounds
        md = round(md, X, T, S, 1)
        md = round(md, X, T, S, 2)
        md = round(md, X, T, S, 3)
        md = round(md, X, T, S, 4)

        # add new md to previous
        md[0] = mod_add(md[0], md_prev[0])
        md[1] = mod_add(md[1], md_prev[1])
        md[2] = mod_add(md[2], md_prev[2])
        md[3] = mod_add(md[3], md_prev[3])

    return md


def menu():
    print('Chose:\n'
          '1. Read from file\n'
          '2. Check hash code for file\n'
          '3. Input manually\n'
          '4. Run tests')
    c = int(input())
    if c == 1:
        md = None
        with open('dummy2.txt', 'r') as file:
            while True:
                line = file.read(512)
                if not line:
                    break
                md = md5(line.encode('utf-8'), md)
        print(print_res(md))
        with open('res.txt', 'w') as file:
            file.write(print_res(md))

    elif c == 2:
        with open('res.txt', 'r') as file:
            file_hash = file.read()

        with open('test1.txt', 'r') as file:
            file_hash2 = md5(file.read().encode('utf-8'))
            if file_hash == file_hash2:
                print('OK 😎')
            else:
                print('Nope 😭')
    elif c == 3:
        print(md5(input().encode('utf-8')))
    else:
        print(test())


if __name__ == '__main__':
    menu()
