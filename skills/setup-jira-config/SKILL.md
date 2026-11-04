---
name: setup-jira-config
description: Interview the user once about their team's Jira ticket conventions (summary format, acceptance criteria style, and custom templates that replace the standard Story, Bug, Task, Epic or Spike formats) and save them in a JIRA_CONFIG.md file that create-jira-ticket reads before writing a ticket. Saves a personal user-level file (~/.claude/ai-sam/JIRA_CONFIG.md), a shared repo-level file (JIRA_CONFIG.md in the repo root) that overrides it section by section, or a personal repo-level file (JIRA_CONFIG.local.md, gitignored) that overrides the team's repo file for one person. Use when the user says "set up Jira config", "configure Jira tickets", "save our ticket template", "use our team's ticket format", "set the summary tags", "use Gherkin acceptance criteria", or wants create-jira-ticket to follow team rules. Also use to update or reset an existing JIRA_CONFIG.md. Does not connect to Jira or create tickets.
---

# Setup Jira Config

Ask the user how their team writes Jira tickets, then save the answers in a `JIRA_CONFIG.md` file. `/ai-sam:create-jira-ticket` reads that file and follows it, so the user doesn't repeat these choices on every ticket.

The file holds three things:

1. **Summary format** — how ticket titles are written (plain, with tags like `[FE]`, or a custom pattern).
2. **Acceptance criteria style** — checklist bullets or Gherkin (Given / When / Then).
3. **Templates** — full replacements for any of the standard Story, Bug, Task, Epic or Spike templates.

## Ground rules

- **Ask; don't guess.** Every setting comes from the user's answers, a file they point you at, or text they paste. If an answer is vague or contradicts another one, ask a focused follow-up. Never invent tags, patterns or template sections.
- **Every question uses AskUserQuestion**, except where a step says to let the user paste text in the chat.
  - Give 1–3 suggested options built from what you already know (the existing config, the repo, earlier answers). Mark the best one "(Recommended)".
  - Put examples and drafts in the option's `preview` so the user can see exactly what they're choosing.
  - The user can always type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
- **Let the user fix a wrong answer.** Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change (default: the one just before), re-ask it, and return to where you were. The user can also say "go back" at any time.
- **Only ask about what's being changed.** Each section is optional. A section the user skips is left out of the file, and create-jira-ticket falls back to the next file or the standard behaviour for it.
- **No personal or secret data.** Templates and examples must use placeholders (`<role>`, `<page>`) or made-up data ("Test User", "Applicant A"). Never copy into the file:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If a pasted template or example ticket contains any of this, stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into the config or into AI tools, and ask them to redact it or swap in placeholders. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Where the files live and how they combine

The repo root is `git rev-parse --show-toplevel`, or the current folder if it isn't a git repo.

| Priority | Scope | Path | Use for |
|---|---|---|---|
| 1 (highest) | Local | `JIRA_CONFIG.local.md` in the repo root | One person's overrides of the team rules in one repo; gitignored, never shared |
| 2 | Repo | `JIRA_CONFIG.md` in the repo root | Team rules for one repo; can be committed and shared |
| 3 | User | `~/.claude/ai-sam/JIRA_CONFIG.md` | Personal defaults across every repo |

The files combine **section by section**: for each section, the highest-priority file that sets it wins. The sections are: `Summary format`, `Acceptance criteria style`, and each template type under `Templates` (`Story`, `Bug`, `Task`, `Epic`, `Spike`) on its own. Anything no file sets uses create-jira-ticket's standard behaviour.

A section set to `Standard` means "use the standard behaviour" and still counts as set, so a repo file can switch a user-level custom template back to the standard one, and a local file can do the same for a team template.

Keep a local file small: only the sections the person wants different from the team. Every section it leaves out keeps following the repo file, including later team changes.

## Step 0 — Choose the scope

