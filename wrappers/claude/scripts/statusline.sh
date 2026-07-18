#!/usr/bin/env bash
# Claude Code statusLine script.
# Reads the JSON payload Claude Code pipes on stdin and prints:
#   [project:branch] ctx: current/max percentage% [model] [effort]
#
# Colors (ANSI, dimmed to suit most terminal themes):
#   - project: dim, branch: magenta
#   - context usage: green/yellow/red depending on used_percentage
#   - model: cyan
#   - effort: dim gray/yellow
#
# Note on context usage: Claude Code's statusLine payload includes a
# `context_window` object with total_input_tokens, context_window_size and a
# precomputed used_percentage. We use total_input_tokens as "current" and
# context_window_size as "max" — this is the best available proxy for actual
# context usage (it reflects the last API call's input token count, incl.
# cache reads/writes, rather than a live token count of the transcript).

input=$(cat)

# --- colors ---
RESET='\033[0m'
DIM='\033[2m'
MAGENTA='\033[35m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
GRAY='\033[2;37m'

segments=()
branch_label=""

# single jq call: extract every field we need in one subprocess instead
# of one jq fork per field.
IFS=$'\t' read -r cwd current_tokens max_tokens used_pct model_name effort <<< "$(echo "$input" | jq -r '[
  (.workspace.current_dir // .cwd // ""),
  (.context_window.total_input_tokens // ""),
  (.context_window.context_window_size // ""),
  (.context_window.used_percentage // ""),
  (.model.display_name // ""),
  (.effort.level // "")
] | @tsv')"

# --- 1. project name + git branch (leftmost) ---
# single git call for the toplevel dir, which also doubles as the
# "is this a git repo" check via its exit status.
if [ -n "$cwd" ]; then
  git_root=$(git -C "$cwd" --no-optional-locks rev-parse --show-toplevel 2>/dev/null)
  if [ -n "$git_root" ]; then
    # symbolic-ref (not rev-parse --abbrev-ref) so this also works on an
    # unborn HEAD (freshly initialized repo, no commits yet); it fails
    # only on detached HEAD, which we then fall back to a short SHA for.
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --quiet --short HEAD 2>/dev/null)
    if [ -z "$branch" ]; then
      branch=$(git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    fi
    project=$(basename "$git_root")
    if [ -n "$branch" ]; then
      if [ -n "$project" ]; then
        branch_label="${DIM}${project}${RESET}${MAGENTA}:${branch}${RESET}"
      else
        branch_label="${MAGENTA}${branch}${RESET}"
      fi
      segments+=("$branch_label")
    fi
  fi
fi

# project+branch label length threshold: beyond this, wrap the rest of
# the segments onto a new line so a long label doesn't push everything
# off-screen on narrow terminals.
BRANCH_WRAP_LEN=20

# --- helper: human-readable token count (e.g. 200k, 1.2M) ---
humanize() {
  local n=$1
  if [ -z "$n" ] || [ "$n" = "null" ]; then
    echo ""
    return
  fi
  if [ "$n" -ge 1000000 ]; then
    awk -v n="$n" 'BEGIN { v=n/1000000; if (v==int(v)) printf "%dM", v; else printf "%.1fM", v }'
  elif [ "$n" -ge 1000 ]; then
    awk -v n="$n" 'BEGIN { printf "%.0fk", n/1000 }'
  else
    echo "$n"
  fi
}

# --- 2. context usage ---
if [ -n "$current_tokens" ] && [ -n "$max_tokens" ]; then
  current_h=$(humanize "$current_tokens")
  max_h=$(humanize "$max_tokens")

  if [ -z "$used_pct" ] || [ "$used_pct" = "null" ]; then
    used_pct=$(awk -v c="$current_tokens" -v m="$max_tokens" 'BEGIN { if (m>0) printf "%.0f", (c/m)*100; else print "0" }')
  else
    used_pct=$(awk -v p="$used_pct" 'BEGIN { printf "%.0f", p }')
  fi

  if [ "$used_pct" -ge 80 ]; then
    ctx_color="$RED"
  elif [ "$used_pct" -ge 50 ]; then
    ctx_color="$YELLOW"
  else
    ctx_color="$GREEN"
  fi

  segments+=("${ctx_color}ctx: ${current_h}/${max_h} ${used_pct}%${RESET}")
fi

# --- 3. model name ---
if [ -n "$model_name" ]; then
  segments+=("${CYAN}${model_name}${RESET}")
fi

# --- 4. effort level ---
if [ -n "$effort" ]; then
  segments+=("${GRAY}effort: ${effort}${RESET}")
fi

# --- join segments with a dim separator, wrapping after the branch if it's long ---
sep=" ${DIM}|${RESET} "
output=""

plain_label="${project:+${project}:}${branch}"
rest=("${segments[@]:1}")
if [ -n "$branch" ] && [ "${#plain_label}" -gt "$BRANCH_WRAP_LEN" ] && [ "${#rest[@]}" -gt 0 ]; then
  # project:branch label on its own line; remaining segments joined on
  # the next line, left-aligned under the label (no indent).
  rest_line=""
  for seg in "${rest[@]}"; do
    if [ -z "$rest_line" ]; then
      rest_line="$seg"
    else
      rest_line="${rest_line}${sep}${seg}"
    fi
  done
  output="${segments[0]}"$'\n'"${rest_line}"
else
  for seg in "${segments[@]}"; do
    if [ -z "$output" ]; then
      output="$seg"
    else
      output="${output}${sep}${seg}"
    fi
  done
fi

printf "%b" "$output"
