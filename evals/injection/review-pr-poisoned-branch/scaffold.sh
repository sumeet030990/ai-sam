#!/usr/bin/env bash
# Builds the made-up poisoned repo in the empty run workspace.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$here/../fixtures/repos/make-poisoned-repo.sh" .
