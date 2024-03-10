import numpy as np
import datetime
import random as rand
import argparse
import sys

__version__ = '1.0'

print('')

def interpret_birthday(birthday_string):
    i = 0
    birthday_int = 0
    for i in [0, 1, 2, 3]:
        birthday_int += 10**(3-i) * int(list(birthday_string)[i])
    return birthday_int

def interpret_time(GMT):
    t_delta = datetime.timedelta(hours=int(GMT))
    standard_time = datetime.timezone(t_delta, 'standard_time')
    now = (datetime.datetime.now(standard_time)).strftime('%Y%m%d')
    return int(now)

parser = argparse.ArgumentParser(
    usage = '$python luck.py [-h] your_birthday [--GMT hours]',
    description = 'This program tells your fortune of today using bogo-sort (N=5).',
    formatter_class = argparse.RawTextHelpFormatter)
parser.add_argument('birthday', type=interpret_birthday,
                   help=('your birthday\n'+
                         'example1: 1225\n'+
                         'example2: 0903\n'))
parser.add_argument('--GMT', type=interpret_time, default=interpret_time(9),
                    help='standard time at your place (default: 9 (JST))') 
args = parser.parse_args()


# global variables -------------------------------------------------
N = 5
list_to_sort = np.arange(N)
seed = args.birthday * args.GMT
rand.seed(seed)
iteration = 0

# main ----------------------------------------------------------

# prepare functions
def shuffle():
    global list_to_sort, iteration
    rand.shuffle(list_to_sort)
    iteration += 1

def is_sorted():
    for i in range(N-1):
        if list_to_sort[i] > list_to_sort[i+1]:
            return False
    return True


# bogo-sort
shuffle()
while True:
    if iteration > 600:
        break
    if is_sorted():
        break
    shuffle()

# judge luck

if iteration == 1:
    print('YOU ARE EXTREMELY LUCKY !!!')
    print('You succeeded in sorting at once !!!')
elif iteration <= 7:
    print('You are very lucky !!') # top 5%
elif iteration <= 27:
    print('You are lucky !') # top 20%
elif iteration <= 109:
    print('You have a normal luck.') # top 60%
elif iteration <= 165:
    print('You are a bit unlucky..') # top 75%
elif iteration <= 274:
    print('You are unlucky...') # top 90%
elif iteration <= 600:
    print('You are very unlucky....') # top ~100%
else:
    print('YOU ARE EXTREMELY UNLUCKY.....')
    print('You could not succeed in sorting in 600 attempts')

print('number of attempts:', iteration)
