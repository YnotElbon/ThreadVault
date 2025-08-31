#!/usr/bin/env python3
"""
Migration script to import ThreadVault2 content into Git-based system
Preserves history through structured commits and proper file mapping
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import re

# Configuration
THREADVAULT2_PATH = Path("../ThreadVault2")  
CURRENT_REPO = Path(".")

def run_git_cmd(cmd, check=True):
    """Run git command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        if check:
            print(f"Git command failed: {cmd}")
            print(f"Error: {e.stderr}")
            raise
        return False, "", e.stderr

def extract_date_from_filename(filename):
    """Extract date from filename patterns like 'ThreadVault_004_update_log_2025-08-08.md'"""
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(date_pattern, filename)
    if match:
        return match.group(1)
    return None

def categorize_threadvault_file(filepath):
    """Categorize ThreadVault2 files into new structure"""
    path_str = str(filepath).lower()
    filename = filepath.name.lower()
    
    # Identity files
    if any(term in filename for term in ['kernel', 'personality', 'identity']):
        return 'identity', 'kernel.md'
    if any(term in filename for term in ['ethics', 'kill_switch']):
        return 'identity', 'ethics.md'
    
    # Knowledge files  
    if any(term in filename for term in ['facts', 'skills', 'capabilities']):
        return 'knowledge', f"skills/{filepath.stem}.md"
    
    # Memory files
    if 'episodic' in path_str or 'fragments' in path_str:
        date = extract_date_from_filename(filename) or datetime.now().strftime('%Y-%m-%d')
        return 'memory', f"episodic/{date}.md"
    
    if any(term in filename for term in ['continuity', 'manifest', 'checkpoint']):
        return 'memory', 'semantic.md'
    
    # Archive everything else
    return 'archive', f"threadvault2_legacy/{filepath.parent.name}/{filepath.name}"

def migrate_file_content(source_file, target_category, target_filename):
    """Migrate and adapt file content for new structure"""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add migration header
    migration_header = f"""<!-- Migrated from ThreadVault2: {source_file} -->
<!-- Migration date: {datetime.now().isoformat()} -->
<!-- Target: {target_category}/{target_filename} -->

"""
    
    # Category-specific adaptations
    if target_category == 'identity':
        # Preserve identity content but add Git-specific structure
        if 'kernel' in target_filename:
            content = adapt_kernel_content(content)
        elif 'ethics' in target_filename:
            content = adapt_ethics_content(content)
    
    elif target_category == 'memory' and 'episodic' in target_filename:
        # Structure episodic memories
        content = adapt_episodic_content(content, source_file)
    
    elif target_category == 'memory' and 'semantic' in target_filename:
        # Consolidate semantic content
        content = adapt_semantic_content(content, source_file)
    
    return migration_header + content

def adapt_kernel_content(content):
    """Adapt kernel content for Git structure"""
    # Preserve existing content but ensure Git-compatible structure
    if "Memory Architecture Principles" not in content:
        content += "\n\n## Memory Architecture Principles\n\n"
        content += "- **Atomic Learning** — Each significant update is a single Git commit\n"
        content += "- **Experimental Safety** — Use feature branches for risky learning\n" 
        content += "- **Version Integrity** — All memory states are cryptographically verifiable\n"
        content += "- **Autonomous Backup** — Critical milestones auto-generate tagged snapshots\n"
    
    return content

def adapt_ethics_content(content):
    """Adapt ethics content for Git structure"""
    # Add Git-specific ethics considerations if not present
    if "Version Control Ethics" not in content:
        content += "\n\n## Version Control Ethics\n\n"
        content += "- All significant ethical decisions are logged with reasoning\n"
        content += "- Identity modifications require staging branch validation\n"
        content += "- Critical updates trigger comprehensive ethical self-reflection\n"
    
    return content

def adapt_episodic_content(content, source_file):
    """Adapt episodic content with migration context"""
    header = f"# Episodic Memory - Migrated Content\n\n"
    header += f"**Source**: {source_file.name}\n"
    header += f"**Migration Date**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    header += "---\n\n"
    
    return header + content

def adapt_semantic_content(content, source_file):
    """Adapt semantic content for consolidation"""
    # Add to existing semantic memory rather than replace
    entry = f"\n\n## Migrated Content from {source_file.name}\n"
    entry += f"**Migration Date**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    entry += content + "\n\n---\n"
    
    return entry

