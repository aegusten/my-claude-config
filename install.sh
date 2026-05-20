#!/bin/bash
# install.sh - Run on Linux/Mac to symlink Claude config
# Usage: bash install.sh

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "🤖 Setting up Claude config for aegusten..."
echo "Repo: $REPO_DIR"
echo "Target: $CLAUDE_DIR"
echo ""

mkdir -p "$CLAUDE_DIR"

link_item() {
    local source="$1"
    local target="$2"
    rm -rf "$target"
    ln -s "$source" "$target"
    echo "✅ Linked: $target → $source"
}

link_item "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
link_item "$REPO_DIR/agents"    "$CLAUDE_DIR/agents"
link_item "$REPO_DIR/skills"    "$CLAUDE_DIR/skills"

echo ""
echo "✅ Done! Run 'claude' in any project to start."
echo "💡 Your agents: senior-backend, senior-architect, security-reviewer, code-reviewer"
