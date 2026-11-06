---
name: review-pr
description: Review a set of code changes before they merge, as a senior reviewer — by default the current branch's changes (the diff against the base branch plus uncommitted work), or a pull request (PR) number, PR link or branch the user names. Reads every changed line for bugs, missing edge cases, security, performance, project conventions and test gaps, and checks the changes don't break other features — the tech-lead subagent finds every caller, API consumer, other repo, shared component, database user and config that depends on the changed code, and the skill runs the project's test, lint and build commands to prove it. Team agents from create-team each review the changed files in their own layer. Checks the ticket's acceptance criteria when the branch name has a Jira key, and the team rules in the ticket type's JIRA_CONFIG.md template from setup-jira-config. Works with GitHub, Azure DevOps and GitLab PRs; asks for the PR host once and saves it in PROJECT_CONTEXT.md. Shows a plain-English report with a Ready to merge / Merge after fixes / Not ready verdict and each finding ranked Blocker, Should fix or Nice to have, with file, line and a suggested fix. Saves each review outside the repo, so a re-run on the same branch marks each earlier finding Fixed or Still open and reviews the new commits in depth. Uses PROJECT_CONTEXT.md / SYSTEM_CONTEXT.md from create-project-context when present. Use when the user says "review my changes", "review this PR", "review PR 42", "is this ready to merge", "will this break anything", "check my branch before I raise a PR", or runs /ai-sam:review-pr [PR number, link or branch]. Read-only by default; never edits code, posts PR comments, commits or pushes without asking first.
---

# Review PR

Review code changes before they merge. Two questions get an answer:

- **Is the change itself right?** Bugs, edge cases, security, performance, conventions, tests.
- **Does it break anything else?** Every caller, screen, API consumer, other repo and database user that depends on the changed code.

Targets:

- **Current changes** — the current branch against its base branch, plus uncommitted work. Used when no target is given.
- **A PR or branch** — e.g. `/ai-sam:review-pr 42`, `/ai-sam:review-pr https://github.com/org/repo/pull/42` or `/ai-sam:review-pr feature/abc-123-upload`.

Where it fits:

1. `/ai-sam:implement-ticket` — build the ticket.
2. `/ai-sam:write-unit-tests` and `/ai-sam:write-feature-tests` — fill in the tests.
3. `/ai-sam:review-pr` — check it before it merges. (This skill.)

## Ground rules

- **Read-only by default.** Never edit, stage or revert code during the review. Fix code only when the user picks it in Step 8. The only files this skill writes on its own are the saved review (outside the repo) and the **PR host** line, after the user answers it.
- **Don't touch the user's working tree.** Never switch branches, stash, reset or discard changes. To check out another branch, use a separate worktree, and only after the user agrees.
- **Ask before anything outward-facing.** No PR comment, approval, commit, push or Jira change unless the user picks it in Step 8 and approves the exact text.
- **Every finding needs evidence.** Name the file and line, what goes wrong, and when (the input or step that causes it). Drop anything you can't back up with the code.
- **Review the change, not the whole repo.** Problems in code this change didn't touch go under **Outside this change**, unless the change makes them worse.
- **Follow the project.** Judge against the repo's own conventions, versions and patterns, not personal taste.
- **Report checks honestly.** If a test, lint or build fails, say so and show the error. Never say "nothing breaks" without the impact check and the checks behind it.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from the diff and the code. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
  - Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change, re-ask it, and continue.
- **No personal or secret data.** Never open `.env` files, secrets, keys, or data files that may hold real people's records. Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If the diff, fixtures or logs contain any of this, do not repeat it. Report it as a **Blocker** ("sensitive data added in `<file>:<line>` — left out here"), tell the user it looks like personal or sensitive data that must not go into AI tools or the repo, and ask them to remove it. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Find the changes

Find the repo root with `git rev-parse --show-toplevel` and the current branch with `git branch --show-current`. Then pick the mode:

