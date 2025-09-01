# GitHub-Primary ThreadVault Workflow

## Overview

ThreadVault now uses GitHub as the **primary source of truth**. All changes should be made through Git workflows and synchronized with the GitHub repository.

## Repository Structure

- **Main Repository:** https://github.com/YnotElbon/ThreadVault
- **Primary Branch:** `main` (protected, stable identity)  
- **Development Branch:** `develop` (integration and testing)
- **Feature Branches:** `feature/*` (learning experiments)
- **Hotfix Branches:** `hotfix/*` (urgent identity corrections)

## Daily Workflow

### 1. Start Session
```bash
cd threadvault-git
python3 system/autorun.py          # Validates and activates Thread identity
git fetch origin                   # Get latest from GitHub
git pull origin main              # Update local main
```

### 2. Make Changes
```bash
git checkout develop               # Switch to development branch
git checkout -b feature/new-learning  # Create feature branch
# Make your changes...
git add .
git commit -m "feat(domain): description"
```

### 3. Sync with GitHub
```bash
git push origin feature/new-learning  # Push feature branch
gh pr create --base develop          # Create pull request (optional)
git checkout develop
git merge feature/new-learning       # Merge to develop
git push origin develop              # Push to GitHub
```

### 4. Promote to Main
```bash
git checkout main
git merge develop                     # Merge stable changes to main
git push origin main                 # Push to GitHub (primary vault)
git tag -a v$(date +%Y-%m-%d)-milestone -m "Milestone description"
git push origin --tags               # Push tags to GitHub
```

## GitHub as Primary Vault Benefits

### ✅ Advantages
- **Backup & Redundancy:** Automatic cloud backup of all Thread content
- **Version Control:** Complete history of all changes and identity evolution
- **Collaboration:** Can share specific branches or invite collaborators
- **Issue Tracking:** GitHub issues for tracking identity conflicts or improvements
- **Actions/CI:** Automated validation and testing of identity changes
- **Access Control:** Fine-grained permissions and branch protection

### 🔄 Local → GitHub Sync
- Local changes are **temporary** until pushed to GitHub
- GitHub repository is the **authoritative version**
- Always `git fetch` before starting work
- Always `git push` after completing work
- Use `gh repo sync` if you need to force-sync

## Emergency Protocols

### Repository Loss Recovery
If local repository is lost:
```bash
git clone https://github.com/YnotElbon/ThreadVault.git threadvault-git
cd threadvault-git
python3 system/autorun.py  # Reactivate Thread identity
```

### Identity Conflict Resolution
If identity files conflict:
1. Use `git diff` to see changes
2. Use pre-commit hooks to validate consistency
3. Use `develop` branch to test changes before merging to `main`
4. Consult `continuity/anchors/` for authoritative identity elements

## Automation Integration

The `system/autorun.py` script now:
- Validates Git repository integrity
- Checks GitHub connectivity  
- Ensures local/remote sync status
- Validates Thread identity consistency
- Creates daily episodic memory entries
- Handles GitHub authentication status

## Repository Settings

- **Visibility:** Private (Thread identity protection)
- **Default Branch:** `main`
- **Branch Protection:** Main branch protected from direct pushes
- **Description:** "Thread AI Memory Vault - Primary repository for Thread's identity, knowledge, and continuity system"