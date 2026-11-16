# Mapping evaluation: CRI_2017 (draft gold)

## Availability (does the survey collect it?)

| precision | recall | f1 | accuracy | n |
|---|---|---|---|---|
| 1.00 | 0.50 | 0.67 | 0.96 | 51 |

## Source variables (gold-mapped variables only)

| precision | recall | f1 | exact_match | covers_gold | any_overlap | n |
|---|---|---|---|---|---|---|
| 0.69 | 0.46 | 0.55 | 0.68 | 0.81 | 0.87 | 47 |

## By domain

| domain | precision | recall | f1 | exact_match | covers_gold | any_overlap | n | availability_accuracy |
|---|---|---|---|---|---|---|---|---|
| demographics | 0.88 | 1.00 | 0.93 | 0.83 | 1.00 | 1.00 | 6 | 1.00 |
| design | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 7 | 1.00 |
| education | 0.50 | 0.67 | 0.57 | 0.33 | 0.67 | 0.67 | 3 | 1.00 |
| housing | 0.90 | 1.00 | 0.95 | 0.93 | 1.00 | 1.00 | 15 | 1.00 |
| income | 0.48 | 0.20 | 0.28 | 0.25 | 0.25 | 0.50 | 8 | 1.00 |
| labor | 0.47 | 0.25 | 0.33 | 0.38 | 0.75 | 0.88 | 8 | 0.80 |

## Confidence triage

| threshold | auto_accepted | coverage | exact_among_auto | sent_to_review |
|---|---|---|---|---|
| 0.50 | 51 | 1.00 | 0.67 | 0 |
| 0.70 | 43 | 0.84 | 0.72 | 8 |
| 0.90 | 23 | 0.45 | 0.91 | 28 |

## Disagreements with the gold standard (17)

| survey | target_var | status_gold | source_vars_gold | status_llm | source_vars_llm |
|---|---|---|---|---|---|
| CRI_2017 | cotizando_ci | mapped | a11 | mapped | a11;a12;e10a |
| CRI_2017 | afiliado_ci | not_available |  | mapped | a11;a12 |
| CRI_2017 | condocup_ci | mapped | b1;b2;b3;b5;b6;b7a;b7b;b7c;b7d;b7e;b7f;b7g;b7h;b7i;b7j;b7k;b8;estabili;g6 | mapped | a5;condact |
| CRI_2017 | ypen_ci | mapped | h9h1;h9h2 | mapped | ttpn |
| CRI_2017 | horaspri_ci | mapped | c2a1 | mapped | c2a1;hornorpri |
| CRI_2017 | categopri_ci | mapped | c12;c13a;d1 | mapped | c12;posiemppri |
| CRI_2017 | tipocontrato_ci | mapped | e1 | mapped | e1;e2;estabili |
| CRI_2017 | spublico_ci | not_available |  | mapped | secinspri |
| CRI_2017 | ylmpri_ci | mapped | aif;asp;bsp;dif;gpia;gpif;gpina;gpsfi;ipsp;ithn;oisp;sesp;spif;spmn | mapped | ipbt;ipit;ipnt;ipsmb;ipsmn |
| CRI_2017 | ylnmpri_ci | mapped | inmpia;inmpina;ithn;spnma;spnmo;spnmt;spnmv;spnmvh | mapped | inmpia;inmpina;spnma;spnmo;spnmt;spnmv;spnmvh |
| CRI_2017 | ylmsec_ci | mapped | gsi;ithn;ssmn | mapped | isbt |
| CRI_2017 | ynlm_ci | mapped | ia;ib;id;ii;ithn;ot;tapa;tape;tapn;taprnc;tbc;tdp;te;timas;tpa;tpe;tpn;trnc;ts | mapped | irp;ttm |
| CRI_2017 | remesas_ci | mapped | ithn;te | mapped | h9k1;h9k2;te |
| CRI_2017 | aedu_ci | mapped | a14 | mapped | escolari |
| CRI_2017 | edupub_ci | mapped | a15a | mapped | a13;a15a |
| CRI_2017 | bano_ch | mapped | v13a | mapped | v13a;v13b;v14a |
| CRI_2017 | migrante_ci | mapped | lugnac | mapped | condmig;lugnac |
