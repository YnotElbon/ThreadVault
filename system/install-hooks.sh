#!/bin/bash
"""
ThreadVault Git Hooks Installation Script
Links system hooks to .git/hooks directory
"""

set -e

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SOURCE_DIR="$REPO_ROOT/system/hooks"
HOOKS_TARGET_DIR="$REPO_ROOT/.git/hooks"

echo "🔧 Installing ThreadVault Git Hooks"
echo "=================================="

# Check if we're in a git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_TARGET_DIR"

# Install each hook
for hook in "$HOOKS_SOURCE_DIR"/*; do
    if [ -f "$hook" ] && [ -x "$hook" ]; then
        hook_name=$(basename "$hook")
        target_hook="$HOOKS_TARGET_DIR/$hook_name"
        
        echo "📋 Installing $hook_name..."
        
        # Backup existing hook if it exists
        if [ -f "$target_hook" ]; then
            echo "  📦 Backing up existing hook to $target_hook.backup"
            mv "$target_hook" "$target_hook.backup"
        fi
        
        # Link the hook
        ln -sf "$hook" "$target_hook"
        chmod +x "$target_hook"
        
        echo "  ✅ $hook_name installed and executable"
    fi
done

echo ""
echo "🎉 Git hooks installation completed!"
echo ""
echo "Installed hooks:"
ls -la "$HOOKS_TARGET_DIR" | grep -v "backup" | grep -v "sample"
echo ""
echo "💡 Hooks will now run automatically on git operations"
echo "   • pre-commit: Validates memory integrity before commits"
echo "   • post-merge: Triggers consolidation and reflection after merges"