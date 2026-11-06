# ai-sam

End to end workflow skills for any projects you work on, packaged as a Claude Code plugin.

## Skills

- `/ai-sam:create-project-context` — interviews you about a repo (goals, stack, dependency manifests, commands) and writes a `PROJECT_CONTEXT.md` that later coding sessions read before writing code. In a parent folder it writes a `SYSTEM_CONTEXT.md` that maps the repos and how they connect.
- `/ai-sam:create-jira-ticket` — asks the questions a story, bug, task, epic or spike needs, then writes the ticket in plain, point-wise English using the standard format for that type. Shows the finished ticket in the chat as Markdown, ready to paste into Jira or any rich text editor, with Retry and Retry with edits options before it is final. Follows the team's `JIRA_CONFIG.md` when one exists.
- `/ai-sam:setup-jira-config` — asks once how your team writes tickets (summary format such as `[FE]` tags or a custom pattern, checklist or Gherkin acceptance criteria, and custom templates that fully replace the standard Story, Bug, Task, Epic or Spike formats) and saves it in a `JIRA_CONFIG.md`. Save it for the team per repo (`JIRA_CONFIG.md` in the repo root, shareable by committing it), for yourself across all repos (`~/.claude/ai-sam/JIRA_CONFIG.md`), or for yourself in one repo (`JIRA_CONFIG.local.md` in the repo root, gitignored) to override the team's rules without changing them for anyone else.

- `/ai-sam:analyze-ticket` — acts as the project's senior tech lead on a ticket (a Jira key or pasted text). First checks it is ready to start: clear goal, testable acceptance criteria, gaps and questions to ask, with a Ready / Needs small fixes / Not ready verdict, checked against `JIRA_CONFIG.md` when one exists. Then reads `PROJECT_CONTEXT.md` / `SYSTEM_CONTEXT.md`, scans the code, and shows a plan: the approach, which files to update, which new files to create and where, which file delivers each acceptance criterion, tests, risks and open questions. Works from a code scan alone when no context file exists. Read-only.
- `/ai-sam:implement-ticket` — builds a ticket end to end. Reuses or makes a plan with `tech-lead`, and waits for your approval before writing code. If you're already on the ticket's branch it works there; otherwise it asks whether to create a branch, create a worktree or use the current branch. Then it writes the code and a test for every acceptance criterion, runs the project's test, lint and build commands, and shows a report of what changed. Checks for a builder agent that owns each part (from `create-team`, `.claude/agents/` or `~/.claude/agents/`) and hands it the ticket, plan, branch and rules in one brief; builds the rest itself. Never commits, pushes, opens a PR or changes Jira without asking.
- `/ai-sam:write-unit-tests [file]` — writes or updates unit tests for a whole existing file, frontend (component, hook, service) or backend (controller, service, repository, handler), or, with no file given, for the code changed on the current branch (against the base branch, plus uncommitted work). Checks for existing tests first: keeps the ones that still fit, updates outdated ones, removes ones for code that no longer exists, adds the missing cases, and creates a test file only when none exists. Detects the test framework, mocking library and file layout from the repo (Jest, Vitest, xUnit, NUnit, pytest, JUnit and more) and copies the closest existing test. Shows a test plan (main path, edge cases, errors, each branch) for approval, then writes the tests, runs them and reports coverage for the changed files. If a test finds a real bug, it shows the bug and a proposed fix and edits source code only on a yes. Hands the work to a QA agent from `create-team` when one exists. Never commits, pushes or adds packages without asking.
- `/ai-sam:write-feature-tests [ticket, feature or endpoint]` — writes or updates feature tests that check a whole feature works end to end: browser E2E tests for the frontend (Playwright, Cypress and more) and API or integration tests for the backend (WebApplicationFactory, Testcontainers, Supertest, TestClient, Spring Boot Test and more). Works from a Jira ticket's acceptance criteria, a named screen or endpoint, or, with nothing given, the changes on the current branch. Checks existing feature tests first and reuses the repo's page objects, login and test data setup. Shows a Given / When / Then plan mapped to each acceptance criterion for approval, writes the tests, asks before starting any app or container, runs them and reports which acceptance criteria pass. Uses `.feature` files only if the repo already uses Gherkin. Never runs against production, and never commits, pushes or adds packages without asking.
- `/ai-sam:write-test-cases [ticket, feature or endpoint]` — writes manual test cases (step-by-step checks a tester follows by hand) in three groups: positive (the happy path works), negative (bad input, wrong role and failures are blocked with a clear message) and edge cases (limits, empty values, boundaries, timing), only where they apply. Asks whether to add accessibility, security, browser and device, or performance cases. Works from a Jira or Azure DevOps ticket's acceptance criteria, a named screen or endpoint, or, with nothing given, the changes on the current branch, and reads the code for the real required fields, limits, roles and error messages. Shows the cases with a coverage table per acceptance criterion for approval, then asks how to save them: a Markdown file, an Excel file (one sheet per group, with Status and Notes columns for the tester) — both in `docs/test-cases/`, which it creates if missing and adds to `.gitignore` — or a comment on the ticket when Jira, Azure DevOps, GitHub or GitLab is connected. For Azure DevOps (Azure Test Plans) or Jira with Xray, it asks whether to comment, create one linked test case item per case, or both. It can also upload to a shared location (SharePoint, OneDrive, Google Drive or Confluence): it asks for the site and folder once, saves them as a **Test cases share** line in `PROJECT_CONTEXT.md`, and offers that location on every later run. Writes no test code, and never posts to a ticket or creates items without showing them first.
- `/ai-sam:smoke-regression-report [release, sprint or branch range]` — sorts every ticket in a release into Smoke (a short check that the build works), Regression (a deeper check that existing features still work; includes smoke) or Skip (docs, test-only or build-file changes). Takes tickets from a Jira fix version or Azure DevOps iteration, the active sprint, or the ticket keys in commits between two branches or tags. Scores each ticket's risk from its code changes: critical area, shared code, database or login changes, priority, change size, recent bug fixes and missing tests. Applies the team's rules (critical areas, always-smoke and always-skip rules, score limits, smoke list limit), set up on the first run and saved in `TEST_SCOPE_CONFIG.md` (team, `.local` for one person in one repo, or `~/.claude/ai-sam/` for one person everywhere). For each ticket shows the reason, the screens and endpoints to check, and the tests that already cover it, with gaps flagged. Shows the report for approval and lets you move a ticket or save the move as a team rule. Then asks where to save: Markdown or Excel in `docs/test-scope/` (added to `.gitignore`), SharePoint, OneDrive, Google Drive, a Confluence page, or smoke / regression labels on the tickets. The first answer is saved in `TEST_SCOPE_CONFIG.md` and offered first on later runs. Never labels, uploads or posts without showing it first.
- `/ai-sam:schedule-tests [run | list | remove]` — sets up an automatic agent that runs all of a repo's checks at a set time, like a cron job: lint, type-check, build, unit tests and feature (E2E) tests. Asks each time where to run it: a scheduled CI pipeline (GitHub Actions, Azure DevOps or GitLab), your own machine (launchd on macOS, cron on Linux, Task Scheduler on Windows, running Claude Code headless), or a Claude Code cloud routine. Then asks when (days, time, time zone) and which checks to include. Runs on the latest base branch in a separate worktree, so your open work is never touched. Saves a dated pass/fail report after every run, listing each failing test with its file and first error line, in `~/.claude/ai-sam/scheduled-tests/<repo>/reports/` (as a build artifact for CI, or in the run's transcript for a cloud routine). `run` runs everything now, and `list` / `remove` show, change or delete schedules. Never runs against production, never stores secret values, and never commits, pushes or creates a pipeline without asking.
- `/ai-sam:review-pr [PR number, link or branch]` — reviews code changes before they merge: by default the current branch against its base branch plus uncommitted work, or a named PR or branch. Reads every changed line for bugs, edge cases, security, performance, conventions and test gaps, and checks the acceptance criteria when the branch has a Jira key, plus the team rules in the ticket type's `JIRA_CONFIG.md` template. Team agents from `create-team` each review the files in their own layer. Checks the change doesn't break other features: `tech-lead` finds every caller, API consumer, other repo, database user and config that depends on the changed code, and the skill runs the project's type-check, lint, build and test commands (in a temporary worktree for another branch, after asking). Works with GitHub, Azure DevOps and GitLab PRs; asks for the PR host once and saves it in `PROJECT_CONTEXT.md`. Shows a Ready to merge / Merge after fixes / Not ready verdict with each finding ranked Blocker, Should fix or Nice to have, with file, line and a fix. Saves each review in `~/.claude/ai-sam/reviews/`, so a re-run on the same branch marks earlier findings Fixed or Still open. Read-only by default; fixes code or posts PR comments only after you approve the exact change or text.
- `/ai-sam:create-team` — scans the repo you're in and suggests one builder subagent per layer (Frontend, Backend, Database, API, DevOps, QA test automation and more), each backed by the files that justify it. Writes the ones you pick to `.claude/agents/` (shared with the team when committed) or `~/.claude/agents/` (only you), and lists them in a **Team** section of the repo's `CLAUDE.md`. Each agent knows the folders it owns, the patterns to copy, the commands to run and what it must not touch. `tech-lead` then names which agent builds each part of a plan.

