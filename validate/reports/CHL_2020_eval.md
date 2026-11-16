# Mapping evaluation: CHL_2020 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 0.93 | 0.70 | 0.80 | 0.87 | 55 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.28 | 0.61 | 0.39 | 0.51 | 0.71 | 0.83 | 35 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.71 | 0.83 | 0.77 | 0.67 | 0.83 | 0.83 | 6 | 1.00 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 9 | 1.00 |
| education | 0.43 | 0.75 | 0.55 | 0.00 | 0.50 | 1.00 | 2 | 1.00 |
| housing | 0.60 | 0.90 | 0.72 | 0.40 | 0.80 | 1.00 | 5 | 1.00 |
| income | 0.03 | 0.13 | 0.05 | 0.00 | 0.20 | 0.40 | 5 | 0.45 |
| labor | 0.46 | 0.50 | 0.48 | 0.38 | 0.62 | 0.75 | 8 | 0.90 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 55 | 1.00 | 0.58 | 0 |
| 0.70 | 48 | 0.87 | 0.67 | 7 |
| 0.90 | 17 | 0.31 | 0.76 | 38 |

## Disagreements with the gold standard (23)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CHL_2020 | afroind_ci | mapped | r3 | mapped | etnia;r3 |
| CHL_2020 | condocup_ci | mapped | edad;o1;o2;o3;o6 | mapped | activ;edad |
| CHL_2020 | horaspri_ci | mapped | y2_hrs | not_available |  |
| CHL_2020 | ocupa_ci | mapped | oficio4_88 | mapped | activ;oficio1_08;oficio4_08 |
| CHL_2020 | rama_ci | mapped | rama4 | mapped | activ;rama1;rama4 |
| CHL_2020 | ylmpri_ci | mapped | yoprcor | mapped | y0101;y0101c;y0301;y0302;y0303;y0304;y0305;y0306;y0401;y0402;y0403;y0404;y0701;y0701c;yoprcor |
| CHL_2020 | ylnmpri_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512;y0801 |
| CHL_2020 | ylmsec_ci | mapped | yoprcor;ytrabajocor | mapped | yosa;yosi |
| CHL_2020 | ylm_ci | mapped | ytrabajocor | mapped | y0101;y0301;y0302;y0303;y0304;y0305;y0306;y0401;y0402;y0403;y0404;y0701;yosa;yosi |
| CHL_2020 | ylnm_ci | not_available |  | mapped | y0501;y0502;y0503;y0504;y0505;y0506;y0507;y0508;y0509;y0510;y0511;y0512;y0801 |
| CHL_2020 | ynlm_ci | mapped | yautcor;ysub;ytrabajocor | mapped | y2801;y280202;y2803;y2804;yah1;yah2;yama;ydes;ydim;ydon;yesp;yfa1;yfa2;yfam;yids;yinv02;yinv03;ymes;ymon;yorf;yotp;yotr;yre1;yre2;yre3;yrut;ysub;yta1;yta2;ytro |
| CHL_2020 | rentaimp_ch | not_available |  | mapped | yaimh |
| CHL_2020 | remesas_ci | not_available |  | mapped | yfa1;yfa2 |
| CHL_2020 | asiste_ci | mapped | e2 | mapped | asiste2;e2 |
| CHL_2020 | aedu_ci | mapped | e2;e6a;e6b | mapped | e6a;e6b;educ;esc;esc2 |
| CHL_2020 | aguared_ch | mapped | v20 | mapped | v20;v20_red;v22 |
| CHL_2020 | aguafuente_ch | mapped | v20;v22 | mapped | v20;v20_esp;v20_red |
| CHL_2020 | viviprop_ch | mapped | v13;v13_propia | mapped | v13;v13_arrendada;v13_cedida;v13_propia |
| CHL_2020 | lp_ci | not_available |  | mapped | lp |
| CHL_2020 | lpe_ci | not_available |  | mapped | li |
| CHL_2020 | cotizando_ci | mapped | o32 | mapped | activ;o32 |
| CHL_2020 | ypen_ci | mapped | y28_1a;y28_1b;y28_1c;y28_1d;y28_1e;y28_1f;y28_1g;y28_1h | mapped | y280201;y280202;y2803;yinv01;yinv02;yinv03;ymon;yorf |
| CHL_2020 | migrante_ci | mapped | r1b | mapped | inmigrante |
