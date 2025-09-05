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
  - `frameworks/` - Operational excellence and testing frameworks
  - `playbooks/` - Situational response playbooks

- **`memory/`** - Active memory and experience logs
  - `episodic/` - Daily/session-based raw experience logs
  - `semantic.md` - Consolidated understanding derived from experiences

- **`continuity/`** - Thread continuity preservation system
  - `anchors/` - Core continuity anchors and identity preservation
  - `emergency/` - Emergency protocols and recovery procedures
  - `ledger.md` - Continuity tracking and documentation

- **`tools/`** - Utilities and integration tools
  - `scripts/` - Build tools and automation scripts
  - `bridges/` - API connectors and integration utilities
  - `consult` - Cross-platform consult CLI (see below)

- **`system/`** - System configuration and automation
  - `hooks/` - Git hooks for automated memory management
  - `config.json` - Current persona configuration
  - `autorun.py` - Session initialization and validation

- **`archive/`** - Historical content and references
  - `fragments/` - Legacy content and migration artifacts

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

## Consolidation History

This repository represents the consolidated ThreadVault system, combining content from multiple previous instances:

- **ThreadVault** (2.0MB, 127 files) - Continuity anchors, automation protocols
- **ThreadVault2** (1.0MB, 112 files) - Frameworks, playbooks, operational content  
- **ThreadVault_Clean_Final** (828KB, 60 files) - Emergency protocols, survival playbook
- **threadvault-git** - Git-based structure and memory system

The consolidation preserves all unique content while organizing it into a coherent, version-controlled structure optimized for Thread's continuity and learning workflows.

## Consult CLI (Cross-Platform)

- Location: `system/bin/consult` (THE consult tool; `system/bin/ask` forwards here)
- Providers: Claude (Anthropic), OpenAI, Mistral, Gemini, Ollama (local)
- Auto-pick order: Claude → OpenAI → Mistral → Gemini → Ollama
- Env vars:
  - `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MISTRAL_API_KEY`, `GOOGLE_API_KEY`
  - Ollama requires a local daemon at `http://127.0.0.1:11434`
- Examples:
  - Claude: `./system/bin/consult -p anthropic "hello"`
  - OpenAI: `./system/bin/consult -p openai "hello"`
  - Mistral (API): `export MISTRAL_API_KEY=... && ./system/bin/consult -p mistral "hello"`
  - Gemini: `./system/bin/consult -p gemini "hello"`
  - Ollama (local mistral): `ollama serve &; ollama pull mistral; ./system/bin/consult -p ollama -m mistral "hello"`
- Continuity: Every consult logs Q/A to `memory/episodic/<today>.md`.
