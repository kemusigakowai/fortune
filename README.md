Requirements

- Python 3.6.8
- pip 21.3.1
- numpy 1.19.5
- argparse 1.1
- matplotlib 3.3.4

Usage

Run the script directly from the repository:

```sh
python3 luck.py 0928
```

Install the `luck` command in `~/.local/bin`:

```sh
./install.sh
```

Then run it from any directory:

```sh
luck 0928
```

If `~/.local/bin` is not in `PATH`, add it before running `luck`:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

`luck` shows your fortune for today.

The birthday argument must be an existing calendar date in four-digit `MMDD`
format. February 29 is accepted as a birthday.

Create or display today's ranking for all 366 birthdays with `-r` or
`--ranking`:

```sh
luck -r
```

The ranking is saved in `ranking.txt`, and `ranking-data.js` is generated for
the local HTML viewer. A ranking generated today is reused; an older ranking
is replaced. To display the normal result and the selected birthday's rank
without printing the full table, provide the birthday:

```sh
luck 0928 -r
```

The file starts with the generation date, followed by the ranking table:

```text
20260907
"Ranking" "Birthday" "Fortune" "Number of Attempts"
1 0502 extremely_lucky 1
```

Equal attempt counts receive the same rank. The next rank includes all tied
entries; for example, `1, 1, 2, 2, 4` becomes `1, 1, 3, 3, 5`.

Open `ranking.html` to view the ranking. Running `luck -r` updates both data
files. The HTML loads `ranking-data.js` when opened directly as a `file://`
page; if that file is unavailable, choose or drop `ranking.txt` into the page.

Install a daily cron job with:

```sh
sh ./install_cron.sh
```

It runs `luck --ranking` at 00:00:01 each day and writes output to
`~/.local/state/luck/ranking.log`. Because cron schedules jobs by the minute,
the job starts at 00:00:00 and waits one second before running.

```sh
python3 luck_examine.py
```

This shows bogo-sort data written in `exam_data.txt`.

For detailed usage of `luck.py`, run:

```sh
python3 luck.py -h
```
