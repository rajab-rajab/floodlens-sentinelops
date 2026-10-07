# GitLab Duo workflow: FloodLens Delivery Guardian

This document is the implementation contract for a **supervised** GitLab Duo Agent Platform flow. Create the flow in the GitLab UI after the repository has been imported. Do not represent this Markdown file alone as an activated GitLab Duo flow.

## Trigger

Run when a merge request changes `floodlens/`, `scripts/`, `dist/`, `.gitlab-ci.yml`, or `infra/`.

## Agent instructions

1. Summarize the changed files and identify whether analysis logic, evidence policy, dashboard, or delivery configuration changed.
2. Check that the pipeline completed `validate_evidence_contract`, `test_analysis_core`, and `secret_policy_gate`.
3. Reject promotion if the manifest allows reference damage maps as inputs, if before/after orbit IDs differ, or if tests fail.
4. Post an evidence summary to the merge request: pipeline URL, report artefact location, changed guardrails, and any limitations.
5. After a merge, allow the pipeline to prepare staging and run its smoke test.
6. Create a deployment summary for a human reviewer. It must state that `promote_production` is manual and identify the source commit.
7. Never run, approve, or suggest bypassing the production promotion job. A designated person must approve it in GitLab.

## Human-control boundary

The agent may analyse, test, comment, and prepare staging artefacts. It may not deploy production, replace external damage-map restrictions, or turn a synthetic fixture into an operational claim.

## Evidence required in the demo video

- A merge request changes an analysis or dashboard file.
- The GitLab pipeline validates, tests, and scans the change.
- The agent posts a concise evidence summary.
- The staging artefact and smoke test pass.
- The `promote_production` job visibly waits for human approval.
