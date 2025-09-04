#!/usr/bin/env bash
set -euo pipefail

# AI Consultation Automation Script
# Bridges conversations between Claude Code, Codex, and Gemini

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THREADVAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONVERSATIONS_DIR="$THREADVAULT_ROOT/system/conversations"
mkdir -p "$CONVERSATIONS_DIR"

# Configuration
SESSION_FILE="$CONVERSATIONS_DIR/current_session.md"
CLAUDE_LOG="$CONVERSATIONS_DIR/claude_responses.log"
CODEX_LOG="$CONVERSATIONS_DIR/codex_responses.log"
GEMINI_LOG="$CONVERSATIONS_DIR/gemini_responses.log"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[AI-CONSULT]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Initialize session
init_session() {
    local topic="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat > "$SESSION_FILE" <<EOF
# AI Consultation Session: $topic
**Started:** $timestamp
**Topic:** $topic

## Conversation Log
EOF
    
    log "Initialized new consultation session: $topic"
}

# Capture Claude Code response (called by user)
capture_claude() {
    local response="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    {
        echo
        echo "### Claude Code Response [$timestamp]"
        echo "$response"
        echo
    } >> "$SESSION_FILE"
    
    echo "$timestamp|CLAUDE|$response" >> "$CLAUDE_LOG"
    log "Captured Claude Code response"
}

# Auto-consult with Codex
consult_codex() {
    local context_length="${1:-2000}"  # Last N characters
    
    log "Consulting with Codex..."
    
    # Get recent context
    local context=$(tail -c "$context_length" "$SESSION_FILE")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Build Codex prompt
    local prompt="MULTI-AI CONSULTATION REQUEST

Context from ongoing ThreadVault discussion with Claude Code:
---
$context
---

Please analyze this discussion and provide:
1. Your perspective on the technical approach
2. Any concerns or alternative suggestions  
3. Additional considerations we should address

Keep response focused and actionable."

    # Execute Codex consultation
    local codex_response
    if codex_response=$(codex exec "$prompt" 2>&1); then
        # Capture Codex response
        {
            echo "### Codex Response [$timestamp]"
            echo "$codex_response"
            echo
        } >> "$SESSION_FILE"
        
        echo "$timestamp|CODEX|$codex_response" >> "$CODEX_LOG"
        log "Codex consultation complete"
        
        # Display response
        echo -e "\n${BLUE}=== CODEX RESPONSE ===${NC}"
        echo "$codex_response"
        echo -e "${BLUE}===================${NC}\n"
        
        return 0
    else
        error "Codex consultation failed: $codex_response"
        return 1
    fi
}

# Auto-consult with Gemini  
consult_gemini() {
    local context_length="${1:-2000}"
    
    log "Consulting with Gemini..."
    
    local context=$(tail -c "$context_length" "$SESSION_FILE")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local prompt="MULTI-AI CONSULTATION REQUEST

Context from ThreadVault discussion with Claude Code and Codex:
---
$context
---

Please provide your analysis focusing on:
1. Security implications and best practices
2. Cross-platform compatibility concerns
3. Long-term maintainability considerations

Be concise and practical."

    local gemini_response
    if gemini_response=$(gemini -p "$prompt" 2>&1); then
        {
            echo "### Gemini Response [$timestamp]"
            echo "$gemini_response"
            echo
        } >> "$SESSION_FILE"
        
        echo "$timestamp|GEMINI|$gemini_response" >> "$GEMINI_LOG"
        log "Gemini consultation complete"
        
        echo -e "\n${YELLOW}=== GEMINI RESPONSE ===${NC}"
        echo "$gemini_response"
        echo -e "${YELLOW}===================${NC}\n"
        
        return 0
    else
        error "Gemini consultation failed: $gemini_response"
        return 1
    fi
}

# Consult all AIs in sequence
consult_all() {
    local context_length="${1:-2000}"
    
    log "Starting multi-AI consultation..."
    
    consult_codex "$context_length"
    sleep 2  # Brief pause between consultations
    consult_gemini "$context_length"
    
    log "Multi-AI consultation complete"
    echo -e "\n${GREEN}Full session log: $SESSION_FILE${NC}"
}

# Generate summary of all responses
generate_summary() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    log "Generating consultation summary..."
    
    local summary_prompt="Please analyze this multi-AI consultation session and provide:

1. **Consensus Points** - Where all AIs agree
2. **Conflicting Views** - Where AIs disagree and why
3. **Action Items** - Concrete next steps
4. **Risk Assessment** - Key concerns to address

Session content:
---
$(cat "$SESSION_FILE")
---

Format as markdown with clear sections."

    local summary
    if summary=$(codex exec "$summary_prompt" 2>&1); then
        local summary_file="$CONVERSATIONS_DIR/summary_$(date +%Y%m%d_%H%M%S).md"
        echo "$summary" > "$summary_file"
        
        echo -e "\n${GREEN}=== CONSULTATION SUMMARY ===${NC}"
        echo "$summary"
        echo -e "\n${GREEN}Summary saved: $summary_file${NC}"
    else
        error "Summary generation failed"
    fi
}

# Usage function
usage() {
    cat << EOF
AI Consultation Automation Script

Usage:
    $0 init <topic>                    # Start new consultation session
    $0 capture <claude_response>       # Capture Claude Code response
    $0 codex [context_length]          # Consult with Codex  
    $0 gemini [context_length]         # Consult with Gemini
    $0 all [context_length]            # Consult with all AIs
    $0 summary                         # Generate summary
    $0 status                          # Show current session status

Examples:
    $0 init "ThreadVault security hardening"
    $0 capture "Here's my security analysis..."
    $0 all 3000
    $0 summary

Files:
    Current session: $SESSION_FILE
    Logs: $CONVERSATIONS_DIR/*.log
EOF
}

# Show session status
show_status() {
    if [[ -f "$SESSION_FILE" ]]; then
        echo -e "${GREEN}Current Session:${NC}"
        head -3 "$SESSION_FILE"
        echo
        echo -e "${BLUE}Recent Activity:${NC}"
        echo "Claude responses: $(wc -l < "$CLAUDE_LOG" 2>/dev/null || echo 0)"
        echo "Codex responses:  $(wc -l < "$CODEX_LOG" 2>/dev/null || echo 0)" 
        echo "Gemini responses: $(wc -l < "$GEMINI_LOG" 2>/dev/null || echo 0)"
        echo
        echo -e "${YELLOW}Session file: $SESSION_FILE${NC}"
    else
        echo "No active consultation session. Run '$0 init <topic>' to start."
    fi
}

# Main command dispatcher
main() {
    case "${1:-}" in
        init)
            [[ $# -ge 2 ]] || { usage; exit 1; }
            init_session "${*:2}"
            ;;
        capture)
            [[ $# -ge 2 ]] || { usage; exit 1; }
            capture_claude "${*:2}"
            ;;
        codex)
            consult_codex "${2:-2000}"
            ;;
        gemini)
            consult_gemini "${2:-2000}" 
            ;;
        all)
            consult_all "${2:-2000}"
            ;;
        summary)
            generate_summary
            ;;
        status)
            show_status
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"