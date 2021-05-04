import math
from random import randint

with open("data.dat", 'w') as f:
    for i in range(2 ** 14):
        f.write(str(i) + '\t' + str(randint(-5000, 5000) + 300 * math.sin(100.0 * 2.0 * math.pi * i / 1000)) + '\n')
