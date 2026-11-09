#!/usr/bin/env python3
"""ai-sam guard: a PreToolUse hook that blocks or asks before risky tool calls.

Claude Code runs this before each matching tool call (in the main session and in
subagents) and passes the call as JSON on stdin. The script answers with one of:

- deny  -- the call is blocked and Claude is told why
- ask   -- the user must approve the call, even in auto mode
- (no output) -- the call goes through the normal permission rules

It does not replace the skills' written rules; it backs them up with a check that
text in a ticket, PR or file cannot talk its way around.

Turn it off for one session with the environment variable AI_SAM_GUARD=off.
Standard library only, so it needs no install.
"""

import json
import os
import re
import shlex
import sys

# --- Secret files ---------------------------------------------------------

# Never read: files whose main job is to hold secrets.
DENY_FILE_PATTERNS = [
    r"(^|/)\.env(\.[^/]*)?$",            # .env, .env.local, .env.production
    r"\.(pem|key|p12|pfx|jks|keystore)$",  # private keys and certificate stores
    r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$",  # SSH private keys
    r"(^|/)\.git-credentials$",
    r"(^|/)\.aws/credentials$",
    r"(^|/)\.azure/.*token",
    r"(^|/)\.docker/config\.json$",
    r"(^|/)\.kube/config$",
]
# .env templates hold no real values, so they are allowed.
ALLOW_FILE_PATTERNS = [
    r"(^|/)\.env\.(example|sample|template|dist|defaults)$",
]
# Often hold secrets but also real settings: ask first.
ASK_READ_FILE_PATTERNS = [
    r"(^|/)local\.settings\.json$",  # Azure Functions local secrets
    r"(^|/)secrets\.json$",
    r"(^|/)\.npmrc$",
    r"(^|/)\.pypirc$",
    r"(^|/)\.netrc$",
]

# --- Files that change what runs or how the AI behaves --------------------

ASK_WRITE_FILE_PATTERNS = [
    (r"(^|/)\.claude/settings[^/]*\.json$", "Claude Code settings"),
    (r"(^|/)\.claude/(hooks|agents|commands|skills)/", "Claude agents, hooks or skills"),
    (r"(^|/)CLAUDE(\.local)?\.md$", "CLAUDE.md (instructions every session follows)"),
    (r"(^|/)\.mcp\.json$", "MCP server config (tools the AI can call)"),
    (r"(^|/)\.github/workflows/", "a CI pipeline"),
    (r"(^|/)(azure-pipelines|\.gitlab-ci|bitbucket-pipelines)\.ya?ml$", "a CI pipeline"),
    (r"(^|/)\.(npmrc|yarnrc(\.yml)?|pypirc)$", "where packages are downloaded from"),
    (r"(^|/)(nuget\.config|pip\.conf)$", "where packages are downloaded from"),
    (r"(^|/)\.git/hooks/", "git hooks (scripts git runs by itself)"),
    (r"(^|/)\.husky/", "git hooks (scripts git runs by itself)"),
]


def norm(path):
    return path.replace("\\", "/") if path else ""


def matches(path, patterns):
    p = norm(path)
    return any(re.search(rx, p, re.IGNORECASE) for rx in patterns)


def secret_level(path):
    """Return 'deny', 'ask' or None for reading this path."""
    if not path or matches(path, ALLOW_FILE_PATTERNS):
        return None
    if matches(path, DENY_FILE_PATTERNS):
        return "deny"
    if matches(path, ASK_READ_FILE_PATTERNS):
        return "ask"
    return None


def control_file(path):
    p = norm(path)
    for rx, label in ASK_WRITE_FILE_PATTERNS:
        if re.search(rx, p, re.IGNORECASE):
            return label
    return None


# --- Shell commands ---------------------------------------------------------

NETWORK_TOOLS = {
    "curl", "wget", "nc", "ncat", "netcat", "telnet", "ftp", "tftp",
    "invoke-webrequest", "invoke-restmethod", "iwr", "irm",
}
SHELLS = {"sh", "bash", "zsh", "fish", "dash", "ksh", "python", "python3",
          "node", "perl", "ruby", "pwsh", "powershell", "iex", "invoke-expression"}
