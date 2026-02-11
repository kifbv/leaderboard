#!/bin/bash
# Ralph Loop - Autonomous AI agent loop for greenfield project development
# Usage: ./ralph.sh [mode] [max_iterations]
#
# Modes:
#   interview              Phase 1: Interactive project interview (no loop)
#   discover [max]         Phase 2: Feature spec generation
#   plan [max]             Phase 3: Gap analysis + task list
#   plan-work "desc" [max] Scoped planning for a specific work branch
#   build [max]            Phase 4: Implementation (default)
#   [max]                  Shorthand for build mode
#
# Environment variables:
#   RALPH_MODEL    Model to use (default: opus for plan, sonnet for build)
#   RALPH_DELAY    Seconds between iterations (default: 3)
#   PUSH_AFTER_ITERATION  Set to "true" to git push after each iteration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default configuration
MODE="build"
MAX_ITERATIONS=0
WORK_DESCRIPTION=""
DELAY="${RALPH_DELAY:-3}"

# Parse arguments
case "${1:-}" in
  interview)
    MODE="interview"
    shift
    ;;
  discover)
    MODE="discover"
    shift
    [[ "${1:-}" =~ ^[0-9]+$ ]] && { MAX_ITERATIONS="$1"; shift; }
    ;;
  plan)
    MODE="plan"
    shift
    [[ "${1:-}" =~ ^[0-9]+$ ]] && { MAX_ITERATIONS="$1"; shift; }
    ;;
  plan-work)
    MODE="plan-work"
    shift
    WORK_DESCRIPTION="${1:-}"
    shift || true
    [[ "${1:-}" =~ ^[0-9]+$ ]] && { MAX_ITERATIONS="$1"; shift; }
    if [ -z "$WORK_DESCRIPTION" ]; then
      echo "Error: plan-work requires a description argument"
      echo "Usage: ./ralph.sh plan-work \"user authentication\" [max_iterations]"
      exit 1
    fi
    ;;
  build)
    MODE="build"
    shift
    [[ "${1:-}" =~ ^[0-9]+$ ]] && { MAX_ITERATIONS="$1"; shift; }
    ;;
  *)
    # If first arg is a number, treat as max_iterations for build mode
    if [[ "${1:-}" =~ ^[0-9]+$ ]]; then
      MAX_ITERATIONS="$1"
      shift
    fi
    ;;
esac

# Select prompt file based on mode
case "$MODE" in
  interview)   PROMPT_FILE="$SCRIPT_DIR/../prompts/PROMPT_interview.md" ;;
  discover)    PROMPT_FILE="$SCRIPT_DIR/../prompts/PROMPT_discover.md" ;;
  plan)        PROMPT_FILE="$SCRIPT_DIR/../prompts/PROMPT_plan.md" ;;
  plan-work)   PROMPT_FILE="$SCRIPT_DIR/../prompts/PROMPT_plan_work.md" ;;
  build)       PROMPT_FILE="$SCRIPT_DIR/../prompts/PROMPT_build.md" ;;
esac

# When running inside a scaffolded project, use local prompts if they exist
LOCAL_PROMPT="$PROJECT_DIR/ralph/$(basename "$PROMPT_FILE")"
if [ -f "$LOCAL_PROMPT" ]; then
  PROMPT_FILE="$LOCAL_PROMPT"
fi

# Verify prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

# Select model based on mode
if [ -n "${RALPH_MODEL:-}" ]; then
  MODEL="$RALPH_MODEL"
elif [ "$MODE" = "plan" ] || [ "$MODE" = "plan-work" ] || [ "$MODE" = "discover" ]; then
  MODEL="opus"
else
  MODEL="sonnet"
fi

# State file paths
PRD_FILE="$PROJECT_DIR/prd.json"
PROGRESS_FILE="$PROJECT_DIR/progress.txt"
ARCHIVE_DIR="$PROJECT_DIR/archive"
LAST_BRANCH_FILE="$PROJECT_DIR/.last-branch"

# --- Archive previous run if branch changed ---
if [ -f "$PRD_FILE" ] && [ -f "$LAST_BRANCH_FILE" ]; then
  CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE" 2>/dev/null || echo "")
  LAST_BRANCH=$(cat "$LAST_BRANCH_FILE" 2>/dev/null || echo "")

  if [ -n "$CURRENT_BRANCH" ] && [ -n "$LAST_BRANCH" ] && [ "$CURRENT_BRANCH" != "$LAST_BRANCH" ]; then
    DATE=$(date +%Y-%m-%d)
    FOLDER_NAME=$(echo "$LAST_BRANCH" | sed 's|^ralph/||')
    ARCHIVE_FOLDER="$ARCHIVE_DIR/$DATE-$FOLDER_NAME"

    echo "Archiving previous run: $LAST_BRANCH"
    mkdir -p "$ARCHIVE_FOLDER"
    [ -f "$PRD_FILE" ] && cp "$PRD_FILE" "$ARCHIVE_FOLDER/"
    [ -f "$PROGRESS_FILE" ] && cp "$PROGRESS_FILE" "$ARCHIVE_FOLDER/"
    echo "  Archived to: $ARCHIVE_FOLDER"

    # Reset progress file for new run
    echo "## Codebase Patterns" > "$PROGRESS_FILE"
    echo "" >> "$PROGRESS_FILE"
    echo "---" >> "$PROGRESS_FILE"
    echo "" >> "$PROGRESS_FILE"
    echo "# Ralph Progress Log" >> "$PROGRESS_FILE"
    echo "Started: $(date)" >> "$PROGRESS_FILE"
    echo "---" >> "$PROGRESS_FILE"
  fi
