
from bitarray import bitarray
from tzi_lab2 import hash 

class Random():

    def __init__(self):
        self.m =  (2**19)-1 #модуль порівняння (2**19)-1
        self.a =  6**3 #множник 6**3
        self.c =  55 #приріст 55
        self.X0 =  1024 #початкове значення 1024

    def gen(self, count):
        X = self.X0
        usedNum = []
        for i in range(count):
            X = (self.a*X+self.c)%self.m
            usedNum.append(X)
        return usedNum



class RC5:
    
    def __init__(self, w, R, key, stripNulls=False):
        self.w = w 
        self.R = R
        self.key = key
        self.rand = rand
        self.stripNulls = stripNulls
        
        self.T = 2 * (R + 1)
        self.w4 = w // 4
        self.w8 = w // 8
        self.mod = 2 ** self.w
        self.mask = self.mod - 1
        self.keyLen = len(key)
        
        self.constFirst = False
        self.constSecond = False

        self.keyAlign()
        self.getVectorInit()


    def __lshift(self, val, n):
        n %= self.w
        return ((val << n) & self.mask) | ((val & self.mask) >> (self.w - n))

    def __rshift(self, val, n):
        n %= self.w
        return ((val & self.mask) >> n) | (val << (self.w - n) & self.mask)

    def __const(self):
        if self.rand:
            return (self.rand[0], self.rand[1])
        else:
            if self.w == 16:
                return (0xB7E1, 0x9E37)
            elif self.w == 32:
                return (0xB7E15163, 0x9E3779B9)
            elif self.w == 64:
                return (0xB7E151628AED2A6B, 0x9E3779B97F4A7C15)

    def keyAlign(self):
        if self.keyLen == 0:
            self.c = 1
        else:
            self.c = self.keyLen // self.w8
        KeyByteL = [0] * self.c
        for i in range(self.keyLen - 1, -1, -1):
            KeyByteL[i // self.w8] = (KeyByteL[i // self.w8] << 8) + self.key[i]
        self.KeyByteL = KeyByteL

    def getVectorInit(self):
        if not self.constFirst and not self.constSecond:
            constFirst, constSecond = self.__const()
        else:
            constFirst, constSecond = self.constFirst, self.constSecond
        self.VectorInit = [(constFirst + i * constSecond) % self.mod for i in range(self.T)]


    def mixing(self):
        i, j, A, B = 0, 0, 0, 0
        for k in range(3 * max(self.c, self.T)):
            A = self.VectorInit[i] = self.__lshift((self.VectorInit[i] + A + B), 3)
            B = self.KeyByteL[j] = self.__lshift((self.KeyByteL[j] + A + B), A + B)
            i = (i + 1) % self.T
            j = (j + 1) % self.c

    def encryptBlockCBC(self, data):
        self.getVectorInit()
        A = int.from_bytes(data[:self.w8], byteorder='little')
        B = int.from_bytes(data[self.w8:], byteorder='little')
        A = (A + self.VectorInit[0]) % self.mod
        B = (B + self.VectorInit[1]) % self.mod
        for i in range(1, self.R + 1):
            A = (self.__lshift((A ^ B), B) + self.VectorInit[2 * i]) % self.mod
            B = (self.__lshift((A ^ B), A) + self.VectorInit[2 * i + 1]) % self.mod
        self.constFirst, self.constSecond = A, B
        return (A.to_bytes(self.w8, byteorder='little')
                + B.to_bytes(self.w8, byteorder='little'))
    
    def encryptBlock(self, data):
        self.getVectorInit()
        A = int.from_bytes(data[:self.w8], byteorder='little')
        B = int.from_bytes(data[self.w8:], byteorder='little')
        A = (A + self.VectorInit[0]) % self.mod
        B = (B + self.VectorInit[1]) % self.mod
        for i in range(1, self.R + 1):
            A = (self.__lshift((A ^ B), B) + self.VectorInit[2 * i]) % self.mod
            B = (self.__lshift((A ^ B), A) + self.VectorInit[2 * i + 1]) % self.mod
        return (A.to_bytes(self.w8, byteorder='little')
                + B.to_bytes(self.w8, byteorder='little'))

    def decryptBlockCBC(self, data):
        A = int.from_bytes(data[:self.w8], byteorder='little')
        B = int.from_bytes(data[self.w8:], byteorder='little')
        self.getVectorInit()
        self.constFirst, self.constSecond = A, B
        for i in range(self.R, 0, -1):
            B = self.__rshift(B - self.VectorInit[2 * i + 1], A) ^ A
            A = self.__rshift(A - self.VectorInit[2 * i], B) ^ B
        B = (B - self.VectorInit[1]) % self.mod
        A = (A - self.VectorInit[0]) % self.mod
        return (A.to_bytes(self.w8, byteorder='little')
                + B.to_bytes(self.w8, byteorder='little'))

    def decryptBlock(self, data):
        A = int.from_bytes(data[:self.w8], byteorder='little')
        B = int.from_bytes(data[self.w8:], byteorder='little')
        for i in range(self.R, 0, -1):
            B = self.__rshift(B - self.VectorInit[2 * i + 1], A) ^ A
            A = self.__rshift(A - self.VectorInit[2 * i], B) ^ B
        B = (B - self.VectorInit[1]) % self.mod
        A = (A - self.VectorInit[0]) % self.mod
        self.getVectorInit()
        return (A.to_bytes(self.w8, byteorder='little')
                + B.to_bytes(self.w8, byteorder='little'))

    def encryptFile(self, inpFileName, outFileName):
        self.mixing()
        self.constFirst, self.constSecond = False, False
        with open(inpFileName, 'rb') as inp, open(outFileName, 'wb') as out:
            out.write(self.encryptBlock(self.rand[0].to_bytes(length=len(str(self.rand[0])), byteorder='little')))
            out.write(self.encryptBlock(self.rand[1].to_bytes(length=len(str(self.rand[1])), byteorder='little')))
            run = True
            while run:
                text = inp.read(self.w4)
                if not text:
                    break
                if len(text) != self.w4:
                    text = text.ljust(self.w4, b'\x00')
                    run = False
                text = self.encryptBlockCBC(text)
                out.write(text)

    def decryptFile(self, inpFileName, outFileName):
        self.constFirst, self.constSecond = False, False
        self.getVectorInit()
        with open(inpFileName, 'rb') as inp, open(outFileName, 'wb') as out:
            text = inp.read((2*(self.w4)))
            self.rand = [int.from_bytes(self.decryptBlock(text[:4]), byteorder='little'), int.from_bytes(self.decryptBlock(text[4:]), byteorder='little')]
            while True:
                text = inp.read(self.w4)
                if not text:
                    break
                text = self.decryptBlockCBC(text)
                if self.stripNulls:
                    text = text.rstrip(b'\x00')
                out.write(text)

message = "Hello, world, anouther world!"

rand = Random().gen(2)
rand = [int(bin(rand[0])[:15],2),int(bin(rand[1])[:15],2)]
rc5 = RC5(16,8,bytearray.fromhex(hash(message)), rand)
rc5.encryptFile("test","out")
rc5.decryptFile("out","res")



