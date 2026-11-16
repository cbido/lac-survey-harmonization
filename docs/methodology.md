# Method and limits

This note describes what the pipeline does, what was measured, and where the results
should not be trusted. Every number comes from a file in the repository, named beside it.

## 1. The question

Statistical offices change their questionnaires from one round to the next, and no two
countries name their variables alike. Harmonizing them by hand takes weeks per survey. A
language model can draft the mapping in minutes. The work here measures how good those
drafts are and builds the checks that make them usable.

## 2. Design

**Target schema.** 58 variables with the names and codes of the IDB's harmonized household
surveys (`config/target_schema.yml`).

**Reference.** The IDB publishes the Stata program it uses for each survey. A parser reads
which raw variables feed each harmonized variable (`harmonize/extract_gold_from_idb.py`).
Of 697 raw-variable names extracted from eight programs, 687 exist in the corresponding
data dictionary (`docs/reference_across_rounds.md`).

**Mapping.** The model receives the survey's data dictionary and the list of targets, and
names the raw variables for each or says the survey lacks the information
(`harmonize/propose_mappings.py`). It never sees microdata or the reference.

**Evaluation.** Proposals are scored against the reference on availability and on the
variables chosen (`validate/evaluate_mappings.py`, `docs/results.md`).

**Review.** For Casen 2022 every disagreement was settled by a person
(`validate/review/CHL_2022_review.csv`), which gives a reviewed gold standard.

**Code.** From the reviewed mappings the model writes one SQL expression per variable,
with a note and its assumptions (`harmonize/code/CHL_2022.yml`). Each expression is run
and tested before it enters the table (`harmonize/build_harmonized.py`).

**Open-text coding.** For a random sample of workers the model reads the job title,
the tasks and what the workplace does, and assigns an occupation and an industry code
from the survey's own lists (`coding/`). The ministry's codes are the reference.

**Indicators and small areas.** Poverty and inequality with the survey design in R, and
a Fay-Herriot model by comuna checked against the ministry's published estimates.

## 3. What was found

### Mapping (eight surveys, 464 proposals)

- Two proposals named a variable absent from the dictionary. Validation caught both.
- Agreement with the reference on exact variables runs from 49% to 68% by survey, and
  the model includes every reference variable in 57% to 91% of targets.
- In Casen 2022 the reference marks 20 targets as unavailable. The model mapped 15, and
  the review accepted all 15.

### Review (Casen 2022, 33 disagreements)

The reviewer took the model's mapping in 25, accepted both in 6 and kept the reference in
2. Two of the 25 were later corrected because the data proved them wrong (next section),
which leaves the model exactly right on 92% of scored targets against the reviewed gold,
and 49% against the untouched reference.

### Generated code (Casen 2022, 50 expressions)

| Outcome | Variables |
|---|---|
| Passed every test on the first attempt and stayed unchanged | 40 |
| Failed to run and was corrected by hand (a date stored as milliseconds) | 1 |
| Ran, produced valid codes, and was wrong | 4 |
| Declined by the model because the schema defines no codes for the target | 5 |

The four that ran and were wrong are the instructive ones. None raised an error:

- **Bedrooms** used a question asked only of households that share a dwelling, so 96% of
  rows were missing. The coverage warning caught it.
- **Occupation** used the one-digit code, which cannot separate sales from service
  workers, so one of the nine target groups was empty. The unused-code warning caught it.
- **Public school attendance** coded people who do not study as 0.
- **Non-labor income** had negative values after a subtraction.

The findings were sent back to the model, which rewrote all four correctly. The first
two also traced back to review decisions, recorded in
`validate/review/CHL_2022_corrections.csv`.

### Occupation and industry coding (Casen 2022, 1,500 workers, `coding/output/`)

| Agreement with the ministry's code | Occupation, 4 digits | Industry, survey category |
|---|---|---|
| Model, all cases | 61.1% (58.6 to 63.5) | 70.3% (68.0 to 72.6) |
| Lookup table built from all other coded workers, texts it has seen | 72.0% | 79.1% |
| Model, those same cases | 67.5% | 75.0% |
| Model, texts the table has never seen | 50.2% | 66.3% |
| Lookup table where it has the text, model otherwise | 63.9% | 72.1% |

At one digit the model agrees on 79.5% of occupations (kappa 0.76) and on 87.3% of
industry sections (kappa 0.86). Among groups with 40 cases or more, agreement is lowest for technicians (57% at one digit),
skilled agricultural workers (60%) and, in industry, for other services (48%) and
administrative and support services (59%).

Three things follow. A lookup table beats the model on texts it has already seen, so a
previously coded file is worth more than the model where one exists. The table has seen
only 63% of job titles and 46% of workplace texts, and the model codes the rest. And the
model's confidence is informative: cases rated 0.9 or higher, a quarter of the sample,
agree at four digits 94.5% of the time, so a review queue ordered by confidence is
feasible.

### Poverty (Casen 2022, `indicators/output/CHL_2022_indicators.csv`)

The official variable, carried untouched, gives 6.5% (standard error 0.14 points), which
is the published rate. Harmonized income reaches that figure only in steps:

| Income definition, per equivalent person | Poverty rate |
|---|---|
| Harmonized labor and non-labor income | 18.9% |
| Adding harmonized imputed rent | 8.8% |
| Replacing raw labor components with the ministry's corrected labor income | 7.3% |
| Ministry's total household income (official) | 6.5% |

Two harmonization choices move the indicator more than any sampling error: whether
imputed rent counts as income, and whether labor income is the sum of raw components or
the ministry's aggregate, which includes imputation for non-response. Raw components add
up to 91% of the corrected total.

### Small areas (`sae/output/`)

Fay-Herriot on the arcsine scale for 325 comunas, synthetic estimates for the other 20.

| Estimate | Mean absolute difference from the official estimate | Inside the official interval |
|---|---|---|
| Direct | 2.6 points | 79% |
| Random forest on the same auxiliary variables | 2.4 points | 79% |
| Fay-Herriot | 1.7 points | 92% |

## 4. Limits

**The reviewed gold is not independent of the model.** The reviewer saw the model's
answer, and targets where model and reference agreed were accepted without review. One
survey of eight is reviewed.

**The reference is one way to harmonize.** Several disagreements are choices between a
ministry aggregate and its components. The review recorded five of them as the model
being right where "both acceptable" would also be defensible.

**The small-area model uses the 2020 official estimate as an auxiliary variable.** The
ministry's model relies on administrative records that are not published in ready form.
The 2020 estimate carries much of the signal and is itself a product of the ministry's
model, so closeness to the 2022 official figures is partly inherited. The official
estimate is also a model output and not the truth.

**Sampling variances are smoothed crudely.** One median design effect is applied to all
comunas. The ministry fits a variance function.

**Published figures still to check.** Bolivia's poverty rates against INE's, and Chile's
2015 to 2020 rates against the report of each round (`docs/ingest_checks.md`).

**Open-text coding is scored against one coder.** The ministry's coders work with the
full questionnaire and their own manuals, and two human coders do not always agree
either. No second human coding of the sample exists here to say how much of the
disagreement is the model's error. The model saw three text fields and nothing else
about the worker. The sample is 1,500 of 85,502 coded workers, from one survey.

**Not built.** Harmonized tables for the other seven surveys, and Costa Rica's
microdata, which could not be obtained.

**One model, one prompt, one run.** No comparison across models or prompts, and no
repeated runs to measure variability.
