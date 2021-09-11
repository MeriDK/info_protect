from hashlib import md5


w = 16
r = 16
b = 64

key = 'password'

# prepare key
key = md5(key.encode()).digest()[8:]

# create L
w8 = w // 8
L = [0] * (b // w8)
for i in range(b // 8 - 1, -1, -1):
    L[i // w8] = (L[i // w8] << 8) + key[i]

mod = 2 ** w
mask = mod - 1
c = b // w8


def generator(n=1, m=mod, a=47073, c=40503, x0=17):
    nums = []
    for _ in range(n):
        x0 = (a * x0 + c) % m
        nums.append(x0)
    return nums


# create S
t = 2 * (r + 1)
S = generator(t)


def lshift(val, n):
    n %= w
    return ((val << n) & mask) | ((val & mask) >> (w - n))


def rshift(val, n):
    n %= w
    return ((val & mask) >> n) | (val << (w - n) & mask)


# shuffle
i, j, a, b = 0, 0, 0, 0
for k in range(3 * max(c, t)):
    a = S[i] = lshift((S[i] + a + b), 3)
    b = L[j] = lshift((L[j] + a + b), a + b)
    i = (i + 1) % t
    j = (j + 1) % c

# encrypt file
with open('in.txt', 'rb') as inp, open('res.txt', 'wb') as out:
    empty = False
    while not empty:
        # read text
        text = inp.read(w // 4)

        if not text:
            break
        if len(text) != w // 4:
            empty = True
            text = text.ljust(w // 4, b'\x00')

        # encrypt text
        a = int.from_bytes(text[:w8], byteorder='little')
        b = int.from_bytes(text[w8:], byteorder='little')
        a = (a + S[0]) % mod
        b = (b + S[1]) % mod
        for i in range(1, r + 1):
            a = (lshift((a ^ b), b) + S[2 * i]) % mod
            b = (lshift((a ^ b), a) + S[2 * i + 1]) % mod
        text = a.to_bytes(w8, byteorder='little') + b.to_bytes(w8, byteorder='little')

        # write text
        out.write(text)

# decrypt
with open('res.txt', 'rb') as inp, open('out.txt', 'wb') as out:
    empty = False
    while not empty:
        # read text
        text = inp.read(w // 4)
        if not text:
            break
        if len(text) != w // 4:
            empty = True

        # decrypt text
        a = int.from_bytes(text[:w8], byteorder='little')
        b = int.from_bytes(text[w8:], byteorder='little')
        for i in range(r, 0, -1):
            B = rshift(b - S[2 * i + 1], a) ^ a
            a = rshift(a - S[2 * i], b) ^ b
        b = (b - S[1]) % mod
        a = (a - S[0]) % mod
        text = a.to_bytes(w8, byteorder='little') + b.to_bytes(w8, byteorder='little')

        # write text
        if empty:
            text = text.rstrip(b'\x00')
        out.write(text)


