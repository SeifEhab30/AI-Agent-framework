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

For each row, judge narrowly: does this exact test genuinely exercise this exact bullet's claim? Not "does it look reasonable" — does an assertion in this test actually check the behavior the bullet describes. A test that exists but asserts something unrelated, or that's a copy-paste of another test with names changed but behavior unchecked, fails.

Rows:
{{ROWS}}

Output exactly one line of JSON and nothing else — no markdown fence, no explanation before or after:
{"eligible": true|false, "failing_rows": [{"bullet": "...", "reason": "..."}]}

"eligible" is true only if every row passes. If even one row fails, "eligible" is false and "failing_rows" names each failing row with a one-sentence reason. If all rows pass, "failing_rows" is an empty array.
