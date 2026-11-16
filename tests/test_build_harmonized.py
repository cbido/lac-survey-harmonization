import duckdb
import pandas as pd

from harmonize.build_harmonized import test_expression as check_expression

SEX = {"name": "sexo_ci", "type": "int", "values": {1: "male", 2: "female"}}
AGE = {"name": "edad_ci", "type": "int", "range": [0, 120]}
GROUP = {"name": "ocupa_ci", "type": "int", "range": [1, 3]}


def source(tmp_path):
    path = tmp_path / "raw.parquet"
    pd.DataFrame({"sexo": [1, 2, 2, 9] * 25, "edad": [10, 40, 130, 5] * 25, "g": [1, 1, 3, None] * 25,
                  "rare": [None] * 99 + [1]}).to_parquet(path)
    return duckdb.connect(), f"read_parquet('{path}')"


def test_statuses(tmp_path):
    con, src = source(tmp_path)
    assert check_expression(con, src, "CASE WHEN sexo IN (1,2) THEN sexo END", SEX)["status"] == "ok"
    assert check_expression(con, src, "sexo", SEX)["status"] == "invalid_values"          # the 9 is not a valid code
    assert check_expression(con, src, "edad", AGE)["status"] == "invalid_values"          # 130 is out of range
    assert check_expression(con, src, "no_such_column", SEX)["status"] == "sql_error"
    assert check_expression(con, src, "CAST(NULL AS INTEGER)", SEX)["status"] == "all_missing"


def test_warnings_for_code_that_runs_but_looks_wrong(tmp_path):
    con, src = source(tmp_path)
    empty_code = check_expression(con, src, "g", GROUP)
    assert empty_code["status"] == "ok" and "codes never produced: [2]" in empty_code["warning"]
    rare = check_expression(con, src, "rare", {"name": "x", "type": "int"})
    assert rare["status"] == "ok" and "only 1.0% of rows" in rare["warning"]