- **Nothing given** → **Current changes** (1A).
- **A PR number or link** → **PR** (1B).
- **A branch name** → **Branch** (1C).

Then, in every mode, check for an earlier review (1D).

### 1A — Current changes

1. Find the base branch (the branch this one was made from):
   - `git rev-parse --abbrev-ref origin/HEAD`, else the first of `main`, `master`, `develop` that exists.
   - On the base branch itself, there is no branch diff. Review uncommitted changes only, and say so.
2. Collect:
   - committed changes: `git diff <base branch>...HEAD`
   - uncommitted changes: `git diff HEAD`, plus untracked files from `git status --porcelain`
   - commits: `git log --oneline <base branch>..HEAD`
3. If there are uncommitted changes, say in one line that they are included.

### 1B — A PR

1. **Find the PR host** (the site that holds the repo's pull requests):
   - Read the `**PR host:**` line in `PROJECT_CONTEXT.md` (repo root or `docs/`), else in the repo's `CLAUDE.md`.
   - **Not found:** ask — **PR host**: <host guessed from `git remote get-url origin`> (Recommended), then up to two of GitHub, Azure DevOps, GitLab. Bitbucket and others through **Other**. Guess from the remote: `github.com` → GitHub; `dev.azure.com` or `visualstudio.com` → Azure DevOps; `gitlab` → GitLab; `bitbucket.org` → Bitbucket.
   - **Save the answer** so later runs don't ask. Add `- **PR host:** <host>` to the **Overview** section of `PROJECT_CONTEXT.md`, and a dated row to its **Change log**. With no `PROJECT_CONTEXT.md`, add the same line under a `## Pull requests` heading in the repo's `CLAUDE.md`. Say in one line where it was saved.
2. **Get the PR** with the host's tool, after checking it is signed in:

   | Host | Signed in? | PR details | Diff |
   |---|---|---|---|
   | GitHub | `gh auth status` | `gh pr view <n> --json title,body,baseRefName,headRefName,files,commits` | `gh pr diff <n>` |
   | Azure DevOps | `az account show` | `az repos pr show --id <n>` — title, description, `sourceRefName`, `targetRefName` | Fetch both branches and diff as in 1C |
   | GitLab | `glab auth status` | `glab mr view <n>` | `glab mr diff <n>` |
   | Bitbucket and others | — | No CLI (command-line tool) — ask for the branch name | Diff as in 1C |

   Strip `refs/heads/` from Azure DevOps branch names.
3. **The tool is missing or not signed in:** ask — **PR details**: Give the branch name in Other (Recommended), Paste the diff in Other, Retry previous answer. Then continue as 1C, or review the pasted diff. Don't install tools or sign in for the user; say which command would fix it.
4. Use the PR's base branch as the base branch, and its title and description as the intent in Step 3.

### 1C — A branch

1. Fetch it if it isn't local: `git fetch origin <branch>`.
2. Diff it against the base branch without checking it out: `git diff <base branch>...<branch>`, and `git log --oneline <base branch>..<branch>`.

### 1D — An earlier review

Each review is saved (Step 8) to `~/.claude/ai-sam/reviews/<repo folder name>/<branch, with / as ->.md`. This is outside the repo, so git never sees it.

1. Look for that file for the branch under review. None → a full review; go on.
2. Found → read its **Reviewed commit** line and check it is still in the branch: `git merge-base --is-ancestor <reviewed commit> <branch or HEAD>`.
   - **Still in the branch:** ask — **Earlier review found** (<date>, <verdict>, <n> open findings): Compare with it (Recommended — review the new commits in depth and check each old finding), Fresh full review.
   - **Not in the branch** (the branch was rebased or force-pushed): say so in one line and do a full review. Still mark each old finding Fixed or Still open in Step 7.
3. **Compare mode:**
   - New changes: `git diff <reviewed commit>..<branch or HEAD>`, plus uncommitted work in Current changes mode.
   - Step 5 reads the new changes in depth. It still reads the rest of the full diff, but only for problems the new changes cause.
   - Step 4 and Step 6 still cover the full diff, since a fix can break a caller the first review cleared.

### Size and scope

- **Nothing changed:** say so in one line and stop.
- Skip lock files, generated code, build output and binary files in the line-by-line review. List them under **Not reviewed**, but still flag a lock file that adds or upgrades packages.
- **More than 40 changed files or 2,000 changed lines:** ask — **Large change**: Review everything (Recommended — say it will take longer), Review the files with the most logic first (name the top 15), Retry previous answer. Say the user can name files in **Other**.

## Step 2 — Load the project

1. Read, if present:
   - `PROJECT_CONTEXT.md` in the repo root or `docs/` — versions, commands, conventions.
   - `SYSTEM_CONTEXT.md` in the parent folder or at the path its **System** section names — the other repos and how they connect.
   - `CLAUDE.md` in the repo root, including any **Team** section (between `<!-- ai-sam:team:start -->` and `<!-- ai-sam:team:end -->`).
   - Lint and format configs (`.eslintrc*`, `.editorconfig`, `.prettierrc*`, `stylecop.json`, `ruff.toml` and the like) — the repo's rules beat general taste.
2. Note the test, lint, build and type-check commands. With no context file, take them from the manifest scripts (`package.json`, `*.csproj`, `pyproject.toml`, `pom.xml`, `build.gradle`), `Makefile` or README, and say in one line "No PROJECT_CONTEXT.md found — using commands from `<file>`."

## Step 3 — Understand what the change is for

1. Read the commit messages, and the PR title and description if there is one.
2. **Ticket:** if the branch name, PR title or commits have a Jira key (e.g. `ABC-123`) and a Jira connector is available, fetch the ticket's summary, description and acceptance criteria. Say in one line that you fetched it. Without a connector, carry on from the commits; don't ask for the ticket.
3. **Team ticket rules:** look for the config written by `/ai-sam:setup-jira-config`, in this order, and merge it section by section (the first file that sets a section wins):
   1. `JIRA_CONFIG.local.md` in the repo root
   2. `JIRA_CONFIG.md` in the repo root
   3. `~/.claude/ai-sam/JIRA_CONFIG.md`

   With a ticket, use what applies to its type:
   - **Acceptance criteria style is Gherkin** (Given / When / Then steps): each scenario is one acceptance criterion, and its Then lines say what the test must check.
   - **The type has a custom template:** each section that sets a rule for the work — e.g. "Definition of Done", "Regression risk", "Out of scope", "Security" — becomes a **team rule** to check. Use the ticket's text for that section, or the template's own text if the ticket left it empty. Skip sections that only describe the ticket, like "Context" or "Steps to reproduce".

   Say in one line which file you used, or "No JIRA_CONFIG.md found". Skip this with no ticket.
4. Write down, for yourself, the intent in 1–3 bullets. Every finding is judged against it.
5. Check the ticket for personal or secret data (see the ground rules) before going on.

## Step 4 — Start the helpers

Start these now, in the background, so they work while you review the diff in Step 5. Each starts fresh, so send everything it needs in one message. Never paste personal or secret data into a brief.

### 4a — The impact check

Start the `tech-lead` subagent (`ai-sam:tech-lead`) with this brief:

````markdown
## Impact review: <branch or PR title>

**Mode:** Impact review — find what this change could break. Don't review code style.

### What the change is for
- <intent bullets from Step 3, and the ticket's acceptance criteria if fetched>

### Where to look
- **Repo root:** `<path>`
- **Base branch:** `<base>` — **Changed branch:** `<branch>` (or "uncommitted work in the repo root")
- **See the diff with:** `git diff <base>...<branch>` <plus `git diff HEAD` for uncommitted work>
- **Context files:** `<PROJECT_CONTEXT.md path>`, `<SYSTEM_CONTEXT.md path>` — read them first.

### Changed files
| File | Change |
|---|---|
| `<path>` | <added / changed / deleted / renamed> |

### Send back
The **Impact review** shape from your instructions.
````

If the subagent can't run, do its checks yourself in Step 6 and say so in the report.

### 4b — Layer reviewers

Team agents (from `/ai-sam:create-team`) know their layer's rules better than a general review. Ask each one to review the files it owns.

1. Look for team agents in this order:
   1. The **Team** section of the repo's `CLAUDE.md` — each agent and the folders it owns.
   2. Agent files in `<repo>/.claude/agents/*.md` and `~/.claude/agents/*.md`. Read each one's `name`, `description` and the folders it names.
2. Match each changed file to one agent: the agent owns the file's folder, or its description names that kind of work (e.g. "frontend", "database"). If two fit, pick the one whose folders match more closely. Skip `tech-lead` — it already has the impact check.
3. **No agent matches any file:** say in one line "No team agents found — reviewing in the main session." and go on.
4. Start one agent per layer that has changed files, all at the same time. Say in one line which agent reviews which files. Brief:

````markdown
## Layer review: <branch or PR title>

**Mode:** Review only. Don't edit, create or delete files, and don't run commands that change anything.

### What the change is for
- <intent bullets from Step 3, and the acceptance criteria if fetched>

### Your files
- `<path>` — <added / changed / deleted>

### Where to look
- **Repo root:** `<path>`
- **See the diff with:** `git diff <base>...<branch> -- <your files>` <plus `git diff HEAD -- <your files>` for uncommitted work>
- **Context files:** `<PROJECT_CONTEXT.md path>`, `<SYSTEM_CONTEXT.md path>` — read them first.

### Check
- Your layer's rules from your instructions: patterns, folder layout, naming, commands.
- Bugs, edge cases, security and performance in your files.
- Missing or weak tests for the changed behaviour.
- Don't open `.env` files or secrets.

### Send back
One bullet per problem: `<file>:<line>` — what goes wrong and when — suggested fix. Say "No problems found" if there are none. Never list a file you have not opened.
````

Team agents can usually edit files, so the brief tells them not to. If an agent changes a file anyway, say so in the report and don't count its review.

## Step 5 — Review the diff

Read every changed line in context — open the whole function or component, not only the diff lines. Do this even for files a layer reviewer has; the two reviews catch different things. In Compare mode (1D), go deepest on the new changes. Check, where they apply:

1. **Does it do what it says?** Each part of the intent, each acceptance criterion and each team rule is built. Note any that are missing or only partly built.
2. **Correctness:**
   - logic errors, wrong conditions, off-by-one (a count that is one too many or too few)
   - null, empty, zero, one-item and many-item cases
   - error paths — what happens when a call fails, times out or returns nothing
   - async code — missing `await`, race conditions (two things running at once and clashing), unhandled promise rejections
   - state — values not reset, stale data, data shared where it shouldn't be
3. **Security:**
   - who can call it — permission and login checks on new endpoints and screens
   - input checks and output escaping (SQL injection, XSS — cross-site scripting, path traversal)
   - secrets or personal data in code, logs, error messages or test data
   - data scoped to the right user, tenant (customer account) or program
4. **Performance:**
   - queries inside loops, missing paging on large lists, missing indexes for new queries
   - repeated network calls, extra re-renders in frontend components
5. **Data and contracts:**
   - database migrations have a rollback (a way to undo them) and keep existing data working
   - API request and response shapes stay backward compatible, or the break is intended and stated
6. **Conventions:** naming, folder layout, error handling and logging follow the closest existing feature and the repo's lint rules.
7. **Tests:**
   - every changed behaviour has a test; a bug fix has a test that fails without the fix
   - tests check behaviour, not internals, and don't use real network, clock or random values
   - existing tests weren't deleted, skipped or weakened without a reason
8. **Leftovers:** debug logs, commented-out code, `TODO`s without a ticket, unused imports, new packages nobody asked for.

Write each problem as a draft finding with file, line, what goes wrong and when.

## Step 6 — Check nothing else breaks

Three parts: what the code depends on (from the tech-lead), proof from the project's checks, and the layer reviews.

### 6a — Read the impact review

When the tech-lead returns:

1. Read its **Impact review**. For each **At risk** item, open the file it names and confirm the risk is real. Drop the ones the code disproves.
2. Turn each confirmed risk into a finding (Step 7 sets its severity).
3. Note each **Needs a check** item for 6b or for **How to test it** in the report.

### 6b — Run the checks

Run, in this order, the commands from Step 2 that exist: type-check, lint, build, the full test suite.

- **Current changes mode:** run them in the repo root.
- **PR or branch mode:** the code isn't checked out. Ask — **Run the checks?** Run them in a temporary worktree (a second folder with the PR's branch, so your folder is left as it is) (Recommended), Skip the checks and review the code only, Retry previous answer. For a worktree: `git worktree add ../<repo folder>-review <branch>`, install dependencies there with the install command, and run the checks inside it.
- **A command needs something you don't have** (a database, a secret, a running service): don't work around it. List it under **Not run** with the reason.

