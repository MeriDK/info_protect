class RC5:
    def __init__(self, key):
        self.w = 16
        self.r = 16
        self.b = 64 // 8

        self.S = []
        self.L = []
        self.c = 0
        self.mod = 2 ** self.w
        self.mask = self.mod - 1
        self.t = 2 * (self.r + 1)
        self.w4 = self.w // 4
        self.w8 = self.w // 8

        self.key = key
        self.key_align()
        self.key_extend()
        self.shuffle()

    def key_align(self):
        if self.b == 0:
            self.c = 1
        elif self.b % self.w8 == 0:
            self.c = self.b // self.w8
        else:
            self.key += b'\x00' * (self.w8 - self.b % self.w8)
            self.b = len(self.key)
            self.c = self.b // self.w8

        L = [0] * self.c
        for i in range(self.b - 1, -1, -1):
            L[i // self.w8] = (L[i // self.w8] << 8) + self.key[i]
        self.L = L

    def key_extend(self):
        p = 0xB7E1
        q = 0x9E37
        self.S = [(p + i * q) % self.mod for i in range(self.t)]

    def shuffle(self):
        i, j, A, B = 0, 0, 0, 0
        for k in range(3 * max(self.c, self.t)):
            A = self.S[i] = self.lshift((self.S[i] + A + B), 3)
            B = self.L[j] = self.lshift((self.L[j] + A + B), A + B)
            i = (i + 1) % self.t
            j = (j + 1) % self.c

    def lshift(self, val, n):
        n %= self.w
        return ((val << n) & self.mask) | ((val & self.mask) >> (self.w - n))

    def rshift(self, val, n):
        n %= self.w
        return ((val & self.mask) >> n) | (val << (self.w - n) & self.mask)

    def encrypt_block(self, data):
        a = int.from_bytes(data[:self.w8], byteorder='little')
        b = int.from_bytes(data[self.w8:], byteorder='little')
        a = (a + self.S[0]) % self.mod
        b = (b + self.S[1]) % self.mod
        for i in range(1, self.r + 1):
            a = (self.lshift((a ^ b), b) + self.S[2 * i]) % self.mod
            b = (self.lshift((a ^ b), a) + self.S[2 * i + 1]) % self.mod
        return a.to_bytes(self.w8, byteorder='little') + b.to_bytes(self.w8, byteorder='little')

    def encrypt_file(self, inp_file_name, out_file_name):
        with open(inp_file_name, 'rb') as inp, open(out_file_name, 'wb') as out:
            is_empty = False
            while not is_empty:
                text = inp.read(self.w4)
                if not text:
                    break
                if len(text) != self.w4:
                    is_empty = True
                    text = text.ljust(self.w4, b'\x00')
                text = self.encrypt_block(text)
                print(text)
                out.write(text)

    def decrypt_block(self, data):
        a = int.from_bytes(data[:self.w8], byteorder='little')
        b = int.from_bytes(data[self.w8:], byteorder='little')
        for i in range(self.r, 0, -1):
            B = self.rshift(b - self.S[2 * i + 1], a) ^ a
            a = self.rshift(a - self.S[2 * i], b) ^ b
        b = (b - self.S[1]) % self.mod
        a = (a - self.S[0]) % self.mod
        return a.to_bytes(self.w8, byteorder='little') + b.to_bytes(self.w8, byteorder='little')

    def decrypt_file(self, inp_file_name, out_file_name):
        with open(inp_file_name, 'rb') as inp, open(out_file_name, 'wb') as out:
            is_empty = False
            while not is_empty:
                text = inp.read(self.w4)
                if not text:
                    break
                if len(text) != self.w4:
                    is_empty = True
                text = self.decrypt_block(text)
                if is_empty:
                    text = text.rstrip(b'\x00')
                out.write(text)


rc5 = RC5('hzQqzAEN'.encode())
rc5.encrypt_file('in.txt', 'res.txt')
rc5.decrypt_file('res.txt', 'out.txt')
