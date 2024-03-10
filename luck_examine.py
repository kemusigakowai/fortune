import numpy as np
import datetime
import random as rand
import argparse
import sys
import matplotlib.pyplot as plt

print('')


# global variables -------------------------------------------------
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = int(datetime.datetime.now(JST).strftime('%Y%m%d'))

N = 5
list_to_sort = np.arange(N)
rand.seed(now)
iteration = 0

exam_size = 100000
data = []
for i in range(10000):
    data.append(0)

# prepare functions --------------------------------------------

def shuffle():
    global list_to_sort, iteration
    rand.shuffle(list_to_sort)
    iteration += 1

def is_sorted():
    for i in range(N-1):
        if list_to_sort[i] > list_to_sort[i+1]:
            return False
    return True

def reset():
    global list_to_sort, iteration
    list_to_sort = np.arange(N).copy()
    iteration = 0

# main ----------------------------------------------------------

for i in range(exam_size):
    if i%10000 == 0:
        print('examined:', i, 'seeds')
    now += i
    rand.seed(now)
    shuffle()
    while True:
        if is_sorted():
            break
        shuffle()
    data[iteration] += 1
    reset()

# file output -------------------------------------------------
    
def exam_percent(percent):
    sum = 0
    for i in range(len(data)):
        count = data[i]
        sum += count
        if sum > percent * 0.01 * exam_size:
            return i

exam_list = []
percent_list = np.arange(1, 101)
with open('exam_data.txt', 'w') as file:
    for percent in percent_list:
        exam_list.append(exam_percent(percent))
        file.write(f'{percent}% {exam_percent(percent)}\n')

plt.plot(exam_list, percent_list)
plt.xlabel('number of attempts')
plt.ylabel('possibility (%)')
plt.title('possibility of succeeding in bogo-sort (N=5)')
plt.show()
