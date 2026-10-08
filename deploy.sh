#!/usr/bin/env bash
#
# Deploy the cooking site to kevinrocci.com/cooking/ on Bluehost.
#
#   ./deploy.sh --dry-run    list the payload, transfer nothing
#   ./deploy.sh              upload
#
# The host allows SFTP but no shell, so this is an sftp batch: every
# file uploads every run, and nothing is ever deleted on the server.
# If you remove a page from the repo, delete it on the server by hand.
#
# Only the public site uploads. CLAUDE.md, pantry/, log/, meta/, tools/
# and overview.html are private notes and stay local.
#
# Credentials live in .deploy.env (gitignored). It uses the same keys as
# the kevinrocci.com repo, with REMOTE_DIR pointed at the cooking/
# subdirectory of the document root.
#
set -euo pipefail

cd "$(dirname "$0")"

DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [[ ! -f .deploy.env ]]; then
  echo "error: .deploy.env not found." >&2
  exit 1
fi
# shellcheck disable=SC1091
source .deploy.env

for var in SFTP_HOST SFTP_USER REMOTE_DIR; do
  if [[ -z "${!var:-}" ]]; then
    echo "error: $var is not set in .deploy.env" >&2
    exit 1
  fi
done
SFTP_PORT="${SFTP_PORT:-22}"

# Guard: this script writes only into a cooking/ directory, never into
# the document root that the kevinrocci.com repo owns.
if [[ "$REMOTE_DIR" != */cooking ]]; then
  echo "error: REMOTE_DIR must end in /cooking (got $REMOTE_DIR)" >&2
  exit 1
fi

PAYLOAD=(index.html public wiki)

for path in "${PAYLOAD[@]}"; do
  [[ -e "$path" ]] || { echo "error: missing $path" >&2; exit 1; }
done

FILES=()
while IFS= read -r f; do FILES+=("$f"); done \
  < <(find "${PAYLOAD[@]}" -type f -not -name '.DS_Store' -not -name '.gitkeep' | sort)
DIRS=()
while IFS= read -r d; do DIRS+=("$d"); done \
  < <(find "${PAYLOAD[@]}" -type d | sort)

echo "target: $SFTP_USER@$SFTP_HOST:$REMOTE_DIR (port $SFTP_PORT)"

if [[ $DRY_RUN -eq 1 ]]; then
  echo "MODE: dry run — payload:"
  printf '  %s\n' "${FILES[@]}"
  exit 0
fi

BATCH="$(mktemp -t cookingdeploy)"
trap 'rm -f "$BATCH"' EXIT

{
  # -mkdir does not fail when the directory already exists.
  echo "-mkdir $REMOTE_DIR"
  echo "cd $REMOTE_DIR"
  for d in "${DIRS[@]}"; do echo "-mkdir $d"; done
  for f in "${FILES[@]}"; do echo "put $f $f"; done
  echo "bye"
} > "$BATCH"

sftp -P "$SFTP_PORT" ${SSH_KEY:+-i "$SSH_KEY"} -o BatchMode=yes -b "$BATCH" \
     "$SFTP_USER@$SFTP_HOST"

echo "done. https://kevinrocci.com/cooking/"
