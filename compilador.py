import os
import sys

argv = sys.argv[1]

operators = []

for i in range(len(argv)):

    if(argv[i] == "+" or argv[i] == "-"):

        operators.append(i)


begining = 0
numbers = []
for ops in operators:
    ss = argv[begining:ops]
    numbers.append(int(ss))
    begining = ops+1
numbers.append(int(argv[begining:]))
res = numbers[0]
for ops in range(0, len(operators)):
    if(argv[operators[ops]] == "+"):
        res += numbers[ops+1]
    elif(argv[operators[ops]] == "-"):
        res -= numbers[ops+1]

print(res)
