import pandas as pd
import pandera.errors
import pyreadstat
import pytest

from ingest.to_parquet import _repair, build_dictionary, convert
from validate.checks import build_schema, weighted_total_check


def test_chunked_conversion_and_dictionary(tmp_path):
    raw, parquet = tmp_path / "mini.dta", tmp_path / "mini.parquet"
    df = pd.DataFrame(
        {
            "SEXO": [1, 2, 2, 1, 2],
            "edad": [30, 41, 7, 7, 65],
            "ingreso": [1000.5, None, None, 250.0, 80.0],   # missing in a whole chunk
            "oficio": ["", "", "", "profesora", "chofer"],  # text that starts empty
        }
    )
    pyreadstat.write_dta(
        df, str(raw),
        column_labels=["Sexo de la persona", "Edad", "Ingreso", "Oficio"],
        variable_value_labels={"SEXO": {1: "Hombre", 2: "Mujer"}},
    )
    meta, n_rows = convert(str(raw), str(parquet), chunksize=2)   # three chunks
    assert n_rows == 5
    back = pd.read_parquet(parquet)
    assert list(back.columns) == ["sexo", "edad", "ingreso", "oficio"]
    assert back["ingreso"].isna().sum() == 2
    assert back["oficio"].iloc[4] == "chofer"

    d = build_dictionary(meta, str(parquet)).set_index("variable")
    assert d.loc["sexo", "label"] == "Sexo de la persona"
    assert '"1": "Hombre"' in d.loc["sexo", "value_labels"]
    assert d.loc["edad", "n_unique"] == 4
    assert d.loc["ingreso", "n_missing"] == 2


def test_repair_of_truncated_utf8():
    broken = "Educación Bás".encode("utf-8") + b"\xc3"      # cut inside the next character
    assert _repair(broken.decode("latin-1")) == "Educación Bás"
    assert _repair(None) is None


def test_repair_of_windows_1252_text():
    raw = "Niño".encode("cp1252") + b"\x81"                  # 0x81 is undefined in Windows-1252
    assert _repair(raw.decode("latin-1"), "windows-1252") == "Niño\ufffd"


def test_schema_checks_codes_and_ranges():
    schema = build_schema("config/target_schema.yml", level="person")
    good = pd.DataFrame({"sexo_ci": [1, 2], "edad_ci": [0, 99], "zona_c": [0, 1]})
    schema.validate(good, lazy=True)
    bad = pd.DataFrame({"sexo_ci": [1, 3], "edad_ci": [5, 140]})
    with pytest.raises(pandera.errors.SchemaErrors) as err:
        schema.validate(bad, lazy=True)
    assert set(err.value.failure_cases["column"]) == {"sexo_ci", "edad_ci"}


def test_weighted_total_check():
    df = pd.DataFrame({"factor_ci": [100.0, 150.0, 250.0]})
    assert weighted_total_check(df, "factor_ci", official_total=505)["ok"]
    assert not weighted_total_check(df, "factor_ci", official_total=600)["ok"]
