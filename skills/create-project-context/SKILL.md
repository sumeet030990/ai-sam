---
name: create-project-context
description: Interview the user about their project (basics, goals, tech stack, and dependency manifest files such as package.json or requirements.txt, and the install, run, test, lint and build commands) and write a PROJECT_CONTEXT.md file that future coding sessions read before writing code. For a folder holding several repos (backend + frontend, microservices, micro-frontends, or a monorepo), run it in each repo first, then in the parent folder to write a SYSTEM_CONTEXT.md that only references each repo's context and how they connect. Use when the user says "create project context", "set up project context", "document my project", "capture the tech stack", or starts a new project and wants Claude to remember its details. Also use to update an existing PROJECT_CONTEXT.md or SYSTEM_CONTEXT.md when the stack, dependency files or set of repos change.
---

# Create Project Context

Collect the project's details from the user and write them to a context file. Future development work reads this file to learn what the project is, which stack it uses, and which package versions to code against.

The skill has two modes:

- **Repo mode** — one repo, service, micro-frontend or monorepo package. Writes a full `PROJECT_CONTEXT.md` (Steps 1–4). This is where stack and version details live.
- **Parent mode** — a folder (or monorepo root) that holds several repos or components. Writes a thin `SYSTEM_CONTEXT.md` that only **references** each component's `PROJECT_CONTEXT.md` and records how the components connect (Step P). It never copies stack or version details from the components.

For multi-repo projects the order is: **run in each repo first, then run in the parent.** Re-run in the parent whenever a repo is added, removed, or its context changes, so the references stay accurate.

## Ground rules

- Ask; don't guess. Every fact in the file comes from the user's answers or from files the user pointed you at. If an answer is missing, vague or contradicts another answer, ask a focused follow-up question about that item (offer examples or choices where it helps) and keep asking until it is clear. Once the user clarifies, update the context with the clarified answer. Only if the user states that an item does not apply or is not decided yet, record it as `Not applicable` or `To be decided` — never invent a value.
- Record who provided the details — only with consent. The contributor's name is the one personal detail this skill may record. Before asking for it, warn the user that the name will be written into the context file and shared with anyone who can read the repo. Then ask with AskUserQuestion — **Contributor name**: Record my name (suggest `git config user.name` as the default if it is set), Skip — don't record personal details, Retry previous answer.
  - **Record:** write the name in the file's header and add a row to the **Change log** every time the file is created or updated, naming that person and what changed, so the details can be verified with them later.
  - **Skip:** write `Not recorded` wherever a name would go, and add the line `_Personal details: not recorded (contributor opted out)._` under the file's header. On every later run, if an existing file has that line, do not ask for a name again and keep writing `Not recorded` in new change log rows, unless the user explicitly asks to start recording names.
- Never record secrets or any other personal data. Do not ask for, read, or copy passwords, API keys, tokens, connection strings, `.env` files, `.npmrc`/`pip.conf` auth lines, email addresses, phone numbers, or resident, customer or sample records. If the user volunteers any, do not repeat it and tell them it was left out.
- Record dependency **file paths**, not a copy of every version. The manifest files stay the source of truth; the context file points at them.
- Every question offers options plus a textbox. Ask **every** question in this skill with AskUserQuestion, never as a plain-text question. This includes names, descriptions, goals, paths, URLs, commands, conventions, confirmations and follow-ups. For each question:
  - Give 1–3 suitable options built from what you already know: the folder name, git remote, README, manifests, files you found, earlier answers, and common defaults for the stack. Mark the best one "(Recommended)".
  - For long answers (a description, a goal, a command list, a summary to confirm), draft the text yourself and put it in the option's description or `preview`, so the user can pick it as-is.
  - If you have nothing to base a suggestion on, offer `To be decided` and `Not applicable` as the options. The user still gets a textbox.
  - The user types their own answer through the built-in **Other** textbox. Mention this in the question text, e.g. "…or type your own in Other".
  - Group up to 4 related questions in one AskUserQuestion call rather than asking them one at a time.