1. Check which of the three files already exist and read them.
2. Ask with AskUserQuestion (first call of the run, so no **Retry previous answer**) — **Which config do you want to set up?**
   - **This repo (team)** — writes `JIRA_CONFIG.md` in the repo root. Recommend this when the current folder is a git repo and it has no `JIRA_CONFIG.md` yet.
   - **Just me, this repo (override the team config)** — writes `JIRA_CONFIG.local.md` in the repo root. Recommend this when the repo already has a `JIRA_CONFIG.md`. Offer it only inside a git repo.
   - **Just me (all repos)** — writes `~/.claude/ai-sam/JIRA_CONFIG.md`. Recommend this outside a git repo.

   Name the full path in each option's description, and note which files already exist.
3. If the chosen file exists, show a short summary of what it sets and ask: **Update some sections (Recommended)**, **Start over**, **Show the file only**.
   - **Update some sections** — ask which sections to change (multi-select: Summary format, Acceptance criteria style, Templates). Run only those steps and keep the rest of the file as it is.
   - **Start over** — run every step; the file is replaced at the end.
   - **Show the file only** — show it and stop.
4. As you go, say which sections of lower-priority files the chosen file will override: the user file's for the repo scope, and the repo and user files' for the local scope.
5. For the local scope, start with **Update some sections** even when the file is new: ask which sections to override (multi-select), and run only those steps. Show the team's current value for each section in a `preview` so the user sees what they're changing.

## Step 1 — Summary format

Ask **How should ticket summaries (titles) be written?** with a `preview` example for each option:

- **Plain** — create-jira-ticket's standard patterns ("<Who> can <do something>", "<What is wrong> when <situation>", "<Verb> <thing>"). Saved as `Standard`.
- **Tags in front** — one or more tags before the summary, e.g. `[FE] Applicant can upload documents`.
- **Custom pattern** — the team's own shape, e.g. `<Area>: <what changes>`.

If **Tags in front**:

1. Ask which tags the team uses (multi-select). Suggest tags from the repo if you can tell (a `frontend/` folder suggests `[FE]`, migrations suggest `[DB]`), otherwise offer `[FE]`, `[BE]`, `[API]`, `[DB]`, `[Infra]`; **Other** for their own list.
2. Ask, in one call: what each tag means (draft one-line meanings in a `preview` for them to confirm), and whether a ticket can carry **one tag only** or **several** (e.g. `[FE][API]`).
3. Ask whether any ticket types skip tags (e.g. Epics and Spikes).

If **Custom pattern**:

1. Ask for the pattern with `<placeholders>` (Other textbox), suggesting one or two drafts.
2. Ask for one example summary written in that pattern, using made-up content, so create-jira-ticket has a model to copy.
3. Ask whether it applies to all ticket types or only some, and what the others use.

Keep the same rules on length: under ~80 characters, plain words.

## Step 2 — Acceptance criteria style

Ask **How should acceptance criteria be written?** with a `preview` of each:

- **Checklist** — create-jira-ticket's standard. Saved as `Standard`.

  ```markdown
  - [ ] The applicant can upload a PDF up to 10 MB
  - [ ] The system shows an error for other file types
  ```

- **Gherkin** — one scenario per behaviour, in Given / When / Then steps.

  ```markdown
  **Scenario: Upload a valid PDF**
  - **Given** the applicant is on the Documents page
  - **When** they upload a PDF under 10 MB
  - **Then** the file appears in their document list
  ```

If **Gherkin**, ask whether Bugs also use it, or keep a checklist for bugs (some teams find "Following the steps above, the system now…" clearer).

This style applies to the acceptance criteria section of both standard and custom templates.

## Step 3 — Custom templates

A custom template **fully replaces** the standard one for that ticket type. Types without a custom template keep the standard format.

1. Ask (multi-select) **Which ticket types should use your own template?** — Story, Bug, Task, Epic; Spike through **Other**. Mention that unpicked types keep the standard template. If the user picks none, skip to Step 4 and leave the `Templates` section out (or, in **Update some sections**, keep what the file already has).
   - In the repo scope, if the user file has custom templates, also offer to set a type back to `Standard` for this repo.
   - In the local scope, if the repo file has custom templates, also offer to set a type back to `Standard` for this person.
