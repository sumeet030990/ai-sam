---
name: create-ticket
description: Interview the user and write a clear ticket (story, bug, task, epic or spike) for any tracker — Jira, Bitbucket, Azure DevOps, GitHub, GitLab or similar — in plain, simple English with point-wise sections, using the standard format for its type or the team's own format saved in TICKET_CONFIG.md by setup-ticket-config. Shows the finished ticket in the chat as Markdown that pastes cleanly into the tracker or any rich text editor such as Confluence, Word, Google Docs or email. Use when the user says "create a ticket", "create a Jira ticket", "create a Bitbucket issue", "write a ticket", "draft a story", "log a bug", "write up this task", "turn this into a ticket", or pastes rough notes and asks for a ticket. Does not save files or create the ticket in the tracker.
---

# Create Ticket

Ask the user the questions that matter for the kind of ticket they want, then write the ticket in plain English, point by point, and show it in the chat ready to copy and paste into the team's tracker (Jira, Bitbucket, Azure DevOps, GitHub, GitLab or similar) or any rich text editor.

## Ground rules

- **Ask; don't guess.** Every fact in the ticket comes from the user's answers, files they pointed you at, or notes they pasted. If an answer is missing, vague or contradicts another one, ask a focused follow-up. If the user says something is not known yet, write `To be decided` — never invent details, numbers, dates or names.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from what you already know (earlier answers, pasted notes, the repo, the ticket type). Mark the best one "(Recommended)".
  - For long answers (a description, a list of steps, acceptance criteria), draft the text yourself and put it in the option's `preview`, so the user can pick it as-is.
  - The user can always type their own answer in the built-in **Other** textbox. Say so in the question text, e.g. "…or type your own in Other".
  - Group up to 4 related questions in one call.
- **Let the user fix a wrong answer.** Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change (default: the one just before), re-ask it, update it, and return to where you were. The user can also say "go back" at any time.
- **Let the user redo anything you drafted.** Whenever you show text you wrote (summary drafts, acceptance criteria, steps, the full ticket), offer these two options alongside the others:
  - **Retry** — write a fresh version from the same answers, with different wording or structure. Don't repeat the previous draft.
  - **Retry with edits** — ask what to change (e.g. "shorter", "add a step for admins", "less technical", "drop the out-of-scope section") through a follow-up AskUserQuestion with likely edits as options and the **Other** textbox for their own. Apply only those changes, keep everything else as it was, and show the result again.

  Both can be repeated as many times as the user likes. AskUserQuestion allows only 4 options, so when a question also needs **Retry previous answer**, show one suggested draft with it. The user can also type "retry" or "retry with …" in **Other** at any time.
- **Keep it short.** Skip questions the user's notes already answer — show what you understood and ask them to confirm instead. Don't ask about optional fields one by one; ask once whether they want any of them.
- **No personal or secret data.** Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If the user pastes any of this (in notes, logs, screenshots or error messages), stop, do not repeat it, tell them it looks like personal or sensitive data that must not go into the ticket or into AI tools, and ask them to redact it or use made-up example data (e.g. "Test User", "Applicant A", `****1234`). Follow your organisation's data policy if it is stricter.

## Writing style — plain, simple, point-wise

Write as if explaining to a smart colleague who doesn't know the system. Apply these to every section:

1. **Short sentences.** Aim for under 20 words. One idea per bullet.
2. **Everyday words.** "Use" not "utilise", "start" not "initiate", "fix" not "remediate", "show" not "render".
3. **Explain jargon once.** If a technical term is needed, add a plain meaning in brackets the first time — e.g. "API (the connection between the website and the server)". Spell out acronyms on first use.
4. **Active voice, real people.** "The applicant clicks Submit" — not "Submit is clicked". Name the role (applicant, admin, case worker), never a real person.
5. **Bullets and numbered lists, not paragraphs.** Numbered lists for steps that happen in order; bullets for everything else. No paragraph longer than 2 sentences.
6. **Say what, not how** in the main sections. Technical detail (file names, code, queries) goes only in an optional **Technical notes** section at the end.
7. **Concrete over vague.** "The page takes more than 10 seconds to load" — not "the page is slow". If the user only knows it's "slow", ask for a rough number or write `To be decided`.
8. **Testable acceptance criteria.** Each one is a single check someone can say yes or no to. Start each with the person or the system: "The admin can…", "The system shows…".
9. **Friendly but neutral.** No blame, no slang, no emojis, no exclamation marks.

## Step 0 — Load the team config

Before the first question, look for saved team conventions (written by `/ai-sam:setup-ticket-config`):

