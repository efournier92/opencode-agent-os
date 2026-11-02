# Markdown Style (Every Agent, Every File)

Applies to every Markdown file an agent writes or edits: specs, handoffs, memory entries, docs, skill content, and pasted text blocks, plus any Markdown an agent posts, such as a PR or issue body.
The instruction docs themselves comply with these rules, except that headings predating rule 6 are corrected when each file is next edited.

1. **No em dashes, en dashes, or typographic special characters.**
   - No long or medium dashes, no arrows, no ellipsis (`…`) in prose.
   - Always use straight quotes and apostrophes (`"`, `'`). Never smart or curly quotes (`“`, `”`, `‘`, `’`).
   - Use a comma, a colon, or split the sentence.
   - Exception: verbatim quotes or code you did not write keep their original characters.
2. **No obvious LLM artifacts.**
   - Avoid the telltale AI phrasing: `delve`, `furthermore`, `moreover`, `it's worth noting`, `in conclusion`, `notably`, `seamless`, `robust`, `leverage` as filler, `as an AI`, `I'd be happy to`.
   - Write like a careful human: short sentences, concrete words, edit once.
3. **Blank line after every heading.**
   - Always. Every heading, `#` through `######`, is followed by one empty line before the first body line, no exceptions.
   - Never put text on the line directly after a heading, in any Markdown an agent produces.
4. **Never split a sentence across lines.**
   - A sentence stays on one line in the source. No line breaks mid-sentence for width.
   - Favor point form: each bullet is a short, full sentence ending in a period.
   - Split extra clauses into nested sub-bullets.
   - Use an ordered list when order matters, or use a bulleted list when it does not.
5. **Short Sentences, Periods, Not Semicolons.**
   - Break a semicolon into two sentences. A period is the default.
   - A semicolon in prose reads as machine-written, because LLMs use it to join two thoughts without ending either one.
   - When the halves are too close for a full stop, use a colon when the second explains the first, or a comma plus `and`, `but`, or `so`.
   - Do not use a semicolon as a compact separator inside a bullet either. Give the bullet one short sentence, or nest sub-bullets (rule 4).
   - Exempt: inline code spans, fenced code blocks, and verbatim quotes.
6. **Capitalize Every Word In Titles And Headings.**
   - Every word in a title or heading (`#` through `######`) starts with a capital letter, including short words such as `a`, `of`, `the`, and `and`.
   - This covers the document title (the H1) and every header below it.
   - Fenced code blocks, quoted text, and inline code spans are exempt, so apply the rule to the heading line's own words.
   - This rule is review-enforced, so the linter does not check it, because proper nouns and acronyms are hard to detect automatically.
   - Existing headings that violate it are corrected when the file is next edited, not in a mass rewrite.

Enforcement: when a Markdown file is the deliverable (spec, handoff, doc), the verification step runs `scripts/lint-markdown.py` against it before PASS.
The linter machine-checks five rules: banned characters and smart quotes, banned LLM-artifact phrases, a blank line after every heading, sentences split across lines, and no semicolon in prose.
Existing semicolon violations are grandfathered in `scripts/markdown-semicolon-baseline.txt`, and a file must drop to zero semicolons the next time it is edited, lowering its baseline entry with `--write-semicolon-baseline`.
Rule 6 (title case) is review-enforced, so the verification step checks headings by eye.
Inline code spans, fenced code blocks, YAML frontmatter, and blockquote lines are exempt, so verbatim quotes stay legal.
The scripts live in the plugin repository under `scripts/`, so run them from the repository checkout, because the installer copies agents, skills, `AGENTS.md`, and `docs/rulebook/` into the config directory but not the scripts.
