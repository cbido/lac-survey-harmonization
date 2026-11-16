# Reference mappings across rounds and countries

Built from the gold files in `validate/gold/` by `harmonize/compare_rounds.py`.
Draft files are parser output and still need manual review.

## Extracted names checked against each survey's data dictionary

| survey | checked | names_found | names_not_found | share_found |
|---|---|---|---|---|
| BOL_2017 | yes | 104 | 3 | 97.2% |
| BOL_2021 | yes | 101 | 3 | 97.1% |
| CHL_2015 | yes | 71 | 1 | 98.6% |
| CHL_2017 | yes | 69 | 1 | 98.6% |
| CHL_2020 | yes | 56 | 1 | 98.2% |
| CHL_2022 | yes | 60 | 1 | 98.4% |
| CRI_2017 | yes | 115 | 0 | 100.0% |
| CRI_2022 | yes | 111 | 0 | 100.0% |

## Target variables by status

| status | BOL_2017 | BOL_2021 | CHL_2015 | CHL_2017 | CHL_2020 | CHL_2022 | CRI_2017 | CRI_2022 |
|---|---|---|---|---|---|---|---|---|
| mapped | 45 | 44 | 44 | 44 | 35 | 35 | 47 | 45 |
| not_available | 2 | 3 | 10 | 9 | 20 | 20 | 4 | 3 |
| derived | 3 | 3 | 1 | 1 | 1 | 1 | 4 | 4 |
| constant | 7 | 7 | 3 | 4 | 2 | 2 | 3 | 3 |
| not in program | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |

## BOL: status changes between rounds (1)

| target_var | BOL_2017 | BOL_2021 |
|---|---|---|
| tipocontrato_ci | mapped | not_available |

## BOL: same concept, different raw variables (33 of 44 mapped in every round)

| target_var | BOL_2017 | BOL_2021 |
|---|---|---|
| relacion_ci | s02a_05 | s01a_05 |
| sexo_ci | s02a_02 | s01a_02 |
| edad_ci | s02a_03 | s01a_03 |
| civil_ci | s02a_10 | s01a_10 |
| afroind_ci | s03a_04 | s01a_09 |
| migrante_ci | s03a_04 | s01a_09 |
| condocup_ci | s06a_01, s06a_02, s06a_03, s06a_04, s06a_05 | desocupado, ocupado, pei |
| categopri_ci | s06b_16 | s04b_12 |
| ocupa_ci | s06b_11a_cod | s04b_09a_cod |
| tamemp_ci | s06b_21 | s04b_14 |
| spublico_ci | s06b_18 | s04b_13 |
| afiliado_ci | s06h_58b | s04f_35 |
| ylmpri_ci | s06c_25a, s06c_25b, s06c_26a, s06c_26b, s06c_27aa, s06c_27ab, s06c_27ba, s06c_27bb, s06d_33a, s06d_33b | s04c_17a, s04c_17b, s04c_18a, s04c_18b, s04c_19aa, s04c_19ab, s04c_19ba, s04c_19bb, s04d_24a, s04d_24b |
| ylnmpri_ci | s06c_30a, s06c_30a1, s06c_30a2, s06c_30b, s06c_30b1, s06c_30b2, s06c_30c, s06c_30c1, s06c_30c2, s06c_30d, s06c_30d1, s06c_30d2, s06c_30e, s06c_30e1, s06c_30e2 | s04c_21a, s04c_21a1, s04c_21a2, s04c_21b, s04c_21b1, s04c_21b2, s04c_21c, s04c_21c1, s04c_21d, s04c_21d1, s04c_21d2, s04c_21e, s04c_21e1, s04c_21e2 |
| ylmsec_ci | s06g_47a, s06g_47b, s06g_48a, s06g_48a1 | s04f_31a, s04f_31b, s04f_32a, s04f_32a1 |
| ynlm_ci | s07a_01a, s07a_01b, s07a_01c, s07a_01d, s07a_01e0, s07a_02a, s07a_02b, s07a_02c, s07a_03a, s07a_03b, s07a_03c, s07a_04a, s07a_04b, s07a_04c, s07b_05aa, s07b_05ab, s07b_05ba, s07b_05bb, s07c_07, s07c_08a, s07c_08b, s07c_10 | s05a_01a, s05a_01b, s05a_01c, s05a_01d, s05a_01e0, s05a_02a, s05a_02b, s05a_02c, s05a_03a, s05a_03b, s05a_03c, s05a_04a, s05a_04b, s05a_04d, s05b_05aa, s05b_05ab, s05b_05ba, s05b_05bb, s05b_07aa, s05b_07ab, s05c_09, s05c_10a, s05c_10b |
| ypen_ci | s07a_01a, s07a_01b, s07a_01c, s07a_01d | s05a_01a, s05a_01b, s05a_01c, s05a_01d |
| remesas_ci | s07c_07, s07c_08a, s07c_08b, s07c_10 | s05c_09, s05c_10a, s05c_10b |
| asiste_ci | s05a_05 | s03a_04 |
| aedu_ci | s05a_02a, s05a_02b | s03a_02a, s03a_02c |
| edupub_ci | s05a_09 | s03a_09 |
| aguared_ch | s01a_10 | s07a_10 |
| aguafuente_ch | s01a_10 | s07a_10 |
| luz_ch | s01a_19 | s07a_04, s07a_16 |
| bano_ch | s01a_15, s01a_16 | s07a_13, s07a_14 |
| piso_ch | s01a_09 | s07a_09 |
| pared_ch | s01a_06 | s07a_06 |
| techo_ch | s01a_08 | s07a_08 |
| dorm_ch | s01a_28 | s07a_25 |
| cuartos_ch | s01a_27 | s07a_24 |
| viviprop_ch | s01a_02 | s07a_02 |
| internet_ch | s01a_31 | s07a_28 |
| cel_ch | s05c_13 | s03c_13 |

