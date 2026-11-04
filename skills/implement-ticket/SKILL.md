---
name: implement-ticket
description: Build a Jira ticket (story, bug or task) in the code, end to end — get the ticket, reuse or make a plan with the tech-lead subagent, create a branch, write the code and a test for every acceptance criterion, run the project's test, lint and build commands, check each criterion is met, and show a plain-English summary of what changed. Uses the PROJECT_CONTEXT.md / SYSTEM_CONTEXT.md from create-project-context for versions and commands, and checks for a builder agent (from create-team, .claude/agents/ or ~/.claude/agents/) that owns each part, handing it the ticket, plan, branch and rules in one brief. Use when the user says "implement this ticket", "build ABC-123", "work on this ticket", "code this story", "fix this bug", or runs /ai-sam:implement-ticket <ticket key>. Edits code on a new branch only; never commits, pushes, opens a PR or changes Jira without asking first.
---

# Implement Ticket

Take a ticket and build it: plan, code, test, check. The user sees the plan before any code is written, and sees the result before anything is committed.

Where it fits:

1. `/ai-sam:analyze-ticket` — is the ticket ready, and how should we build it?
2. `/ai-sam:implement-ticket` — build it. (This skill.)

## Ground rules

- **Plan first, then code.** Never edit a file before the user approves the plan in Step 4.
- **Know where the code goes before writing it.** Step 5 picks the ticket's branch, a new branch, a worktree or the current branch. Edit `main`, `master` or `develop` only if the user picks it after a warning.
- **Ask before anything outward-facing.** No commit, push, pull request (PR) or Jira change unless the user picks it in Step 9. Never force-push or rewrite history.
- **Stay in scope.** Build only what the acceptance criteria ask for. List anything else you notice under **Follow-ups**, don't fix it.
- **Follow the project.** Use the versions in the manifest files, the commands in `PROJECT_CONTEXT.md`, and the patterns of the closest existing feature. Don't add or upgrade packages unless the plan says so and the user agreed.
- **Report test results honestly.** If a test, lint or build fails, say so and show the error. Never mark a criterion as met without evidence.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from the ticket, the plan and the code. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
  - Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change, re-ask it, and continue.
- **No personal or secret data.** Never open `.env` files, secrets, keys, or data files that may hold real people's records. Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If the ticket, logs or code contain any of this, stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into AI tools, and ask them to redact it. Test data uses made-up values only ("Test User", "Applicant A"). Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Get the ticket

- **A Jira key (e.g. `ABC-123`) and a Jira connector is available:** fetch the summary, type, description, acceptance criteria, linked issues and sub-tasks. Say in one line that you fetched it.
- **A key but no Jira connector:** ask with AskUserQuestion (the first question, so no **Retry previous answer**) — **Ticket details**: Paste the summary, description and acceptance criteria in Other (Recommended), Describe the change in a few lines in Other.
- **Pasted text:** use it as is.

Check the ticket for personal or secret data (see the ground rules) before going on.

**Epics and spikes:** don't build them. An epic is too big for one run — ask which of its stories to build. A spike's output is a decision, not code — offer `/ai-sam:analyze-ticket` instead.

## Step 2 — Quick readiness check

Check only what blocks building:

- There is at least one acceptance criterion, or for a bug, the expected behaviour.
- Each criterion can be checked with a yes or no.
- A bug has steps to reproduce, or enough detail to find the code.

If something blocks, ask — **Ticket gaps**: Answer the gaps now (Recommended), Run `/ai-sam:analyze-ticket` first, Build with my best reading and list my assumptions. Small gaps go under **Assumptions** in the final report.

## Step 3 — Load the project

1. Find the repo root with `git rev-parse --show-toplevel`.
2. Read, if present:
   - `PROJECT_CONTEXT.md` in the repo root or `docs/` — versions, commands, conventions.
   - `SYSTEM_CONTEXT.md` in the parent folder or at the path its **System** section names.
   - `CLAUDE.md` in the repo root, including any **Team** section (between `<!-- ai-sam:team:start -->` and `<!-- ai-sam:team:end -->`).
3. Note the install, test, lint and build commands. With no context file, take them from the manifest scripts, `Makefile` or README, and say in one line "No PROJECT_CONTEXT.md found — using commands from `<file>`."

## Step 4 — Get an approved plan

1. **Reuse a plan if one exists:**
   - a `/ai-sam:analyze-ticket` plan earlier in this conversation, or
   - a saved plan at `docs/design/<ticket key>.md`.

   Say in one line which plan you are using. Check its files still exist.
2. **No plan:** start the `tech-lead` subagent (`ai-sam:tech-lead`). Give it the full ticket, the answers from Step 2, the repo root(s) and the context file paths.
3. Show the plan in the chat. Add, at the top:
   - **Build by:** the agents you expect to use (see Step 6a), or Main session.
   - **Where:** the branch or worktree you expect to use in Step 5.
