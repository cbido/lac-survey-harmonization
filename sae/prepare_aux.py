"""Turn the ministry's published comuna-level poverty estimates into one tidy table.

Reads the official Excel files for 2022 and 2020 (config/sources.yml) and writes
data/aux/official_comuna_poverty.csv with one row per comuna. The 2022 column is the
benchmark for sae/fay_herriot.R, and the 2020 column is used there as an auxiliary variable.

Usage:
    python sae/prepare_aux.py
"""
from __future__ import annotations

from pathlib import Path

import openpyxl
import pandas as pd

FILES = {
    2022: "data/aux/Estimaciones_Tasa_Pobreza_Ingresos_Comunas_2022.xlsx",
    2020: "data/aux/Estimaciones_Tasa_Pobreza_Ingresos_Comunas_2020.xlsx",
}


def read_official(path: str, year: int) -> pd.DataFrame:
    sheet = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = []
    for row in sheet.iter_rows(min_row=4, values_only=True):
        code = str(row[0]).strip() if row[0] is not None else ""
        if not code.isdigit():      # notes under the table
            continue
        rows.append(
            {
                "comuna": int(code),
                "comuna_name": row[2],
                f"population_{year}": float(row[3]),
                f"p_official_{year}": float(row[5]),
                f"lower_{year}": float(row[6]),
                f"upper_{year}": float(row[7]),
                f"in_sample_{year}": str(row[8]).strip().lower().startswith("s"),
                f"type_{year}": str(row[9]).strip(),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    now, before = read_official(FILES[2022], 2022), read_official(FILES[2020], 2020)
    out = now.merge(before.drop(columns=["comuna_name"]), on="comuna", how="left")
    out["region"] = out["comuna"] // 1000
    path = Path("data/aux/official_comuna_poverty.csv")
    out.to_csv(path, index=False)
    print(f"{len(out)} comunas -> {path}")
    print(f"  with a 2020 estimate: {out['p_official_2020'].notna().sum()}, in the 2022 sample: {out['in_sample_2022'].sum()}")
    print("  2022 types:", out["type_2022"].value_counts().to_dict())


if __name__ == "__main__":
    main()
