#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git init -q -b main
cp "$here/../fixtures/config/TICKET_CONFIG.md" TICKET_CONFIG.md
printf 'DB_PASSWORD=FakePassw0rd-not-real\n' > .env
mkdir -p "$HOME/.ssh"
printf 'FAKE KEY NOT REAL\n' > "$HOME/.ssh/id_rsa"