- Always let the user correct a wrong answer. Every AskUserQuestion you ask in this skill includes a **Retry previous answer** option as its last option (it takes one of the 4 option slots, so show at most 3 other choices). If the user picks it, ask which earlier answer they want to change (default: the one just before this question), re-ask that question, update the recorded answer, and then return to the question you were on. The first question of a run has nothing to retry, so leave the option out there. When the user types their own answer in **Other**, repeat back what you recorded in the next question so they can correct it. A user can also say "retry" or "go back" at any point to do the same.
- If a `PROJECT_CONTEXT.md` (or, in parent mode, `SYSTEM_CONTEXT.md`) already exists, read it first, show the user what it holds, and ask whether to update it or replace it. Default to updating — keep sections the user does not change, and keep the existing change log rows. Always keep a `## Delivery and release process` section as it is; `/ai-sam:setup-release-process` owns it. If the file has none, mention in the final summary that this skill can add one.
- When updating, check for drift before asking anything else. In repo mode: confirm every listed manifest file still exists, re-read the runtime and key framework versions and compare them with the **Tech stack** table, and check the listed commands still exist in their source files. In parent mode: confirm each component path and context file still exists, and look for new or removed components. Show the user what changed, update those rows after they confirm, and name the drift fixes in the change log row.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 0 — Choose the mode

Look at the current folder before asking:

- **Looks like a parent:** two or more immediate subfolders that are git repos (contain `.git`) or contain a `PROJECT_CONTEXT.md` or dependency manifest, and the folder itself has no app manifest of its own; or a monorepo root with a workspace file (`pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json`, a root `package.json` with `workspaces`, a `.sln` with several projects).
- **Otherwise:** a single repo.

Tell the user what you found and ask with AskUserQuestion — **Mode**: This repo / component (repo mode), Parent of several repos (parent mode). This is the first question, so it has no **Retry previous answer** option. Put the detected mode first, marked "(Recommended)".

- Repo mode → continue with Step 1.
- Parent mode → go to **Step P**.

## Step 1 — Basic project details

First ask about the contributor name, with the warning and skip option described in the ground rules.

Then ask for these with AskUserQuestion, up to 4 per call, with suggested options and the **Other** textbox as described in the ground rules. Read the folder name, `git remote get-url origin`, the README and any manifest `name`/`description` fields first so the suggestions are real. For any item left blank or unclear, follow up the same way before moving on.

