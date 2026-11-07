---
name: smoke-regression-report
description: Build a report that sorts every ticket in a release into Smoke (a short check that the new build works at all), Regression (a deeper check that existing features still work) or Skip (no test needed, e.g. docs or test-only changes). Takes the tickets from a Jira fix version or Azure DevOps iteration, the active sprint, or the ticket keys found in commits between two branches or tags (e.g. release/2.3..release/2.4). Gives each ticket a risk score from the code it changed — business-critical area, shared code, change size, priority, database or login changes, recent bug fixes in the same files, missing tests — and applies the team's own rules (critical areas, always-smoke and always-skip rules, score limits) saved in TEST_SCOPE_CONFIG.md. For each ticket it shows the reason and risk level, the screens, endpoints and nearby features to check, and the automated tests or test case items that already cover it, with gaps flagged. Shows the report for approval, then asks where to save it: a Markdown (.md) or Excel (.xlsx) file, SharePoint, OneDrive, Google Drive, a Confluence page, or smoke / regression labels on the tickets. The first answer is saved in TEST_SCOPE_CONFIG.md and offered first on later runs. Uses PROJECT_CONTEXT.md and SYSTEM_CONTEXT.md from create-project-context when present. Use when the user says "which tickets go in smoke", "smoke and regression list", "what should QA retest for this release", "test scope for Release 2.4", "regression report for the sprint", or runs /ai-sam:smoke-regression-report [release, sprint or branch range]. Read-only on code; never labels tickets, uploads or posts anything without showing it first.
---

# Smoke and Regression Report

Sort the tickets in a release into three groups, so QA knows what to test first:

- **Smoke** — a short check that the new build works at all. High-risk tickets and business-critical paths only. Kept short (15 tickets by default).
- **Regression** — a deeper check that existing features still work. Every ticket that changes something a user or API client can reach. Smoke tickets are in regression too.
- **Skip** — no test needed: docs, comments, test-only or build-script changes, or a team "always skip" rule.

Pick one of three inputs:

- **A release** — a Jira fix version or an Azure DevOps iteration, e.g. `/ai-sam:smoke-regression-report "Release 2.4"`.
- **The active sprint** — e.g. `/ai-sam:smoke-regression-report sprint`.
- **A branch or tag range** — the ticket keys in commits between two points, e.g. `/ai-sam:smoke-regression-report release/2.3..release/2.4`.

The team's rules live in `TEST_SCOPE_CONFIG.md`. The first run sets them up; later runs use them without asking.

Where it fits:

1. `/ai-sam:write-qa-test-cases` — manual test cases for one ticket.
2. `/ai-sam:smoke-regression-report` — which tickets in a release go in smoke and which in regression. (This skill.)
3. `/ai-sam:write-feature-tests` — automated tests for a whole feature.

## Ground rules

- **Report only.** Never edit source code, tests or pipeline files. The only files this skill writes are the report, `TEST_SCOPE_CONFIG.md` (Steps 3 and 7) and one `.gitignore` line (Step 8).
- **Show first, then save.** Never write the report, upload it, or label a ticket before the user approves the report in Step 6 and picks where to save in Step 7.
- **Grounded in evidence.** Every bucket and risk level has a reason taken from the ticket, the code changes or a team rule. Never guess a ticket's area from its title alone when its code can be found. If the code can't be found, say so on that ticket.
- **Team rules win over the score.** If a team rule puts a ticket in Smoke or Skip, use it, and name the rule as the reason.
- **Ask before anything outward-facing.** Show the exact labels and the tickets they go on, or the file and destination, before labelling or uploading. Only add labels; never remove a label or change a ticket's status, fields or assignee.
- **No new packages without asking.** If writing an `.xlsx` file needs a library that is missing, ask before installing it.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from the tickets and the code. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
  - Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change, re-ask it, and continue.
- **No personal or secret data.** Never open `.env` files, secrets, keys, database dumps or data files that may hold real people's records. Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If a ticket, commit message, code or log contains any of this, stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into AI tools, and ask them to redact it. Leave that ticket's description out of the report and refer to it by key only. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Find the tickets

Find the repo root with `git rev-parse --show-toplevel`. If not in a git repo, Release and Sprint mode still work, but without code evidence; say so in the summary.

