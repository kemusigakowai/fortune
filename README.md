# Fortune

Fortune calculates a daily birthday fortune with bogo sort and generates a
ranking for all 366 valid birthdays.

## Requirements

- Python 3.6.8
- Runtime dependencies: `setup/requirements.txt`
- Examination dependencies: `setup/requirements-exam.txt`
- A C++17 compiler and Make for the C++ examination program

## Installation

### Runtime environment

Create a virtual environment and install the runtime dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r setup/requirements.txt
```

Install the additional Python examination dependencies with:

```sh
python3 -m pip install -r setup/requirements-exam.txt
```

### Command installation

Install the `luck` command in `~/.local/bin`:

```sh
./setup/install.sh
```

Add `~/.local/bin` to `PATH` when required by the shell environment:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

Run the script directly from the repository:

```sh
python3 luck.py 0928
```

Run the installed command from any directory:

```sh
luck 0928
```

The birthday is a four-digit `MMDD` value representing an existing calendar
date. February 29 is accepted.

Display detailed command-line help with:

```sh
python3 luck.py -h
```

## Ranking

Create or display today's ranking for all 366 birthdays:

```sh
luck --ranking
```

Display the fortune and rank for one birthday:

```sh
luck 0928 --ranking
```

The ranking cache is stored in `data/ranking.txt`. The browser data is stored
in `data/ranking-data.js`. Both paths are resolved relative to the repository,
and cached ranking data is reused after its date and contents are validated.

### Ranking data format

The ranking data begins with its generation date and table header:

```text
20260907
"Ranking" "Birthday" "Fortune" "Number of Attempts"
1 0502 extremely_lucky 1
```

Equal attempt counts receive the same rank. The next rank includes all tied
entries; for example, `1, 1, 2, 2, 4` becomes `1, 1, 3, 3, 5`.

Birthdays with equal attempt counts are displayed in a reproducibly shuffled
order for each day. The ranking shuffle seed is calculated as:

```text
sum of the digits in YYYYMMDD
+ MM * 10
+ DD * 3
+ floor(MM * sin(YYYY))
```

This shuffle is independent of the random sequence used to calculate each
birthday's number of attempts.

## Browser ranking

Open `ranking.html` to view the ranking. Running `luck --ranking` updates both
ranking data files. The page loads `data/ranking-data.js` and provides search,
month, day, Fortune, and attempt-count filters. Filter conditions are stored in
the URL for reloading and sharing the same view.

When served by Apache, the root `.htaccess` exposes `ranking.html` and
`data/ranking-data.js`. The `data/.htaccess` file protects the remaining files
in `data`. Open the page as `/fortune/ranking.html` and enable the legacy host
access directives with `AllowOverride Limit`.

## Scheduled ranking updates

### Cron

Install the daily cron job with:

```sh
sh ./setup/install_cron.sh
```

The job starts at 00:00:00, waits one second, and runs `luck --ranking` at
00:00:01. Logs are written to `~/.local/state/luck/ranking.log`.

### Ranking loop

Run the aligned ranking loop in a detached tmux session:

```sh
tmux new -s luck-ranking
sh ./setup/ranking_loop.sh
```

Detach with `Ctrl-b d` and reattach with:

```sh
tmux attach -t luck-ranking
```

The loop checks at 00:00:01, 06:00:01, 12:00:01, and 18:00:01. It runs
`luck --ranking` when the date differs from the previous successful execution.

## Examination tools

### C++

Build and run the C++17 examination program:

```sh
make -C exam
make -C exam run
```

The run writes percentile data to `exam/exam_data.txt` and the plot to
`exam/exam_plot.svg`.

Remove the compiled program with:

```sh
make -C exam clean
```

### Python

Run the Python examination program with:

```sh
make -C exam python
```

It writes percentile data to `exam/exam_data.txt` and displays the plot with
Matplotlib.
