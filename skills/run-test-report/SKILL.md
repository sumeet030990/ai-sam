---
name: run-test-report
description: Run a repo's test suites — unit tests and feature tests (end-to-end browser tests and API or integration tests), for the frontend, the backend, or both — and build a pass/fail report. Finds the test commands from PROJECT_CONTEXT.md, the manifest scripts, test config files or CI files, shows a run plan (exact commands, what it starts, rough time) for approval, asks before starting any app, server or container, and never runs against production. Saves the raw results in a temporary folder, then reports totals per suite, every failing test with its file, first error line and likely cause (test problem, app bug, environment, or flaky), slow tests, and coverage when a coverage command exists. Can compare against the base branch to split new failures from ones that were already failing. Shows the report for approval, then asks where to save it: a Markdown (.md) or Excel (.xlsx) file in docs/test-runs/, SharePoint, OneDrive, Google Drive, a Confluence page, or a comment on a Jira ticket. The first answer is saved in PROJECT_CONTEXT.md and offered first on later runs. Use when the user says "run all the tests", "run unit and feature tests and give me a report", "test report for this branch", "are the tests green", "run the test suite", or runs /ai-sam:run-test-report [unit | feature | all] [filter]. Read-only on code: never fixes, skips or changes a test or source file, and never uploads or posts without showing it first.
---

# Run Test Report

Run the repo's tests and report the results, so a developer, QA or manager knows what passes and what is broken:

- **Unit tests** — small tests for one function or class on its own (e.g. Jest, Vitest, xUnit, NUnit, pytest, JUnit).
- **Feature tests** — tests that check a whole feature works, the way a user or API client uses it:
  - **Frontend** — end-to-end tests (E2E: tests that drive the real app in a browser), e.g. Playwright or Cypress.
  - **Backend** — API and integration tests (tests that call real endpoints with a test database), e.g. WebApplicationFactory, Supertest or Testcontainers.

Pick what to run:

- **All** — unit and feature tests. Used when nothing is given, e.g. `/ai-sam:run-test-report`.
- **Unit** or **Feature** only — e.g. `/ai-sam:run-test-report unit`.
- **A filter** — a folder, file, tag or test name, e.g. `/ai-sam:run-test-report feature checkout`.

Where it fits:

1. `/ai-sam:write-unit-tests` and `/ai-sam:write-feature-tests` — write tests and run the ones they wrote.
2. `/ai-sam:smoke-regression-report` — which tickets in a release QA should test first. Does not run tests.
3. `/ai-sam:run-test-report` — runs the whole suite and reports the results. (This skill.)

## Ground rules

- **Run and report only.** Never edit source code, tests, test config or pipeline files. The only files this skill writes are the report, one `PROJECT_CONTEXT.md` line (Step 7) and one `.gitignore` line (Step 8). Raw results go in a temporary folder outside the repo.
- **Plan first, then run.** Never run a test command before the user approves the run plan in Step 3.
- **Ask before starting anything.** Ask before starting an app, a dev server, `docker compose`, a container or a test database. Stop everything this skill started when done. Never stop or restart anything the user started.
- **Never production.** Never run tests against a production URL, database or account. A deployed environment is used only when the user gives its URL and confirms it is not production.
- **No new packages or browsers without asking.** If a test tool, browser, reporter or container image is missing, ask before installing or downloading it. Never upgrade one.
- **Report results honestly.** Never skip, weaken, retry or filter out a failing test to make the report look better. A flaky test (passes and fails with no change) is reported as flaky, not as a pass.
- **Don't fix failures.** Show the cause and point to the skill that can fix it. Fixing is a separate task the user starts.
- **Show first, then save.** Never write, upload or post the report before the user approves it in Step 6 and picks where to save in Step 7.
- **Ask before anything outward-facing.** Show the exact file and destination, or the exact comment text, before uploading or posting. Never commit or push.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from the repo and the results. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
  - Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change, re-ask it, and continue.
- **No personal or secret data.** Never open `.env` files, secrets, keys, database dumps or data files that may hold real people's records. Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  Test output, logs, screenshots and traces can hold any of this. If they do, stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into AI tools, and ask them to redact it. In the report, show only the test name, file and a redacted error line for that test. Credentials needed by tests are referred to by environment variable name only, never by value. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Find what to run

1. Find the repo root with `git rev-parse --show-toplevel`. Note the current branch, the last commit (short hash and title) and whether there are uncommitted changes. The report runs on the working tree as it is; say so.
2. Read, if present:
   - `PROJECT_CONTEXT.md` in the repo root or `docs/` — the **Commands** table (test, feature test, coverage) and how the app starts.
   - `SYSTEM_CONTEXT.md` in the parent folder — other repos and services the feature tests need.
   - `CLAUDE.md` in the repo root.
