# ThreadVault Git - AI Memory System

A Git-based memory and continuity system for AI assistants, evolved from the original ThreadVault folder structure.

## Architecture

### Directory Structure

- **`identity/`** - Core identity and ethical foundations (rarely changed)
  - `kernel.md` - Core personality and identity definition
  - `ethics.md` - Ethical doctrine and invariants

- **`knowledge/`** - Structured information and learned skills
  - `facts.json` - Discrete, verified facts
  - `skills/` - Learned capabilities and code snippets

- **`memory/`** - Active memory and experience logs
  - `episodic/` - Daily/session-based raw experience logs
  - `semantic.md` - Consolidated understanding derived from experiences

- **`system/`** - System configuration and automation
  - `hooks/` - Git hooks for automated memory management
  - `config.json` - Current persona configuration

## Memory Workflows

### Daily Cycle
1. **Experience** - AI has interactions/processes data
2. **Logging** - Raw experiences appended to `memory/episodic/`
3. **Consolidation** - Batch commit with structured semantic updates
4. **Reflection** - Post-commit hooks trigger validation and integration

### Branching Strategy
- **`main`** - Stable, canonical identity (protected)
- **`develop`** - Integration testing branch
- **`feature/*`** - Learning experiments and skill acquisition
- **`hotfix/*`** - Urgent corrections to core identity/ethics

### Commit Message Format
- `feat(domain): description` - New capabilities or knowledge
- `fix(domain): description` - Corrections to existing memory
- `chore(memory): description` - Routine consolidation
- `docs(domain): description` - Documentation updates

## Git Hooks

### Pre-commit
- Validates markdown/JSON syntax
- Checks for contradictions in identity/ethics
- Prevents corrupted memory commits

### Post-merge
- Triggers self-reflection process
- Updates consolidated knowledge
- Validates memory integrity

## Migration from ThreadVault2

Files from the original folder structure are mapped as follows:
- `Anchors/` → `identity/`
- `Doctrine/` → `identity/ethics.md`
- `Bundles/` → Git tags for milestone states
- `Sandbox/` → `feature/*` branches

## Usage

### Initialize new memory session
```bash
git checkout develop
git checkout -b feature/learn-topic
# Make learning commits
git checkout develop
git merge feature/learn-topic
```

### Create memory milestone
```bash
git tag -a v$(date +%Y-%m-%d)-milestone -m "Milestone: learned X"
```

### Review memory history
```bash
git log --oneline --graph
git show --stat TAG_NAME
```

## Tags and Releases

Major milestones and identity updates are tagged with semantic versioning:
- `v2025-08-31-baseline` - Initial migration from ThreadVault2
- `v2025-09-01-learning-X` - After acquiring new capability X
- `v2025-09-02-ethics-update` - After ethical reasoning evolution

Each tag represents a complete, self-contained memory state that can be restored.