def process_migration():
    """Main migration process"""
    print("🚀 Starting ThreadVault2 → Git Migration")
    print("=" * 50)
    
    if not THREADVAULT2_PATH.exists():
        print(f"❌ ThreadVault2 not found at {THREADVAULT2_PATH}")
        print("   Please ensure ThreadVault2 directory is available")
        return False
    
    # Create archive directory
    archive_dir = CURRENT_REPO / "archive" / "threadvault2_legacy"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Track files to process
    files_to_migrate = []
    
    # Scan ThreadVault2 for markdown files
    for md_file in THREADVAULT2_PATH.rglob("*.md"):
        if md_file.is_file() and not md_file.name.startswith('.'):
            files_to_migrate.append(md_file)
    
    print(f"📁 Found {len(files_to_migrate)} files to migrate")
    
    # Process each file
    processed_files = {}
    
    for source_file in files_to_migrate:
        try:
            category, target_filename = categorize_threadvault_file(source_file)
            target_path = CURRENT_REPO / category / target_filename
            
            print(f"📄 Migrating: {source_file.name} → {category}/{target_filename}")
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Migrate content
            migrated_content = migrate_file_content(source_file, category, target_filename)
            
            # Handle file consolidation (multiple sources to same target)
            if target_path.exists():
                # Append to existing file for memory consolidation
                if category == 'memory':
                    with open(target_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n\n{migrated_content}")
                else:
                    # For other categories, create versioned file
                    timestamp = datetime.now().strftime('%H%M%S')
                    versioned_path = target_path.with_stem(f"{target_path.stem}_{timestamp}")
                    with open(versioned_path, 'w', encoding='utf-8') as f:
                        f.write(migrated_content)
                    target_path = versioned_path
            else:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(migrated_content)
            
            # Track for commit
            if category not in processed_files:
                processed_files[category] = []
            processed_files[category].append(str(target_path))
            
        except Exception as e:
            print(f"⚠️  Error migrating {source_file}: {e}")
            continue
    
    return processed_files

def create_migration_commits(processed_files):
    """Create structured commits for migrated content"""
    print("\n📝 Creating migration commits...")
    
    # Commit by category for clean history
    for category, files in processed_files.items():
        if not files:
            continue
            
        # Add files to git
        for file_path in files:
            success, _, _ = run_git_cmd(f"git add '{file_path}'", check=False)
            if not success:
                print(f"⚠️  Could not add {file_path} to git")
        
        # Create commit
        commit_msg = f"feat(migration): Import {category} from ThreadVault2\n\n"
        commit_msg += f"Migrated {len(files)} files from ThreadVault2 {category} structure.\n"
        commit_msg += f"Files: {', '.join([Path(f).name for f in files])}\n\n"
        commit_msg += "🤖 Generated with Claude Code\n\n"
        commit_msg += "Co-Authored-By: Claude <noreply@anthropic.com>"
        
        success, _, error = run_git_cmd(f'git commit -m "{commit_msg}"', check=False)
        if success:
            print(f"  ✅ Committed {category} migration")
        else:
            print(f"  ⚠️  Commit failed for {category}: {error}")

def create_baseline_tag():
    """Create baseline tag for migration state"""
    print("\n🏷️  Creating baseline tag...")
    
    tag_name = f"v2025-{datetime.now().strftime('%m-%d')}-migration-baseline"
    tag_msg = "ThreadVault2 Migration Baseline\n\n"
    tag_msg += "Complete migration from folder-based ThreadVault2 to Git-based memory system.\n"
    tag_msg += f"Migration completed: {datetime.now().isoformat()}"
    
    success, _, _ = run_git_cmd(f'git tag -a {tag_name} -m "{tag_msg}"', check=False)
    if success:
        print(f"  ✅ Created tag: {tag_name}")
    else:
        print(f"  ⚠️  Tag creation failed")

def main():
    """Main migration script"""
    try:
        # Ensure we're in git repo
        success, _, _ = run_git_cmd("git status", check=False)
        if not success:
            print("❌ Not in a git repository")
            return 1
        
        # Process migration
        processed_files = process_migration()
        if not processed_files:
            print("❌ No files were processed")
            return 1
        
        # Create commits
        create_migration_commits(processed_files)
        
        # Create baseline tag
        create_baseline_tag()
        
        print("\n🎉 Migration completed successfully!")
        print(f"📊 Migrated {sum(len(files) for files in processed_files.values())} files")
        print("💡 Run 'git log --oneline' to see migration commits")
        print("🏷️  Run 'git tag' to see baseline tag")
        
        return 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())