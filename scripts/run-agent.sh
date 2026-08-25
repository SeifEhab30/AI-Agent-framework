#!/usr/bin/env bash
# Thin, swappable adapter between a workflow/script and whichever agent CLI
# actually evaluates a prompt. This is the ONLY file in the repo that names
# a specific CLI -- every caller (currently just check_merge_gate.py's
# semantic review step) goes through this script, never invokes a CLI
# directly. Swapping Claude Code for a different agent means editing the
# case statement below, not the workflow, the permissions contract, the
# calling script, or the prompt content in docs/references/.
#
# Contract:
#   - Prompt comes in on stdin.
#   - Model's raw text response goes out on stdout, nothing else -- no
#     progress text, no logging -- so callers can pipe stdout straight into
#     a JSON parser.
#   - Non-zero exit means the call itself failed (auth, network, CLI error),
#     not a judgment about the prompt's content. Callers must not treat a
#     failed call as an eligible/ineligible verdict either way.
#
# Usage:
#   scripts/run-agent.sh < prompt.txt
#   echo "$PROMPT" | scripts/run-agent.sh

set -euo pipefail

AGENT_CLI="${AGENT_CLI:-claude}"

case "$AGENT_CLI" in
claude)
  # Headless/print mode: no interactive loop, no tool access, reads the
  # prompt from stdin, prints the response and exits. Requires
  # ANTHROPIC_API_KEY in the environment -- not this script's job to set.
  exec claude -p --output-format text
  ;;
github-models)
  # NOT CURRENTLY USABLE (found 2026-08-25): a live test against this
  # endpoint returned "410 github_models_retirement_brownout" -- GitHub is
  # mid-retirement of this product. Kept here, not wired into
  # merge-gate.yml (which currently runs --mechanical-only instead), in
  # case GitHub ships a successor endpoint under the same auth model. Do
  # not re-enable without testing it actually responds first.
  #
  # Original intent: no separate API key or billing account, authenticates
  # with the same GITHUB_TOKEN the workflow already has, gated by the
  # job's own `permissions: models: read`. Model swappable via
  # GITHUB_MODELS_MODEL without touching this script.
  : "${GITHUB_TOKEN:?GITHUB_TOKEN must be set for github-models}"
  MODEL="${GITHUB_MODELS_MODEL:-openai/gpt-4o-mini}"

  PROMPT_FILE="$(mktemp)"
  trap 'rm -f "$PROMPT_FILE"' EXIT
  cat >"$PROMPT_FILE"

  GITHUB_TOKEN="$GITHUB_TOKEN" MODEL="$MODEL" PROMPT_FILE="$PROMPT_FILE" python3 <<'PYEOF'
import json
import os
import urllib.request

token = os.environ["GITHUB_TOKEN"]
model = os.environ["MODEL"]
with open(os.environ["PROMPT_FILE"], "r", encoding="utf-8") as f:
    prompt = f.read()

req = urllib.request.Request(
    "https://models.github.ai/inference/chat/completions",
    data=json.dumps(
        {"model": model, "messages": [{"role": "user", "content": prompt}]}
    ).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as resp:
    body = json.loads(resp.read().decode("utf-8"))
print(body["choices"][0]["message"]["content"])
PYEOF
  ;;
*)
  echo "run-agent.sh: unknown AGENT_CLI '$AGENT_CLI' -- add a case for it here" >&2
  exit 1
  ;;
esac
