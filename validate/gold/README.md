# Gold standards

Two kinds of file live here.

`<survey>_gold_draft.csv` is the IDB harmonization program as parsed by
`harmonize/extract_gold_from_idb.py`. It is the reference, untouched.

`<survey>_gold.csv` is the reviewed gold standard. It exists only once a person has gone
through the disagreements between the model and the reference.

## Review procedure

1. `python validate/build_review.py` writes one sheet per survey to `validate/review/`,
   listing every target where the model and the reference disagree, with the variables
   of each side, their labels and the model's reasoning.
2. The reviewer fills `decision` for every row, checking the questionnaire and codebook
   in `data/questionnaires/` where the labels are not enough.

   | decision | meaning |
   |---|---|
   | reference | keep the reference mapping |
   | model | the model's mapping is the correct one |
   | both | either set of variables is acceptable |
   | neither | both are wrong, and `final_source_vars` holds the correct variables |

3. `python validate/apply_review.py --survey <survey>` writes the reviewed gold file. It
   keeps the reference mapping of every target on record next to the final one.

## Two limits of this procedure

Targets where the model and the reference agree are accepted without a manual check.
Agreement between two independent sources is good evidence, and it is weaker than a
review.

The reviewer sees the model's answer, so the reviewed gold is not independent of the
model. For that reason results are reported against both files: the draft shows
agreement with the IDB program, and the reviewed file shows accuracy as judged by a
person who had both answers in front of her.

## Scope of the review so far

Casen 2022 is reviewed in full (`CHL_2022_gold.csv`). The other seven surveys have their
review sheets in `validate/review/` and no reviewed gold, so their results are agreement
with the reference only.