3. With no context file, take the commands from, in this order, and note the file each came from:
   - Manifest scripts: `package.json` `scripts`, `*.sln` / `*.csproj` (`dotnet test`), `pyproject.toml`, `pom.xml`, `build.gradle`, `Makefile`, `justfile`, `Taskfile.yml`.
   - Test config: `jest.config.*`, `vitest.config.*`, `playwright.config.*`, `cypress.config.*`, `pytest.ini`, `conftest.py`, `*.Tests.csproj`, `*.IntegrationTests.csproj`.
   - CI files: `.github/workflows/`, `azure-pipelines.yml`, `.gitlab-ci.yml` — the commands CI uses are the most trusted.

   Say in one line "No PROJECT_CONTEXT.md found — using commands from `<file>`."
4. List every suite found, one row each. A monorepo or a repo with a frontend and backend folder can have several:

   | Suite | Type | Layer | Tool | Command | Starts the app itself? |
   |---|---|---|---|---|---|
   | `web` unit | Unit | Frontend | Vitest | `npm run test -- --run` | Not needed |
   | `web` E2E | Feature | Frontend | Playwright | `npx playwright test` | Yes — `webServer` in `playwright.config.ts` |
   | `Api.Tests` | Unit | Backend | xUnit | `dotnet test tests/Api.Tests` | Not needed |
   | `Api.IntegrationTests` | Feature | Backend | WebApplicationFactory + Testcontainers | `dotnet test tests/Api.IntegrationTests` | Yes — needs Docker running |

   Tell unit and feature tests apart by folder and project names (`unit`, `e2e`, `integration`, `IntegrationTests`), test tags or categories, and the tool.
5. Keep only what the user asked for (All, Unit, Feature, or a filter). If a filter matches nothing, say so and ask which suite or folder they meant.
6. **No tests found** for a type the user asked for: say so in one line, suggest `/ai-sam:write-unit-tests` or `/ai-sam:write-feature-tests`, and go on with the rest.
7. **Nothing given and it is unclear**: ask — **What should I run?** Options: All — unit and feature tests (Recommended), Unit tests only, Feature tests only. Say the user can type a folder, file or tag in **Other**.

## Step 2 — Prepare the run

For each suite:

1. **Machine-readable results.** Add a reporter flag that writes results to a file in a temporary folder outside the repo, so the report is built from data, not from scrolling output. Use reporters the tool already has; never install one without asking.

   | Tool | Flag (example) |
   |---|---|
   | Jest | `--json --outputFile=<tmp>/jest.json` |
   | Vitest | `--reporter=default --reporter=junit --outputFile=<tmp>/vitest.xml` |
   | Playwright | `--reporter=list,junit` with `PLAYWRIGHT_JUNIT_OUTPUT_NAME=<tmp>/playwright.xml` |
   | Cypress | `--reporter junit --reporter-options mochaFile=<tmp>/cypress-[hash].xml` |
   | dotnet test | `--logger "trx;LogFileName=<tmp>/<project>.trx"` |
   | pytest | `--junitxml=<tmp>/pytest.xml` |
   | Maven / Gradle | Read `target/surefire-reports/` or `build/test-results/` after the run |

   If no file reporter is available, read the console output instead and say so.
2. **No early stop.** Don't add `--bail`, `-x` or `--maxfail`. Every test runs, so the report is complete. Keep any flags the repo's own command already has.
3. **Coverage** (optional) — note the coverage command if one exists (e.g. `npm run test:coverage`, `dotnet test --collect:"XPlat Code Coverage"`, `pytest --cov`). Don't add a coverage tool.
4. **What the feature tests need** — the base URL, test database, Docker, seed scripts, test logins (by environment variable name only), and any service in another repo. Check what is already running (the base URL responds, `docker ps`).
5. **Rough time** — from CI run times, a previous report in `docs/test-runs/`, or the number of test files. Say "unknown" if there is no clue.

## Step 3 — Show the run plan

Show:

````markdown
## Run plan: <repo> on `<branch>` (<short hash>)

**Runs:** <n> suites — <n> unit, <n> feature. <Uncommitted changes are included / Working tree is clean.>
**Rough time:** <e.g. 6–9 minutes / unknown>

