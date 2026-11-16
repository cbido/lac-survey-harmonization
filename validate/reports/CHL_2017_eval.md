# Mapping evaluation: CHL_2017 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 0.60 | 0.33 | 0.43 | 0.85 | 53 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.58 | 0.64 | 0.61 | 0.52 | 0.77 | 0.82 | 44 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.75 | 1.00 | 0.86 | 0.83 | 1.00 | 1.00 | 6 | 1.00 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 7 | 0.78 |
| education | 0.17 | 0.20 | 0.18 | 0.00 | 0.33 | 0.33 | 3 | 1.00 |
| housing | 0.72 | 0.65 | 0.68 | 0.50 | 0.64 | 0.71 | 14 | 0.87 |
| income | 0.18 | 0.18 | 0.18 | 0.00 | 0.40 | 0.60 | 5 | 0.64 |
| labor | 0.70 | 1.00 | 0.82 | 0.44 | 1.00 | 1.00 | 9 | 1.00 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 51 | 0.96 | 0.51 | 2 |
| 0.70 | 42 | 0.79 | 0.55 | 11 |
| 0.90 | 18 | 0.34 | 0.83 | 35 |

## Disagreements with the gold standard (27)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CHL_2017 | upm_ci | not_available |  | mapped | varunit |
| CHL_2017 | estrato_ci | not_available |  | mapped | varstrat |
| CHL_2017 | condocup_ci | mapped | edad;o1;o2;o3;o6 | mapped | activ;edad;o1;o2;o3;o5;o6 |
| CHL_2017 | ocupa_ci | mapped | oficio4 | mapped | oficio1;oficio4 |
| CHL_2017 | rama_ci | mapped | rama4 | mapped | rama1;rama4 |
| CHL_2017 | ylmpri_ci | mapped | yoprcor | mapped | y0101c;y0701c;yoprcor |
| CHL_2017 | ylnmpri_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512 |
| CHL_2017 | ylmsec_ci | mapped | yoprcor;ytrabajocor | mapped | yosa;yosi |
| CHL_2017 | ylm_ci | mapped | ytrabajocor | mapped | yoprcor;ytrabajocor |
| CHL_2017 | ylnm_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512;y0801;yac2 |
| CHL_2017 | ynlm_ci | mapped | yautcor;ysub;ytrabajocor | mapped | yaimcorh;ytotcor;ytrabajocor |
| CHL_2017 | rentaimp_ch | not_available |  | mapped | yaimcorh;yaimh |
| CHL_2017 | remesas_ci | not_available |  | mapped | yfa1;yfa2 |
| CHL_2017 | asiste_ci | mapped | e3 | mapped | asiste;e3 |
| CHL_2017 | aedu_ci | mapped | e3;e6a;e6b | mapped | esc |
| CHL_2017 | edupub_ci | mapped | e9depen | mapped | depen;e10;e3 |
| CHL_2017 | aguafuente_ch | mapped | v20;v22 | mapped | v20;v21 |
| CHL_2017 | bano_ch | mapped | v23 | mapped | v23;v27b |
| CHL_2017 | luz_ch | mapped | v24 | not_available |  |
| CHL_2017 | dorm_ch | mapped | v27a | mapped | v30a |
| CHL_2017 | cuartos_ch | mapped | v27a;v27b;v28 | not_available |  |
| CHL_2017 | auto_ch | mapped | r15 | mapped | r14;r15 |
| CHL_2017 | viviprop_ch | mapped | v9 | mapped | v13 |
| CHL_2017 | afiliado_ci | mapped | o28 | mapped | o28;o29 |
| CHL_2017 | tipocontrato_ci | mapped | o16;o17 | mapped | o12;o16;o17 |
| CHL_2017 | ypen_ci | mapped | y26_2bm1;y26_2bm2;y26_2c;y26_2em1;y26_2em2;y26_2f;y26_2g;y26_2h;y26_2i;y26_2j | mapped | y260201c;y2603c;yinv01;yinv03;ymon;yorf;yotp |
| CHL_2017 | migrante_ci | mapped | r1b | mapped | r1a;r1b;r2 |