1. **Local file** — `TICKET_CONFIG.local.md` in the repo root (`git rev-parse --show-toplevel`; the current folder if it isn't a git repo). One person's overrides of the team rules.
2. **Repo file** — `TICKET_CONFIG.md` in the repo root. The team's shared rules.
3. **User file** — `~/.claude/ai-sam/TICKET_CONFIG.md`. Personal defaults across every repo.

Older versions saved these as `JIRA_CONFIG.md` / `JIRA_CONFIG.local.md` (same paths, same format). If a `TICKET_CONFIG` file is missing but the old-named one exists, use the old one in its place.

Merge them section by section: `Summary format`, `Acceptance criteria style`, and each type under `Templates` (`Story`, `Bug`, `Task`, `Epic`, `Spike`). For each section, use the first file in the order above that sets it, otherwise the standard behaviour in this skill. A section set to `Standard` means the standard behaviour.

- If a file exists, say in one line which file(s) you're using. When the local file overrides the repo file, name the overridden sections, e.g. "Using TICKET_CONFIG.local.md (Acceptance criteria style) over TICKET_CONFIG.md". Don't ask about the settings — just follow them.
- If none exists, carry on with the standard behaviour and mention once, in one line, that `/ai-sam:setup-ticket-config` can save the team's summary format, acceptance criteria style and templates.
- Don't edit the config files from this skill. If the user wants a setting changed, point them to `/ai-sam:setup-ticket-config`.

## Step 1 — What kind of ticket

If the user pasted notes or gave a description with the request, read it first and use it to suggest answers.

Ask with AskUserQuestion (the first call of a run, so no **Retry previous answer**) — **Ticket type**: Story (new feature or change for users), Bug (something is broken), Task (work that needs doing, e.g. setup or clean-up); Epic and Spike (research) through **Other**. Recommend the type that fits the user's notes. If the notes already make the type obvious, skip the question and say which type you picked.

Use the config's custom template for that type if Step 0 found one; otherwise use the standard format (see **Standard templates**). Don't ask the user which template to use.

## Step 2 — Gather the details

Ask only what the ticket type needs. Group questions (up to 4 per call), suggest answers from what you already know, and skip anything already answered.

**Don't ask who the work is for or who is affected.** The person writing the ticket already knows the audience. Use a role only if it appears in the user's notes or answers; otherwise write around it (e.g. "Users can…") and leave role-only lines out.

### All ticket types

- **Summary (title)** — one line, under ~80 characters, plain words. Suggest 2–3 drafts. Bugs: "<What is wrong> when <situation>". Stories: "<Who> can <do something>". Tasks: "<Verb> <thing>".
  - If the config sets a **Summary format**, follow it for the types it applies to. **Tags**: suggest the tag(s) that fit the work (one or several, as the config allows) and put them first, e.g. `[FE] Applicant can upload documents`. **Pattern**: fill the pattern, using its example as the model.
- **Why it matters** — the problem or the value, in one or two points.

### Story

- What the user wants to do, and what they can't do today.
- The main steps of how it should work (the "happy path").
- Acceptance criteria — draft them from the answers and show them in a `preview` for the user to confirm or edit.
- What is **not** included (out of scope), so the team doesn't build too much.

### Bug

- What happened (actual result).
- What should have happened (expected result).
- Steps to reproduce — numbered. Ask for the starting page/screen and the exact clicks or inputs, using made-up test data.
- Where it happens — environment (e.g. Production, QA, Dev), browser or device, and version if known.
- How often — every time, sometimes, once.
- Impact — roughly how many users, is there a workaround, does it block work or lose data. Suggest a **priority** from this (Highest / High / Medium / Low) and let the user confirm.
- Error messages, logs or screenshots — remind them to redact personal data first.

### Task

- What needs to be done, as a short checklist.
- Why it's needed now.
- How we'll know it's done.

### Epic

- The overall goal.
- What's in scope and out of scope.
- The main pieces of work (these may become child tickets later).
- How success will be measured, if known.

### Spike (research)

- The question we need answered.
- Options already considered.
- Time limit (time-box), e.g. 2 days.
- What the output should be (a recommendation, a demo, a document).

### Custom templates

When the config gives a custom template for the ticket type, it replaces the per-type list above. Ask for what each of its sections needs instead:

- Ask the Summary and Why questions from **All ticket types** only if the template has a place for them.
- For each other section, ask one question built from its heading and any `<!-- comment -->` under it, grouping related sections (up to 4 per call). Draft answers in a `preview` where you can.
- Fill every `<placeholder>`. Drop sections and lines the user has no answer for, unless they say to keep them as `To be decided`.
- Keep the template's section names and order. Apply the **Writing style** rules to the content.

### Acceptance criteria style

If the config sets **Gherkin**, write acceptance criteria (in standard and custom templates) as scenarios instead of checklist items, unless the config says Bugs keep a checklist:

```markdown
**Scenario: <short name>**
- **Given** <starting situation>
- **When** <action>
- **Then** <result someone can check>
```

One scenario per behaviour. Each **Then** is a single yes-or-no check.

### Optional fields — ask once

Ask one multi-select AskUserQuestion: "Do you want to add any of these?" — Priority, Labels / components, Story points / estimate, Links (related tickets, designs, documents), Dependencies or blockers, Technical notes. Then ask only about the ones picked. Leave the rest out of the ticket entirely (don't write empty headings).

## Step 3 — Draft, review, and finish

1. Write the ticket using the config's custom template for this type or the matching standard template below, the config's summary and acceptance criteria style, the **Writing style** rules, and the answers from Step 2.
2. Show the full draft in the chat and ask with AskUserQuestion: Looks good (Recommended), Retry, Retry with edits, Retry previous answer.
   - **Retry** — rewrite the whole ticket from the same answers in a fresh way, then show it and ask again.
   - **Retry with edits** — ask what to change, with common edits as options (Make it shorter, Simpler language, Change a section) and **Other** for their own. Apply only those changes, then show it and ask again.
   - **Retry previous answer** — go back to a question from Step 2, update the answer, and redraft.

   Repeat until the user picks **Looks good**.
3. Once the user picks **Looks good**, show the final ticket in the chat (see **Output format**) and stop. Don't ask any more questions — no saving to a file, copying to the clipboard, choosing a paste destination or creating it in the tracker. If the user asks for one of these afterwards, do it then.

## Output format

Show the final ticket in the chat in this order:

1. **Summary** on its own line, as plain text — it goes in the tracker's separate title field (Summary in Jira, Title in Bitbucket, Azure DevOps, GitHub and GitLab).
2. The description inside one fenced ```markdown block, so the user can copy the raw text in one go. Use `###` headings, `**bold**`, `-` bullets, `1.` numbered lists and `- [ ]` for acceptance criteria checklists. No tables (they paste less reliably). Jira Cloud, Bitbucket, Azure DevOps, GitHub, GitLab and most rich text editors (Confluence, Teams, Google Docs with Markdown enabled) turn pasted Markdown into proper formatting.
3. One short line: fields like Priority, Labels and Story points are set in the tracker's own fields (e.g. Jira's side panel); they're listed in the description only for reference. Leave this line out if the ticket has none of them.

If the user says they use Jira Server / Data Center, use Jira wiki markup instead (`h3. Heading`, `*bold*`, `* bullet`, `# numbered`, `{code}...{code}`, `[text|https://...]`) inside a fenced ```text block.

## Standard templates

The section order for each ticket type, used when the config doesn't give a custom template for it. Drop optional sections the user didn't ask for, and lines whose answer you don't have (such as a role nobody mentioned).

### Story

````markdown
**Summary:** <Who> can <do something>

### Background
- <What happens today, in one or two points>
- <Why this matters / the problem it solves>

### User story
- **As a** <role from the notes, or "user">
- **I want to** <do something>
- **So that** <benefit>

### How it should work
1. <Step 1 of the happy path>
2. <Step 2>
3. <Step 3>

### Acceptance criteria
- [ ] <The role can …>
- [ ] <The system shows …>
- [ ] <When …, then …>

### Out of scope
- <What this ticket will not cover>

### Additional details
- **Priority:** <…>
- **Links:** <designs, documents, related tickets>
- **Dependencies:** <what must happen first>

### Technical notes
- <Only if the user added them>
````

### Bug

````markdown
**Summary:** <What is wrong> when <situation>

### What is happening
- <The problem in plain words>

### What should happen
- <The expected behaviour>

### Steps to reproduce
1. Go to <page/screen>
2. <Click / enter …>
3. <See the problem>

### Where it happens
- **Environment:** <Production / QA / Dev>
- **Browser / device:** <…>
- **How often:** <Every time / Sometimes / Once>

### Impact
- **How many users:** <rough number or share>
- **Workaround:** <yes — describe / none>
- **Priority:** <Highest / High / Medium / Low> — <one-line reason>

### Acceptance criteria
- [ ] <Following the steps above, the system now …>
- [ ] <Nothing else on the page changes>

### Evidence
- <Error message, log excerpt or screenshot reference — redacted>
````

### Task

````markdown
**Summary:** <Verb> <thing>

### Why
- <Why this is needed now>

### What needs to be done
- [ ] <Item 1>
- [ ] <Item 2>

### Done when
- <Clear, checkable result>

### Additional details
- <Links, dependencies, notes — only if added>
````

### Epic

````markdown
**Summary:** <Goal in a few words>

### Goal
- <What we want to achieve>

### Why it matters
- <Business value or problem solved>

### In scope
- <Main piece of work 1>
- <Main piece of work 2>

### Out of scope
- <…>

### How we'll measure success
- <Measure, or To be decided>
````

### Spike

````markdown
**Summary:** Research: <question>

### Question to answer
- <The question in plain words>

### Why we need to know
- <What decision this unblocks>

### Options to look at
- <Option A>
- <Option B>

### Time limit
- <e.g. 2 days>

### Expected output
- <Recommendation / demo / short document>
````