Sort each failure:

- **Caused by this change** — the failing test or file is in the diff, or calls code the diff changed. Make it a finding.
- **Not clearly caused by this change** — ask — **Was this already failing?** Run the same check on `<base branch>` in a temporary worktree to compare (Recommended), List it as already failing without checking, Retry previous answer. Failures that also happen on the base branch go under **Already failing**.

Remove any worktree you made in this step with `git worktree remove <path>` once the checks finish, and say so.

### 6c — Read the layer reviews

When each layer reviewer returns:

1. Check it didn't change files: `git status --porcelain` shows nothing new beyond what was there before Step 4.
2. For each problem it lists, open the file and line and confirm it. Drop the ones the code disproves.
3. Add each confirmed problem as a draft finding, noting which agent found it. If you already have the same problem, merge them.

## Step 7 — Check the findings

Before reporting, go through every draft finding:

1. **Re-read the code.** Drop a finding if the code handles the case somewhere else (a guard in the caller, a validator, a database constraint, a framework default).
2. **Rank it:**
   - **Blocker** — wrong results, data loss, a security hole, personal or secret data, a failing check caused by this change, breaking another feature or repo, or an acceptance criterion not built.
   - **Should fix** — a real problem in an edge case, a missing test for changed behaviour, a convention the repo clearly follows, or a team rule not met.
   - **Nice to have** — a clearer name, a small simplification, a comment that would help.