fi

# Track current branch
if [ -f "$PRD_FILE" ]; then
  CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE" 2>/dev/null || echo "")
  if [ -n "$CURRENT_BRANCH" ]; then
    echo "$CURRENT_BRANCH" > "$LAST_BRANCH_FILE"
  fi
fi

# Initialize progress file if it doesn't exist
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "## Codebase Patterns" > "$PROGRESS_FILE"
  echo "" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
  echo "" >> "$PROGRESS_FILE"
  echo "# Ralph Progress Log" >> "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

# --- Display session info ---
echo ""
echo "============================================"
echo "  Ralph Loop"
echo "============================================"
echo "  Mode:   $MODE"
echo "  Model:  $MODEL"
echo "  Prompt: $(basename "$PROMPT_FILE")"
echo "  Branch: $(cd "$PROJECT_DIR" && git branch --show-current 2>/dev/null || echo 'N/A')"
[ "$MAX_ITERATIONS" -gt 0 ] && echo "  Max:    $MAX_ITERATIONS iterations"
[ -n "$WORK_DESCRIPTION" ] && echo "  Scope:  $WORK_DESCRIPTION"
echo "============================================"
echo ""

# --- Interview mode: single interactive session (not looped) ---
if [ "$MODE" = "interview" ]; then
  echo "Starting interactive interview session..."
  echo "Press Ctrl+C to abort at any time."
  echo ""
  cd "$PROJECT_DIR"
  claude --dangerously-skip-permissions \
    --model "$MODEL" \
    < "$PROMPT_FILE"
  exit 0
fi

# --- Progress summary ---
if [ -f "$PRD_FILE" ]; then
  TOTAL=$(jq '.userStories | length' "$PRD_FILE" 2>/dev/null || echo 0)
  PASSING=$(jq '[.userStories[] | select(.passes == true)] | length' "$PRD_FILE" 2>/dev/null || echo 0)
  if [ "$TOTAL" -gt 0 ]; then
    PERCENT=$((PASSING * 100 / TOTAL))
    echo "Progress: $PASSING/$TOTAL stories passing ($PERCENT%)"
    echo ""
  fi
fi

# --- Main loop ---
ITERATION=0

while true; do
  # Check max iterations
  if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
    echo ""
    echo "Reached max iterations: $MAX_ITERATIONS"
    break
  fi

  echo ""
  echo "======================== ITERATION $((ITERATION + 1)) ========================"
  echo ""

  # Prepare prompt content
  if [ "$MODE" = "plan-work" ]; then
    # Substitute work scope into the prompt
    PROMPT_CONTENT=$(WORK_SCOPE="$WORK_DESCRIPTION" envsubst '$WORK_SCOPE' < "$PROMPT_FILE")
  else
    PROMPT_CONTENT=$(cat "$PROMPT_FILE")
  fi

  # Run Claude with the selected prompt
  cd "$PROJECT_DIR"
  OUTPUT=$(echo "$PROMPT_CONTENT" | claude -p \
    --dangerously-skip-permissions \
    --output-format=stream-json \
    --model "$MODEL" \
    --verbose 2>&1 | tee /dev/stderr) || true

  # Check for completion signal
  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo ""
    echo "============================================"
    echo "  Ralph completed all tasks!"
    echo "  Finished at iteration $((ITERATION + 1))"
    echo "============================================"
    exit 0
  fi

  # Optional: push after each iteration
  if [ "${PUSH_AFTER_ITERATION:-}" = "true" ]; then
    CURRENT_BRANCH=$(cd "$PROJECT_DIR" && git branch --show-current)
    cd "$PROJECT_DIR"
    git push origin "$CURRENT_BRANCH" 2>/dev/null || \
      git push -u origin "$CURRENT_BRANCH" 2>/dev/null || true
  fi

  ITERATION=$((ITERATION + 1))

  echo ""
  echo "Iteration $ITERATION complete. Continuing in ${DELAY}s... (Ctrl+C to stop)"
  sleep "$DELAY"
done

echo ""
echo "Ralph reached max iterations ($MAX_ITERATIONS) without completing all tasks."
[ -f "$PROGRESS_FILE" ] && echo "Check progress.txt for status."
exit 1