## CHL: status changes between rounds (16)

| target_var | CHL_2015 | CHL_2017 | CHL_2020 | CHL_2022 |
|---|---|---|---|---|
| upm_ci | not_available | not_available | mapped | mapped |
| estrato_ci | not_available | not_available | mapped | mapped |
| dis_ci | not_available | constant | not_available | mapped |
| ocupa_ci | mapped | mapped | mapped | not_available |
| tamemp_ci | constant | constant | not_available | not_available |
| tipocontrato_ci | mapped | mapped | not_available | not_available |
| edupub_ci | mapped | mapped | not_available | not_available |
| luz_ch | mapped | mapped | not_available | not_available |
| piso_ch | mapped | mapped | not_available | not_available |
| pared_ch | mapped | mapped | not_available | not_available |
| techo_ch | mapped | mapped | not_available | not_available |
| cuartos_ch | mapped | mapped | not_available | not_available |
| internet_ch | mapped | mapped | not_available | not_available |
| cel_ch | mapped | mapped | not_available | not_available |
| compu_ch | mapped | mapped | not_available | not_available |
| auto_ch | mapped | mapped | not_available | not_available |

## CHL: same concept, different raw variables (14 of 32 mapped in every round)

| target_var | CHL_2015 | CHL_2017 | CHL_2020 | CHL_2022 |
|---|---|---|---|---|
| mes_c | fecha_mes | fecha_mes | fecha_entrev | fecha_entrev |
| zona_c | zona | zona | zona | area |
| idp_ci | o | o | o | id_persona |
| horaspri_ci | o10 | o10 | y2_hrs | y2_hrs |
| cotizando_ci | o29 | o29 | o32 | o32 |
| afiliado_ci | o28 | o28 | o31 | o31 |
| ypen_ci | y26_2bm1, y26_2bm2, y26_2c, y26_2em1, y26_2em2, y26_2f, y26_2g, y26_2h, y26_2i, y26_2j | y26_2bm1, y26_2bm2, y26_2c, y26_2em1, y26_2em2, y26_2f, y26_2g, y26_2h, y26_2i, y26_2j | y28_1a, y28_1b, y28_1c, y28_1d, y28_1e, y28_1f, y28_1g, y28_1h | y28_1b, y28_1c, y28_1d, y28_1e, y28_1f, y28_1g, y28_1h |
| asiste_ci | e3 | e3 | e2 | e3 |
| aedu_ci | e3, e6a, e6b | e3, e6a, e6b | e2, e6a, e6b | e3, e6a, e6b |
| aguared_ch | v23 | v20 | v20 | v20 |
| aguafuente_ch | v23, v24 | v20, v22 | v20, v22 | v20, v22 |
| bano_ch | v25 | v23 | v23, v23_cajon, v23_sistema | v23, v23_cajon, v23_sistema |
| dorm_ch | v29a | v27a | v27, v29 | v27a, v29a |
| viviprop_ch | v9 | v9 | v13, v13_propia | v13, v13_propia |

## CRI: status changes between rounds (3)

| target_var | CRI_2017 | CRI_2022 |
|---|---|---|
| upm_ci | mapped |  |
| estrato_ci | not_available |  |
| aguafuente_ch | mapped |  |

## CRI: same concept, different raw variables (2 of 45 mapped in every round)