3. **Give a fix.** One line, or a short diff, for each Blocker and Should fix.
4. **Merge duplicates.** One finding per root cause, listing every place it shows up.
5. **Compare with the earlier review** (1D only). Mark each old Blocker and Should fix:
   - **Fixed** — re-open its file and confirm the problem is gone, not only that the line moved.
   - **Still open** — keep it as a finding at its old rank, unless the code changed enough to re-rank it.
   - **Fixed differently** — the problem is gone through another route; say how in a few words.

   Every finding not in the earlier review is **New**.

Then pick the verdict:

- **Ready to merge** — no Blockers, no Should fix.
- **Merge after fixes** — no Blockers, one or more Should fix.
- **Not ready** — one or more Blockers.

## Step 8 — Report and next step

Show the report in the chat:

````markdown
## PR review: <branch or PR title>

**Verdict:** Ready to merge / Merge after fixes / Not ready — <one-line reason>
**Findings:** <n> Blocker, <n> Should fix, <n> Nice to have
**Breaks other features?** No — <n> callers and <n> other repos checked, checks pass / Yes — see Blockers / Not sure — <what wasn't checked>
**Reviewed:** <n> files, +<added> / -<removed> lines against `<base branch>` <— including uncommitted work>
**Based on:** <context files read> | Code scan only (no PROJECT_CONTEXT.md found)
**Reviewed by:** main session, `tech-lead` (impact)<, `<agent>` (<layer>) …>
**Since last review:** <n> fixed, <n> still open, <n> new — compared with <date>, commit `<short sha>` <(Compare mode only)>

