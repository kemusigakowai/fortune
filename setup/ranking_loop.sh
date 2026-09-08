#!/bin/sh
set -eu

setup_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$setup_dir/.." && pwd)
luck_command=${LUCK_COMMAND:-"$HOME/.local/bin/luck"}
ranking_file=${RANKING_FILE:-"$repo_dir/data/ranking.txt"}
slot_seconds=21600

if [ ! -x "$luck_command" ]; then
    printf 'luck command not found at %s.\n' "$luck_command" >&2
    printf 'Run install.sh first, or set LUCK_COMMAND to its absolute path.\n' >&2
    exit 1
fi

if ! date -d 'today 00:00:00' +%s >/dev/null 2>&1; then
    printf 'This script requires GNU date with the -d option.\n' >&2
    exit 1
fi

last_run_date=''
if [ -f "$ranking_file" ]; then
    first_line=$(sed -n '1p' "$ranking_file")
    case "$first_line" in
        ????????) last_run_date=$first_line ;;
    esac
fi

trap 'exit 0' INT TERM

while :; do
    now_epoch=$(date +%s)
    midnight_epoch=$(date -d 'today 00:00:00' +%s)
    next_wakeup=$((midnight_epoch + 1))
    while [ "$next_wakeup" -le "$now_epoch" ]; do
        next_wakeup=$((next_wakeup + slot_seconds))
    done

    sleep_seconds=$((next_wakeup - now_epoch))
    printf 'Next ranking check at %s (sleep %s seconds)\n' \
        "$(date -d "@$next_wakeup" '+%Y-%m-%d %H:%M:%S')" "$sleep_seconds"
    sleep "$sleep_seconds"

    current_date=$(date +%Y%m%d)
    if [ "$current_date" != "$last_run_date" ]; then
        printf 'Running luck --ranking for %s\n' "$current_date"
        if "$luck_command" --ranking; then
            last_run_date=$current_date
        else
            printf 'luck --ranking failed; it will be retried at the next check.\n' >&2
        fi
    else
        printf 'Ranking for %s already ran; waiting for the next check.\n' "$current_date"
    fi
done
