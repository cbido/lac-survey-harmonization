# Mapping evaluation: BOL_2021 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 1.00 | 0.33 | 0.50 | 0.96 | 47 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.74 | 0.82 | 0.78 | 0.57 | 0.84 | 0.91 | 44 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.62 | 0.83 | 0.71 | 0.67 | 0.83 | 0.83 | 6 | 1.00 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 6 | 1.00 |
| education | 0.40 | 0.50 | 0.44 | 0.00 | 0.67 | 0.67 | 3 | 1.00 |
| housing | 0.67 | 0.86 | 0.75 | 0.50 | 0.83 | 0.92 | 12 | 1.00 |
| income | 0.80 | 0.78 | 0.79 | 0.38 | 0.62 | 0.88 | 8 | 0.89 |
| labor | 0.69 | 1.00 | 0.81 | 0.67 | 1.00 | 1.00 | 9 | 0.91 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 46 | 0.98 | 0.57 | 1 |
| 0.70 | 45 | 0.96 | 0.56 | 2 |
| 0.90 | 20 | 0.43 | 0.80 | 27 |

## Disagreements with the gold standard (21)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| BOL_2021 | afroind_ci | mapped | s01a_09 | mapped | s01a_09;s01a_09npioc |
| BOL_2021 | cotizando_ci | not_available |  | mapped | s04f_36 |
| BOL_2021 | condocup_ci | mapped | desocupado;ocupado;pei | mapped | condact;desocupado;ocupado;pei;pet;s04a_01 |
| BOL_2021 | ocupa_ci | mapped | s04b_09a_cod | mapped | cob_op;s04b_09a_cod |
| BOL_2021 | rama_ci | mapped | caeb_op | mapped | caeb_op;s04b_10a_cod |
| BOL_2021 | ylmpri_ci | mapped | s04c_17a;s04c_17b;s04c_18a;s04c_18b;s04c_19aa;s04c_19ab;s04c_19ba;s04c_19bb;s04d_24a;s04d_24b | mapped | yprilab |
| BOL_2021 | ylnmpri_ci | mapped | s04c_21a;s04c_21a1;s04c_21a2;s04c_21b;s04c_21b1;s04c_21b2;s04c_21c;s04c_21c1;s04c_21d;s04c_21d1;s04c_21d2;s04c_21e;s04c_21e1;s04c_21e2 | mapped | s04c_21a;s04c_21a1;s04c_21a2;s04c_21b;s04c_21b1;s04c_21b2;s04c_21c;s04c_21c1;s04c_21c2;s04c_21d;s04c_21d1;s04c_21d2;s04c_21e;s04c_21e1;s04c_21e2 |
| BOL_2021 | ylmsec_ci | mapped | s04f_31a;s04f_31b;s04f_32a;s04f_32a1 | mapped | s04f_31a;s04f_31b;s04f_33a;s04f_33b;s04f_34a;s04f_34b;yseclab |
| BOL_2021 | ynlm_ci | mapped | s05a_01a;s05a_01b;s05a_01c;s05a_01d;s05a_01e0;s05a_02a;s05a_02b;s05a_02c;s05a_03a;s05a_03b;s05a_03c;s05a_04a;s05a_04b;s05a_04d;s05b_05aa;s05b_05ab;s05b_05ba;s05b_05bb;s05b_07aa;s05b_07ab;s05c_09;s05c_10a;s05c_10b | mapped | s05a_01a;s05a_01b;s05a_01c;s05a_01d;s05a_01e0;s05a_02a;s05a_02b;s05a_02c;s05a_03a;s05a_03b;s05a_03c;s05a_04a;s05a_04b;s05a_04c;s05a_04d;s05b_05aa;s05b_05ab;s05b_05ba;s05b_05bb;s05b_07aa;s05b_07ab;s05c_09;s05c_10a;ynolab |
| BOL_2021 | remesas_ci | mapped | s05c_09;s05c_10a;s05c_10b | mapped | s05b_05ba;s05b_05bb;s05c_08;s05c_09;s05c_10a;s05c_10b |
| BOL_2021 | rentaimp_ch | not_available |  | mapped | s07a_02;s07a_05 |
| BOL_2021 | aedu_ci | mapped | s03a_02a;s03a_02c | mapped | aestudio |
| BOL_2021 | asiste_ci | mapped | s03a_04 | mapped | s03a_04;s03b_10 |
| BOL_2021 | edupub_ci | mapped | s03a_09 | mapped | s03a_04;s03a_09 |
| BOL_2021 | bano_ch | mapped | s07a_13;s07a_14 | mapped | s07a_13;s07a_14;s07a_15 |
| BOL_2021 | luz_ch | mapped | s07a_04;s07a_16 | mapped | s07a_16 |
| BOL_2021 | piso_ch | mapped | s07a_09 | mapped | s07a_09;s07a_09e |
| BOL_2021 | pared_ch | mapped | s07a_06 | mapped | s07a_06;s07a_06e |
| BOL_2021 | techo_ch | mapped | s07a_08 | mapped | s07a_08;s07a_08e |
| BOL_2021 | cel_ch | mapped | s03c_13 | mapped | item;s09c_14 |
| BOL_2021 | migrante_ci | mapped | s01a_09 | mapped | s01b_11a;s01b_11e |
