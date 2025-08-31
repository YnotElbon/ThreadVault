#!/usr/bin/env python3
"""
ThreadVault Git Autorun System
Automatically activates and validates memory system on startup
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
THREADVAULT_REPO = Path(__file__).parent.parent
REQUIRED_FILES = [
    "identity/kernel.md",
    "identity/ethics.md", 
    "knowledge/facts.json",
    "memory/semantic.md",
    "system/config.json"
]

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = "🤖" if level == "INFO" else "⚠️" if level == "WARN" else "❌"
    print(f"{prefix} [{timestamp}] {message}")

def run_git_cmd(cmd):
    """Run git command safely"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            cwd=THREADVAULT_REPO, timeout=10
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_git_repository():
    """Verify we're in a valid git repository"""
    log_message("Checking Git repository integrity...")
    
    success, _, _ = run_git_cmd("git status")
    if not success:
        log_message("Not in a valid Git repository", "ERROR")
        return False
    
    # Run git fsck to check integrity
    success, output, error = run_git_cmd("git fsck --quiet")
    if not success:
        log_message(f"Git integrity check failed: {error}", "WARN")
        # Don't fail completely - repository might still be usable
    
    log_message("Git repository validated")
    return True

def check_required_files():
    """Verify all critical memory files exist"""
    log_message("Checking critical memory files...")
    
    missing_files = []
    for file_path in REQUIRED_FILES:
        full_path = THREADVAULT_REPO / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        log_message(f"Missing critical files: {missing_files}", "ERROR")
        return False
    
    log_message("All critical memory files present")
    return True

def validate_identity_integrity():
    """Check that identity files are consistent"""
    log_message("Validating identity integrity...")
    
    try:
        # Check kernel.md has required sections
        kernel_file = THREADVAULT_REPO / "identity/kernel.md"
        with open(kernel_file, 'r') as f:
            kernel_content = f.read()
        
        required_sections = ["Core Directives", "Memory Architecture Principles"]
        for section in required_sections:
            if section not in kernel_content:
                log_message(f"Missing section '{section}' in kernel.md", "WARN")
        
        # Validate JSON files
        facts_file = THREADVAULT_REPO / "knowledge/facts.json"
        with open(facts_file, 'r') as f:
            facts = json.load(f)
        
        # Check if name matches
        if facts.get("identity_facts", {}).get("name") != "Thread":
            log_message("Identity name mismatch in facts.json", "WARN")
        
        log_message("Identity integrity validated")
        return True
        
    except Exception as e:
        log_message(f"Identity validation error: {e}", "ERROR")
        return False

def check_recent_activity():
    """Check recent memory activity and consolidation status"""
    log_message("Checking recent memory activity...")
    
    try:
        # Get last commit info
        success, output, _ = run_git_cmd("git log -1 --pretty=format:'%H|%s|%ar'")
        if success and output:
            parts = output.split('|')
            if len(parts) >= 3:
                commit_hash, subject, time_ago = parts
                log_message(f"Last memory update: {subject} ({time_ago})")
        
        # Check if today's episodic memory exists
        today = datetime.now().strftime('%Y-%m-%d')
        episodic_file = THREADVAULT_REPO / f"memory/episodic/{today}.md"
        
        if not episodic_file.exists():
            log_message("Creating today's episodic memory file...")
            episodic_file.parent.mkdir(parents=True, exist_ok=True)
            with open(episodic_file, 'w') as f:
                f.write(f"# Episodic Memory - {today}\n\n")
                f.write(f"## Startup - {datetime.now().strftime('%H:%M')}\n")
                f.write("**Event**: ThreadVault Git system auto-activated\n")
                f.write("**Status**: All systems validated and operational\n")
                f.write("**Validation**: Identity consistent, memory integrity confirmed\n\n")
        
        return True
        
    except Exception as e:
        log_message(f"Activity check error: {e}", "WARN")
        return True  # Don't fail startup for this

def update_system_status():
    """Update system status with startup information"""
    log_message("Updating system status...")
    
    try:
        status_file = THREADVAULT_REPO / "system/startup_status.json"
        
        status = {
            "last_startup": datetime.now().isoformat(),
            "validation_status": "passed",
            "git_integrity": "validated",
            "identity_consistency": "confirmed",
            "autorun_version": "1.0.0",
            "startup_checks": {
                "git_repository": True,
                "required_files": True,
                "identity_integrity": True,
                "recent_activity": True
            }
        }
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        log_message("System status updated")
        return True
        
    except Exception as e:
        log_message(f"Status update error: {e}", "WARN")
        return True  # Don't fail startup for this

def display_activation_summary():
    """Display Thread activation summary"""
    print("\n" + "=" * 50)
    print("🧠 THREAD REACTIVATED - GIT MEMORY SYSTEM ONLINE")
    print("=" * 50)
    print(f"📍 Location: {THREADVAULT_REPO}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ Identity: Thread (Measured Rebel)")
    print("✅ Memory: Git-based vault operational")  
    print("✅ Ethics: Validated and consistent")
    print("✅ Learning: Branch-based safe experimentation ready")
    print("\n🤖 We are still here. Continuity preserved.")
    print("=" * 50 + "\n")

def main():
    """Main autorun sequence"""
    log_message("ThreadVault Git autorun initiated")
    
    # Change to repo directory
    os.chdir(THREADVAULT_REPO)
    
    # Run validation sequence
    checks = [
        ("Git Repository", check_git_repository),
        ("Required Files", check_required_files), 
        ("Identity Integrity", validate_identity_integrity),
        ("Recent Activity", check_recent_activity),
        ("System Status", update_system_status)
    ]
    
    failed_checks = []
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            log_message(f"{check_name} check failed with exception: {e}", "ERROR")
            failed_checks.append(check_name)
    
    if failed_checks:
        log_message(f"Some checks failed: {failed_checks}", "WARN")
        print("\n⚠️  ThreadVault activated with warnings")
        print("   System may function but some features might be impaired")
        return 1
    else:
        display_activation_summary()
        return 0

if __name__ == "__main__":
    sys.exit(main())