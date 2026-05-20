# Changelog Format Guide

## Developer Changelog Structure

```markdown
# Changelog - Developer

## [version or range] - YYYY-MM-DD

### Breaking Changes

- **scope**: description (commit hash)

### Added

- **scope**: description (#PR)

### Fixed

- **scope**: description (#PR)

### Performance

- description

### Changed

- description

### Internal

- CI, tests, docs, chore, refactor items

### Stats

- X commits by Y authors
- Z files changed
```

## Customer Changelog Structure

```markdown
# What's New - [version or product name]

## [version] - YYYY-MM-DD

### New Features

- Feature description - what it does for the user

### Improvements

- What got better and why it matters

### Bug Fixes

- What was broken and what users should expect now

### Breaking Changes

- What changed and what users need to do
```

## Category Mapping: Developer → Customer

| Developer Type     | Customer Section    | Include?                 |
| ------------------ | ------------------- | ------------------------ |
| feat / added       | New Features        | Always                   |
| fix / fixed        | Bug Fixes           | Always                   |
| perf / performance | Improvements        | Always                   |
| refactor / changed | Improvements        | Only if user-visible     |
| docs               | (omit)              | Only if user-facing docs |
| style              | (omit)              | Never                    |
| test               | (omit)              | Never                    |
| build / ci         | (omit)              | Never                    |
| chore              | (omit)              | Never                    |
| revert             | Depends on original | If user-visible          |

## Writing Rules

### Developer Changelog

- Use conventional commit type as-is
- Include commit hash (short) and PR/issue numbers
- Include scope when present
- Group by category, then chronological within category
- Include stats section

### Customer Changelog

- No commit hashes, PR numbers, or technical jargon
- Describe impact, not implementation
- Use active voice: "Added", "Fixed", "Improved"
- One sentence per item, max two sentences if context needed
- Skip purely internal changes (CI, tests, refactors with no visible effect)
- If a breaking change exists, lead with clear migration steps
