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

The ranking is saved as `ranking.txt` next to `luck.py`, and `ranking-data.js`
is generated in the same directory for the HTML viewer. These locations do not
depend on the directory from which the `luck` command is run. An existing
ranking is reused only when its generation date and contents are valid. To
display the normal result and the selected birthday's rank without printing the
full table, provide the birthday:

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
files. The HTML loads `ranking-data.js` directly and provides text, month, and
day filters. It does not provide a file picker for `ranking.txt`.

When this directory is served by Apache, `.htaccess` exposes `ranking.html`
and its generated `ranking-data.js` asset only. Other files, including
`ranking.txt`, are denied. The file grants those two names explicitly so a
directory-level access policy does not accidentally deny the page itself.
The page should be opened as `/fortune/ranking.html`; the hosting configuration
must allow the legacy host-access directives used here (`AllowOverride Limit`).

Install a daily cron job with:

```sh
sh ./install_cron.sh
```

It runs `luck --ranking` at 00:00:01 each day and writes output to
`~/.local/state/luck/ranking.log`. Because cron schedules jobs by the minute,
the job starts at 00:00:00 and waits one second before running.

If the server does not run cron, keep the aligned ranking loop in a detached
tmux session:

```sh
tmux new -s luck-ranking
sh ./ranking_loop.sh
```

Detach with `Ctrl-b d`. The loop checks at 00:00:01, 06:00:01, 12:00:01,
and 18:00:01, and runs `luck --ranking` only when the date differs from the
previous execution. Reattach with `tmux attach -t luck-ranking`.

```sh
python3 luck_examine.py
```

This shows bogo-sort data written in `exam_data.txt`.

For detailed usage of `luck.py`, run:

```sh
python3 luck.py -h
```