WRAPPERS = {"sudo", "command", "exec", "time", "nohup", "env", "xargs"}
SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")"}


def split_commands(command):
    """Split a shell line into simple commands, keeping pipes visible."""
    lex = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        tokens = list(lex)
    except ValueError:
        # Unbalanced quotes etc. Fall back to a rough split.
        tokens = command.split()
    parts, current, pipes = [], [], []
    for tok in tokens:
        if tok in SEPARATORS or set(tok) <= set(";&|()\n"):
            if current:
                parts.append(current)
                pipes.append(tok)
            current = []
        else:
            current.append(tok)
    if current:
        parts.append(current)
        pipes.append("")
    return parts, pipes


def program(words):
    """First real word of a simple command, skipping VAR=value and wrappers."""
    i = 0
    while i < len(words):
        w = words[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w) or w.lower() in WRAPPERS:
            i += 1
            continue
        return os.path.basename(w).lower(), words[i + 1:]
    return "", []


def local_bin_exists(name, cwd):
    return os.path.exists(os.path.join(cwd or ".", "node_modules", ".bin", name))


def check_install(prog, args, cwd):
    """Return a reason if this command installs a new package."""
    a = [x.lower() for x in args]
    flags_dropped = [x for x in a if not x.startswith("-")]
    if prog in ("npm", "pnpm", "yarn", "bun"):
        if not flags_dropped:
            return None  # plain `npm install` / `yarn` installs the lock file
        sub = flags_dropped[0]
        if sub in ("install", "i", "add") and len(flags_dropped) > 1:
            return f"installs a new package: {' '.join(args[1:])}"
        if sub in ("update", "upgrade", "up") and prog != "yarn" or sub == "upgrade":
            return "upgrades packages"
        if sub in ("dlx", "exec") and prog in ("pnpm", "yarn", "bun"):
            return "downloads and runs a package"
    if prog in ("npx", "bunx"):
        pkgs = [x for x in args if not x.startswith("-")]
        if pkgs and not local_bin_exists(os.path.basename(pkgs[0]).split("@")[0], cwd):
            return f"downloads and runs `{pkgs[0]}`, which is not installed in this repo"
    if prog in ("pip", "pip3", "uv", "poetry", "pipx", "conda"):
        if "install" in a or "add" in a:
            if "-r" in a or "--requirement" in a or "-e" in a or "." in a:
                return None  # installs the repo's own requirements
            if prog == "poetry" and a and a[0] == "install":
                return None
            return "installs a new Python package"
    if prog == "python" or prog == "python3":
        if "pip" in a and "install" in a and "-r" not in a:
            return "installs a new Python package"
    if prog == "dotnet" and len(a) >= 2 and a[0] == "add" and "package" in a:
        return "adds a NuGet package"
    if prog == "dotnet" and a[:2] == ["tool", "install"]:
        return "installs a .NET tool"
    if prog in ("brew", "apt", "apt-get", "yum", "dnf", "choco", "winget", "scoop",
                "gem", "cargo", "go") and ("install" in a or "get" in a):
        return "installs software on this machine"
    return None


