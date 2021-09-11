key = '0111111110'
print('Key:', key)
text = '01111110'
print('Text:', text)


def p10(el):
    ind = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    return ''.join(el[i - 1] for i in ind)


print('Put this key into P.10 Table and permute the bits.')
step2 = p10(key)
print(step2)


def divide(el):
    return el[:len(el) // 2], el[len(el) // 2:]


step3l, step3r = divide(step2)
print('Divide the key into two halves, left half and right half')
print(step3l, step3r)


def round_shift(el):
    return el[1:] + el[0]


step4l = round_shift(step3l)
step4r = round_shift(step3r)
print('Now apply the one bit Round shift on each half')
print(step4l, step4r)


def combine(el1, el2):
    return el1 + el2


def p8(el):
    ind = [6, 3, 7, 4, 8, 5, 10, 9]
    return ''.join(el[i - 1] for i in ind)


print('Now  once again combine both halve of the bits, right and left. Put them into the P8 table. '
      'The output and K1 or key One will be:')
step5 = p8(combine(step4l, step4r))
k1 = step5
print(step5)

step6l, step6r = step4l, step4r
print('Go in step 4 copy both halves, each one consists of 5 bits')
print(step6l, step6r)

print('Apply two round shift circulate on each half of the bits')
step7l = round_shift(round_shift(step6l))
step7r = round_shift(round_shift(step6r))
print(step7l, step7r)


print('Combine both together. Put the bits into 8-P Table. The output of the bits are your Second key or K2:')
step8 = p8(combine(step7l, step7r))
print(step8)
k2 = step8


def ip8(el):
    ind = [2, 6, 3, 1, 4, 8, 5, 7]
    return ''.join(el[i - 1] for i in ind)


print('Put the plain text into IP-8(initial permutation) table and permute the bits.')
step2 = ip8(text)
print(step2)

print('Now break the bits into two halves, each half will consist of 4 bits.')
step3l, step3r = divide(step2)
step3r_init = step3r
print(step3l, step3r)


def ep(el):
    ind = [4, 1, 2, 3, 2, 3, 4, 1]
    return ''.join(el[i - 1] for i in ind)


print('Take the right 4 bits and put them into E.P (expand and per-mutate) Table.')
step4 = ep(step3r)
print(step4)


def xor(el1, el2):
    return ''.join(['1' if el1[i] != el2[i] else '0' for i in range(len(el1))])


# hardcode delete this later
# step4 = '01000001'

print('Step 5: Now, just take the output and XOR it with First key')
step5 = xor(step4, k1)
print(step5)


def s0(row, col):
    tab = [
        ['01', '00', '11', '10'],
        ['11', '10', '01', '00'],
        ['00', '10', '01', '11'],
        ['11', '01', '11', '10']
    ]
    return tab[row][col]


def s1(row, col):
    tab = [
        ['00', '01', '10', '11'],
        ['10', '00', '01', '11'],
        ['11', '00', '01', '00'],
        ['10', '01', '00', '11']
    ]
    return tab[row][col]


def calc(el1, el2):
    res = int(el2) * 1 + int(el1) * 2
    return res


step6l, step6r = divide(step5)
print('Put the left half into S-0 box and put the right half into S-1 Box.')
step6l = s0(calc(step6l[0], step6l[-1]), calc(step6l[1], step6l[2]))
step6r = s1(calc(step6r[0], step6r[-1]), calc(step6r[1], step6r[2]))
print(step6l, step6r)

# hardcode delete this later
# step6l, step6r = '00', '11'


step7 = combine(step6l, step6r)
print('Now combine these two halves together.')
print(step7)


def p4(el):
    ind = [2, 4, 3, 1]
    return ''.join(el[i - 1] for i in ind)


print('Now take these 4 bits and put them in P-4 (permutation 4) table and get the result.')
step8 = p4(step7)
print(step8)

print('Now get XOR the output with left 4 bits of Initial Per-mutation')
step9 = xor(step3l, step8)
print(step9)

print('Now get the right half of the initial permutation, which is step 3, and combine that with this out- put.')
step10 = combine(step9, step3r)
print(step10)

print('Now once again break the out-put into two halves, left and right;')
step11l, step11r = divide(step10)
print(step11l, step11r)

print('Now swap both halves, which means put the left half in place of right and vice versa.')
step11l, step11r = step11r, step11l
print(step11l, step11r)

print('Now let’s take these halves and once again start the same procedure from step 2 but with K2')
# step2 = ip8(combine(step11l, step11r))
# print('Step  2', step2)
step3l, step3r = step11l, step11r
print('Step  3', step3l, step3r)
step4 = ep(step3r)
print('Step  4', step4)
step5 = xor(step4, k2)
print('Step  5', step5)
step6l, step6r = divide(step5)
t = step6r
step6l = s0(calc(step6l[0], step6l[-1]), calc(step6l[1], step6l[2]))
step6r = s1(calc(step6r[0], step6r[-1]), calc(step6r[1], step6r[2]))
print('Step  6', step6l, step6r)
step7 = combine(step6l, step6r)
print('Step  7', step7)
step8 = p4(step7)
print('Step  8', step8)
step9 = xor(step3l, step8)
print('Step  9', step9)
step10 = combine(step9, step11r)
print('Step 10', step10)
# step11l, step11r = divide(step10)
# print('Step 11', step11l, step11r)
# step11l, step11r = step11r, step11l
# print('Step 12', step11l, step11r)


def ip_1(el):
    ind = [4, 1, 3, 5, 7, 2, 8, 6]
    return ''.join(el[i - 1] for i in ind)


res = ip_1(step10)
print('Result', res)
