# FloodLens SentinelOps

FloodLens SentinelOps is a supervised geospatial incident-analysis prototype for flood response. It combines a deterministic satellite change-analysis core with infrastructure exposure and road-network reachability checks, then produces an evidence-linked situation report.

This repository is designed for the **GitLab Transcend: Life After Code** challenge. The product is deliberately safety-first: automated checks can prepare evidence and a staging release, but production promotion remains a human approval step.

## What works today

- Validates before/after Sentinel STAC metadata, including same-orbit safeguards.
- Calculates a reproducible flood/debris change score from supplied observation samples.
- Flags supplied infrastructure assets intersecting impacted grid cells.
- Finds settlements disconnected from a nominated response hub using a road graph.
- Writes a JSON situation report whose numbers are derived from analysis outputs.
- Runs a GitLab CI/CD pipeline for validation, tests, policy checks, staging artefacts, smoke tests, and manual production approval.
- Includes a dashboard in `dist/index.html` for the product story and evidence workflow.

## Safety and data boundaries

This is an educational prototype, not an operational safety system. Confirm any decision with local authorities and field teams. Do not use Copernicus EMS, UNOSAT, or other published damage maps as model inputs. They may be used only for evaluation after analysis.

The included fixture data is synthetic. It proves the pipeline mechanics; it does **not** make claims about the real Trishuli event.

## Run the analysis demo

Requires Python 3.11+ and no third-party packages.

```bash
python scripts/run_demo.py
python -m unittest discover -s tests -v
```

The first command writes `artifacts/demo-situation-report.json`. Open `dist/index.html` in a browser for the dashboard prototype.

## GitLab delivery workflow

`.gitlab-ci.yml` implements a supervised lifecycle:

1. **Validate** input structure and data-policy boundaries.
2. **Test** the deterministic analysis core.
3. **Secure** the repository with a lightweight secret-pattern gate.
4. **Package** the report artefact and static dashboard.
5. **Deploy staging** as a reviewable artefact.
6. **Smoke test** the report schema.
7. **Promote production** only through GitLab's manual approval job.

`docs/gitlab-duo-workflow.md` provides the exact operating contract to create as a GitLab Duo Agent Platform flow after importing this repository into GitLab. It makes decisions and evidence visible, and it never permits an agent to silently promote a response dashboard to production.

## Input contract

`scripts/run_analysis.py` accepts one JSON manifest. It expects:

- `before` and `after`: STAC-like objects with `datetime`, `sat:relative_orbit`, and a same-sized `values` matrix.
- `assets`: objects with `id`, `kind`, and `cells` identifying grid cells.
- `roads`: `{ "from": "...", "to": "...", "blocked": false }` graph edges.
- `settlements` and a `response_hub`.

The algorithm makes a change score by comparing paired sample values. A production adapter should obtain permitted Sentinel-1/2 rasters, perform calibrated preprocessing, and convert them to the documented grid contract. Never substitute the synthetic fixtures for satellite data.

## Deployment notes

The existing `infra/` directory is an AWS CDK starter for evidence intake and asynchronous jobs. It is intentionally not deployed by this repository. Before a real deployment, use encrypted storage, least-privilege roles, audit logs, a cost limit, and a human review gate.

## License

MIT. See [LICENSE](LICENSE).
