from random import randint as random
#import math
import sys

dictionary = []

#read in dictionary
for line in sys.stdin :
    dictionary.append(line.rstrip())

print(len(dictionary))

out = []
for i in range(100000):
    index = random(1, len(dictionary)) - 1
    out.append(dictionary[index])
    dictionary.remove(dictionary[index])

f = open("small_dict.txt", "w")
f.write("\n".join(out))
f.close()