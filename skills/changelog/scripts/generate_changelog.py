#!/usr/bin/env python3
"""
Generate structured changelog data from git history.

Outputs JSON with categorized commits between two refs (tags, commits, branches).
Supports conventional commits parsing and PR/issue reference extraction.

Usage:
    python3 generate_changelog.py [--from REF] [--to REF] [--repo PATH]

If --from is omitted, uses the previous tag (or root commit if no tags).
If --to is omitted, uses HEAD.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Commit:
    hash: str
    short_hash: str
    author: str
    date: str
    subject: str
    body: str
    type: str = "other"
    scope: Optional[str] = None
    breaking: bool = False
    pr_numbers: list = field(default_factory=list)
    issue_numbers: list = field(default_factory=list)
    files_changed: list = field(default_factory=list)


# Conventional commit pattern: type(scope)!: description
CC_PATTERN = re.compile(
    r'^(?P<type>\w+)'
    r'(?:\((?P<scope>[^)]+)\))?'
    r'(?P<breaking>!)?'
    r':\s*(?P<description>.+)$'
)

# PR/issue references
PR_PATTERN = re.compile(r'#(\d+)')
BREAKING_FOOTER = re.compile(r'^BREAKING[ -]CHANGE:', re.MULTILINE)

# Map conventional commit types to categories
TYPE_MAP = {
    'feat': 'added',
    'fix': 'fixed',
    'perf': 'performance',
    'refactor': 'changed',
    'docs': 'docs',
    'style': 'style',
    'test': 'tests',
    'build': 'build',
    'ci': 'ci',
    'chore': 'chore',
    'revert': 'reverted',
}


def run_git(args: list[str], repo: str = '.') -> str:
    result = subprocess.run(
        ['git', '-C', repo] + args,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"git error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_previous_tag(repo: str, ref: str = 'HEAD') -> Optional[str]:
    """Find the most recent tag before the given ref."""
    try:
        result = subprocess.run(
            ['git', '-C', repo, 'describe', '--tags', '--abbrev=0', f'{ref}^'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_root_commit(repo: str) -> str:
    return run_git(['rev-list', '--max-parents=0', 'HEAD'], repo).split('\n')[0]


def get_tag_list(repo: str) -> list[str]:
    """Get all tags sorted by date."""
    result = subprocess.run(
        ['git', '-C', repo, 'tag', '--sort=-creatordate'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return [t for t in result.stdout.strip().split('\n') if t]
    return []


def get_files_changed(repo: str, commit_hash: str) -> list[str]:
    result = subprocess.run(
        ['git', '-C', repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return [f for f in result.stdout.strip().split('\n') if f]
    return []


def parse_commit(raw: str, repo: str) -> Commit:
    """Parse a single commit from git log --format output."""
    lines = raw.split('\n')
    hash_full = lines[0]
    short_hash = lines[1]
    author = lines[2]
    date = lines[3]
    subject = lines[4]
    body = '\n'.join(lines[5:]).strip()

    commit = Commit(
        hash=hash_full,
        short_hash=short_hash,
        author=author,
        date=date,
        subject=subject,
        body=body,
    )

    # Parse conventional commit
    match = CC_PATTERN.match(subject)
    if match:
        cc_type = match.group('type').lower()
        commit.type = TYPE_MAP.get(cc_type, cc_type)
        commit.scope = match.group('scope')
        commit.breaking = bool(match.group('breaking'))

    # Check body for BREAKING CHANGE footer
    if BREAKING_FOOTER.search(body):
        commit.breaking = True

    # Extract PR/issue refs from subject + body
    all_text = f"{subject}\n{body}"
    commit.pr_numbers = list(set(PR_PATTERN.findall(all_text)))
    commit.issue_numbers = commit.pr_numbers  # GitHub uses same # syntax

    # Get files changed
    commit.files_changed = get_files_changed(repo, hash_full)

    return commit


def get_commits(repo: str, from_ref: str, to_ref: str) -> list[Commit]:
    """Get all commits between two refs."""
    separator = '---COMMIT_SEP---'
    fmt = f'%H%n%h%n%an%n%as%n%s%n%b{separator}'

    log_range = f'{from_ref}..{to_ref}'
    raw = run_git(['log', '--format=' + fmt, log_range], repo)

    if not raw:
        return []

    commits = []
    for chunk in raw.split(separator):
        chunk = chunk.strip()
        if not chunk:
            continue
        # Ensure we have at least 5 lines (hash, short, author, date, subject)
        lines = chunk.split('\n')
        if len(lines) >= 5:
            commits.append(parse_commit(chunk, repo))

    return commits


def categorize(commits: list[Commit]) -> dict:
    """Group commits by category."""
    categories = {}
    for c in commits:
        cat = c.type
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(asdict(c))
    return categories


def get_stats(commits: list[Commit]) -> dict:
    """Compute summary statistics."""
    all_files = set()
    authors = set()
    breaking_count = 0
    for c in commits:
        all_files.update(c.files_changed)
        authors.add(c.author)
        if c.breaking:
            breaking_count += 1

    return {
        'total_commits': len(commits),
        'unique_authors': list(authors),
        'files_changed': len(all_files),
        'breaking_changes': breaking_count,
    }


def main():
    parser = argparse.ArgumentParser(description='Generate changelog data from git history')
    parser.add_argument('--from', dest='from_ref', help='Start ref (tag/commit/branch)')
    parser.add_argument('--to', dest='to_ref', default='HEAD', help='End ref (default: HEAD)')
    parser.add_argument('--repo', default='.', help='Repository path (default: current dir)')
    args = parser.parse_args()

    repo = args.repo
    to_ref = args.to_ref

    # Determine from_ref
    if args.from_ref:
        from_ref = args.from_ref
    else:
        from_ref = get_previous_tag(repo, to_ref)
        if not from_ref:
            from_ref = get_root_commit(repo)

    commits = get_commits(repo, from_ref, to_ref)
    tags = get_tag_list(repo)

    output = {
        'from': from_ref,
        'to': to_ref,
        'tags': tags[:10],  # Recent tags for context
        'stats': get_stats(commits),
        'categories': categorize(commits),
        'commits': [asdict(c) for c in commits],
    }

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
