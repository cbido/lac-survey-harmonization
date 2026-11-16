"""Quality checks for a harmonized table, generated from config/target_schema.yml.

Two kinds of check:
  - value checks: allowed codes and ranges declared in the schema (pandera)
  - population check: weighted total against an official population figure

Usage (from Python):
    from validate.checks import build_schema, weighted_total_check
    build_schema("config/target_schema.yml", level="person").validate(df, lazy=True)
"""
from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
import yaml


def build_schema(schema_path: str, level: str | None = None) -> pa.DataFrameSchema:
    """Build a pandera schema. Only columns present in the data are checked."""
    with open(schema_path, encoding="utf-8") as f:
        variables = yaml.safe_load(f)["variables"]
    columns = {}
    for var in variables:
        if level and var["level"] not in (level, "survey"):
            continue
        checks = []
        if var.get("values"):
            checks.append(pa.Check.isin(list(var["values"].keys())))
        if var.get("range"):
            low, high = var["range"]
            if low is not None:
                checks.append(pa.Check.ge(low))
            if high is not None:
                checks.append(pa.Check.le(high))
        columns[var["name"]] = pa.Column(checks=checks, nullable=True, required=False)
    return pa.DataFrameSchema(columns)


def weighted_total_check(df: pd.DataFrame, weight: str, official_total: float, tolerance: float = 0.02) -> dict:
    """Compare the sum of expansion factors with an official population total."""
    total = float(df[weight].sum())
    gap = (total - official_total) / official_total
    return {"weighted_total": total, "official_total": official_total, "relative_gap": gap, "ok": abs(gap) <= tolerance}
