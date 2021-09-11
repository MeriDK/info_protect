"""18 variant"""


# generate n values
def generator(n=1, m=2**27-1, a=14**3, c=2584, x0=17):
    nums = []
    for _ in range(n):
        x0 = (a * x0 + c) % m
        nums.append(x0)
    return nums


# run generator
res = generator(50)

# print res
print(' '.join(str(el) for el in res))

# write res to file
with open('lab1_res.txt', 'w') as file:
    file.write(' '.join(str(el) for el in res))


# function to find period
def find_period(x0=17):
    x0 = generator()[0]
    x1 = generator(x0=x0)[0]
    period = 1
    while x1 != x0:
        period += 1
        x1 = generator(x0=x1)[0]
    return period


# find period
print(find_period())
