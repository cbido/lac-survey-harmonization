# Mapping evaluation: CHL_2022 (reviewed gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 1.00 | 1.00 | 1.00 | 1.00 | 55 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.99 | 0.97 | 0.98 | 0.92 | 0.92 | 0.96 | 50 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 7 | 1.00 |
| design | 0.89 | 0.89 | 0.89 | 0.89 | 0.89 | 0.89 | 9 | 1.00 |
| education | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 3 | 1.00 |
| housing | 1.00 | 0.90 | 0.95 | 0.80 | 0.80 | 1.00 | 10 | 1.00 |
| income | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 11 | 1.00 |
| labor | 0.93 | 0.93 | 0.93 | 0.90 | 0.90 | 0.90 | 10 | 1.00 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 54 | 0.98 | 0.93 | 1 |
| 0.70 | 48 | 0.87 | 0.94 | 7 |
| 0.90 | 18 | 0.33 | 1.00 | 37 |

## Disagreements with the gold standard (4)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CHL_2022 | estrato_ci | mapped | estrato | mapped | varstrat |
| CHL_2022 | ocupa_ci | mapped | oficio4_08 | mapped | oficio1_08 |
| CHL_2022 | dorm_ch | mapped | v27a;v29a | mapped | v29a |
| CHL_2022 | viviprop_ch | mapped | v13;v13_propia | mapped | v13 |
