#!/usr/bin/env python3
"""Run the synthetic demo fixture; not for operational or event-result claims."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts" / "run_analysis.py"), str(ROOT / "fixtures" / "demo-manifest.json"), "--output", str(ROOT / "artifacts" / "demo-situation-report.json")]))
