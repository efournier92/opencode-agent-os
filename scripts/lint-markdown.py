#!/usr/bin/env python3
"""Markdown style lint for the agent plugin tree.

Enforces the "Markdown Style" section of AGENTS.md:

  1. No em dashes, en dashes, arrows, ellipsis, or smart/curly quotes in
     prose. Inline code spans, fenced code blocks, and blockquote lines
     (verbatim quotes) are exempt.
  2. Every ATX heading (# .. ######) is followed by a blank line.
  3. No sentence is split across source lines. A prose or list line that
     ends without sentence-final punctuation and continues on the next
     line is a wrapped sentence.
  4. No banned LLM-artifact phrases ("delve", "furthermore", ...) in
     prose. Inline code spans, fenced code blocks, and YAML frontmatter
      are exempt, matching rule 1.

Rule 5 of AGENTS.md (title case for titles and headings) is
review-enforced and is not checked here, because proper nouns and
acronyms are hard to detect automatically.

Exit code 0 = clean, 1 = violations found.
"""

import re
import sys
from pathlib import Path

BANNED = "\u2014\u2013\u2026\u2192\u2190\u21d2\u201c\u201d\u2018\u2019"
BANNED_PHRASES = [
    "delve",
    "furthermore",
    "moreover",
    "it's worth noting",
    "in conclusion",
    "notably",
    "seamless",
    "robust",
    "leverage",
    "as an AI",
    "I'd be happy to",
]
BANNED_PHRASE_PATTERNS = [
    (phrase, re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE))
    for phrase in BANNED_PHRASES
]
HEADER_RE = re.compile(r"^#{1,6} ")
FENCE_RE = re.compile(r"^```")
INLINE_CODE_RE = re.compile(r"(`[^`]*`)")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
SENTENCE_END_RE = re.compile(r'[.!?:;]["\')\]]*$')


def is_list_item(line):
    return LIST_ITEM_RE.match(line) is not None


def lint_file(path):
    errors = []
    lines = path.read_text().split("\n")
    in_fence = False
    in_frontmatter = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if i == 0 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if FENCE_RE.match(stripped):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not raw.strip():
            continue
        if stripped.startswith(">"):
            continue
        if stripped.startswith("|"):
            continue
        prose_parts = INLINE_CODE_RE.split(raw)[::2]
        if any(any(ch in BANNED for ch in prose) for prose in prose_parts):
            errors.append(f"{path}:{i+1}: banned character in prose")
        for phrase, pat in BANNED_PHRASE_PATTERNS:
            if any(pat.search(prose) for prose in prose_parts):
                errors.append(f"{path}:{i+1}: banned phrase '{phrase}'")
        if HEADER_RE.match(raw):
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            if nxt is None or nxt.strip() != "":
                errors.append(f"{path}:{i+1}: heading must be followed by a blank line")
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if nxt.strip() == "":
            continue
        if is_list_item(nxt) or HEADER_RE.match(nxt) or nxt.strip().startswith((">", "|", "```")):
            continue
        if not SENTENCE_END_RE.search(raw.rstrip()):
            errors.append(f"{path}:{i+1}: sentence split across lines")
    return errors


def main(argv):
    targets = [Path(a) for a in argv] if argv else [Path(".")]
    files = []
    for t in targets:
        if t.is_dir():
            files.extend(t.rglob("*.md"))
        else:
            files.append(t)
    files = sorted(set(files))
    errors = []
    for f in files:
        errors.extend(lint_file(f))
    for e in errors:
        print(e)
    if errors:
        bad_files = len(set(e.split(":")[0] for e in errors))
        print(f"\n{len(errors)} violation(s) across {bad_files} file(s)")
        return 1
    print("markdown lint clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
