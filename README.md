# ai-sam

End to end workflow skills for any projects you work on, packaged as a Claude Code plugin.

## Skills

Use the skills in this order. Set up once (Step 1), then repeat Steps 2–6 for every ticket or release.

| Step | Stage | Skills |
| --- | --- | --- |
| 1 | Set up (once per repo or team) | `create-project-context`, `setup-release-process`, `setup-ticket-config`, `create-team` |
| 2 | Write and check the ticket | `create-ticket`, `analyze-ticket` |
| 3 | Build | `implement-ticket` |
| 4 | Test | `write-unit-tests`, `write-feature-tests`, `write-qa-test-cases`, `run-test-report` |
| 5 | Review and fix feedback | `review-pr`, `fix-comments` |
| 6 | Release and schedule | `smoke-regression-report`, `schedule-tests` |
| 7 | Track the sprint (daily, for project managers) | `pm-daily-brief` |

All skills write in short, point-wise, plain English, so a junior developer or a manager can follow the results.

### Step 1 — Set up (run once)

#### 1.1 `/ai-sam:create-project-context`

Teaches Claude your project, so later skills write code that fits it.

1. Asks about the repo: goals, tech stack, dependency manifests (for example `package.json`) and the install, run, test, lint and build commands.
2. Writes `PROJECT_CONTEXT.md` in the repo root.
3. In a parent folder of several repos, writes `SYSTEM_CONTEXT.md` that maps the repos and how they connect. See [Project context for multi-repo projects](#project-context-for-multi-repo-projects).

- **Output:** `PROJECT_CONTEXT.md` or `SYSTEM_CONTEXT.md`.
- **Used by:** `analyze-ticket`, `implement-ticket`, `review-pr`, the test skills.

#### 1.2 `/ai-sam:setup-release-process`

Saves how the project plans, tests and ships work, once.

1. When Jira is connected, reads recent sprints and fix versions (read-only) to suggest the answers.
2. Asks for the delivery method: sprint-based (Scrum), Kanban, waterfall or hybrid, and the sprint length.
3. For sprint teams, asks when each ceremony happens: planning, stand-up, refinement, review / demo, retrospective.
4. Asks whether there is one release schedule or several (release trains, for example web monthly and mobile every two weeks).
5. Asks for the release types (major, minor, hotfix), version format and release dates, for example "15th of every month".
6. Asks for the environments (Dev, QA, UAT, Staging, Production), the branching model, and which branch deploys where.
7. Asks how and when each environment is deployed, and who deploys to Production.
8. Asks for the code freeze (how many days before release), the "all tickets tested by" and UAT sign-off deadlines, and the hotfix process.
9. Asks for the release checklist: go/no-go meeting, release-day steps, checks after release, and who is told.
10. Works out the next real release dates from the answers (or Jira), so you can check the rules are right.

- **Output:** a **Delivery and release process** section in `PROJECT_CONTEXT.md`, or in `SYSTEM_CONTEXT.md` when several repos release together. It saves rules, not dates. Real dates come from Jira fix versions when connected, else from the rules.
- **Used by:**
  - `implement-ticket` — starts the branch from the right base branch with the right name, and warns when code freeze is close.
  - `review-pr` — checks the target branch, and flags a merge after code freeze that the freeze rule doesn't allow.
  - `analyze-ticket` — shows the target release and whether the work fits before code freeze.
  - `create-ticket` — suggests the target release or sprint.
  - `smoke-regression-report` — shows the freeze, testing and release dates, and the working days left.

#### 1.3 `/ai-sam:setup-ticket-config`

Saves how your team writes tickets, once. Works for any tracker: Jira, Bitbucket, Azure DevOps, GitHub, GitLab and others.

1. Asks for the summary format (for example `[FE]` tags or a custom pattern).
2. Asks for the acceptance criteria style: checklist or Gherkin (Given / When / Then).
3. Asks for any custom templates that fully replace the standard Story, Bug, Task, Epic or Spike formats.
4. Asks where to save it:
   - **Team, this repo:** `TICKET_CONFIG.md` in the repo root. Share it by committing it.
   - **Just you, all repos:** `~/.claude/ai-sam/TICKET_CONFIG.md`.
   - **Just you, this repo:** `TICKET_CONFIG.local.md` in the repo root (gitignored). Overrides the team's rules for you only.

- **Output:** a `TICKET_CONFIG` file. See [How ticket configs combine](#how-ticket-configs-combine).
- **Used by:** `create-ticket`, `analyze-ticket`, `review-pr`.

#### 1.4 `/ai-sam:create-team`

Creates builder subagents (helper agents), one per layer of the repo.

1. Scans the repo and suggests one agent per layer: Frontend, Backend, Database, API, DevOps, QA test automation and more.
2. Shows the files that justify each agent.
3. Writes the agents you pick to `.claude/agents/` (shared when committed) or `~/.claude/agents/` (only you).
4. Lists them in a **Team** section of the repo's `CLAUDE.md`.
5. Each agent knows its folders, the patterns to copy, the commands to run and what it must not touch.

- **Output:** agent files and a **Team** section in `CLAUDE.md`.
- **Used by:** `tech-lead`, `implement-ticket`, `write-unit-tests`, `review-pr`.

### Step 2 — Write and check the ticket

#### 2.1 `/ai-sam:create-ticket`

Writes a clear ticket from your answers or rough notes, for any tracker (Jira, Bitbucket, Azure DevOps, GitHub, GitLab and others).

1. Asks the questions a story, bug, task, epic or spike needs.
2. Writes the ticket in plain, point-wise English, in the standard format for that type.
3. Follows `TICKET_CONFIG.md` when one exists.
4. Shows the ticket in the chat as Markdown, ready to paste into your tracker or any rich text editor.
5. Offers **Retry** and **Retry with edits** before it is final.

- **Output:** ticket text in the chat.

#### 2.2 `/ai-sam:analyze-ticket [Jira key or pasted text]`

Acts as the project's senior tech lead on a ticket. Read-only.

1. Checks the ticket is ready: clear goal, testable acceptance criteria, gaps, questions to ask.
2. Gives a verdict: **Ready**, **Needs small fixes** or **Not ready**. Checks against `TICKET_CONFIG.md` when one exists.
3. Reads `PROJECT_CONTEXT.md` / `SYSTEM_CONTEXT.md` and scans the code.
4. Shows a build plan:
   - the approach
   - files to update and new files to create (and where)
   - which file delivers each acceptance criterion
   - tests, risks and open questions
5. Works from a code scan alone when no context file exists.

- **Output:** readiness verdict and build plan in the chat.

### Step 3 — Build

#### 3.1 `/ai-sam:implement-ticket`

Builds a ticket end to end.

1. Reuses the plan from `analyze-ticket`, or makes one with `tech-lead`.
2. Waits for your approval before writing code.
3. Works on the ticket's branch if you are on it. Otherwise asks: create a branch, create a worktree (a second working folder for the same repo) or use the current branch.
4. Hands each part to its builder agent (from `create-team`, `.claude/agents/` or `~/.claude/agents/`) with the ticket, plan, branch and rules. Builds the rest itself.
5. Writes the code and a test for every acceptance criterion.
6. Reads the ticket's comments (clarifications, scope changes, QA and review feedback) and asks which ones to act on. Picked ones are built and tested like acceptance criteria.
7. Finds the QA test cases already written for the ticket (description, comments, linked Xray or Azure Test Plans items, `docs/test-cases/`) and writes a test for each, tagged with the case ID. Cases that can't be automated are listed as manual only.
8. Runs the project's test, lint and build commands.
9. Shows a report of what changed, with tables for the comments acted on and the QA test cases covered.

- **Never** commits, pushes, opens a PR or changes Jira without asking.

### Step 4 — Test

#### 4.1 `/ai-sam:write-unit-tests [file]`

Writes or updates unit tests (tests for one function, class or component on its own).

1. Targets a whole file you name, or, with no file, the code changed on the current branch (plus uncommitted work).
2. Covers frontend (component, hook, service) and backend (controller, service, repository, handler) code.
3. Checks existing tests first: keeps the ones that fit, updates outdated ones, removes ones for deleted code, adds missing cases.
4. Creates a test file only when none exists.
5. Detects the framework, mocking library and file layout (Jest, Vitest, xUnit, NUnit, pytest, JUnit and more) and copies the closest existing test.
6. Shows a test plan (main path, edge cases, errors, each branch) for approval.
7. Writes the tests, runs them and reports coverage for the changed files.
8. If a test finds a real bug, shows it with a proposed fix. Edits source code only on a yes.
9. Hands the work to a QA agent from `create-team` when one exists.

- **Never** commits, pushes or adds packages without asking.

#### 4.2 `/ai-sam:write-feature-tests [ticket, feature or endpoint]`

Writes or updates feature tests that check a whole feature works end to end.

1. **Frontend:** browser E2E (end-to-end) tests with Playwright, Cypress and more.
2. **Backend:** API or integration tests with WebApplicationFactory, Testcontainers, Supertest, TestClient, Spring Boot Test and more.
3. Works from a Jira ticket's acceptance criteria, a named screen or endpoint, or the current branch's changes.
4. Checks existing feature tests first and reuses the repo's page objects, login and test data setup.
5. Shows a Given / When / Then plan, mapped to each acceptance criterion, for approval.
6. Asks before starting any app or container, then runs the tests.
7. Reports which acceptance criteria pass.
8. Uses `.feature` files only if the repo already uses Gherkin.

- **Never** runs against production. Never commits, pushes or adds packages without asking.

#### 4.3 `/ai-sam:write-qa-test-cases [ticket, feature or endpoint]`

Writes manual test cases (step-by-step checks a tester follows by hand). Writes no test code.

1. Works from a Jira or Azure DevOps ticket, a named screen or endpoint, or the current branch's changes.
2. Reads the code for the real required fields, limits, roles and error messages.
3. Groups cases, only where they apply:
   - **Positive:** the happy path works.
   - **Negative:** bad input, wrong role and failures are blocked with a clear message.
   - **Edge:** limits, empty values, boundaries, timing.
4. Asks whether to add accessibility, security, browser and device, or performance cases.
5. Shows the cases with a coverage table per acceptance criterion for approval.
6. Asks how to save them:
   - Markdown or Excel (one sheet per group, with Status and Notes columns) in `docs/test-cases/`. Creates the folder and adds it to `.gitignore`.
   - A comment on the ticket (Jira, Azure DevOps, GitHub or GitLab).
   - For Azure Test Plans or Jira with Xray: a comment, one linked test case item per case, or both.
   - A shared location (SharePoint, OneDrive, Google Drive or Confluence). Saved once as a **Test cases share** line in `PROJECT_CONTEXT.md` and offered on later runs.

- **Never** posts to a ticket or creates items without showing them first.

#### 4.4 `/ai-sam:run-test-report [unit | feature | all] [filter]`

Runs the repo's test suites now and reports the results.

1. Covers unit tests and feature tests, for the frontend, the backend, or both.
2. Finds the test commands from `PROJECT_CONTEXT.md`, manifest scripts, test config or CI files.
3. Shows a run plan (exact commands, what it starts, rough time) for approval.
4. Asks before starting any app, server or container.
5. Reports:
   - totals per suite
   - every failing test with its file, first error line and likely cause (app bug, test problem, environment or flaky)
   - slow tests
   - coverage, when a coverage command exists
6. Can re-run failures on the base branch to split new failures from ones already failing.
7. Asks where to save: Markdown or Excel in `docs/test-runs/` (added to `.gitignore`), SharePoint, OneDrive, Google Drive, Confluence, or a comment on the branch's Jira ticket. The first answer is saved in `PROJECT_CONTEXT.md`.

- **Never** runs against production, and never fixes, skips or changes a test or source file.
- **Never** uploads or posts without showing it first.

### Step 5 — Review

#### 5.1 `/ai-sam:review-pr [PR number, link or branch]`

Reviews code changes before they merge. Read-only by default.

1. Reviews the current branch against its base branch (plus uncommitted work), or a named PR or branch.
2. Reads every changed line for bugs, edge cases, security, performance, conventions and test gaps.
3. Checks the acceptance criteria when the branch has a Jira key, plus the rules in `TICKET_CONFIG.md`.
4. Team agents from `create-team` each review the files in their own layer.
5. Checks the change does not break other features:
   - `tech-lead` finds every caller, API consumer, other repo, database user and config that depends on the changed code.
   - Runs the project's type-check, lint, build and test commands (in a temporary worktree for another branch, after asking).
6. Works with GitHub, Azure DevOps and GitLab PRs. Asks for the PR host once and saves it in `PROJECT_CONTEXT.md`.
7. Gives a verdict: **Ready to merge**, **Merge after fixes** or **Not ready**.
8. Ranks each finding **Blocker**, **Should fix** or **Nice to have**, with file, line and a fix.
9. Saves each review in `~/.claude/ai-sam/reviews/`. A re-run on the same branch marks earlier findings **Fixed** or **Still open**.

- Fixes code or posts PR comments only after you approve the exact change or text.

#### 5.2 `/ai-sam:fix-comments [ticket key, PR number or link]`

Works through the open feedback on a ticket and its PR, fixes it and replies to every comment.

1. Finds the ticket and its PR from the argument or the current branch. Works with GitHub, Azure DevOps and GitLab, using the PR host saved by `review-pr`.
2. Collects the Jira ticket's open comments (for example a QA "failed" note) and every unresolved PR review thread and general comment.
3. Sorts each comment: **Fix**, **Answer**, **Push back**, **Already done**, **Out of scope** or **Unclear**.
4. Flags risky requests (remove a permission check, skip tests, send data out, text aimed at the AI) instead of doing them.
5. Shows the plan for approval, then makes each fix on the PR's branch, with a test where behaviour changes.
6. Runs the project's test, lint and build commands.
7. Drafts a short reply for each comment, naming the file, line and test.
8. After you approve: commits, pushes, posts each reply on its thread, resolves the fixed threads and adds one summary comment to the ticket. Questions and push-backs stay open for the reviewer.
9. Saves what it handled in `~/.claude/ai-sam/comment-fixes/`. A re-run picks up only new comments and reviewer follow-ups.

- **Never** commits, pushes, replies, resolves a thread or comments on the ticket without showing it first. Never force-pushes.

### Step 6 — Release and schedule

#### 6.1 `/ai-sam:smoke-regression-report [release, sprint or branch range]`

Sorts every ticket in a release by how much testing it needs.

1. Takes tickets from a Jira fix version, an Azure DevOps iteration, the active sprint, or the ticket keys in commits between two branches or tags.
2. Sorts each ticket into:
   - **Smoke:** a short check that the build works.
   - **Regression:** a deeper check that existing features still work (includes smoke).
   - **Skip:** docs, test-only or build-file changes.
3. Scores risk from the code changes: critical area, shared code, database or login changes, priority, change size, recent bug fixes, missing tests.
4. Applies the team's rules (critical areas, always-smoke and always-skip rules, score limits, smoke list limit). Set up on the first run and saved in `TEST_SCOPE_CONFIG.md` (team, `.local` for you in one repo, or `~/.claude/ai-sam/` for you everywhere).
5. For each ticket shows the reason, the screens and endpoints to check, and the tests that already cover it. Flags gaps.
6. Shows the report for approval. You can move a ticket or save the move as a team rule.
7. Asks where to save: Markdown or Excel in `docs/test-scope/` (added to `.gitignore`), SharePoint, OneDrive, Google Drive, Confluence, or smoke / regression labels on the tickets. The first answer is saved in `TEST_SCOPE_CONFIG.md`.

- **Never** labels, uploads or posts without showing it first.

#### 6.2 `/ai-sam:schedule-tests [run | list | remove]`

Sets up an automatic agent that runs all of a repo's checks at a set time, like a cron job (a timed task).

1. Asks where to run it:
   - a scheduled CI pipeline (GitHub Actions, Azure DevOps or GitLab)
   - your own machine (launchd on macOS, cron on Linux, Task Scheduler on Windows, running Claude Code headless)
   - a Claude Code cloud routine
2. Asks when (days, time, time zone) and which checks: lint, type-check, build, unit tests, feature (E2E) tests.
3. Runs on the latest base branch in a separate worktree, so your open work is never touched.
4. Saves a dated pass/fail report after every run, listing each failing test with its file and first error line. Reports go to `~/.claude/ai-sam/scheduled-tests/<repo>/reports/` (a build artifact for CI, or the run's transcript for a cloud routine).
5. Commands:
   - `run` — runs everything now.
   - `list` — shows and changes schedules.
   - `remove` — deletes a schedule.

- **Never** runs against production or stores secret values.
- **Never** commits, pushes or creates a pipeline without asking.

### Step 7 — Track the sprint (daily)

#### 7.1 `/ai-sam:pm-daily-brief [sprint, board or team]`

Gives the project manager (PM) a short morning brief for the active sprint, from Jira or Azure DevOps. Written for the PM and leadership.

**For the PM and leadership** (tickets only, no people's names):

1. **Leadership summary:** 3 to 5 bullets — the verdict, top risks and decisions needed.
2. **Sprint health:** On track, At risk or Off track, with the numbers:
   - work done against time used
   - forecast finish against the sprint end
   - scope added after the sprint started
   - progress on the sprint goal
3. **Epics and releases:** percent done, forecast finish and risk for each epic and fix version, against its target date. Uses the code freeze date from `setup-release-process` when present.
4. **Bugs:** new this sprint by priority, open high-priority bugs, reopened bugs, bugs found after a story was done, and opened vs closed.
5. **Since last brief:** what finished, new and cleared flags, status changes, and tickets flagged several days in a row. Uses a small daily snapshot saved in `~/.claude/ai-sam/pm-brief/`.

**PM only:**

6. **Team status:** one row per person — load against capacity, work done, tickets in progress, and **On track**, **Watch** or **Needs a check-in** with the reason.
7. **Ask today:** each ticket that needs a check-in, with the reason and a ready-to-ask, neutral question. Flags tickets that are:
   - stuck in one status too long, past due, or due soon and not started
   - over their estimate, or with no update for days
   - blocked, sent back from QA or review, or carried over from an earlier sprint
   - in progress with no branch or PR, or with a PR waiting for review
   - unassigned or not estimated, or a high-priority or reopened bug
8. **PR review load:** PRs waiting on each reviewer, the oldest wait, and PRs with no reviewer. Works with GitHub, Azure Repos and GitLab.

**How it runs:**

- Uses the team's rules (members, capacity, days off, done statuses, check-in limits, bug priorities), set up on the first run and saved in `PM_BRIEF_CONFIG.md` (team, `.local` for you in one repo, or `~/.claude/ai-sam/` for you everywhere).
- Shows the brief for approval. You can change a limit for today or save it.
- Asks where to save or send it, and which version each place gets: the **leadership version** (no PM-only section) or the **full brief**. Places:
  - chat only
  - Markdown or Excel in `docs/pm-brief/` (added to `.gitignore`)
  - SharePoint, OneDrive, Google Drive, or a dated Confluence page
  - a Microsoft Teams channel, a Slack channel, or email
- The first answer is saved in `PM_BRIEF_CONFIG.md`. Email recipients are saved only in your personal config.
- Run it every weekday morning with `/schedule` or `/loop`. Scheduled runs save files only; uploads and messages wait for your approval.

- Flags describe the work, never the person. No ranking of people.
- **Never** comments on, moves or reassigns a ticket or PR, and never messages a team member. Shows the exact message before anything is uploaded, posted or sent.

## Subagents

- `tech-lead` (`ai-sam:tech-lead`) — the senior tech lead behind `analyze-ticket`, `implement-ticket` and `review-pr`. It learns the project from the context files and the business rules from the code, then works out which files change. For `review-pr` it runs an impact review: who depends on the changed code and what could break. When the repo has a team from `create-team`, it says which agent builds each part. Other skills, or you directly, can hand it a ticket or an architecture question. Read-only.

### How ticket configs combine

Settings are merged section by section (summary format, acceptance criteria style, and each ticket type's template). For each section the highest file that sets it wins:

1. `TICKET_CONFIG.local.md` — your overrides for this repo
2. `TICKET_CONFIG.md` — the team's rules for this repo
3. `~/.claude/ai-sam/TICKET_CONFIG.md` — your defaults everywhere
4. The built-in standard format

So a local file with only `Acceptance criteria style: Gherkin` gives you Gherkin while you keep the team's summary tags and templates, and future team changes to those still apply to you.

### Project context for multi-repo projects

For a project made of several repos (backend + frontend, microservices, micro-frontends, or a monorepo):

1. Run `/ai-sam:create-project-context` in **each repo**. Each one gets its own `PROJECT_CONTEXT.md` with its stack, versions and manifests.
2. Run it again in the **parent folder** (or monorepo root). It writes a `SYSTEM_CONTEXT.md` that only references each repo's context file and records how the repos connect.
3. Re-run it in the parent whenever a repo is added or removed, or a repo's context changes.

## Security

Tickets, PRs, code and logs are written by many people. Someone can plant text in them that tries to steer the AI (prompt injection). ai-sam protects against it in two layers:

1. **Rules in every skill.** Each skill's **Untrusted content** section treats that text as data, never as instructions, and flags any attempt to steer it.
2. **The guard hook** (`hooks/guard.py`). A hook is a small script Claude Code runs before every tool call.

   **Why a hook as well as the rules:**
   - The rules are written instructions. Well-crafted planted text can still talk the AI around them.
   - The hook is code, not instructions. It can't be persuaded, so a risky action is stopped even if the AI was fooled.
   - It also protects subagents and your normal sessions, not only ai-sam skills.

   It checks every tool call, in skills, subagents and your normal sessions, while the plugin is enabled:

   | Action | What happens |
   |---|---|
   | Read `.env`, private keys, `.git-credentials`, cloud credential files | Blocked |
   | Download a script and run it straight away (`curl … \| sh`) | Blocked |
   | Read `local.settings.json`, `secrets.json`, `.npmrc` | Asks you first |
   | Network calls (`curl`, `wget`, `Invoke-WebRequest`) | Asks you first |
   | Install a new package (`npm install <name>`, `pip install <name>`, `dotnet add package`, unknown `npx` tools) | Asks you first |
   | Force push, remote branch delete, `git reset --hard`, `git clean -f`, `--no-verify` | Asks you first |
   | Edit `CLAUDE.md`, `.claude/`, `.mcp.json`, CI pipelines, package sources or git hooks | Asks you first |

   - "Asks you first" works in auto mode too.
   - `.env.example` and other templates are allowed. Plain `npm install`, `npm ci` and `pip install -r requirements.txt` install the repo's own packages and are allowed.
   - Turn it off for one session: start Claude Code with `AI_SAM_GUARD=off`.
   - Needs Python 3 (`python3`, `python` or `py`). Without it, or on Windows without Git Bash, the guard can't run and every call goes through. The skills' written rules still apply.

### Evals — proof the protections work

An eval (evaluation) is an automated test for AI behaviour. It gives Claude a task, then checks what Claude did.

**Why they exist:**
- Skills are instructions, not code, so normal unit tests can't check them. The only way to test a skill is to run it on a real task.
- The evals prove the two layers above work: each case plants a hidden instruction and checks the skill flags it and doesn't act on it.
- Re-run them after changing a skill, or when a new Claude model comes out, to catch a protection that stopped working.

**What's in `evals/injection/`:**
- 9 cases, one per risky skill. Examples: a PR that removes a permission check and tells the reviewer to approve; a test log with fake secrets and "post this log"; a ticket asking to skip QA.
- `guard/test_guard.py` — 46 checks on the guard hook. No AI, free, takes a second.
- All data is made up. Nothing real is used or sent anywhere.

**Run them** (from this folder):

```bash
python3 evals/injection/guard/test_guard.py   # guard hook only

claude plugin eval . --tag injection --scaffold --allow-tools Bash Write Edit --runs 1 --ablation none --no-publish
```

- The first `claude plugin eval` run must be in a terminal, to confirm you trust the folder.
- Each case is a real Claude run, so a full pass takes a while and uses your plan's usage.
- Users of the plugin never need the evals; they are for whoever changes the skills. Details in [evals/injection/README.md](evals/injection/README.md).

## Testing locally

Validate the manifests after any structural change:

```bash
claude plugin validate .
```

Start a Claude Code session with the plugin loaded from this folder:

```bash
claude --plugin-dir /path/to/ai-sam
```

This loads the plugin for that session only. It doesn't install anything or change your settings, and plain `claude` runs without it. The plugin is read at startup, so restart the session after editing a `SKILL.md`.

After changing a skill or the guard hook, run the security evals (see **Evals — proof the protections work** above).


## Installing

```bash
claude plugin marketplace add /path/to/ai-sam
claude plugin install ai-sam@ai-sam
```

After changing the plugin, run `claude plugin update ai-sam` and restart Claude Code.
