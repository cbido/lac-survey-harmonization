import pandas as pd

from harmonize.compare_rounds import across_countries, load_gold, name_check, within_country

COLUMNS = ["survey", "target_var", "status", "source_vars", "not_in_dictionary", "names_checked"]
TARGETS = ["sexo_ci", "aguared_ch", "internet_ch"]


def write(path, rows):
    pd.DataFrame(rows, columns=COLUMNS).to_csv(path, index=False)


def make_gold(tmp_path):
    write(tmp_path / "AAA_2017_gold_draft.csv", [
        ("AAA_2017", "sexo_ci", "mapped", "sexo", "", "yes"),
        ("AAA_2017", "aguared_ch", "mapped", "v23", "aux", "yes"),
        ("AAA_2017", "internet_ch", "mapped", "r20", "", "yes"),
    ])
    write(tmp_path / "AAA_2020_gold_draft.csv", [
        ("AAA_2020", "sexo_ci", "mapped", "sexo", "", "yes"),
        ("AAA_2020", "aguared_ch", "mapped", "WRONG", "", "yes"),
        ("AAA_2020", "internet_ch", "not_available", "", "", "yes"),
    ])
    # reviewed file wins over the draft
    write(tmp_path / "AAA_2020_gold.csv", [
        ("AAA_2020", "sexo_ci", "mapped", "sexo", "", "yes"),
        ("AAA_2020", "aguared_ch", "mapped", "v20", "", "yes"),
        ("AAA_2020", "internet_ch", "not_available", "", "", "yes"),
    ])
    write(tmp_path / "BBB_2017_gold_draft.csv", [
        ("BBB_2017", "sexo_ci", "mapped", "s01a_02", "", "no"),
        ("BBB_2017", "internet_ch", "mapped", "s06_01", "", "no"),
    ])
    return load_gold(str(tmp_path), TARGETS)


def test_changes_within_a_country(tmp_path):
    res = within_country(make_gold(tmp_path))
    assert res["AAA"]["surveys"] == ["AAA_2017", "AAA_2020"]
    assert list(res["AAA"]["status_changes"]["target_var"]) == ["internet_ch"]
    assert list(res["AAA"]["source_changes"]["target_var"]) == ["aguared_ch"]
    assert res["AAA"]["source_changes"]["AAA_2020"].iloc[0] == "v20"
    assert res["AAA"]["n_always_mapped"] == 2


def test_coverage_across_countries(tmp_path):
    cross = across_countries(make_gold(tmp_path)).set_index("target_var")
    assert cross.loc["sexo_ci", "mapped_in_every_survey"] == "yes"
    assert cross.loc["internet_ch", "AAA"] == "1/2"
    assert cross.loc["aguared_ch", "BBB"] == "0/1"      # absent from that program
    assert cross.loc["aguared_ch", "mapped_in_every_survey"] == ""


def test_name_check(tmp_path):
    check = name_check(make_gold(tmp_path)).set_index("survey")
    assert check.loc["AAA_2017", "names_found"] == 3
    assert check.loc["AAA_2017", "names_not_found"] == 1
    assert check.loc["AAA_2017", "share_found"] == "75.0%"
    assert check.loc["BBB_2017", "checked"] == "no"