| # | Suite | Type | Command | Needs |
|---|---|---|---|---|
| 1 | `web` unit | Unit | `npm run test -- --run` | Nothing |
| 2 | `Api.IntegrationTests` | Feature | `dotnet test tests/Api.IntegrationTests` | Docker running |
| 3 | `web` E2E | Feature | `npx playwright test` | Starts `npm run dev` on port 5173 itself |

**Will start:** <exact commands, ports and containers this skill starts, or "nothing">
**Not running:** <suite — reason, e.g. "`mobile` E2E — needs a device emulator">
````

Then ask, in one call:

1. **Run these tests?** Run the plan (Recommended), Unit tests only, Feature tests only, Retry previous answer.
2. **Also measure coverage?** (only if a coverage command exists): No (Recommended when the suite is slow), Yes — `<command>`, Retry previous answer.
3. **Feature test environment** (only if a feature suite needs an app that doesn't start itself): Start `<exact commands>` and stop them afterwards (Recommended), It's already running at a URL I give in Other, Skip feature tests, Retry previous answer.
4. **Compare with the base branch?** (only on a branch other than the base): No (Recommended), Yes — run the failing tests again on `<base branch>` to split new failures from ones already failing, Retry previous answer.

A URL given by the user: ask that it is not production before using it. If it looks like production (no `dev`, `qa`, `test`, `staging` or `localhost` in it), don't use it, and say why.

## Step 4 — Run

1. Run unit suites first, then feature suites, one at a time. Run each in the background when it may take over 2 minutes, and wait for it to finish.
2. Give each suite a time limit: 3 times the rough time, or 30 minutes when unknown. If it runs over, stop it, record it as **Timed out**, keep any partial results and go on.
3. **Can't start a suite** (Docker not running, a missing secret, a service in another repo, a missing browser): don't work around it. Record it as **Not run** with the reason and the command the user can run later. If a browser or package is missing, ask before installing it.
4. Record for each suite: command, start time, how long it took, exit code, and the results file.
5. **Flaky check** — run only the failed tests once more (e.g. `npx playwright test <file> -g "<name>"`, `dotnet test --filter "FullyQualifiedName=<name>"`, `pytest <file>::<name>`). A test that passes on the second run is **Flaky**, not a pass. Skip this step when more than 20 tests failed, and say so.
6. **Base branch compare** (only if picked in Step 3) — make a temporary worktree of the base branch outside the repo (`git worktree add <tmp>/base <base branch>`), install packages there only if the user agreed, run only the failed tests, and remove the worktree after. A test that also fails on the base branch is **Already failing**.
7. Run coverage, if picked.
8. Stop every app, server and container this skill started. Leave test databases clean.

## Step 5 — Read the results

1. Read every results file. Count per suite: total, passed, failed, skipped, flaky, and how long it took.
2. For each failing test, note:
   - Suite, file, test name, and line if known.
   - The first error line (e.g. `Expected 201, received 500`, `Timed out waiting for getByRole('button', { name: 'Save' })`). Redact any personal or secret data.
   - The screenshot, trace or video path for frontend failures, if the tool saved one.
3. Sort each failure by its likely cause, and say what points to it:
   - **App bug** — the test matches the expected behaviour but the app does something else, e.g. a 500 error, a wrong value, a missing element that the code removed.
   - **Test problem** — a bad selector, outdated expected value, missing wait, test data clash, or a test the latest change made out of date.
   - **Environment** — a service down, port in use, missing seed data, missing environment variable, Docker not running.
   - **Flaky** — failed, then passed on the second run.
   - **Already failing** — also fails on the base branch (only when compared).
   - **Unclear** — say what to check next.
4. Link a failure to the current branch when the failing test or the code it covers is in `git diff --name-only <base branch>...HEAD`. Mark it **Changed on this branch**.
5. Group failures with the same error (e.g. 14 tests failing on the same login timeout). Report the group once, with the number of tests and one example.
6. List the 5 slowest tests in each suite if the results file has times.

Don't open or fix the source code beyond what is needed to name the likely cause.

## Step 6 — Show the report

Show it in the chat:

````markdown
## Test run report: <repo> on `<branch>` (<short hash>)

**Result:** All passed / <n> failing / Partly run — <one-line reason>
**Run on:** <YYYY-MM-DD HH:MM time zone> — <working tree clean / includes uncommitted changes>
**Totals:** <n> tests — <n> passed, <n> failed, <n> flaky, <n> skipped — took <m> min <s> s

### By suite
| Suite | Type | Passed | Failed | Flaky | Skipped | Time | Result |
|---|---|---|---|---|---|---|---|
| `web` unit | Unit | 412 | 0 | 0 | 3 | 48 s | Pass |
| `Api.IntegrationTests` | Feature (API) | 86 | 2 | 1 | 0 | 3 min 10 s | Fail |
| `web` E2E | Feature (browser) | — | — | — | — | — | Not run — Docker not running |

### Failures (<n>)
| # | Suite | Test | File | Error (first line) | Likely cause | Changed on this branch |
|---|---|---|---|---|---|---|
| 1 | `Api.IntegrationTests` | `CreateOrder_ValidRequest_Returns201` | `tests/Api.IntegrationTests/OrdersTests.cs:42` | Expected 201, received 500 | App bug — `OrderService.Create` throws on empty notes | Yes |

### Flaky (<n>)
- `<test>` — `<file>` — failed, then passed on the second run

### Already failing on `<base branch>` (<n>)
- `<test>` — `<file>`

### Coverage
| Suite | Lines | Branches |
|---|---|---|
| `web` unit | 78% | 64% |

### Slowest tests
- `<test>` — 41 s — `<file>`

### Not run
- `<suite>` — <reason> — run later with `<command>`

### How to run these tests yourself
1. <start command, if needed>
2. `<test command>` for each suite

### Next steps
- <e.g. "Fix 2 app bugs in `OrderService` — then re-run `/ai-sam:run-test-report feature`">
- <e.g. "Repair the outdated test with `/ai-sam:write-feature-tests ABC-123`">
````

Leave out empty sections, except **By suite** and **How to run these tests yourself**.

Then ask — **Report**: This looks right (Recommended), Re-run the failed tests, Ask a follow-up, Retry with edits.

- **Re-run the failed tests** — run only the failing tests again (Step 4, 5 and 6 for those tests only) and show the updated report.
- **Ask a follow-up** — answer, reading the code or results again if needed.
- **Retry with edits** — ask what to change (Run another suite, Add coverage, Compare with base branch, or **Other**). Run only that and show the report again.

Repeat until the user picks **This looks right**.

## Step 7 — Ask where to save

### 7a — Check what is saved and connected

1. Look for a saved place: the `**Test run report save to:**` line in `PROJECT_CONTEXT.md` (repo root or `docs/`), else in the repo's `CLAUDE.md`.
2. Check which upload tools work: a Microsoft 365, SharePoint, Google Drive or Atlassian connector; `m365 status` (the CLI — command-line tool — for Microsoft 365); a Jira connector for a ticket comment.

### 7b — First run (nothing saved)

Ask — **Where should I save this report?** (multi-select):

- **Markdown or Excel file in the repo** — in `docs/test-runs/`. (Recommended when no upload tool is connected.) A follow-up asks which.
- **SharePoint, OneDrive or Google Drive** — a team folder. A follow-up asks for the place.
- **Confluence page** — under a parent page you name. Only if an Atlassian connector is available.
- **Comment on a Jira ticket** — a short summary on the ticket in the branch name. Only if Jira is connected and the branch has a ticket key.

Say the user can type another place in **Other**. Then ask the follow-ups, in one call, only for what was picked:

| Picked | Follow-up |
|---|---|
| File in the repo | **Which file type?** (multi-select): Markdown (.md) (Recommended), Excel (.xlsx). And the folder: `docs/test-runs/` (Recommended), or type another in **Other** |
| SharePoint | Site URL (e.g. `https://<company>.sharepoint.com/sites/<team>`), document library (default `Documents`), folder path (e.g. `QA/Test runs`) |
| OneDrive | Folder path |
| Google Drive | Folder link or path, and shared drive name if any |
| Confluence | Space key and parent page title |
| Any shared folder | **File type for the shared copy**: Excel (.xlsx) (Recommended), Markdown (.md) |
| Jira comment | **Which ticket?**: `<key from branch>` (Recommended), or type another key in **Other** |

If `PROJECT_CONTEXT.md` has a `**Test cases share:**` line from `/ai-sam:write-test-cases`, offer that location as the first suggestion for a shared folder.

Never ask for or save passwords, tokens or any other credential — only where the file goes.

**Save the answer** as one line in `PROJECT_CONTEXT.md` (repo root or `docs/`), under **Notes**, with a dated **Change log** line. If there is no `PROJECT_CONTEXT.md`, add the line to the repo's `CLAUDE.md` instead, and say so. A Jira comment is not saved, since the ticket changes each run.

```markdown
- **Test run report save to:** Markdown file — folder `docs/test-runs/`; SharePoint — site `<site URL>` — library `Documents` — folder `QA/Test runs` — format .xlsx
```

Say in one line where the choice was saved.

### 7c — Later runs (a place is saved)

Ask — **Where should I save this report?**:

- **Same as last time** — list the saved places in one line, e.g. "Markdown in `docs/test-runs/` + SharePoint `QA/Test runs`". (Recommended)
- **Change where to save** — run 7b again and replace the saved line.
- **Only this time: somewhere else** — run 7b's questions but don't save the answers.
- **Retry previous answer**.

### Before saving

- If a file with the same name exists, ask: Replace it (Recommended), Save as `<name>-2`, Retry previous answer.
- If a saved folder no longer exists or access is denied, say so and offer **Change where to save**.

## Step 8 — Save

Do each place the user picked. File name: `<YYYY-MM-DD>-<branch>-test-run`, with `/` and spaces changed to `-` (e.g. `2026-11-06-feature-ABC-123-test-run.md`).

### 8a — Get the repo folder ready

Only when a repo file was picked:

1. Create the folder if missing (`mkdir -p docs/test-runs/`).
2. Keep it out of git — the report is a working note, not code:
   - If `git check-ignore -q <folder>/x.md` says it is already ignored, do nothing.
   - Otherwise add the folder on its own line at the end of the repo root `.gitignore`, under `# Test run reports from ai-sam run-test-report`. Create `.gitignore` if missing. Don't change any other line.
3. Say in one line what was created and added.

### 8b — Markdown file

Write the Step 6 report, with the first line `# Test run report: <repo> on <branch>` and a `**Written:** <YYYY-MM-DD>` line under it.

### 8c — Excel file

1. Use the `xlsx` skill if this session has one. Otherwise write a short Python script in a temporary folder outside the repo using `openpyxl`.
2. If `openpyxl` is missing, ask — **Excel needs the `openpyxl` Python library**: Install it with `pip install --user openpyxl` (Recommended), Save as CSV (a plain table file Excel opens) instead, Skip Excel, Retry previous answer.
3. Sheets: **Summary** (result, totals, branch, commit, date), **By suite**, **Failures**, and **Flaky**, **Coverage**, **Not run** when they have rows.
4. **Failures** columns: Suite, Type, Test, File, Error, Likely cause, Changed on this branch, plus empty **Owner**, **Ticket** and **Notes** columns for the team.
5. Bold header row, frozen top row, wrapped text and readable column widths.
6. Open the saved file once to check every failure is in it, then delete the temporary script.

### 8d — Shared folder (SharePoint, OneDrive, Google Drive)

1. Build the file as in 8b or 8c. If no repo file was picked, build it in a temporary folder outside the repo and delete it after upload.
2. Upload, using the first that works:
   - A connector for that service in this session.
   - SharePoint or OneDrive: `m365 spo file add --webUrl <site URL> --folder "<library>/<folder path>" --path <file>`, if `m365 status` shows it is signed in.
   - Neither: say no upload tool is connected and which connector would make it work. Save the file in `docs/test-runs/` as in 8a, and give the exact place to upload it by hand.
3. Show the file name and full destination. Ask — **Upload to <service>?**: Upload (Recommended), Change the folder for this file only, Retry previous answer. Upload only on yes.
4. Give the link to the uploaded file. If the upload fails, show the error in one line, save the file in the repo folder instead, and say so.

### 8e — Confluence page

1. Build the page from the Step 6 report, titled `Test run report: <repo> <branch> <YYYY-MM-DD>`.
2. If a page with that title exists under the parent, ask: Update it (Recommended), Create `<title> (2)`, Retry previous answer.
3. Show the title, space and parent. Ask — **Create this page?**: Create it (Recommended), Change the parent page, Retry previous answer. Create only on yes, then give the link.

### 8f — Jira comment

1. Build a short comment: result line, totals, the **By suite** table, up to 10 failures (test, error, likely cause), and the link to the saved file if there is one.
2. Show the exact comment text and the ticket key. Ask — **Post this comment on `<key>`?**: Post it (Recommended), Change the text, Retry previous answer. Post only on yes, then give the link.

## Step 9 — Report back

Show a short report in the chat:

````markdown
## Report saved: <repo> on `<branch>`

**Result:** <All passed / n failing> — <n> passed, <n> failed, <n> flaky, <n> not run
**Saved to:**
- `docs/test-runs/<name>.md`
- SharePoint — <link>
- Confluence — <link>
- Jira comment on <key> — <link>

**Next step:** <e.g. "Fix the 2 app bugs, then re-run `/ai-sam:run-test-report feature`">
````

Leave out lines that don't apply. Add a line if `.gitignore`, `PROJECT_CONTEXT.md` or `CLAUDE.md` was changed — those changes are uncommitted. Never commit or push anything.
