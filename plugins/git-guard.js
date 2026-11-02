const OVERRIDE_TOKEN = "OPENCODE_GIT_GUARD=0";

const OVERRIDE_SUFFIX = /#\s*git-guard:\s*allow\s*$/;
const SEGMENT_SEP = /&&|\|\||;|\||\n/;
const SHELLS = new Set(["bash", "sh", "zsh", "dash", "ksh"]);

function isOverride(command) {
  const trimmed = command.trim();
  return trimmed.startsWith(OVERRIDE_TOKEN) || OVERRIDE_SUFFIX.test(trimmed);
}

// Quotes are stripped so "--hard" and '--hard' compare as --hard.
function tokenize(text) {
  const tokens = [];
  let current = "";
  let quote = null;
  for (const ch of text) {
    if (quote) {
      if (ch === quote) quote = null;
      else current += ch;
    } else if (ch === '"' || ch === "'") {
      quote = ch;
    } else if (/\s/.test(ch)) {
      if (current) {
        tokens.push(current);
        current = "";
      }
    } else {
      current += ch;
    }
  }
  if (current) tokens.push(current);
  return tokens;
}

function basename(token) {
  return token.split("/").pop();
}

function shortFlagHas(flags, letter) {
  return flags.some((t) => /^-[A-Za-z]+$/.test(t) && t.slice(1).includes(letter));
}

function block(rule) {
  return { rule, message: rule + " (set " + OVERRIDE_TOKEN + " to override)." };
}

function checkGit(args) {
  let i = 0;
  while (i < args.length) {
    const a = args[i];
    if (a === "--no-pager") i += 1;
    else if (a === "-C" || a === "-c" || a === "--git-dir" || a === "--work-tree") i += 2;
    else if (/^(--(git-dir|work-tree)=|-C|-c)/.test(a)) i += 1;
    else break;
  }
  const sub = args[i];
  const flags = args.slice(i + 1);

  if (sub === "reset" && flags.includes("--hard")) return block("git reset --hard");
  if (sub === "clean" && (flags.includes("--force") || shortFlagHas(flags, "f"))) {
    return block("git clean -f deletes untracked files");
  }
  if (sub === "checkout" && (flags.includes("--") || flags.includes("."))) {
    return block("git checkout -- or . discards local changes");
  }
  if (sub === "restore" && !flags.includes("--staged")) {
    return block("git restore discards local changes");
  }
  if (sub === "stash") {
    if (flags[0] === "clear") return block("git stash clear deletes every stash");
    if (flags[0] === "drop") return block("git stash drop deletes a stash");
    if (flags[0] === "pop") return block("git stash pop drops a stash, use git stash apply");
  }
  if (sub === "commit") {
    if (flags.includes("--amend")) return block("git commit --amend rewrites history");
    if (flags.includes("--all") || shortFlagHas(flags, "a")) {
      return block("git commit -a stages files implicitly, stage exact paths");
    }
  }
  if (sub === "add") {
    if (flags.includes("-A") || flags.includes("--all") || flags.includes(".")) {
      return block("git add -A or . stages everything, stage exact paths");
    }
  }
  if (sub === "push") {
    const forced =
      flags.includes("--force") ||
      flags.includes("--force-with-lease") ||
      flags.includes("--mirror") ||
      shortFlagHas(flags, "f") ||
      flags.some((t) => t.startsWith("+") || t.startsWith("--force-with-lease="));
    if (forced) return block("git push force or mirror overwrites remote history");
  }
  return null;
}

function inspect(segment) {
  const tokens = tokenize(segment);
  if (tokens.includes("--no-verify")) return block("--no-verify skips hooks");

  for (let i = 0; i < tokens.length; i += 1) {
    const name = basename(tokens[i]);
    if (SHELLS.has(name) && tokens[i + 1] === "-c") {
      const verdict = inspect(tokens.slice(i + 2).join(" "));
      if (verdict) return verdict;
    }
    if (name === "git") return checkGit(tokens.slice(i + 1));
  }
  if (basename(tokens[0]) === "gh" && tokens[1] === "pr" && tokens[2] === "merge" && tokens.includes("--admin")) {
    return block("gh pr merge --admin bypasses branch protection");
  }
  return null;
}

export function classify(command) {
  // The plugin loader calls every export with its context, so a non-string call returns empty hooks.
  if (typeof command !== "string") return {};
  if (isOverride(command)) return null;
  for (const segment of command.split(SEGMENT_SEP)) {
    const verdict = inspect(segment);
    if (verdict) return verdict;
  }
  return null;
}

export const GitGuard = async () => ({
  "tool.execute.before": async (input, output) => {
    if (input.tool !== "bash") return;
    const command = output?.args?.command;
    if (typeof command !== "string") return;
    let verdict;
    try {
      verdict = classify(command);
    } catch {
      return;
    }
    if (verdict) {
      throw new Error(
        "BLOCKED by git-guard: " + verdict.message + " Override: prefix the command with OPENCODE_GIT_GUARD=0.",
      );
    }
  },
});
