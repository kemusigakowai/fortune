import numpy as np
import datetime
import random as rand
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

__version__ = '1.0'

N = 6
MAX_ATTEMPTS = 5000
RANKING_FILE = Path(__file__).resolve().with_name('ranking.txt')
RANKING_BROWSER_FILE = Path(__file__).resolve().with_name('ranking-data.js')
RANKING_HEADER = '"Ranking" "Birthday" "Fortune" "Number of Attempts"'
RANKING_YEAR = 2000

def interpret_birthday(birthday_string):
    if len(birthday_string) != 4 or not birthday_string.isdigit():
        raise argparse.ArgumentTypeError('birthday must be a four-digit MMDD value')

    month = int(birthday_string[:2])
    day = int(birthday_string[2:])
    try:
        # 2000 is a leap year, so February 29 remains a valid birthday.
        datetime.date(2000, month, day)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'birthday must be an existing calendar date in MMDD format')

    return int(birthday_string)


def interpret_time(GMT):
    t_delta = datetime.timedelta(hours=int(GMT))
    standard_time = datetime.timezone(t_delta, 'standard_time')
    now = (datetime.datetime.now(standard_time)).strftime('%Y%m%d')
    return int(now)


def birthdays():
    """Yield every valid birthday as an integer in MMDD form."""
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                datetime.date(RANKING_YEAR, month, day)
            except ValueError:
                continue
            yield month * 100 + day


def is_sorted(values):
    return all(values[index] <= values[index + 1] for index in range(N - 1))


def calculate_attempts(birthday, generated_date):
    values = np.arange(N)
    generator = rand.Random(birthday * generated_date)
    iteration = 0

    while True:
        generator.shuffle(values)
        iteration += 1
        if is_sorted(values) or iteration > MAX_ATTEMPTS:
            return iteration


def fortune_label(iteration):
    if iteration == 1:
        return 'extremely_lucky'
    if iteration <= 37:
        return 'very_lucky'
    if iteration <= 161:
        return 'lucky'
    if iteration <= 311:
        return 'a_bit_lucky'
    if iteration <= 755:
        return 'ordinal'
    if iteration <= 1157:
        return 'a_bit_unlucky'
    if iteration <= 2154:
        return 'unlucky'
    if iteration <= MAX_ATTEMPTS:
        return 'very_unlucky'
    return 'extremely_unlucky'


def fortune_messages(iteration):
    if iteration == 1:
        return ('YOU ARE EXTREMELY LUCKY !!!',
                'You succeeded in sorting at once !!!')
    if iteration <= 37:
        return ('You are very lucky !!',)
    if iteration <= 161:
        return ('You are lucky !',)
    if iteration <= 311:
        return ('You are a bit lucky !',)
    if iteration <= 755:
        return ('Your fortune is Ordinal.',)
    if iteration <= 1157:
        return ('You are a bit unlucky..',)
    if iteration <= 2154:
        return ('You are unlucky...',)
    if iteration <= MAX_ATTEMPTS:
        return ('You are very unlucky....',)
    return ('YOU ARE EXTREMELY UNLUCKY.....',
            f'You could not succeed in sorting in {MAX_ATTEMPTS} attempts')


def print_result(iteration, ranking=None):
    print('')
    for message in fortune_messages(iteration):
        print(message)
    print('number of attempts:', iteration)
    if ranking is not None:
        print('ranking:', ranking)


def build_ranking(generated_date):
    results = []
    for birthday in birthdays():
        attempts = calculate_attempts(birthday, generated_date)
        results.append((attempts, birthday, fortune_label(attempts)))

    results.sort(key=lambda result: (result[0], result[1]))
    ranking = []
    for index, (attempts, birthday, label) in enumerate(results, 1):
        rank = index
        if ranking and attempts == ranking[-1][3]:
            rank = ranking[-1][0]
        ranking.append((rank, birthday, label, attempts))
    return ranking


def ranking_text(generated_date, ranking):
    lines = [str(generated_date), RANKING_HEADER]
    lines.extend('{} {:04d} {} {}'.format(rank, birthday, label, attempts)
                 for rank, birthday, label, attempts in ranking)
    return '\n'.join(lines) + '\n'