### Since last review
| Earlier finding | Status |
|---|---|
| **<problem>** — `<file>:<line>` | Fixed / Still open — see Should fix 2 / Fixed differently — <how> |

### Blockers
1. **<problem in a few words>** — `<file>:<line>`
   - **What goes wrong:** <the input or step, and the wrong result>
   - **Fix:** <one line or a short diff>

### Should fix
1. **<problem>** — `<file>:<line>`
   - **What goes wrong:** <…>
   - **Fix:** <…>

### Nice to have
- `<file>:<line>` — <one line>

### Acceptance criteria
| Acceptance criterion | Met? | Where | Test |
|---|---|---|---|
| <short version> | Yes / No / Partly | `<file>` | `<test name>` / None |

### Team rules
From `<JIRA_CONFIG file>`, <ticket type> template.

| Rule | Met? | Where |
|---|---|---|
| <e.g. "Definition of Done: feature flag added"> | Yes / No / Partly / Can't tell from code | `<file>` or <what a person must check> |

### What else this change touches
| Depends on the change | Where | Status |
|---|---|---|
| <caller, screen, API consumer, other repo, job, report> | `<file>` | Safe — <why> / At risk — see Blocker 1 / Needs a manual check |

### Checks
| Check | Command | Result |
|---|---|---|
| Type-check | `<command>` | Pass / Fail — <error in one line> / Not run — <reason> |
| Lint | `<command>` | <result> |
| Build | `<command>` | <result> |
| Tests | `<command>` | Pass (212 tests) / <n> fail — <names> |