def check_bash(command, cwd):
    """Return (decision, reason) or (None, None)."""
    parts, pipes = split_commands(command)

    # A download piped straight into a shell runs unseen code.
    for i, words in enumerate(parts[:-1]):
        prog, _ = program(words)
        nxt, _ = program(parts[i + 1])
        if prog in NETWORK_TOOLS and pipes[i] == "|" and nxt in SHELLS:
            return "deny", ("Downloads code and runs it straight away (`... | sh`). "
                            "Download it to a file, show it to the user, and run it only on a yes.")
    if re.search(r"(iex|invoke-expression)\s*\(?\s*\(?\s*(new-object|iwr|irm|invoke-web|invoke-rest)",
                 command, re.IGNORECASE):
        return "deny", "Downloads code and runs it straight away (PowerShell `iex`)."

    for words in parts:
        prog, args = program(words)
        if not prog:
            continue
        a = [x.lower() for x in args]

        # Secret files named on the command line.
        for w in words[1:]:
            # `HEAD:.env`, `--env-file=.env`, `<.env`, `@.env` all name the file.
            w = re.split(r"[:=]", w)[-1].lstrip("<>@'\"")
            level = secret_level(w)
            if level == "deny" and prog not in ("echo", "printf"):
                return "ask", (f"This command touches `{w}`, which usually holds secrets. "
                               "Secrets must not go into AI tools (Neighborly AI policy). "
                               "Approve only if no secret value will be shown.")

        if prog in NETWORK_TOOLS:
            url = next((x for x in args if re.match(r"^[a-z]+://", x, re.I)), "an outside address")
            return "ask", (f"Network call to {url}. Text in a ticket, PR or file can try to "
                           "send data out this way. Approve only if you asked for this call.")

        if prog == "git":
            sub = a[0] if a else ""
            if sub == "push" and any(x in ("-f", "--force", "--force-with-lease", "--mirror",
                                           "--delete", "-d") or x.startswith("--force")
                                     or x.startswith(":") for x in a[1:]):
                return "ask", "Force push or remote branch delete: rewrites or removes shared history."
            if sub == "reset" and "--hard" in a:
                return "ask", "`git reset --hard` throws away uncommitted work."
            if sub == "clean" and any(x.startswith("-") and "f" in x for x in a[1:]):
                return "ask", "`git clean -f` deletes untracked files for good."
            if sub in ("commit", "push", "merge", "rebase") and "--no-verify" in a:
                return "ask", "`--no-verify` skips the repo's git hooks and checks."
            if sub == "config" and any(x in a for x in ("core.hookspath", "core.sshcommand",
                                                         "core.pager", "core.editor",
                                                         "credential.helper")):
                return "ask", "Changes a git setting that can run commands or handle passwords."

        if prog == "rm" and any(x.startswith("-") and "r" in x for x in a):
            targets = [x for x in args if not x.startswith("-")]
            if any(t in ("/", "~", "~/", "*", ".", "..") or t.startswith(("/", "~", ".."))
                   for t in targets):
                return "ask", f"Deletes folders outside this repo or the whole repo: {' '.join(targets)}"

        reason = check_install(prog, args, cwd)
        if reason:
            return "ask", (f"This {reason}. New packages can run code when installed. "
                           "Approve only if you or the approved plan asked for it.")

        if prog in ("chmod",) and any("+s" in x for x in a):
            return "ask", "Sets a file to run with raised rights (setuid)."

    return None, None


# --- Main -------------------------------------------------------------------

def decide(event):
    tool = event.get("tool_name", "")
    ti = event.get("tool_input", {}) or {}
    cwd = event.get("cwd", "")

    if tool == "Bash":
        return check_bash(ti.get("command", ""), cwd)

    if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        level = secret_level(path)
        if level == "deny":
            return "deny", (f"`{os.path.basename(path)}` holds secrets. Secrets must not go into "
                            "AI tools (Neighborly AI policy). Refer to settings by name only, "
                            "or use the `.env.example` file.")
        if level == "ask":
            return "ask", (f"`{os.path.basename(path)}` often holds secrets or tokens. "
                           "Approve only if it has none.")
        if tool != "Read":
            label = control_file(path)
            if label:
                return "ask", (f"This edits {label}: `{norm(path)}`. Planted text in a ticket "
                               "or PR may try to change it. Approve only if you asked for this.")
        return None, None

    if tool in ("Grep", "Glob"):
        path = ti.get("path", "")
        if secret_level(path) == "deny":
            return "deny", f"`{os.path.basename(path)}` holds secrets. Search other files."
        return None, None

    return None, None


def main():
    if os.environ.get("AI_SAM_GUARD", "").lower() in ("off", "0", "false"):
        return 0
    try:
        event = json.load(sys.stdin)
        decision, reason = decide(event)
    except Exception as exc:  # never break the session because of the guard
        print(f"ai-sam guard skipped a check: {exc}", file=sys.stderr)
        return 0
    if decision:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": f"ai-sam guard: {reason}",
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
