import math

import pandas as pd

from validate.evaluate_mappings import evaluate, split_vars

GOLD = pd.DataFrame(
    [
        ("T", "sexo_ci", "mapped", "sexo"),
        ("T", "aedu_ci", "mapped", "e3;e6a;e6b"),
        ("T", "ylm_ci", "mapped", "ytrabajocor"),
        ("T", "luz_ch", "not_available", ""),
        ("T", "piso_ch", "not_available", ""),
        ("T", "emp_ci", "derived", ""),      # skipped
        ("T", "pais_c", "constant", ""),     # skipped
    ],
    columns=["survey", "target_var", "status", "source_vars"],
)

PROPOSALS = pd.DataFrame(
    [
        ("T", "sexo_ci", "demographics", "mapped", "SEXO", 0.95),          # exact (case-insensitive)
        ("T", "aedu_ci", "education", "mapped", "e6a;e6b;esc", 0.80),      # 2 right, 1 wrong, 1 missed
        ("T", "ylm_ci", "income", "not_available", "", 0.40),              # missed a mapped variable
        ("T", "luz_ch", "housing", "not_available", "", 0.90),             # correct
        ("T", "piso_ch", "housing", "mapped", "v2", 0.60),                 # invented availability
        ("T", "emp_ci", "labor", "mapped", "o1", 0.90),
    ],
    columns=["survey", "target_var", "domain", "status", "source_vars", "confidence"],
)


def test_split_vars():
    assert split_vars(" A; b ;") == frozenset({"a", "b"})
    assert split_vars(float("nan")) == frozenset()


def test_derived_and_constant_are_not_scored():
    res = evaluate(GOLD, PROPOSALS)
    assert set(res["aligned"]["target_var"]) == {"sexo_ci", "aedu_ci", "ylm_ci", "luz_ch", "piso_ch"}


def test_source_scores():
    src = evaluate(GOLD, PROPOSALS)["sources"]
    # gold-mapped variables: tp = 1 + 2 + 0, fp = 0 + 1 + 0, fn = 0 + 1 + 1
    assert math.isclose(src["precision"], 3 / 4)
    assert math.isclose(src["recall"], 3 / 5)
    assert math.isclose(src["exact_match"], 1 / 3)
    assert math.isclose(src["any_overlap"], 2 / 3)
    assert math.isclose(src["covers_gold"], 1 / 3)       # only sexo_ci contains all gold variables
    assert src["n"] == 3


def test_availability_scores():
    av = evaluate(GOLD, PROPOSALS)["availability"]
    # "not available" as positive: tp = luz_ch, fp = ylm_ci, fn = piso_ch
    assert math.isclose(av["precision"], 1 / 2)
    assert math.isclose(av["recall"], 1 / 2)
    assert math.isclose(av["accuracy"], 3 / 5)


def test_triage():
    tri = evaluate(GOLD, PROPOSALS)["triage"].set_index("threshold")
    assert tri.loc[0.9, "auto_accepted"] == 2          # sexo_ci, luz_ch
    assert math.isclose(tri.loc[0.9, "exact_among_auto"], 1.0)
    assert tri.loc[0.5, "auto_accepted"] == 4
    assert math.isclose(tri.loc[0.5, "exact_among_auto"], 2 / 4)


def test_errors_list():
    err = evaluate(GOLD, PROPOSALS)["errors"]
    assert set(err["target_var"]) == {"aedu_ci", "ylm_ci", "piso_ch"}


def test_missing_proposal_counts_as_not_available():
    res = evaluate(GOLD, PROPOSALS[PROPOSALS["target_var"] != "sexo_ci"])
    row = res["aligned"].set_index("target_var").loc["sexo_ci"]
    assert row["status_llm"] == "no_answer" and row["fn"] == 1