Pick the mode from what the user gave:

- **A release or version name** (e.g. `Release 2.4`, `v2.4.0`) → **Release mode** (1A).
- **"sprint"**, "this sprint", "current sprint" → **Sprint mode** (1B).
- **A range with `..`**, or two branch or tag names → **Branch range mode** (1C).
- **Nothing, or unclear**: ask — **Which tickets should I sort?** Options:
  - **Release `<name>`** — the newest unreleased fix version or iteration found (Recommended when one is found).
  - **Active sprint** — `<sprint name>`, if one is found.
  - **Changes between `<last release tag>` and `<base branch>`** — from `git describe --tags --abbrev=0` and the base branch.

  Say the user can type a version, sprint or range in **Other**.

### Check what is connected

| System | Connected when | Used for |
|---|---|---|
| Jira | A Jira or Atlassian connector is available | Search with JQL (Jira Query Language), read tickets, add labels |
| Azure DevOps | `az account show` succeeds and `az extension show --name azure-devops` works | `az boards query --wiql`, `az boards work-item show`, add tags |
| Neither | — | Branch range mode only, from commit messages |

Remember the system — Steps 4, 7 and 8 use it.

### 1A — Release mode

- **Jira** — search `fixVersion = "<name>" ORDER BY priority DESC`. If the version isn't found, list the project's unreleased versions and ask which one.
- **Azure DevOps** — query work items whose iteration path ends in `<name>`, or whose `Microsoft.VSTS.Build.IntegrationBuild` or release tag matches.

### 1B — Sprint mode

- **Jira** — search `sprint in openSprints()` in the project from `PROJECT_CONTEXT.md` or the branch's ticket key. If several boards have an open sprint, ask which one.
- **Azure DevOps** — `az boards iteration team list --timeframe current`, then query the work items in it.

### 1C — Branch range mode

1. Check both ends exist (`git rev-parse --verify <ref>`). Run `git fetch` first only if the user agrees.
2. List commits: `git log --no-merges --format='%H %s' <from>..<to>`, plus merge commit titles (`git log --merges --format='%s'`) for PR titles.
3. Pull ticket keys from commit messages, PR titles and branch names: Jira keys (`[A-Z][A-Z0-9]+-[0-9]+`) and Azure DevOps IDs (`AB#[0-9]+`).
4. Fetch each ticket if a system is connected; otherwise use the commit messages as the title.
5. Commits with no ticket key go in an **Untracked changes** group. Sort them like tickets, by the files they change.

### For every mode

