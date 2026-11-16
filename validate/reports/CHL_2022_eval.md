# Mapping evaluation: CHL_2022 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 1.00 | 0.25 | 0.40 | 0.73 | 55 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.30 | 0.45 | 0.36 | 0.49 | 0.57 | 0.71 | 35 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.71 | 0.42 | 0.53 | 0.71 | 0.71 | 0.71 | 7 | 1.00 |
| design | 0.89 | 0.89 | 0.89 | 0.89 | 0.89 | 0.89 | 9 | 1.00 |
| education | 0.33 | 0.25 | 0.29 | 0.00 | 0.50 | 0.50 | 2 | 0.67 |
| housing | 0.78 | 0.70 | 0.74 | 0.20 | 0.40 | 1.00 | 5 | 0.67 |
| income | 0.02 | 0.07 | 0.03 | 0.00 | 0.00 | 0.20 | 5 | 0.45 |
| labor | 0.56 | 0.45 | 0.50 | 0.43 | 0.57 | 0.71 | 7 | 0.70 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 54 | 0.98 | 0.41 | 1 |
| 0.70 | 48 | 0.87 | 0.46 | 7 |
| 0.90 | 18 | 0.33 | 0.56 | 37 |

## Disagreements with the gold standard (33)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CHL_2022 | estrato_ci | mapped | estrato | mapped | varstrat |
| CHL_2022 | condocup_ci | mapped | edad;o1;o2;o3;o6 | mapped | activ;edad |
| CHL_2022 | horaspri_ci | mapped | y2_hrs | mapped | o10 |
| CHL_2022 | ocupa_ci | not_available |  | mapped | oficio1_08 |
| CHL_2022 | rama_ci | mapped | rama4 | mapped | rama1 |
| CHL_2022 | ylmpri_ci | mapped | yoprcor | mapped | y0101;y0301;y0302;y0303;y0304;y0305;y0306;y0701 |
| CHL_2022 | ylnmpri_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512;y0801 |
| CHL_2022 | ylmsec_ci | mapped | yoprcor;ytrabajocor | mapped | yosa;yosi |
| CHL_2022 | ylm_ci | mapped | ytrabajocor | mapped | y0101;y0301;y0302;y0303;y0304;y0305;y0306;y0401;y0402;y0403;y0404;y0701;y0901;y1101;yosa;yosi |
| CHL_2022 | ylnm_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512;y0801;yac2 |
| CHL_2022 | ynlm_ci | mapped | yautcor;ysub;ytrabajocor | mapped | yah1;yah2;yama;ydes;ydim;ydon;yfa1;yfa2;yfam;yids;ymes;yotr;yre1;yre2;yre3;yrut;ysub;yta1;yta2;ytro |
| CHL_2022 | rentaimp_ch | not_available |  | mapped | yaimh |
| CHL_2022 | remesas_ci | not_available |  | mapped | yfa2 |
| CHL_2022 | asiste_ci | mapped | e3 | mapped | asiste;e3 |
| CHL_2022 | aedu_ci | mapped | e3;e6a;e6b | mapped | esc |
| CHL_2022 | edupub_ci | not_available |  | mapped | asiste;depen;e10;e9depen |
| CHL_2022 | aguared_ch | mapped | v20 | mapped | v20;v22 |
| CHL_2022 | aguafuente_ch | mapped | v20;v22 | mapped | v20;v21 |
| CHL_2022 | piso_ch | not_available |  | mapped | v4 |
| CHL_2022 | pared_ch | not_available |  | mapped | v2 |
| CHL_2022 | techo_ch | not_available |  | mapped | v6 |
| CHL_2022 | dorm_ch | mapped | v27a;v29a | mapped | v29a |
| CHL_2022 | auto_ch | not_available |  | mapped | r14 |
| CHL_2022 | internet_ch | not_available |  | mapped | r17a;r17b;r17c;r17d;r17e |
| CHL_2022 | viviprop_ch | mapped | v13;v13_propia | mapped | v13 |
| CHL_2022 | lp_ci | not_available |  | mapped | lp |
| CHL_2022 | lpe_ci | not_available |  | mapped | li |
| CHL_2022 | afiliado_ci | mapped | o31 | mapped | o31;o32 |
| CHL_2022 | tipocontrato_ci | not_available |  | mapped | o12;o18;o19 |
| CHL_2022 | tamemp_ci | not_available |  | mapped | o25 |
| CHL_2022 | ypen_ci | mapped | y28_1b;y28_1c;y28_1d;y28_1e;y28_1f;y28_1g;y28_1h | mapped | y2803;yesp;yinv02;ymon02;yorf;yotp |
| CHL_2022 | migrante_ci | mapped | r1b | mapped | lugar_nac |
| CHL_2022 | dis_ci | mapped | h7a;h7b;h7c;h7d;h7e;h7f | mapped | disc_wg |