All skills write in short, point-wise, plain English, so a junior developer or a manager can follow the results.

## Subagents

- `tech-lead` (`ai-sam:tech-lead`) — the senior tech lead behind `analyze-ticket`, `implement-ticket` and `review-pr`. It learns the project from the context files and the business rules from the code, then works out which files change. For `review-pr` it runs an impact review: who depends on the changed code and what could break. When the repo has a team from `create-team`, it says which agent builds each part. Other skills, or you directly, can hand it a ticket or an architecture question. Read-only.

### How Jira configs combine

Settings are merged section by section (summary format, acceptance criteria style, and each ticket type's template). For each section the highest file that sets it wins:

1. `JIRA_CONFIG.local.md` — your overrides for this repo
2. `JIRA_CONFIG.md` — the team's rules for this repo
3. `~/.claude/ai-sam/JIRA_CONFIG.md` — your defaults everywhere
4. The built-in standard format

So a local file with only `Acceptance criteria style: Gherkin` gives you Gherkin while you keep the team's summary tags and templates, and future team changes to those still apply to you.

### Project context for multi-repo projects

For a project made of several repos (backend + frontend, microservices, micro-frontends, or a monorepo):

1. Run `/ai-sam:create-project-context` in **each repo**. Each one gets its own `PROJECT_CONTEXT.md` with its stack, versions and manifests.
2. Run it again in the **parent folder** (or monorepo root). It writes a `SYSTEM_CONTEXT.md` that only references each repo's context file and records how the repos connect.
3. Re-run it in the parent whenever a repo is added or removed, or a repo's context changes.

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


## Installing

```bash
claude plugin marketplace add /path/to/ai-sam
claude plugin install ai-sam@ai-sam
```

After changing the plugin, run `claude plugin update ai-sam` and restart Claude Code.
