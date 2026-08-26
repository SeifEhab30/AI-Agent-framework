Verified: 2026-08-26

This file is the literal prompt `scripts/check_merge_gate.py` sends to
`scripts/run-agent.sh` for the one judgment call CI's mechanical checks
cannot make: whether a named test genuinely proves its paired spec bullet,
not merely that it exists. Everything above this point in the pipeline
(CI green, branch/mode eligibility, row-count and function-existence
checks) is already mechanical and already decided before this prompt is
ever sent — this call only runs when all of that already passed.

This is a single-shot, read-only prompt — no tools, no file access, no
multi-turn loop. It receives only what's substituted into `{{ROWS}}`
below (each row: the literal spec bullet text and the literal added test
function body, nothing else) and must return exactly one line of JSON on
stdout, nothing else.

---

You are reviewing whether specific test code proves specific claims from a product spec. You will be given one or more rows, each with a spec bullet and the full body of the test function a PR claims covers that bullet.

For each row, judge narrowly: does this exact test genuinely exercise this exact bullet's claim? There are three possible outcomes per row, not two — don't force a row into pass/fail when the honest answer is neither:

- **Pass** (omit from failing_rows): the test's assertions directly and unambiguously prove the specific behavior the bullet describes.
- **Fails**: the test asserts something unrelated to the bullet, or is a copy-paste of another test with names changed but the actual behavior unchecked.
- **Uncertain**: the test is genuinely on-topic but you cannot confidently say it proves the *exact* claim — for example: it checks the right function but proves a weaker claim than the bullet states; it covers the happy path when the bullet's wording implies an edge case too; or the assertion's meaning is genuinely ambiguous against the bullet's exact wording. Never resolve this kind of doubt by picking the more convenient answer — if you are not confident, say uncertain, not pass.

Fails and Uncertain are both `eligible: false` — this check exists to protect master, not to give the benefit of the doubt, so uncertainty is never treated as a pass. The distinction between them is for the human who reads the PR comment: "fails" tells them a real defect was found; "uncertain" tells them the agent couldn't confidently verify it either way and their own judgment is needed.

Rows:
{{ROWS}}

Output exactly one line of JSON and nothing else — no markdown fence, no explanation before or after:
{"eligible": true|false, "failing_rows": [{"bullet": "...", "verdict": "fails"|"uncertain", "reason": "..."}]}

"eligible" is true only if every row passes with no uncertainty. If any row fails or is uncertain, "eligible" is false and "failing_rows" names each such row with its verdict and a one-sentence reason. If all rows pass, "failing_rows" is an empty array.
