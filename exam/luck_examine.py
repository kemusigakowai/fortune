import datetime
import random
import secrets
from pathlib import Path

import matplotlib.pyplot as plt


class BogoSortExaminer:
    """Examine how many shuffles bogo sort needs for a range of seeds."""

    def __init__(self, item_count=5, exam_size=10_000, start_seed=None):
        if item_count < 1:
            raise ValueError('item_count must be at least 1')
        if exam_size < 1:
            raise ValueError('exam_size must be at least 1')

        self.item_count = item_count
        self.exam_size = exam_size
        self.start_seed = self._today_in_jst() if start_seed is None else start_seed
        self.attempt_counts = []
        self.percentile_attempts = []

    @staticmethod
    def _today_in_jst():
        jst = datetime.timezone(datetime.timedelta(hours=9), 'JST')
        return int(datetime.datetime.now(jst).strftime('%Y%m%d'))

    def _attempts_until_sorted(self, seed):
        values = list(range(self.item_count))
        generator = random.Random(seed)
        attempts = 0

        while True:
            generator.shuffle(values)
            attempts += 1
            if values == sorted(values):
                return attempts

    def examine(self, progress_interval=10_000):
        """Run all examinations and return a frequency table by attempt count."""
        self.attempt_counts = []
        seed = self.start_seed
        seed_generator = random.Random(secrets.randbits(256))

        for index in range(self.exam_size):
            if progress_interval and index % progress_interval == 0:
                print('examined:', index, 'seeds\r', end='', flush=True)

            random_factor = seed_generator.randint(1, 10)
            seed += index * random_factor
            attempts = self._attempts_until_sorted(seed)
            if attempts >= len(self.attempt_counts):
                self.attempt_counts.extend(
                    [0] * (attempts - len(self.attempt_counts) + 1))
            self.attempt_counts[attempts] += 1

        self.percentile_attempts = []
        return self.attempt_counts

    def attempts_at_percentile(self, percent):
        if not self.attempt_counts:
            raise RuntimeError('examine() must be called first')
        if not 0 < percent <= 100:
            raise ValueError('percent must be greater than 0 and at most 100')

        target = percent * 0.01 * self.exam_size
        cumulative_count = 0
        for attempts, count in enumerate(self.attempt_counts):
            cumulative_count += count
            if cumulative_count >= target:
                return attempts

        raise RuntimeError('examination results are incomplete')

    def calculate_percentiles(self):
        self.percentile_attempts = [
            self.attempts_at_percentile(step / 10)
            for step in range(1, 1001)
        ]
        return self.percentile_attempts

    def save_percentiles(self, output_path='exam_data.txt'):
        if not self.percentile_attempts:
            self.calculate_percentiles()

        output_path = Path(output_path)
        with output_path.open('w', encoding='utf-8') as output:
            for step, attempts in enumerate(self.percentile_attempts, 1):
                output.write(f'{step / 10:.1f}% {attempts}\n')

    def plot_percentiles(self):
        if not self.percentile_attempts:
            self.calculate_percentiles()

        percentages = [step / 10 for step in range(1, 1001)]
        plt.plot(self.percentile_attempts, percentages)
        plt.xlabel('number of attempts')
        plt.ylabel('possibility (%)')
        plt.title(
            f'possibility of succeeding in bogo-sort (N={self.item_count})')
        plt.show()

    def run(self, output_path='exam_data.txt', progress_interval=10_000):
        self.examine(progress_interval)
        self.calculate_percentiles()
        self.save_percentiles(output_path)
        self.plot_percentiles()


def main():
    item_count = 6
    exam_size = 100_000
    start_seed = 2026  # None means today's date in JST.
    progress_interval = 1_000
    output_path = 'exam_data.txt'

    print('')
    examiner = BogoSortExaminer(
        item_count=item_count,
        exam_size=exam_size,
        start_seed=start_seed,
    )
    examiner.run(
        output_path=output_path,
        progress_interval=progress_interval,
    )


if __name__ == '__main__':
    main()