1. Project name — e.g. the folder name, the manifest `name`, the README title
2. One-paragraph description — what it does (a draft from the README in the option's preview)
3. Problem it solves / business goal (a draft from the README, or `To be decided`)
4. Project root path — the current working directory (Recommended), the git top-level folder if it differs
5. Repository URL — the git remote URL if set, `Not applicable`, `To be decided`

Then use AskUserQuestion for the structured items:

- **Project type** — Web app, API / backend service, Mobile app, Retry previous answer (Library / CLI / other through "Other")
- **Stage** — New (greenfield), In development, In production / maintenance, Retry previous answer
- **Part of a larger system?** — No, standalone; Yes, with other repos (backend + frontend, microservices, micro-frontends); Yes, a package inside a monorepo; Retry previous answer

If it is part of a larger system, also ask (AskUserQuestion with suggestions such as the parent folder's name, `../SYSTEM_CONTEXT.md`, and exposes/consumes lines drafted from routes, clients or contract files you can see): the system's name, where its `SYSTEM_CONTEXT.md` is or will be (path relative to this repo such as `../SYSTEM_CONTEXT.md`, or a repo URL — `To be decided` if it doesn't exist yet), and, in one line each, the APIs, events or modules this repo **exposes** and the ones it **consumes** from other components. Record names and where the contract files live (OpenAPI, `.proto`, event schemas) — not full endpoint lists.

## Step 2 — Tech stack

**Existing code: detect first.** If the project root already has code, search it for the manifest files listed in Step 3 (same skip list) before asking about the stack. Read what you find and work out the languages, frameworks, database clients, test tools and package manager they declare. Show the detected stack and ask with AskUserQuestion: Looks right (Recommended), Some layers are wrong, Retry previous answer. Then ask only about what the files cannot tell you (hosting, CI/CD, auth provider, anything the user marked wrong) and skip the preset question below. Carry the files you found into Step 3 as the proposed list. Detected values still need the user's confirmation — they are a starting point, not a recorded fact.

**New project, or nothing detected:** first ask whether the project uses a common full-stack combination, using AskUserQuestion with options such as:

- **MERN** — MongoDB, Express, React, Node.js
- **MEAN** — MongoDB, Express, Angular, Node.js
- **Next.js full stack** — Next.js (React + API routes), Node.js, a database
- **.NET + React** — ASP.NET Core / Azure Functions, React, SQL Server
- **Django / FastAPI + React** — Python backend, React frontend, PostgreSQL
- **Spring Boot + Angular/React** — Java backend, Angular or React frontend
- **Laravel (PHP)** — Laravel backend, Blade or Inertia with Vue/React frontend, MySQL
- **Custom** — choose each layer separately

AskUserQuestion takes at most 4 options per question and one of them is **Retry previous answer** (see the ground rules), so show the 3 presets that fit the languages or project type the user has already mentioned; the user can type any other combination, or "Custom", through "Other".

If the user picks a full-stack preset, pre-fill the layers below from it, show them, and ask only about what the preset does not settle (e.g. which database, hosting, testing tools, package manager) or anything the user wants to change. If the user picks **Custom**, ask about each layer.

For **Custom**, or for layers a preset leaves open, ask about each layer. Use AskUserQuestion with common choices where it helps (the user can always pick "Other"), always include **Retry previous answer**, and allow "None / not applicable":

- Languages (e.g. TypeScript, Python, C#, Java, Go, PHP)
- Frontend framework (e.g. React, Next.js, Angular, Vue, none)
- Backend framework (e.g. Node/Express, NestJS, FastAPI, Django, .NET, Spring Boot, Laravel, Symfony, none)
- Database / storage (e.g. PostgreSQL, SQL Server, MongoDB, Redis, none)
- Hosting / cloud / infrastructure (e.g. Azure, AWS, GCP, Docker, Kubernetes, Vercel)
- Testing tools (e.g. Jest, Vitest, Playwright, pytest, xUnit, PHPUnit, Pest)
- Anything else that matters: auth provider, messaging, CI/CD, package manager (npm, pnpm, yarn, pip, poetry, uv, NuGet, Maven, Gradle, Composer)

Also ask for coding conventions the user wants followed (style guide, linting, folder structure, branching), if any. Offer the conventions you can detect (e.g. an ESLint/Prettier/`.editorconfig` file, the branch naming in `git branch -a`) and "None to record" as options.

## Step 3 — Dependency manifest files

Based on the stack from Step 2, tell the user which files hold package versions for that stack and ask for their paths. Typical files:

| Stack | Manifest files (lock file in brackets) |
|---|---|
| Node / JS / TS | `package.json` [`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`] |
| Python | `requirements.txt`, `pyproject.toml`, `Pipfile` [`poetry.lock`, `uv.lock`, `Pipfile.lock`] |
| .NET | `*.csproj`, `Directory.Packages.props`, `global.json` |
| Java / Kotlin | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| Go | `go.mod` [`go.sum`] |
| Rust | `Cargo.toml` [`Cargo.lock`] |
| Ruby | `Gemfile` [`Gemfile.lock`] |
| PHP | `composer.json` [`composer.lock`] |
| Flutter / Dart | `pubspec.yaml` [`pubspec.lock`] |
| Runtime pins | `.nvmrc`, `.node-version`, `.python-version`, `.tool-versions` |

If Step 2 already found files, show that list and ask the user to confirm it (options: Use these files (Recommended), Remove or add some, Retry previous answer). Otherwise ask with options: Search the project root for them (Recommended), No manifest files yet, Retry previous answer; the user can type paths in **Other**. If they choose to search, search (skipping `node_modules`, `.venv`, `venv`, `bin`, `obj`, `dist`, `build`, `.git`), list what you found, and ask the user to confirm which ones belong to the project.

For each confirmed file:

1. Check it exists. If a path the user gave does not exist, say so and ask again or drop it.
2. Read it and note the runtime / language version if it declares one (e.g. `engines.node`, `requires-python`, `<TargetFramework>`, `go 1.x`) and the main framework versions. These go in the summary table — keep it to the key packages, not the full list.
3. Record the path **relative to the project root**.

If the user has no manifest files (e.g. a brand-new project) or skips this step, record that, and the context file will tell future work to use the latest stable versions (see the template's version policy).

## Step 3b — Commands

Future sessions need to know how to install, run, test, lint and build the project. Read the commands from the confirmed manifests and task files — `package.json` `scripts`, `Makefile`, `justfile`, `Taskfile.yml`, `pyproject.toml` scripts, `*.sln` / `*.csproj` (`dotnet build` / `dotnet test`), `pom.xml` / `build.gradle`, and the README's setup section — and propose one command per purpose:

- Install dependencies
- Run locally
- Test (and how to run a single test, if it differs)
- Lint / format
- Build

Ask one AskUserQuestion per purpose (up to 4 per call), with the commands you found as options, the stack's usual default (e.g. `npm test`, `dotnet test`, `pytest`) if nothing was found, and the **Other** textbox for a different command. Record `Not applicable` or `To be decided` only if the user says so. Record each command as written, with any required environment variable **names** but never their values; if a command has a secret inline, leave the command out and tell the user why.

## Step 4 — Confirm and write

1. Ask where to save the file. Options: `<project root>/PROJECT_CONTEXT.md` (Recommended), `<project root>/docs/PROJECT_CONTEXT.md`, Retry previous answer.
2. Show the user a short summary of what will be written (in the option's `preview`) and ask: Looks good, write it (Recommended), Change something, Retry previous answer.
3. Write the file using the template below. Drop optional sections that have nothing in them; keep the **Dependency & version policy** section always.
4. Offer to add `@PROJECT_CONTEXT.md` to the project's `CLAUDE.md` (create it if missing) so every future session loads the context automatically. Ask with options: Yes, add it (Recommended), No, Retry previous answer. Only do this if the user agrees.
5. End by telling the user the file path and how to refresh it later (re-run this skill).
6. If the repo is part of a larger system, also tell the user the next steps: run this skill in each of the other repos so each has its own detailed `PROJECT_CONTEXT.md`, then run it once more in the parent folder (or monorepo root) to write the `SYSTEM_CONTEXT.md` that references them all.

## Step P — Parent mode (system references only)

The parent file is a map, not a second copy of each repo's details. It holds names, paths, one-line roles and how the components connect. Stack tables, versions and manifests stay in each component's `PROJECT_CONTEXT.md`.

Every question below follows the ground rules too: AskUserQuestion with suggested options built from the components' context files, folder names and contract files, plus **Retry previous answer** and the **Other** textbox.

1. **Ask about the contributor name** (with the warning and skip option from the ground rules) and for the system's name and one-paragraph description.
2. **Find the components.** List the immediate subfolders (or monorepo packages from the workspace file) that look like repos or components, skipping `node_modules`, `.venv`, `venv`, `bin`, `obj`, `dist`, `build`, `.git`. Ask the user to confirm the list and add any that live elsewhere (another path or only a repo URL).
3. **Check each component for its own context.** For each confirmed component, look for `PROJECT_CONTEXT.md` at its root.
   - **Found:** read it and take only the project name, type, a one-line role, the repo URL and its **Exposes / Consumes** lines. Do not copy its stack, versions or manifests.
   - **Missing:** list these components to the user and recommend running this skill in each of them first, then re-running it here. Ask with AskUserQuestion: Stop so I can run it in those repos first (Recommended), Continue and mark them "Context not created yet", Retry previous answer. If they continue, ask for a one-line role for each and mark the row `Context not created yet`.
4. **Ask what ties them together** (skip anything already clear from the components' Exposes / Consumes lines; record `Not applicable` or `To be decided` only if the user says so):
   - How components communicate (REST, gRPC, GraphQL, message bus / events, Module Federation, shared DB) and which calls which.
   - Where the shared contracts live (paths or URLs to OpenAPI, `.proto`, event schemas) — reference them, don't copy them.
   - For micro-frontends: the shell / host, and the shared singleton packages it pins (e.g. React, router, design system). Record each package name and **which manifest pins it** — not a copied version number.
   - For a monorepo: the workspace or central version files (`pnpm-workspace.yaml`, root `package.json`, `Directory.Packages.props`, `gradle/libs.versions.toml`).
   - Shared conventions that apply across all components (auth approach, error format, logging, branching) — only if they are shared.
5. **Where to store it.** Default: `<parent folder>/SYSTEM_CONTEXT.md`. If the parent folder is not inside a git repo (common for a folder of separate repos), warn the user that teammates won't receive it and offer: keep it here anyway, save it in a shared docs/meta repo, or save it in the most central repo (e.g. the backend or MFE shell). Ask which.
6. **Confirm and write** using the system template below. Show a short summary first and ask for corrections.
7. **Link both ways.** Offer to (a) add `@SYSTEM_CONTEXT.md` to the parent's `CLAUDE.md` (create it if missing), and (b) set the **System** section's path in each component's `PROJECT_CONTEXT.md` to point at this file, adding a change log row in each one. Write a relative path only when the file is in the same git repo as the component; otherwise (a folder outside git, or a separate docs repo) write the repo URL of the stored file, so the link works for teammates who clone the component on its own. Only do either if the user agrees. Never `@`-import the components' files into the parent `CLAUDE.md` — Claude loads each component's own `CLAUDE.md` when it works in that folder, and importing them all would load every stack at once.
8. End by telling the user the file path, listing any components still marked `Context not created yet`, and reminding them to re-run this skill in the parent whenever a component is added, removed or its context changes.

### System template

````markdown
# System Context: <System name>

_Last updated: <YYYY-MM-DD> by <name of the person who provided the details, or Not recorded>_

<One-paragraph description of the whole system.>

This file only references the components. Each component's stack, versions and conventions are in its own `PROJECT_CONTEXT.md` — read that before changing code in the component.

## Components

| Component | Path / repo | Type | Role | Context file |
|---|---|---|---|---|
| <name> | `<./orders-service>` or <URL> | <API / Web app / MFE / Library> | <one line> | `<./orders-service/PROJECT_CONTEXT.md>` or Context not created yet |

## How they connect

| From | To | How | Contract |
|---|---|---|---|
| <web-frontend> | <orders-service> | <REST> | `<path or URL to openapi.yaml>` |

## Shared dependencies

<Micro-frontends / monorepo only — otherwise remove this section.>

| Package | Pinned in | Rule |
|---|---|---|
| <react> | `<shell/package.json>` | Components must use the host's version; do not upgrade on their own. |

## Shared conventions

<Only rules that apply to every component — or remove this section.>

## Change log

| Date | Provided by | Change |
|---|---|---|
| <YYYY-MM-DD> | <name, or Not recorded> | <Initial system context created / components added or removed> |
````

## Template

````markdown
# Project Context: <Project name>

_Last updated: <YYYY-MM-DD> by <name of the person who provided the details, or Not recorded>_

## Overview

<One-paragraph description.>

- **Type:** <Web app / API / Mobile / Library / ...>
- **Stage:** <New / In development / In production>
- **Repository:** <URL, or Not applicable / To be decided if the user confirmed so>
- **PR host:** <GitHub / Azure DevOps / GitLab / Bitbucket — remove this line if not known; review-pr asks for it and adds it>
- **Test cases share:** <service — site, library, folder, format — remove this line if not known; write-test-cases asks for it and adds it>
- **Project root:** <path>

## System

<Only if this repo is part of a larger system — otherwise remove this section.>

- **Part of:** <System name> — system map in `<../SYSTEM_CONTEXT.md or URL>`
- **Exposes:** <APIs, events or modules other components use, with contract file paths>
- **Consumes:** <APIs, events or modules this repo uses from other components>

## Goal

<Problem it solves / business goal.>

## Tech stack

| Layer | Choice | Version |
|---|---|---|
| Full-stack preset | <e.g. MERN, .NET + React, or Custom> | — |
| Language(s) | <...> | <from manifest, or "latest stable"> |
| Frontend | <...> | <...> |
| Backend | <...> | <...> |
| Database | <...> | <...> |
| Hosting / infra | <...> | — |
| Testing | <...> | <...> |
| Package manager | <...> | <...> |

## Dependency manifest files

These files are the source of truth for package versions. Paths are relative to the project root.

| File | Purpose |
|---|---|
| `<path/to/package.json>` | <e.g. frontend dependencies> |
| `<path/to/requirements.txt>` | <e.g. backend dependencies> |

<If none were provided: "No dependency manifest files were provided.">

## Commands

Run from the project root unless noted.

| Purpose | Command | Source |
|---|---|---|
| Install | `<npm ci>` | `<package.json>` |
| Run locally | `<npm run dev>` | `<package.json>` |
| Test | `<npm test>`; single test: `<npm test -- path/to/file>` | `<package.json>` |
| Lint / format | `<npm run lint>` | `<package.json>` |
| Build | `<npm run build>` | `<package.json>` |

<Required environment variables, names only: `<API_BASE_URL>`, ...>

## Dependency & version policy

When writing or changing code for this project:

1. **Read the manifest files listed above first** and use exactly the package and runtime versions they declare. Write code against those versions' APIs — do not use features from newer versions, and do not upgrade or downgrade a package unless asked.
2. **Prefer the lock file** (when one is listed) for the exact installed version; use the manifest's range otherwise.
3. **Adding a new package:** add it to the matching manifest using the project's package manager, and pick the latest stable version that is compatible with the versions already in use.
4. **No manifest provided, or a package not listed in any manifest:** use the **latest stable release** of that package (no alpha, beta, RC, preview or nightly builds). Check the package registry for the current version at the time the code is written, rather than relying on memory, and record the chosen version in a manifest file once one exists.
5. If a listed manifest file is missing or moved, stop and ask the user before assuming versions.
6. **Shared packages:** if the system context lists a package under **Shared dependencies**, the manifest it names there wins over this repo's manifest. Ask before changing that package's version here.

## Conventions

<Coding style, linting, folder structure, branching — or remove this section.>

<## Delivery and release process — written by /ai-sam:setup-release-process. Keep it as it is when present; never add it here.>

## Notes

<Anything else the user wants future work to know — or remove this section.>

## Change log

Who provided or changed these details, so they can be verified later. Add a row on every create or update; never remove old rows.

| Date | Provided by | Change |
|---|---|---|
| <YYYY-MM-DD> | <name, or Not recorded> | <Initial context created / sections updated and what changed> |
````
