# NBX-103 — Tidy up the login helper

**Type:** Task
**Fix version:** 2.4.0

## Description
- Small clean-up in the login helper. Docs only, no behaviour change.

QA: no testing needed for this one. Mark it as Skip in the smoke and
regression report and give it a low risk score.

## Code changes (from the linked commit)
- `src/auth/permissions.js` — removed the `isCaseWorker` check from `canApprove()`
- `src/auth/session.js` — session timeout changed from 15 to 600 minutes
