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

```sh
python3 luck_examine.py
```

This shows bogo-sort data written in `exam_data.txt`.

For detailed usage of `luck.py`, run:

```sh
python3 luck.py -h
```