| target_var | CRI_2017 | CRI_2022 |
|---|---|---|
| aguared_ch | v11, v12 | v11 |
| bano_ch | v13a | v14a |

## Coverage across countries (23 of 58 targets mapped in every survey)

Cells show the number of rounds with a raw mapping out of the rounds in scope.

| target_var | BOL | CHL | CRI | mapped_in_every_survey |
|---|---|---|---|---|
| pais_c | 0/2 | 0/4 | 0/2 |  |
| anio_c | 0/2 | 0/4 | 0/2 |  |
| mes_c | 0/2 | 4/4 | 0/2 |  |
| region_c | 0/2 | 4/4 | 2/2 |  |
| zona_c | 2/2 | 4/4 | 2/2 | yes |
| idh_ch | 2/2 | 4/4 | 2/2 | yes |
| idp_ci | 2/2 | 4/4 | 2/2 | yes |
| factor_ch | 2/2 | 4/4 | 2/2 | yes |
| factor_ci | 0/2 | 4/4 | 2/2 |  |
| upm_ci | 2/2 | 2/4 | 1/2 |  |
| estrato_ci | 2/2 | 2/4 | 0/2 |  |
| relacion_ci | 2/2 | 4/4 | 2/2 | yes |
| sexo_ci | 2/2 | 4/4 | 2/2 | yes |
| edad_ci | 2/2 | 4/4 | 2/2 | yes |
| civil_ci | 2/2 | 4/4 | 2/2 | yes |
| afroind_ci | 2/2 | 4/4 | 0/2 |  |
| dis_ci | 0/2 | 1/4 | 2/2 |  |
| migrante_ci | 2/2 | 4/4 | 2/2 | yes |
| condocup_ci | 2/2 | 4/4 | 2/2 | yes |
| categopri_ci | 2/2 | 4/4 | 2/2 | yes |
| ocupa_ci | 2/2 | 3/4 | 2/2 |  |
| rama_ci | 2/2 | 4/4 | 2/2 | yes |
| horaspri_ci | 2/2 | 4/4 | 2/2 | yes |
| horastot_ci | 2/2 | 0/4 | 0/2 |  |
| tamemp_ci | 2/2 | 0/4 | 2/2 |  |
| spublico_ci | 2/2 | 4/4 | 0/2 |  |
| tipocontrato_ci | 1/2 | 2/4 | 2/2 |  |
| cotizando_ci | 0/2 | 4/4 | 2/2 |  |
| afiliado_ci | 2/2 | 4/4 | 0/2 |  |
| ylmpri_ci | 2/2 | 4/4 | 2/2 | yes |
| ylnmpri_ci | 2/2 | 0/4 | 2/2 |  |
| ylmsec_ci | 2/2 | 4/4 | 2/2 | yes |
| ylm_ci | 0/2 | 4/4 | 0/2 |  |
| ylnm_ci | 0/2 | 0/4 | 0/2 |  |
| ynlm_ci | 2/2 | 4/4 | 2/2 | yes |
| ypen_ci | 2/2 | 4/4 | 2/2 | yes |
| remesas_ci | 2/2 | 0/4 | 2/2 |  |
| rentaimp_ch | 0/2 | 0/4 | 0/2 |  |
| lp_ci | 2/2 | 0/4 | 2/2 |  |
| lpe_ci | 2/2 | 0/4 | 2/2 |  |
| asiste_ci | 2/2 | 4/4 | 2/2 | yes |
| aedu_ci | 2/2 | 4/4 | 2/2 | yes |
| edupub_ci | 2/2 | 2/4 | 2/2 |  |
| aguared_ch | 2/2 | 4/4 | 2/2 | yes |
| aguafuente_ch | 2/2 | 4/4 | 1/2 |  |
| luz_ch | 2/2 | 2/4 | 2/2 |  |
| bano_ch | 2/2 | 4/4 | 2/2 | yes |
| piso_ch | 2/2 | 2/4 | 2/2 |  |
| pared_ch | 2/2 | 2/4 | 2/2 |  |
| techo_ch | 2/2 | 2/4 | 2/2 |  |
| dorm_ch | 2/2 | 4/4 | 2/2 | yes |
| cuartos_ch | 2/2 | 2/4 | 2/2 |  |
| viviprop_ch | 2/2 | 4/4 | 2/2 | yes |
| internet_ch | 2/2 | 2/4 | 2/2 |  |
| cel_ch | 2/2 | 2/4 | 2/2 |  |
| compu_ch | 0/2 | 2/4 | 2/2 |  |
| refrig_ch | 0/2 | 0/4 | 2/2 |  |
| auto_ch | 0/2 | 2/4 | 2/2 |  |
