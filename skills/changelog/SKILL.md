---
name: changelog
description: "Generate changelogs from git history for both developer and customer audiences. Parses conventional commits, extracts PR/issue references, and produces two markdown files: a detailed developer changelog and a user-friendly customer changelog. Use when the user asks to generate a changelog, release notes, what's new, or summarize changes between versions/commits/tags."
---

# Changelog Generator

Generate dual-audience changelogs (developer + customer) from git history.

## Workflow

1. Run the data extraction script to collect commit data
2. Review the JSON output for accuracy
3. Generate both changelog files using the format guide

## Step 1: Extract Commit Data

Run the extraction script from the project root:

```bash
python3 ~/.claude/skills/changelog/scripts/generate_changelog.py --repo . [--from REF] [--to REF]
```

- If user specifies a range, pass `--from` and `--to`
- If user specifies only a version/tag, use `--from <previous-tag> --to <tag>`
- If no range given, the script auto-detects from the previous tag to HEAD
- If no tags exist, it uses the root commit to HEAD

The script outputs JSON with: commit metadata, conventional commit parsing, PR/issue references, file change lists, and summary statistics.

## Step 2: Generate Changelogs

Read [references/format_guide.md](references/format_guide.md) for the exact structure and writing rules.

Generate or update two files in the project root (or user-specified location):

### `CHANGELOG.md` — Developer Changelog
- Full technical detail with commit hashes and PR links
- All commit categories included
- Stats section at bottom

### `CHANGELOG-customer.md` — Customer Changelog
- User-facing language only
- Skip internal changes (CI, tests, chore, style)
- Describe impact, not implementation
- No commit hashes or PR numbers unless the project has a public issue tracker

### Merging with Existing Changelogs

When changelog files already exist:

1. **Read the existing file** before generating
2. **Identify the last recorded commit hash or date** in the existing changelog
3. **Only generate entries for new commits** not already covered — use commit hashes as the source of truth, not dates
4. **Prepend the new date section** above existing entries, preserving the file header
5. **Never modify, replace, or update existing date entries** — each run produces a new `## [version] — YYYY-MM-DD` block for today's new commits only
6. If there are no new commits since the last entry, inform the user and do not modify the file

**Correct structure after multiple runs:**
```markdown
# Changelog — Developer

## 2026-03-17

### Added
- new feature today

## 2026-03-16

### Fixed
- yesterday's bugfix

## 2026-03-14

### Added
- feature from last week
```

**Wrong behavior:** Updating the `2026-03-16` entry to say `2026-03-17` and merging new commits into it. Each date section is immutable once written.

## Handling Edge Cases

- **Non-conventional commits**: Categorize as "other", use best judgment to place in developer changelog. For customer changelog, include only if clearly user-facing.
- **Merge commits**: Skip merge commits that are just branch merges (no content). Include squash merges.
- **Monorepo**: If the repo has multiple packages/services, group by scope or directory.
- **No tags**: Use commit range or full history. Title with date range instead of version.
- **Mixed quality commits**: Clean up wording for customer changelog. Developer changelog preserves original commit messages.
