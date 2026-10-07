# Architecture

```text
Permitted Sentinel/STAC metadata + pre-event OSM
                    |
                    v
         Evidence manifest validation
                    |
                    v
       Deterministic change + exposure core
          |                         |
          v                         v
  impacted grid/assets        road graph reachability
          \                         /
           v                       v
             evidence-linked situation report
                         |
                         v
       GitLab CI -> staging artefact -> smoke test
                         |
                         v
                  human production approval
```

The core is deliberately deterministic for reproducibility. It expects a future, reviewed satellite-ingestion adapter to produce a calibrated grid from Sentinel imagery. Published damage maps are evaluation references only and are rejected as inputs.