4. Ask — **Plan**: Build it (Recommended), Retry with edits, Ask a follow-up.
   - **Retry with edits** — ask what to change (Simpler approach, Fewer files, Different area, or **Other**). Send only that change to the subagent and show the result.
   - **Ask a follow-up** — answer, reading the code again if needed.

   Repeat until the user picks **Build it**.

## Step 5 — Pick where to work

Never stash, reset or discard the user's changes yourself.

**Already on the ticket's branch** — the current branch name (`git branch --show-current`) contains the ticket key, matched without case (`ABC-123` matches `feature/abc-123-upload`):

- Work on it. Don't ask.
- Say in one line: "You're on `<branch>`, the branch for <ticket key> — working here."
- Run `git log --oneline <base branch>..HEAD` and `git status` to see work already done. Build on it; don't redo it.

**Not on the ticket's branch** — ask with AskUserQuestion:

1. Find the suggested branch name: `<ticket key>-<2–4 word summary>`, lower case with hyphens, e.g. `abc-123-upload-documents`. If the repo has a naming pattern (in `PROJECT_CONTEXT.md` **Conventions** or `git branch -a`), follow it, e.g. `feature/ABC-123-upload-documents`.
2. Check for a local or remote branch that already has the ticket key (`git branch -a --list "*<key>*"`, without case).
3. Ask — **Where should I work?** Say in the question that the user can type a new branch name in **Other**. Options, in this order:
   - **Switch to `<existing branch>`** (Recommended) — only if step 2 found one. It replaces the next option.
   - **Create a branch `<suggested name>`** (Recommended) — from the current branch. Only when step 2 found nothing.
   - **Create a worktree** (a second folder with its own branch, so the current folder is left as it is) — at `../<repo folder>-<ticket key>`, on the existing ticket branch if found, else on a new branch `<suggested name>`.
   - **Work on the current branch `<branch>`** — on `main`, `master` or `develop`, add to the description: "Not recommended — changes go straight onto a shared branch."
   - **Retry previous answer.**
4. Do what was picked:

| Choice | Commands | If there are uncommitted changes |
|---|---|---|
| Switch to existing branch | `git switch <branch>` | Ask first — Stop so I can commit or stash them (Recommended), Carry them over, Retry previous answer. If git refuses, stop and tell the user. |
| Create a branch (or a name typed in **Other**) | `git switch -c <name>` | Same question as above. |
| Create a worktree | New branch: `git worktree add ../<repo folder>-<ticket key> -b <name>`. Existing branch: `git worktree add ../<repo folder>-<ticket key> <branch>` | Leave them where they are. Tell the user they stay in the current folder and are not in the worktree. |
| Current branch | none | Carry on; they become part of this ticket's work. Say so. |

**Worktree:** do every later step inside the worktree folder. Give team agents the worktree path as the repo root. Install dependencies there first with the install command from Step 3, since a new worktree has none.

**Several repos:** make the same choice in each repo the plan touches, and use the same branch name.

## Step 6 — Build

### 6a — Check for an agent that can build it

Look for builder agents (agents that can edit files) in this order:

1. The plan's **Who builds each part** table.
2. The **Team** section of the repo's `CLAUDE.md` (made by `/ai-sam:create-team`) — each agent and the folders it owns.
3. Agent files in `<repo>/.claude/agents/*.md` and `~/.claude/agents/*.md`. Read each one's `name`, `description` and `tools`.
4. Agents listed as available in this session.

Match each part of the plan to an agent:

- The agent owns the folders the part changes, or its description names that kind of work (e.g. "frontend", "API", "database", "fix bugs").
- Its `tools` include `Edit` or `Write`. Skip read-only agents such as `tech-lead`, reviewers and search agents.
- One agent per part. If two agents fit, pick the one whose folders match more closely.

Then:

- **Agents found for every part** — hand all the work to them (6b). Say in one line: "Handing this to `<agent>` (owns `<folder>`)."
- **Agents found for some parts** — hand those parts to the agents. Build the rest in the main session.
- **No agent fits** — build it all in the main session (6c). Say in one line: "No builder agent found for this repo — building in the main session."

### 6b — Hand the work to the agent

Each agent starts fresh. It sees only what you send, so give it everything it needs in one message:

````markdown
## Ticket <ticket key>: <summary>

**Type:** <Story / Bug / Task>

### What the ticket asks
<description, in short bullets>

### Acceptance criteria
1. <criterion>

### Answers and assumptions
- <answers from Step 2, and any assumption made>

### Your part of the plan
<the steps and files assigned to this agent, from the approved plan>

| File | New / update | What changes | Copy the pattern from |
|---|---|---|---|
| `<path>` | <update> | <one line> | `<existing file>` |

### Where to work
- **Repo root:** `<path, or the worktree path>`
- **Branch:** `<branch>` — already checked out. Don't switch branches.
- **Context files:** `<PROJECT_CONTEXT.md path>`, `<SYSTEM_CONTEXT.md path>` — read them first.