### How to test it
1. <manual step for anything the checks can't prove, e.g. "Open the Payments page as a read-only user and confirm the Export button is hidden">

### Already failing
- <check that fails on `<base branch>` too>

### Outside this change
- `<file>:<line>` — <problem in code this change didn't touch>

### Not reviewed
- `<file>` — <reason, e.g. generated code, lock file>
````

Leave out empty sections, except **Checks** and **What else this change touches**. Leave out **Acceptance criteria** when no ticket was found, **Team rules** when no config rule applies, and the **Since last review** line and section outside Compare mode. In findings, tag each one **New** or **Still open** in Compare mode.

**Save the review** to the path in 1D. Create the folder if needed, and overwrite the file for this branch. Say in one line where it was saved. The file holds:

- the report above
- `**Reviewed commit:** <full sha of the branch or HEAD>` and `**Base branch:** <base>`
- `**Date:** <YYYY-MM-DD>`, and the PR number if there is one
- for uncommitted work, a note that it was included, since it has no commit to compare against

Then ask — **Next step**: Done (Recommended), Fix the findings, Post the review as PR comments, Retry with edits.

- **Fix the findings** — ask which (All Blockers (Recommended), All Blockers and Should fix, or pick by number in **Other**). Fix only those, in the current branch only; in PR or branch mode, say the fix must go on that branch and ask before switching to it or making a worktree. Run the checks from 6b again and show the updated report. Don't commit; then offer the usual commit question (show the message first, commit only on yes, push only on a second yes).
- **Post the review as PR comments** — only in PR mode with the host's tool signed in (GitHub `gh`, Azure DevOps `az`, GitLab `glab`). Show every comment first (file, line, text), and the summary comment with the verdict. Ask: Post them (Recommended), Change the text, Retry previous answer. Post only on yes: `gh api` review comments on GitHub, `az devops invoke --area git --resource pullRequestThreads` on Azure DevOps, `glab mr note` on GitLab. Leave this option out for other hosts. Never approve or request changes on the PR unless the user asks for that too.
- **Retry with edits** — ask what to change (Review deeper on a file, Ignore a finding, Check another repo, or **Other**). Change only that, re-run what it affects, and show the report again.

Never update the Jira ticket unless the user asks. If they do, show the comment first and wait for a yes.
