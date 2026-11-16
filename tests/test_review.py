import pandas as pd

from validate.apply_review import apply
from validate.evaluate_mappings import evaluate

DRAFT = pd.DataFrame(
    [
        ("T", "sexo_ci", "mapped", "sexo"),                 # agreed, not in the sheet
        ("T", "piso_ch", "not_available", ""),              # model found it
        ("T", "aedu_ci", "mapped", "e6a;e6b"),              # both acceptable
        ("T", "ocupa_ci", "mapped", "oficio4"),             # reference stays
        ("T", "luz_ch", "mapped", "v24"),                   # neither: reviewer writes the answer
        ("T", "emp_ci", "derived", ""),
    ],
    columns=["survey", "target_var", "status", "source_vars"],
)
REVIEW = pd.DataFrame(
    [
        ("piso_ch", "v4", "model", "", "exists in the questionnaire"),
        ("aedu_ci", "esc", "both", "", ""),
        ("ocupa_ci", "oficio1;oficio4", "reference", "", ""),
        ("luz_ch", "", "neither", "V24, v25", ""),
    ],
    columns=["target_var", "model_vars", "decision", "final_source_vars", "note"],
)
TARGETS = ["sexo_ci", "piso_ch", "aedu_ci", "ocupa_ci", "luz_ch", "emp_ci"]


def test_apply_review():
    gold = apply(DRAFT, REVIEW, TARGETS).set_index("target_var")
    assert gold.loc["sexo_ci", "review_decision"] == "agreed"
    assert gold.loc["emp_ci", "review_decision"] == "not scored"
    assert (gold.loc["piso_ch", "status"], gold.loc["piso_ch", "source_vars"]) == ("mapped", "v4")
    assert gold.loc["piso_ch", "reference_status"] == "not_available"       # the reference is kept on record
    assert (gold.loc["aedu_ci", "source_vars"], gold.loc["aedu_ci", "alt_source_vars"]) == ("e6a;e6b", "esc")
    assert gold.loc["ocupa_ci", "source_vars"] == "oficio4"
    assert gold.loc["luz_ch", "source_vars"] == "v24;v25"


def test_reviewed_gold_accepts_the_alternative_set():
    gold = apply(DRAFT, REVIEW, TARGETS)
    proposals = pd.DataFrame(
        [("T", "sexo_ci", "mapped", "sexo"), ("T", "piso_ch", "mapped", "v4"), ("T", "aedu_ci", "mapped", "esc"),
         ("T", "ocupa_ci", "mapped", "oficio1;oficio4"), ("T", "luz_ch", "not_available", "")],
        columns=["survey", "target_var", "status", "source_vars"],
    )
    res = evaluate(gold, proposals)
    rows = res["aligned"].set_index("target_var")
    assert rows.loc["aedu_ci", "exact"]                 # matched through the accepted alternative
    assert rows.loc["piso_ch", "exact"]
    assert not rows.loc["ocupa_ci", "exact"]            # the extra variable still counts against it
    assert set(res["errors"]["target_var"]) == {"ocupa_ci", "luz_ch"}
