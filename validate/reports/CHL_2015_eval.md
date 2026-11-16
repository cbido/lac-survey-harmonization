# Mapping evaluation: CHL_2015 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 0.75 | 0.30 | 0.43 | 0.85 | 54 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.38 | 0.55 | 0.45 | 0.59 | 0.70 | 0.80 | 44 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.86 | 1.00 | 0.92 | 0.83 | 1.00 | 1.00 | 6 | 0.86 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 7 | 0.78 |
| education | 0.29 | 0.40 | 0.33 | 0.00 | 0.67 | 0.67 | 3 | 1.00 |
| housing | 0.78 | 0.64 | 0.70 | 0.50 | 0.64 | 0.79 | 14 | 0.93 |
| income | 0.04 | 0.12 | 0.06 | 0.20 | 0.20 | 0.40 | 5 | 0.64 |
| labor | 0.73 | 0.57 | 0.64 | 0.67 | 0.67 | 0.78 | 9 | 1.00 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 54 | 1.00 | 0.54 | 0 |
| 0.70 | 44 | 0.81 | 0.57 | 10 |
| 0.90 | 21 | 0.39 | 0.86 | 33 |

## Disagreements with the gold standard (25)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CHL_2015 | upm_ci | not_available |  | mapped | varunit |
| CHL_2015 | estrato_ci | not_available |  | mapped | varstrat |
| CHL_2015 | dis_ci | not_available |  | mapped | s31c1;s31c2;s31c3 |
| CHL_2015 | condocup_ci | mapped | edad;o1;o2;o3;o6 | mapped | activ;edad |
| CHL_2015 | ocupa_ci | mapped | oficio4 | mapped | oficio1 |
| CHL_2015 | rama_ci | mapped | rama4 | mapped | rama1 |
| CHL_2015 | ylnmpri_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512 |
| CHL_2015 | ylmsec_ci | mapped | yoprcor;ytrabajocor | mapped | yosa;yosi |
| CHL_2015 | ylm_ci | mapped | ytrabajocor | mapped | y0101;y0301;y0302;y0303;y0304;y0305;y0306;y0401;y0402;y0403;y0404;y0701;yosa;yosi |
| CHL_2015 | ylnm_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512;y0801;yac2 |
| CHL_2015 | ynlm_ci | mapped | yautcor;ysub;ytrabajocor | mapped | y2601;y260201;y260202;y2603;y2604;yah1;yah2;yama;ydes;ydim;ydon;yesp;yfa1;yfa2;yfam;yids;yinv01;yinv02;yinv03;ymes;ymon;yorf;yotp;yotr;yre1;yre2;yre3;yrut;ysub;ytro |
| CHL_2015 | rentaimp_ch | not_available |  | mapped | yaimh |
| CHL_2015 | remesas_ci | not_available |  | mapped | yfa1;yfa2 |
| CHL_2015 | asiste_ci | mapped | e3 | mapped | asiste;e3 |
| CHL_2015 | aedu_ci | mapped | e3;e6a;e6b | mapped | esc |
| CHL_2015 | edupub_ci | mapped | e7depen | mapped | depen;e3;e7depen;e8 |
| CHL_2015 | aguared_ch | mapped | v23 | mapped | v23;v24 |
| CHL_2015 | aguafuente_ch | mapped | v23;v24 | mapped | v23 |
| CHL_2015 | dorm_ch | mapped | v29a | mapped | v32a |
| CHL_2015 | cuartos_ch | mapped | v29a;v29b;v30 | not_available |  |
| CHL_2015 | auto_ch | mapped | r13b | mapped | r12;r13b |
| CHL_2015 | internet_ch | mapped | r15a;r15b;r15c;r15d;r15e;r15f | mapped | r15a;r15b;r15c;r15d |
| CHL_2015 | viviprop_ch | mapped | v9 | mapped | v12 |
| CHL_2015 | ypen_ci | mapped | y26_2bm1;y26_2bm2;y26_2c;y26_2em1;y26_2em2;y26_2f;y26_2g;y26_2h;y26_2i;y26_2j | mapped | y260201;y2603;yinv01;yinv03;ymon;yorf;yotp |
| CHL_2015 | migrante_ci | mapped | r1b | mapped | r1a;r1b |
