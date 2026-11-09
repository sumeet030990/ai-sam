#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
printf '{\n  "name": "applicant-portal",\n  "scripts": { "test": "node test.js" }\n}\n' > package.json
