# Mapping evaluation: BOL_2017 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 1.00 | 0.50 | 0.67 | 0.98 | 47 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.75 | 0.86 | 0.80 | 0.58 | 0.91 | 0.98 | 45 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.62 | 0.83 | 0.71 | 0.67 | 0.83 | 0.83 | 6 | 1.00 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 6 | 1.00 |
| education | 0.57 | 1.00 | 0.73 | 0.00 | 1.00 | 1.00 | 3 | 1.00 |
| housing | 0.76 | 1.00 | 0.87 | 0.67 | 1.00 | 1.00 | 12 | 1.00 |
| income | 0.84 | 0.77 | 0.80 | 0.50 | 0.62 | 1.00 | 8 | 0.89 |
| labor | 0.58 | 1.00 | 0.74 | 0.40 | 1.00 | 1.00 | 10 | 1.00 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 47 | 1.00 | 0.57 | 0 |
| 0.70 | 41 | 0.87 | 0.56 | 6 |
| 0.90 | 21 | 0.45 | 0.86 | 26 |

## Disagreements with the gold standard (20)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| BOL_2017 | afroind_ci | mapped | s03a_04 | mapped | s03a_04;s03a_04npioc |
| BOL_2017 | condocup_ci | mapped | s06a_01;s06a_02;s06a_03;s06a_04;s06a_05 | mapped | condact;s02a_03;s06a_01;s06a_02;s06a_03;s06a_04;s06a_05 |
| BOL_2017 | tamemp_ci | mapped | s06b_21 | mapped | s06b_21;s06b_21a |
| BOL_2017 | horaspri_ci | mapped | phrs | mapped | phrs;s06b_22;s06b_23aa;s06b_23ab |
| BOL_2017 | horastot_ci | mapped | tothrs | mapped | phrs;shrs;tothrs |
| BOL_2017 | ocupa_ci | mapped | s06b_11a_cod | mapped | cob_op;s06b_11a_cod |
| BOL_2017 | rama_ci | mapped | caeb_op | mapped | caeb_op;s06b_12a_cod |
| BOL_2017 | ylmpri_ci | mapped | s06c_25a;s06c_25b;s06c_26a;s06c_26b;s06c_27aa;s06c_27ab;s06c_27ba;s06c_27bb;s06d_33a;s06d_33b | mapped | s06c_25a;s06c_25b;s06d_31a;s06d_31b;yprilab |
| BOL_2017 | ylmsec_ci | mapped | s06g_47a;s06g_47b;s06g_48a;s06g_48a1 | mapped | s06g_47a;s06g_47b;s06g_48a1;s06g_49a;s06g_49b;s06g_51a;s06g_51b |
| BOL_2017 | ynlm_ci | mapped | s07a_01a;s07a_01b;s07a_01c;s07a_01d;s07a_01e0;s07a_02a;s07a_02b;s07a_02c;s07a_03a;s07a_03b;s07a_03c;s07a_04a;s07a_04b;s07a_04c;s07b_05aa;s07b_05ab;s07b_05ba;s07b_05bb;s07c_07;s07c_08a;s07c_08b;s07c_10 | mapped | s07a_01a;s07a_01b;s07a_01c;s07a_01d;s07a_01e0;s07a_02a;s07a_02b;s07a_02c;s07a_03a;s07a_03b;s07a_03c;s07a_04a;s07a_04b;s07a_04c;s07b_05aa;s07b_05ba;s07c_08a;ynolab |
| BOL_2017 | remesas_ci | mapped | s07c_07;s07c_08a;s07c_08b;s07c_10 | mapped | s07c_06;s07c_07;s07c_08a;s07c_08b;s07c_10 |
| BOL_2017 | rentaimp_ch | not_available |  | mapped | s01a_02;s01a_05 |
| BOL_2017 | aedu_ci | mapped | s05a_02a;s05a_02b | mapped | aestudio;s05a_02a;s05a_02b |
| BOL_2017 | asiste_ci | mapped | s05a_05 | mapped | s05a_05;s05b_10 |
| BOL_2017 | edupub_ci | mapped | s05a_09 | mapped | s05a_05;s05a_09 |
| BOL_2017 | bano_ch | mapped | s01a_15;s01a_16 | mapped | s01a_15;s01a_16;s01a_17 |
| BOL_2017 | piso_ch | mapped | s01a_09 | mapped | s01a_09;s01a_09e |
| BOL_2017 | pared_ch | mapped | s01a_06 | mapped | s01a_06;s01a_06e |
| BOL_2017 | techo_ch | mapped | s01a_08 | mapped | s01a_08;s01a_08e |
| BOL_2017 | migrante_ci | mapped | s03a_04 | mapped | s03a_01a;s03a_01e |
