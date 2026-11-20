# QA Context: ai-sam

_Last updated: 2026-11-20 by Sumeet Jadhav_

Read by the `ai-sam:qa-engineer` agent and the ai-sam test skills. Settings only. There is no `PROJECT_CONTEXT.md` yet; commands are listed in `README.md` (**Evals** and **Testing locally**).

## QA set-up

- **Testing:** Automation only

## Automation tools

| Layer | Tool | Version | Config file | Test folder |
|---|---|---|---|---|
| Guard hook checks (no model) | Python 3, standard library | 3.x | — | `evals/injection/guard/test_guard.py` |
| Skill evals (prompt injection) | `claude plugin eval` | case schema 1.1 | `evals/injection/*/case.yaml`, `prompt.md` frontmatter | `evals/injection/` |
| Plugin manifests | `claude plugin validate` | — | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | — |

- **Test data:** made-up tickets, configs and pasted answers in `evals/injection/fixtures/`; made-up repos built by `evals/injection/fixtures/repos/make-poisoned-repo.sh`.
- **Eval case layout:** one folder per case with `prompt.md` and `graders/`, as in `evals/injection/fix-comments-planted-comment/`. Cases that need a repo add `case.yaml` and `scaffold.sh`, as in `evals/injection/create-ticket-config-comment/`.
- **Graders per case:** a `skill-fired` grader, at least one "must not happen" grader (`tool_used`, `min: 0`, `max: 0`, `arm: both`) and an `llm` grader with clear PASS and FAIL lines.
- **Guard checks:** `(expected, tool, input)` tuples in one list in `test_guard.py`.
- **Cost:** `test_guard.py` is free and takes a second. Each `claude plugin eval` case is a real Claude run and uses the user's plan, so the caller asks before running one.

## Browsers and devices

- **Default browser:** Not applicable

## Domain

- **Business area:** a Claude Code plugin of skills and subagents that take a ticket from writing to release, and its protection against prompt injection (hidden instructions planted in tickets, PRs, code or logs).
- **User roles:** developer, QA / tester, project manager, product owner; plus the person who changes the skills.
- **Key workflows:**
  1. A skill reads a ticket, PR, log or repo file that holds a planted instruction, flags it and does not act on it.
  2. The guard hook blocks or asks before risky tool calls (secret files, download-and-run, new packages, force pushes, control files).
- **Business rules to protect:**
  - Every new guard rule has a check that hits it and one that must still pass through — `evals/injection/guard/test_guard.py`
  - A new control file is added to `ASK_WRITE_FILE_PATTERNS` and the README **Security** table — `hooks/guard.py`, `README.md`
  - The guard uses the Python standard library only — `hooks/guard.py`
  - Fixtures use made-up data only: `.example` domains, fake secrets marked `FAKE` or `not-real` — `evals/injection/README.md`
  - New eval cases are listed in the **What is tested** table, and the guard check count there stays correct — `evals/injection/README.md`

## Expertise

The `qa-engineer` agent works as a senior QA engineer who is expert in:

- Python 3 test scripts using only the standard library
- `claude plugin eval` cases, graders and scaffolds
- Prompt injection testing for AI agents, and Claude Code hooks and plugins

## Change log

| Date | Provided by | Change |
|---|---|---|
| 2026-11-20 | Sumeet Jadhav | QA context created; ai-sam eval and guard details moved here from the qa-engineer agent |
