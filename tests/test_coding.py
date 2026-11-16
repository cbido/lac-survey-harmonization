import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "coding" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ev = _load("evaluate_coding")
co = _load("code_occupation_industry")


def test_isco_levels_pad_armed_forces():
    assert ev.isco_levels(5211) == {"1 digit": "5", "2 digits": "52", "3 digits": "521", "4 digits": "5211"}
    assert ev.isco_levels(110)["1 digit"] == "0"
    assert ev.isco_levels(-66) is None
    assert ev.isco_levels("") is None


def test_isic_levels_section_from_division():
    assert ev.isic_levels(101) == {"section": "A", "division": "01", "survey category": "0101"}
    assert ev.isic_levels(4809)["section"] == "G"
    assert ev.isic_levels(9701)["section"] == "T"


def test_agreement_counts_missing_as_disagreement():
    pairs = [(5211, 5211), (5211, 5223), (2522, 9111), (9111, "")]
    a = ev.agreement(pairs, ev.isco_levels)
    assert a["4 digits"]["agreement"] == 0.25
    assert a["2 digits"]["agreement"] == 0.5
    assert a["1 digit"]["agreement"] == 0.5


def test_agreement_weighted():
    a = ev.agreement([(5211, 5211), (2522, 9111)], ev.isco_levels, weights=[3, 1])
    assert a["4 digits"]["weighted"] == 0.75


def test_kappa_is_one_for_identical_and_zero_for_chance():
    assert ev.kappa([("a", "a"), ("b", "b")]) == 1.0
    assert ev.kappa([("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")]) == 0.0


def test_triage_uses_confidence():
    rows = [{"occ_office": "5211", "occ_model": "5211", "occ_conf": "0.95"},
            {"occ_office": "5211", "occ_model": "9111", "occ_conf": "0.6"}]
    t = ev.triage(rows, "occ", ev.isco_levels, "4 digits")
    assert t[0]["coverage"] == 1.0 and t[0]["agreement"] == 0.5
    assert t[2]["coverage"] == 0.5 and t[2]["agreement"] == 1.0


def test_validate_flags_codes_outside_the_list():
    cases = [{"id": 1}, {"id": 2}, {"id": 3}]
    answers = [{"id": 1, "occ": 5211, "occ_conf": 0.9, "ind": 4809, "ind_conf": 0.8},
               {"id": 2, "occ": 1234, "occ_conf": 0.9, "ind": -66, "ind_conf": 0.2}]
    rows = co.validate(answers, cases, occ={5211: "x"}, ind={4809: "y"})
    assert rows[0]["occ_model"] == 5211 and rows[0]["ind_model"] == 4809
    assert rows[1]["occ_model"] == "" and rows[1]["occ_invalid"] == 1234
    assert rows[1]["ind_model"] == -66
    assert rows[2]["occ_model"] == "" and rows[2]["occ_invalid"] == ""


def test_format_cases_keeps_ids():
    text = co.format_cases([{"id": 7, "title": "feriante", "tasks": "vende", "workplace": "feria"}])
    assert "id 7 | occupation: feriante | tasks: vende | workplace: feria" in text
