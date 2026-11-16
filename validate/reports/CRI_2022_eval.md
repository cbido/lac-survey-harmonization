# Mapping evaluation: CRI_2022 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 1.00 | 0.33 | 0.50 | 0.96 | 48 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.57 | 0.42 | 0.49 | 0.62 | 0.76 | 0.84 | 45 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.86 | 0.86 | 0.86 | 0.67 | 0.83 | 1.00 | 6 | 1.00 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 6 | 1.00 |
| education | 0.50 | 0.67 | 0.57 | 0.33 | 0.67 | 0.67 | 3 | 1.00 |
| housing | 0.79 | 1.00 | 0.88 | 0.86 | 1.00 | 1.00 | 14 | 1.00 |
| income | 0.34 | 0.20 | 0.25 | 0.25 | 0.25 | 0.50 | 8 | 1.00 |
| labor | 0.40 | 0.21 | 0.28 | 0.38 | 0.62 | 0.75 | 8 | 0.80 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 47 | 0.98 | 0.62 | 1 |
| 0.70 | 40 | 0.83 | 0.68 | 8 |
| 0.90 | 21 | 0.44 | 0.95 | 27 |

## Disagreements with the gold standard (19)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CRI_2022 | dis_ci | mapped | a8a;a8b | mapped | a8a |
| CRI_2022 | cotizando_ci | mapped | a11 | mapped | a11;a12;e10a |
| CRI_2022 | afiliado_ci | not_available |  | mapped | a11 |
| CRI_2022 | condocup_ci | mapped | b1;b2;b3;b5;b6;b7a;b7b;b7c;b7d;b7e;b7f;b7g;b7h;b7i;b7j;b7k;b8;estabili;g6 | mapped | a5;condact |
| CRI_2022 | ypen_ci | mapped | h9h1;h9h2 | mapped | tape;tapn;tpe;tpn;ttpe;ttpn |
| CRI_2022 | horaspri_ci | mapped | c2a1 | mapped | horefepri;hornorpri |
| CRI_2022 | categopri_ci | mapped | c12;c13a;d1 | mapped | c12;posiemppri |
| CRI_2022 | tipocontrato_ci | mapped | e1 | mapped | e1;estabili;posiemppri |
| CRI_2022 | spublico_ci | not_available |  | mapped | secfuerzatrab;secinspri |
| CRI_2022 | ylmpri_ci | mapped | aif;asp;bsp;dif;gpia;gpif;gpina;gpsfi;ipsp;ithn;oisp;sesp;spif;spmn | mapped | ipbt;ipit;ipnt;ipsbt;ipsmb;spmb |
| CRI_2022 | ylnmpri_ci | mapped | inmpia;inmpina;ithn;spnma;spnmo;spnmt;spnmv;spnmvh | mapped | inmpia;inmpina;spnma;spnmo;spnmt;spnmv;spnmvh;tspnm |
| CRI_2022 | ylmsec_ci | mapped | gsi;ithn;ssmn | mapped | isit;issb |
| CRI_2022 | ynlm_ci | mapped | ia;ib;id;ii;ithn;ot;tapa;tape;tapn;taprnc;tbc;tdp;te;timas;tpa;tpe;tpn;trnc;ts | mapped | irp;ttm |
| CRI_2022 | remesas_ci | mapped | ithn;te | mapped | h9k1;h9k2;te |
| CRI_2022 | aedu_ci | mapped | a14 | mapped | escolari |
| CRI_2022 | edupub_ci | mapped | a15a | mapped | a13;a15a |
| CRI_2022 | aguared_ch | mapped | v11 | mapped | v11;v12 |
| CRI_2022 | bano_ch | mapped | v14a | mapped | v13a;v13b;v14a;v14b |
| CRI_2022 | migrante_ci | mapped | lugnac | mapped | condmig;lugnac |
