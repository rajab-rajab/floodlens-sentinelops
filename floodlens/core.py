"""Small, dependency-free flood-impact analysis for reproducible CI checks.

The module intentionally accepts preprocessed numeric cells rather than claiming to
perform satellite calibration in a browser. A production ingestion adapter must use
only permitted source data and preserve the provenance recorded in the manifest.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any


class AnalysisError(ValueError):
    """Raised when evidence is missing, incompatible, or unsafe to analyse."""


@dataclass(frozen=True)
class GridChange:
    row: int
    column: int
    before: float
    after: float
    change: float


def _matrix(value: Any, name: str) -> list[list[float]]:
    if not isinstance(value, list) or not value or not all(isinstance(row, list) and row for row in value):
        raise AnalysisError(f"{name}.values must be a non-empty matrix")
    width = len(value[0])
    if any(len(row) != width for row in value):
        raise AnalysisError(f"{name}.values rows must have the same width")
    try:
        return [[float(cell) for cell in row] for row in value]
    except (TypeError, ValueError) as exc:
        raise AnalysisError(f"{name}.values must contain numbers") from exc


def _validate_observations(before: dict[str, Any], after: dict[str, Any]) -> tuple[list[list[float]], list[list[float]]]:
    for name, item in (("before", before), ("after", after)):
        if not item.get("datetime"):
            raise AnalysisError(f"{name}.datetime is required")
        if item.get("sat:relative_orbit") in (None, ""):
            raise AnalysisError(f"{name}.sat:relative_orbit is required")
    if before["sat:relative_orbit"] != after["sat:relative_orbit"]:
        raise AnalysisError("before/after observations must use the same relative orbit")
    before_grid, after_grid = _matrix(before.get("values"), "before"), _matrix(after.get("values"), "after")
    if (len(before_grid), len(before_grid[0])) != (len(after_grid), len(after_grid[0])):
        raise AnalysisError("before/after matrices must use the same dimensions")
    return before_grid, after_grid


def _changes(before: list[list[float]], after: list[list[float]], threshold: float) -> list[GridChange]:
    changes: list[GridChange] = []
    for row, before_row in enumerate(before):
        for column, before_value in enumerate(before_row):
            after_value = after[row][column]
            # For radar backscatter samples, a meaningful negative change is a candidate water/debris signal.
            delta = after_value - before_value
            if delta <= -abs(threshold):
                changes.append(GridChange(row, column, before_value, after_value, delta))
    return changes


def _impacted_assets(assets: list[dict[str, Any]], impacted: set[tuple[int, int]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for asset in assets:
        if not asset.get("id") or not asset.get("kind"):
            raise AnalysisError("every asset requires id and kind")
        cells = asset.get("cells", [])
        if not isinstance(cells, list):
            raise AnalysisError(f"asset {asset['id']} cells must be a list")
        hits = sum((int(cell[0]), int(cell[1])) in impacted for cell in cells if isinstance(cell, list) and len(cell) == 2)
        if hits:
            results.append({"id": asset["id"], "kind": asset["kind"], "impacted_cells": hits})
    return results


def _reachable(roads: list[dict[str, Any]], response_hub: str) -> set[str]:
    graph: dict[str, set[str]] = {}
    for road in roads:
        origin, destination = road.get("from"), road.get("to")
        if not origin or not destination:
            raise AnalysisError("every road requires from and to")
        if road.get("blocked", False):
            continue
        graph.setdefault(origin, set()).add(destination)
        graph.setdefault(destination, set()).add(origin)
    visited = {response_hub}
    queue: deque[str] = deque([response_hub])
    while queue:
        current = queue.popleft()
        for neighbour in graph.get(current, set()):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return visited


def analyse(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate evidence and return only values computed from manifest inputs."""
    if manifest.get("reference_damage_maps_used_as_input"):
        raise AnalysisError("published damage maps must never be used as analysis inputs")
    before_grid, after_grid = _validate_observations(manifest.get("before", {}), manifest.get("after", {}))
    threshold = float(manifest.get("change_threshold", 2.0))
    changes = _changes(before_grid, after_grid, threshold)
    impacted_cells = {(change.row, change.column) for change in changes}
    assets = _impacted_assets(manifest.get("assets", []), impacted_cells)
    response_hub = manifest.get("response_hub")
    settlements = manifest.get("settlements", [])
    if not response_hub or not isinstance(settlements, list):
        raise AnalysisError("response_hub and settlements are required")
    reachable = _reachable(manifest.get("roads", []), response_hub)
    cut_off = sorted(set(settlements) - reachable)
    return {
        "analysis_status": "complete",
        "provenance": {
            "before_datetime": manifest["before"]["datetime"],
            "after_datetime": manifest["after"]["datetime"],
            "relative_orbit": manifest["before"]["sat:relative_orbit"],
            "mode": "deterministic-sample-grid",
        },
        "flood_debris": {
            "impacted_cell_count": len(changes),
            "impacted_cells": [{"row": c.row, "column": c.column, "change": c.change} for c in changes],
        },
        "infrastructure": {"impacted_assets": assets, "impacted_asset_count": len(assets)},
        "connectivity": {"response_hub": response_hub, "cut_off_settlements": cut_off, "cut_off_settlement_count": len(cut_off)},
        "situation_report": {
            "summary": (
                f"Analysis found {len(changes)} impacted grid cells, {len(assets)} impacted infrastructure assets, "
                f"and {len(cut_off)} settlements without a road path to {response_hub}."
            ),
            "operational_note": "Educational prototype: confirm all results with field teams before action.",
        },
    }