### Done by other agents
- `<agent>` changed `<file>`: <one line> — or "Nothing yet"

### Rules
- Build only your part. If another part needs a change, say what and stop.
- Write a test for each acceptance criterion in your part. For a bug, a test that fails without the fix.
- Run: `<test command>`, `<lint command>`, `<build command>`.
- Don't commit, push, add packages or touch files outside your part.
- Don't open `.env` files or secrets. Use made-up test data only.

### Send back
- Files changed, each with one line on what changed.
- Which acceptance criteria your part meets, and the test for each.
- Check results: pass, or the error in one line.
- Anything you couldn't do, and why.
````

- Fill the template from the approved plan, Step 2 and Step 3. Leave out sections with nothing in them. Never paste personal or secret data into it.
- Run agents in the plan's order (e.g. database, then backend, then frontend). Agents that don't depend on each other can run at the same time.
- After each agent returns, read its changes. If it missed a criterion or broke the plan, send it back once with what is wrong. If it fails again, finish that part in the main session and say so.

### 6c — Build in the main session

Used for parts no agent owns.

1. Follow the plan's **Files to update** and **New files**. If the code shows the plan is wrong, stop and ask — **Plan change**: the change you propose (Recommended), Keep to the plan, Retry previous answer.
2. Copy the pattern from the file the plan names under **Copy the pattern from**.
3. Write at least one test per acceptance criterion, in the project's test tool and folder layout. For a bug, write a test that fails without the fix.
4. Database changes need a migration and a rollback (a way to undo it). Existing data must keep working.
5. Don't touch files outside the plan, except to fix an import or a test the change breaks.

## Step 7 — Run the checks

Run, in this order, the commands from Step 3 that exist: test, lint, build.

- **All pass:** go on.
- **Something fails because of this change:** fix it and run again. Stop after 3 tries on the same failure and report it.
- **Something fails in code this change didn't touch:** it was likely failing before. List it under **Already failing** and don't fix it. Don't stash or reset to prove it.
- **A command needs something you don't have** (a database, a secret, a running service): don't work around it. Report it under **Not run** with the reason.

## Step 8 — Check the work

1. Read the full diff for the ticket: `git diff <base branch>...` (the branch it was made from, usually `main`), plus uncommitted changes. On an existing ticket branch this includes earlier work, so the criteria check covers all of it.
2. Check:
   - Every acceptance criterion has code **and** a test. Note the test name.
   - Every file in the diff is in the plan, or has a reason.
   - No secrets, personal data, debug logs or commented-out code were added.
   - No new packages unless the plan said so.
3. Fix small slips yourself. For anything bigger, go back to Step 6.

## Step 9 — Report and next step

Show the report in the chat:

````markdown
## Implemented: <ticket key> — <summary>

**Result:** Done / Done with gaps / Blocked — <one-line reason>
**Branch:** `<branch name>` <— in worktree `<path>`, if one was made>
**Branch state:** New this run | Existing ticket branch, <n> earlier commits
**Built by:** <agent name — which part>, Main session — <which part>

### Acceptance criteria
| Acceptance criterion | Met? | Where | Test |
|---|---|---|---|
| <short version> | Yes / No / Partly | `<file>` | `<test name>` |

### Files changed
| File | Change |
|---|---|
| `<path>` | <new / updated>: <one line> |

### Checks
| Check | Command | Result |
|---|---|---|
| Tests | `<command>` | Pass (42 tests) / Fail — <error in one line> / Not run — <reason> |
| Lint | `<command>` | <result> |
| Build | `<command>` | <result> |

### Assumptions
- <a choice made where the ticket was unclear>

### Already failing
- <test or check that failed before this change>

### Follow-ups
- <something noticed outside this ticket's scope>

### How to try it
1. <step, e.g. "Run `npm run dev` and open the Documents page">
````

Leave out empty sections, except **Acceptance criteria** and **Checks**.

Then ask — **Next step**: Done, leave it uncommitted (Recommended); Commit the changes; Retry with edits; Draft a PR description.

- **Commit the changes** — show the commit message first (`<ticket key>: <summary>`, then 2–4 bullets of what changed) and ask: Commit (Recommended), Change the message, Retry previous answer. Commit only the files in the report. Then ask whether to push; push only on yes.
- **Retry with edits** — ask what to change (a criterion, a file, the tests, or **Other**). Change only that, re-run Step 7 and Step 8, and show the report again.
- **Draft a PR description** — write it in the chat: summary, acceptance criteria table, checks, how to try it. Open the PR only if the user then asks, and only after the branch is pushed.

If a worktree was made, end with one line: remove it later with `git worktree remove <path>` once the branch is merged. Don't remove it yourself.

Never update the Jira ticket unless the user asks. If they do, show the comment or status change first and wait for a yes.