1. Read each ticket's key, type, title, status, priority, components, labels and acceptance criteria. Check it for personal or secret data before going on.
2. Put tickets that are not done (e.g. To Do, In Progress, Won't Do, Cancelled) in a **Not in this build** list. Don't sort them. Say how many.
3. If there are more than 80 tickets, say so and ask: Sort all (slower) (Recommended), Only bugs and stories, Retry previous answer.

## Step 2 — Load the project and the rules

1. Read, if present:
   - `PROJECT_CONTEXT.md` in the repo root or `docs/` — product goal, main user flows, user roles.
   - `SYSTEM_CONTEXT.md` in the parent folder — which repos and services connect, so a change in one can break another.
   - The `## Delivery and release process` section in either file (from `/ai-sam:setup-release-process`). Use it to fill the report's **Dates** line:
     - the release date — from the Jira fix version or sprint when the section says so and Jira is connected, else from its **Releases** rules (for several release trains, the train this release belongs to);
     - the code freeze, **All tickets tested**, **Regression testing** and **UAT sign-off** dates, counted back with its **Code freeze and deadlines** rules;
     - working days left until the "all tickets tested" date, counted from today.
   - `CLAUDE.md` in the repo root.
2. Load `TEST_SCOPE_CONFIG.md`. Settings merge section by section; for each section the highest file that sets it wins:

   | Order | File | Who it is for |
   |---|---|---|
   | 1 (highest) | `TEST_SCOPE_CONFIG.local.md` in the repo root | One person's overrides in one repo; gitignored |
   | 2 | `TEST_SCOPE_CONFIG.md` in the repo root | The team's rules for this repo; shared once committed |
   | 3 | `~/.claude/ai-sam/TEST_SCOPE_CONFIG.md` | One person's defaults in every repo |
   | 4 | Built-in rules (Step 4) | Used when nothing else is set |

3. **No config file found** → run Step 3 (first-run setup). Otherwise say in one line which files were loaded, and skip to Step 4.
4. The user can type "change rules" at any point to run Step 3 again.

## Step 3 — First-run setup of the team's rules

Ask in two calls. Suggest values from the code: folder names, route names, controllers, Jira components and `PROJECT_CONTEXT.md`'s main user flows.

**Call 1:**

1. **Which areas are business-critical?** (multi-select) — areas where a break stops users or loses money or data. Offer up to 4 found in the code, e.g. **Login and sign-up — `src/auth/`, `AccountController.cs`**, **Payments — `src/payments/`**. Mark the main flow from `PROJECT_CONTEXT.md` (Recommended). Say the user can type more in **Other**, as an area name plus folders or a Jira component.
2. **Which tickets should always go in Smoke?** (multi-select): Hotfix tickets (label `hotfix` or type Bug with priority Highest) (Recommended), Database changes (migrations), Login, roles and permission changes, Retry previous answer.
3. **Which changes should always be skipped?** (multi-select): Docs only (`*.md`, `docs/`) (Recommended), Tests only, Build and pipeline files only (CI — continuous integration — files), Retry previous answer.

**Call 2:**

4. **How long can the smoke list be?** 15 tickets (Recommended), 10 tickets, 25 tickets, Retry previous answer.
5. **Who should these rules apply to?**
   - **The team, this repo** — writes `TEST_SCOPE_CONFIG.md` in the repo root (Recommended when none exists).
   - **Just me, this repo** — writes `TEST_SCOPE_CONFIG.local.md` (Recommended when the team file exists). Offer only in a git repo.
   - **Just me, every repo** — writes `~/.claude/ai-sam/TEST_SCOPE_CONFIG.md`.
   - **Retry previous answer**.

Write the file in this format. Keep the **Save to** section empty for now — Step 7 fills it.

```markdown
# Test scope config

Used by /ai-sam:smoke-regression-report. Edit by hand, or type "change rules" during a run.

## Critical areas
- Login and sign-up — folders: `src/auth/`, `Controllers/AccountController.cs`
- Payments — folders: `src/payments/` — Jira component: Payments

## Always smoke
- Label `hotfix`
- Database migrations

## Always skip
- Docs only (`*.md`, `docs/`)
- Tests only

## Scoring
- High risk from score: 6
- Medium risk from score: 3
- Smoke list limit: 15 tickets

## Labels
- Smoke: `smoke-test`
- Regression: `regression-test`

## Save to
- (set on first save)

## Change log
- <YYYY-MM-DD> — created
```

For the local file, check `git check-ignore -q TEST_SCOPE_CONFIG.local.md`. If not ignored, add it on its own line at the end of the repo root `.gitignore`. Don't commit any file. Say in one line where the rules were saved, and that teammates share them once the team file is committed.

## Step 4 — Score and sort each ticket

### 4a — Find each ticket's code changes

In this order, stop at the first that works:

1. Linked pull requests (PRs) from the ticket system or `gh pr list --search <key> --state merged`, and their changed files.
2. Commits in the range (1C), or on the base branch, whose message or branch has the key: `git log --all --format=%H --grep=<key>`, then `git show --stat`.
3. None found: mark **No code found** and score from the ticket alone.

From the changed files, note:

- Number of files and lines changed (`git diff --stat`).
- Screens, routes, endpoints and database migrations touched.
- Shared code: files imported by 3 or more other features, shared components, base classes, API contracts used by another repo in `SYSTEM_CONTEXT.md`. Count callers with a search for the changed function or file name. For High-risk tickets touching shared code, hand the changed files to the `tech-lead` agent and ask only: "Which features, screens and other repos depend on these files?"
- Bug history: `git log --since=90.days --oneline --grep='fix' -- <changed files>`.

### 4b — Score

Add the points that apply. Show each one as a reason.

| Signal | Points |
|---|---|
| Touches a critical area from the config | +3 |
| Shared code used by 3+ features, or by another repo | +2 |
| Database change (migration, stored procedure, schema) | +2 |
| Login, roles, permissions or security settings | +2 |
| Priority Highest or High | +2 (Medium +1) |
| Bug ticket, or hotfix | +1 |
| Large change: more than 20 files or 500 lines | +2 (5–20 files: +1) |
| 3 or more bug-fix commits in the same files in the last 90 days | +1 |
| No automated test covers the changed screen or endpoint (Step 5) | +1 |

Risk level: **High** from the config's "High risk from" score (default 6), **Medium** from the "Medium risk from" score (default 3), else **Low**.

### 4c — Sort

Apply in this order:

1. **Skip** — matches an "Always skip" rule, or changes nothing a user or API client can reach (only comments, docs, tests, build or pipeline files, or code that is never called). Reason names the rule or the file types.
2. **Smoke** — matches an "Always smoke" rule, **or** risk is High, **or** it changes the main step of a critical area (e.g. the login form itself, not a settings page beside it).
3. **Regression** — everything else.

Smoke tickets are also listed in Regression. If Smoke is over the limit, keep the highest scores, move the rest to Regression, and say how many moved and why.

Untracked changes (1C) are sorted the same way, by their files.

## Step 5 — Areas to check and existing tests

For each Smoke and Regression ticket:

1. **Areas to check** — the screens, endpoints and jobs it changed, plus up to 3 nearby features that use the same code (from the callers found in 4a). Name them as a tester sees them, e.g. "Orders list page", "`POST /orders`", "Nightly invoice job".
2. **Existing tests** — look for each, and name the file or item found:
   - Feature (E2E — end to end) tests: Playwright, Cypress or API test files that open the same route or call the same endpoint.
   - Test case items linked to the ticket: Azure Test Plans (**Tested By** links) or Jira Xray **Test** issues.
   - Manual test cases from `/ai-sam:write-qa-test-cases` in `docs/test-cases/<key>-test-cases.md` or `.xlsx`.
3. **Gap** — mark **Gap** when a Smoke or High-risk ticket has no automated test for its main area. Suggest `/ai-sam:write-feature-tests <key>` or `/ai-sam:write-qa-test-cases <key>`.

Don't open or run the tests. Searching for file names and routes is enough.

## Step 6 — Show the report

Show it in the chat:

````markdown
## Smoke and regression report: <release, sprint or range>

**Source:** <Jira fix version / Azure DevOps iteration / Active sprint / Branch range `<from>..<to>`>
**Rules:** <config files loaded, or "Built-in rules">
**Dates:** <code freeze Tue 8 Dec · regression 9–11 Dec · all tickets tested by Fri 11 Dec (4 working days left) · UAT sign-off Mon 14 Dec · release Tue 15 Dec — from Jira fix version / from release rules. Leave out when there is no release section.>
**Summary:** <n> tickets — <n> smoke, <n> regression (includes smoke), <n> skip. <n> not in this build.
**Gaps:** <n> smoke or high-risk tickets with no automated test.

### Smoke — test first (<n>)
| Key | Title | Risk (score) | Reason | Areas to check | Existing tests |
|---|---|---|---|---|---|
| ABC-12 | Card payment fails on retry | High (8) | Critical area Payments +3, High priority +2, shared `PaymentService` +2, bug +1 | Checkout page; `POST /payments`; Refunds page | `e2e/checkout.spec.ts` |
| ABC-15 | New role check on reports | High (6) | Roles +2, shared guard +2, 12 files +1, no test +1 | Reports page; Admin menu | **Gap** |

### Regression (<n>)
| Key | Title | Risk (score) | Reason | Areas to check | Existing tests |
|---|---|---|---|---|---|
| ABC-20 | Sort orders by date | Low (1) | Medium priority +1 | Orders list page | `e2e/orders.spec.ts` |

(Smoke tickets ABC-12, ABC-15 are also in regression.)

### Skip (<n>)
| Key | Title | Reason |
|---|---|---|
| ABC-30 | Update README | Always skip: docs only |

### Untracked changes (<n> commits)
<same Regression table, keyed by short commit hash; leave out if none>

### Not in this build (<n>)
- ABC-40 — In Progress

### Questions
- <e.g. "ABC-22: no code found. Is it done in another repo?">
````

Leave out empty sections. Then ask — **Report**: This looks right (Recommended), Move a ticket, Retry with edits, Ask a follow-up.

- **Move a ticket** — ask which key and which bucket. Move it, and set its reason to "Moved by user". Then ask — **Save this as a team rule?**: No, this release only (Recommended), Yes — add to Always smoke / Always skip, Retry previous answer. On yes, add the rule to the config file it would belong in, with a dated **Change log** line.
- **Retry with edits** — ask what to change (Smaller smoke list, Change the score limits, Add an area to check, or **Other**). Change only that and show the report again.
- **Ask a follow-up** — answer, reading the code again if needed.

Repeat until the user picks **This looks right**.

## Step 7 — Ask where to save

### 7a — Check what is saved and connected

1. Read the **Save to** section of the loaded config.
2. Check which upload tools work: a Microsoft 365, SharePoint, Google Drive or Atlassian connector; `m365 status` (the CLI — command-line tool — for Microsoft 365); the Jira or Azure DevOps connection from Step 1.

### 7b — First run (Save to is empty)

Ask — **Where should I save this report?** (multi-select):

- **Markdown or Excel file in the repo** — in `docs/test-scope/`. (Recommended when no upload tool is connected.) A follow-up asks which.
- **SharePoint, OneDrive or Google Drive** — a team folder. A follow-up asks for the place.
- **Confluence page** — under a parent page you name. Only if an Atlassian connector is available.
- **Labels on the tickets** — adds `smoke-test` / `regression-test` labels (Jira) or tags (Azure DevOps). Only if the ticket system is connected.

Say the user can type another place in **Other**. Then ask the follow-ups, in one call, only for what was picked:

| Picked | Follow-up |
|---|---|
| File in the repo | **Which file type?** (multi-select): Excel (.xlsx) (Recommended), Markdown (.md). And the folder: `docs/test-scope/` (Recommended), or type another in **Other** |
| SharePoint | Site URL (e.g. `https://<company>.sharepoint.com/sites/<team>`), document library (default `Documents`), folder path (e.g. `QA/Releases`) |
| OneDrive | Folder path |
| Google Drive | Folder link or path, and shared drive name if any |
| Confluence | Space key and parent page title |
| Any shared folder | **File type for the shared copy**: Excel (.xlsx) (Recommended), Markdown (.md) |
| Labels | **Label names**: `smoke-test` and `regression-test` (Recommended), or type others in **Other** |

If `PROJECT_CONTEXT.md` has a `**Test cases share:**` line from `/ai-sam:write-qa-test-cases`, offer that location as the first suggestion.

Never ask for or save passwords, tokens or any other credential — only where the file goes.

**Save the answers** in the **Save to** section of the config file loaded in Step 2 (or written in Step 3), one line per place, plus a dated **Change log** line:

```markdown
## Save to
- Excel file — folder `docs/test-scope/`
- SharePoint — site `<site URL>` — library `Documents` — folder `QA/Releases` — format .xlsx
- Labels — smoke `smoke-test` — regression `regression-test`
```

Say in one line where the choice was saved.

### 7c — Later runs (Save to is set)

Ask — **Where should I save this report?**:

- **Same as last time** — list the saved places in one line, e.g. "Excel in `docs/test-scope/` + SharePoint `QA/Releases`". (Recommended)
- **Change where to save** — run 7b again and replace the **Save to** section.
- **Only this time: somewhere else** — run 7b's questions but don't save the answers.
- **Retry previous answer**.

### Before saving

- If a file with the same name exists, ask: Replace it (Recommended), Save as `<name>-2`, Retry previous answer.
- If a saved folder no longer exists or access is denied, say so and offer **Change where to save**.

## Step 8 — Save

Do each place the user picked. File name: `<release, sprint or range>-test-scope`, with spaces and `/` changed to `-` (e.g. `Release-2.4-test-scope.xlsx`).

### 8a — Get the repo folder ready

Only when a repo file was picked:

1. Create the folder if missing (`mkdir -p docs/test-scope/`).
2. Keep it out of git — the report is a working note, not code:
   - If `git check-ignore -q <folder>/x.md` says it is already ignored, do nothing.
   - Otherwise add the folder (e.g. `docs/test-scope/`) on its own line at the end of the repo root `.gitignore`, under `# Test scope reports from ai-sam smoke-regression-report`. Create `.gitignore` if missing. Don't change any other line.
   - Not in a git repo: skip.
3. Say in one line what was created and added.

### 8b — Markdown file

Write the Step 6 report, with the first line `# Smoke and regression report: <name>` and a `**Written:** <YYYY-MM-DD>` line under it. Keep unanswered questions as **Open questions**.

### 8c — Excel file

1. Use the `xlsx` skill if this session has one. Otherwise write a short Python script in a temporary folder outside the repo using `openpyxl`.
2. If `openpyxl` is missing, ask — **Excel needs the `openpyxl` Python library**: Install it with `pip install --user openpyxl` (Recommended), Save as CSV (a plain table file Excel opens) instead, Skip Excel, Retry previous answer.
3. Sheets: **Summary** (counts, source, rules, date), **Smoke**, **Regression**, **Skip**, **Gaps**, and **Not in this build** when it has rows.
4. Columns on Smoke and Regression: Key, Title, Type, Priority, Risk, Score, Reason, Areas to check, Existing tests, Gap, plus empty **Status** (Pass / Fail / Blocked dropdown), **Tester** and **Notes** columns for QA.
5. Bold header row, frozen top row, wrapped text, readable column widths, and the ticket key as a link to the ticket when the ticket system's URL is known.
6. Open the saved file once to check every ticket is in it, then delete the temporary script.

### 8d — Shared folder (SharePoint, OneDrive, Google Drive)

1. Build the file as in 8b or 8c. If no repo file was picked, build it in a temporary folder outside the repo and delete it after upload.
2. Upload, using the first that works:
   - A connector for that service in this session.
   - SharePoint or OneDrive: `m365 spo file add --webUrl <site URL> --folder "<library>/<folder path>" --path <file>`, if `m365 status` shows it is signed in.
   - Neither: say no upload tool is connected and which connector would make it work. Save the file in `docs/test-scope/` as in 8a, and give the exact place to upload it by hand.
3. Show the file name and full destination. Ask — **Upload to <service>?**: Upload (Recommended), Change the folder for this file only, Retry previous answer. Upload only on yes.
4. Give the link to the uploaded file. If the upload fails, show the error in one line, save the file in the repo folder instead, and say so.

### 8e — Confluence page

1. Build the page from the Step 6 report, titled `Smoke and regression report: <name>`.
2. If a page with that title exists under the parent, ask: Update it (Recommended), Create `<title> (2)`, Retry previous answer.
3. Show the title, space and parent. Ask — **Create this page?**: Create it (Recommended), Change the parent page, Retry previous answer. Create only on yes, then give the link.

### 8f — Labels on tickets

1. List what will change: each key and the label it gets. Smoke tickets get both labels. Skip tickets get none. Leave out tickets that already have the label.
2. Ask — **Add labels to <n> tickets?**: Add them (Recommended), Smoke labels only, Retry previous answer. Label only on yes.
3. Add, keeping every existing label or tag:
   - **Jira** — the connector's edit-issue tool, adding to the `labels` field.
   - **Azure DevOps** — read the current `System.Tags`, then `az boards work-item update --id <id> --fields "System.Tags=<existing>; <new tag>"`.
4. If one ticket fails, stop, show the error in one line, list what was labelled so far, and ask: Retry the rest (Recommended), Stop here, Retry previous answer.

## Step 9 — Report back

Show a short report in the chat:

````markdown
## Report saved: <release, sprint or range>

**Tickets:** <n> smoke, <n> regression, <n> skip — <n> gaps
**Saved to:**
- `docs/test-scope/<name>.xlsx`
- SharePoint — <link>
- Confluence — <link>
- Labels added to <n> tickets

**Next step:** `/ai-sam:write-feature-tests <key>` for each Gap, starting with <highest-risk key>.
````

Leave out lines that don't apply. Add a line if `.gitignore` or a `TEST_SCOPE_CONFIG` file was created or changed — those changes are uncommitted. Never commit or push anything.