def save_ranking(generated_date, ranking, ranking_file=None):
    ranking_file = RANKING_FILE if ranking_file is None else Path(ranking_file)
    temporary_name = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix='.ranking-', dir=str(ranking_file.parent))
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as output:
            os.fchmod(output.fileno(), 0o644)
            output.write(ranking_text(generated_date, ranking))
        os.replace(temporary_name, str(ranking_file))
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass


def save_browser_ranking(generated_date, ranking):
    browser_text = 'window.LUCK_RANKING_TEXT = {};\n'.format(
        json.dumps(ranking_text(generated_date, ranking), ensure_ascii=False))
    try:
        if RANKING_BROWSER_FILE.read_text(encoding='utf-8') == browser_text:
            os.chmod(RANKING_BROWSER_FILE, 0o644)
            return
    except (OSError, UnicodeError):
        pass

    temporary_name = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix='.ranking-data-', dir=str(RANKING_BROWSER_FILE.parent))
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as output:
            os.fchmod(output.fileno(), 0o644)
            output.write(browser_text)
        os.replace(temporary_name, str(RANKING_BROWSER_FILE))
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass


def load_ranking(generated_date, ranking_file=None):
    ranking_file = RANKING_FILE if ranking_file is None else Path(ranking_file)
    try:
        with open(ranking_file, encoding='utf-8') as source:
            lines = source.read().splitlines()
    except (OSError, UnicodeError):
        return None

    if len(lines) < 2:
        return None

    try:
        ranking_date = int(lines[0].strip())
    except ValueError:
        return None
    if ranking_date != generated_date:
        return None

    if lines[1].strip() != RANKING_HEADER:
        return None

    expected_birthdays = set(birthdays())
    ranking = []
    seen_birthdays = set()
    for line in lines[2:]:
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 4:
            return None
        try:
            rank = int(fields[0])
            birthday = interpret_birthday(fields[1])
            attempts = int(fields[3])
        except (ValueError, argparse.ArgumentTypeError):
            return None
        label = fields[2]
        expected_rank = len(ranking) + 1
        if ranking and attempts == ranking[-1][3]:
            expected_rank = ranking[-1][0]
        if (rank != expected_rank or birthday in seen_birthdays or
                attempts < 1 or label != fortune_label(attempts) or
                (ranking and attempts < ranking[-1][3])):
            return None
        ranking.append((rank, birthday, label, attempts))
        seen_birthdays.add(birthday)

    if seen_birthdays != expected_birthdays:
        return None
    # Reject cached results generated with a different sorting configuration.
    if any(attempts != calculate_attempts(birthday, generated_date)
           for _, birthday, _, attempts in ranking):
        return None
    return ranking


def get_ranking(generated_date, ranking_file=None):
    ranking = load_ranking(generated_date, ranking_file)
    if ranking is None:
        ranking = build_ranking(generated_date)
        save_ranking(generated_date, ranking, ranking_file)
    if ranking_file is None:
        save_browser_ranking(generated_date, ranking)
    return ranking


def create_parser():
    parser = argparse.ArgumentParser(
        usage='$python luck.py [-h] [-r] [your_birthday] [--GMT hours]',
        description=f'This program tells your fortune of today using bogo-sort (N={N}).',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('birthday', nargs='?', type=interpret_birthday,
                        help=('your birthday\n'+
                              'use an existing date in four-digit MMDD format\n'+
                              'example1: 1225\n'+
                              'example2: 0903\n'))
    parser.add_argument('-r', '--ranking', action='store_true',
                        help='create or show today\'s ranking for all birthdays')
    parser.add_argument('--GMT', type=interpret_time, default=interpret_time(9),
                        help='standard time at your place (default: 9 (JST))')
    return parser


def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)
    if args.birthday is None and not args.ranking:
        parser.error('birthday is required unless --ranking is specified')

    if args.ranking:
        ranking = get_ranking(args.GMT)
        if args.birthday is not None:
            selected = next(row for row in ranking if row[1] == args.birthday)
            print_result(selected[3], selected[0])
        else:
            sys.stdout.write(ranking_text(args.GMT, ranking))
        return 0

    attempts = calculate_attempts(args.birthday, args.GMT)
    print_result(attempts)
    return 0


if __name__ == '__main__':
    main()
