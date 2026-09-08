#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
bin_dir=${BIN_DIR:-"$HOME/.local/bin"}
target="$bin_dir/luck"

mkdir -p "$bin_dir"

# Write to a temporary file first so an interrupted install does not leave a
# partially written command in the user's PATH.
tmp_wrapper=$(mktemp "${TMPDIR:-/tmp}/luck.XXXXXX")
cleanup() {
    rm -f "$tmp_wrapper"
}
trap cleanup EXIT HUP INT TERM

printf '%s\n' \
    '#!/bin/sh' \
    "cd \"$repo_dir\" || exit 1" \
    'exec python3 luck.py "$@"' > "$tmp_wrapper"
chmod 755 "$tmp_wrapper"
mv -f "$tmp_wrapper" "$target"

printf 'Installed luck at %s\n' "$target"
if ! printf '%s' ":$PATH:" | grep -Fq ":$bin_dir:"; then
    printf 'Add %s to PATH to run luck directly.\n' "$bin_dir"
fi