2. For each picked type, ask **How do you want to give the <type> template?**
   - **Paste it in the chat (Recommended)** — the user's next message is the template. Tell them to use `<angle-bracket placeholders>` for anything that changes per ticket.
   - **Read it from a file** — ask for the path in **Other**, then read it. Accept Markdown or plain text; if it's Jira wiki markup, convert it to Markdown and show the result.
   - **Start from the standard template** — show the standard template for that type (from create-jira-ticket's **Standard templates**) in a `preview`, ask the user to paste back their edited version.
   - **Copy from an example ticket** — the user pastes a real ticket they like; you turn it into a template by swapping every specific detail for a `<placeholder>`. Check it carefully for personal data first (see **Ground rules**).
3. Check each template and fix it with the user before saving:
   - It has headings (`###`) for each section. If it's one block of text, propose a split into sections.
   - Content that changes per ticket is a `<placeholder>`, not real data.
   - It has no `**Summary:**` line, or if it does, the line follows Step 1's summary format. (create-jira-ticket shows the summary separately either way.)
   - Note which section holds acceptance criteria, if any, so Step 2's style can be applied to it.
   - Add a one-line HTML comment under any section heading whose purpose isn't obvious, saying what goes there (e.g. `<!-- Which existing features this could break -->`). create-jira-ticket turns these into questions.
4. Show the cleaned template and ask: **Looks good (Recommended)**, **Retry with edits**, **Retry previous answer**. For **Retry with edits**, ask what to change (Rename a section, Add a section, Remove a section, Other), apply only that, and show it again.

## Step 4 — Confirm and write

1. Build the file from the **Config file format** below with only the sections the user set (plus, in **Update some sections**, the sections already in the file).
2. Show the whole file in the chat and ask: **Save it (Recommended)**, **Retry with edits**, **Retry previous answer**.
3. On **Save it**, write the file. For the user scope, create `~/.claude/ai-sam/` if needed. Overwrite an existing file only after the user has seen the new version in step 2.
4. For the local scope, check that git ignores the file (`git check-ignore -q JIRA_CONFIG.local.md` from the repo root). If it doesn't, ask **Add JIRA_CONFIG.local.md to .gitignore? (Recommended)** / **No, I'll handle it**, and on yes append the line to the repo root's `.gitignore` (create it if missing). Don't commit either file.
5. Finish with three short lines:
   - where the file was saved;
   - for the repo scope: it can be committed so the team shares it (don't commit it yourself); for the local scope: it stays on this machine and only affects this user's tickets;
   - `/ai-sam:create-jira-ticket` will now use it — and if more than one file exists, which file each section comes from.

## Config file format

All three scopes use the same format. Use these exact headings, because create-jira-ticket merges files by them. Leave out any section the user didn't set.

`````markdown
# Jira Ticket Config

<!-- Written by /ai-sam:setup-jira-config and read by /ai-sam:create-jira-ticket.
     Section by section, JIRA_CONFIG.local.md overrides the repo's JIRA_CONFIG.md,
     which overrides ~/.claude/ai-sam/JIRA_CONFIG.md.
     "Standard" means use create-jira-ticket's built-in behaviour. -->

## Summary format
- **Style:** <Standard | Tags | Pattern>
- **Tags:** <[FE] front end, [API] backend API, …> (Tags only)
- **Tags per ticket:** <One | Several> (Tags only)
- **Pattern:** <`<Area>: <what changes>`> (Pattern only)
- **Example:** <made-up example summary>
- **Applies to:** <All types | Story, Bug, Task — Epic and Spike use Standard>

## Acceptance criteria style
- **Style:** <Standard | Gherkin>
- **Bugs:** <Same | Checklist> (Gherkin only)

## Templates

### Story
<Standard, or the full template in a ````markdown block>

### Bug
<Standard, or the full template in a ````markdown block>

### Task
…

### Epic
…

### Spike
…

## Change log
- <YYYY-MM-DD> — <what was set or changed>
`````

Wrap each custom template in a four-backtick ```` ````markdown ```` fence so code blocks inside it don't break the file. Add a dated **Change log** line on every save.
