#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
luck_command=${LUCK_COMMAND:-"$HOME/.local/bin/luck"}
state_dir=${XDG_STATE_HOME:-"$HOME/.local/state"}
log_file="$state_dir/luck/ranking.log"
marker='# luck daily ranking'

if [ ! -x "$luck_command" ]; then
    if [ ! -f "$repo_dir/install.sh" ]; then
        printf 'luck is not installed and install.sh was not found.\n' >&2
        exit 1
    fi
    sh "$repo_dir/install.sh"
fi

if [ ! -x "$luck_command" ]; then
    printf 'luck command not found at %s.\n' "$luck_command" >&2
    exit 1
fi

if ! command -v crontab >/dev/null 2>&1; then
    printf 'crontab was not found. Install cron before running this script.\n' >&2
    exit 1
fi

mkdir -p "$(dirname -- "$log_file")"
current_crontab=$(crontab -l 2>/dev/null || true)
if printf '%s\n' "$current_crontab" | grep -Fq "$marker"; then
    printf 'The luck daily ranking cron job is already installed.\n'
    exit 0
fi

cron_entry="0 0 * * * sleep 1; \"$luck_command\" --ranking >> \"$log_file\" 2>&1 $marker"
{
    if [ -n "$current_crontab" ]; then
        printf '%s\n' "$current_crontab"
    fi
    printf '%s\n' "$cron_entry"
} | crontab -


printf 'Installed daily ranking cron job: 00:00:01\n'
printf 'Log file: %s\n' "$log_file"
