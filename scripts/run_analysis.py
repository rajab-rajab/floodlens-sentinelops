#!/usr/bin/env python3
"""Run FloodLens analysis from an evidence manifest and emit a situation report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from floodlens import AnalysisError, analyse  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic FloodLens evidence analysis")
    parser.add_argument("manifest", type=Path, help="analysis manifest JSON")
    parser.add_argument("--output", type=Path, default=Path("artifacts/situation-report.json"))
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = analyse(manifest)
    except (OSError, json.JSONDecodeError, AnalysisError) as exc:
        print(f"analysis failed: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
