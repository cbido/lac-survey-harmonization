# Notes for the gold-standard review

## Casen 2022: targets the reference marks as unavailable

The IDB program for Casen 2022 sets 20 of the 58 target variables to missing, and 36 of its
comment lines say that the question is absent from the 2020 survey. Casen 2020 used a reduced
questionnaire, and the 2022 round returned to the full one, so each of these targets was looked
up by label in the Casen 2022 data dictionary (`data/dictionaries/CHL_2022.csv`).

A candidate variable exists for 12 of the 20. They are candidates found by a label search,
and each one is confirmed or discarded against the questionnaire during the review.

| target | candidate variables in Casen 2022 |
|---|---|
| ocupa_ci | `o9a` (o9a. ¿Cuál es su ocupación u oficio?); `oficio1_08` (oficio1_08. Oficio (1 dígito) CIUO 08); `oficio4_08` (oficio4_08. Oficio (4 dígitos) CIUO 08) |
| ylnmpri_ci | none found by label search |
| ylnm_ci | none found by label search |
| rentaimp_ch | `yaimh` (Alquiler imputado del hogar); `yaimcorh` (Alquiler imputado corregido del hogar) |
| remesas_ci | none found by label search |
| edupub_ci | `e9depen` (e9depen. Dependencia administrativa del establecimiento educacional (M); `e10` (e10. En 2022, ¿cuál es la dependencia administrativa del estab. educac) |
| luz_ch | `v24` (v24. La vivienda donde usted vive, ¿dispone de energía eléctrica?) |
| piso_ch | `v4` (v4. ¿Cuál es el material que predomina en el piso de la vivienda?) |
| pared_ch | `v2` (v2. ¿Cuál es el material que predomina en los muros exteriores de la v) |
| techo_ch | `v6` (v6. ¿Cuál es el material que predomina en el techo de la vivienda?) |
| cuartos_ch | none found by label search |
| refrig_ch | none found by label search |
| auto_ch | none found by label search |
| compu_ch | none found by label search |
| internet_ch | `r17a` (r17a. Acceso a Internet en la vivienda: Banda ancha fija); `r17b` (r17b. Acceso a Internet en la vivienda: Banda ancha móvil (módem, Wifi); `r17c` (r17c. Acceso a Internet en la vivienda: Teléfono móvil) |
| cel_ch | none found by label search |
| lp_ci | `lp` (Linea de pobreza) |
| lpe_ci | `li` (Linea de indigencia) |
| tipocontrato_ci | `o18` (o18. En su trabajo principal, ¿qué tipo de contrato o acuerdo de traba); `o19` (o19. En su trabajo principal, ¿tiene contrato de trabajo escrito?) |
| tamemp_ci | `o25` (o25. ¿Cuántas personas trabajan en ese negocio, empresa o institución) |

Where a candidate is confirmed, the reviewed gold file records the target as `mapped` with a
note that it departs from the reference program.

## What the model proposed for those targets

In the first run (`claude-sonnet-5-5`, dictionary only), the model mapped 15 of the 20
targets that the reference marks as unavailable in Casen 2022. For the 12 targets with a
candidate in the table above, it named one of the same variables in 11 cases, working
only from the data dictionary. The exception is `luz_ch`: the model judged that `v24`
records whether the dwelling has electricity and not the main source of lighting.

It also proposed variables for four targets with no candidate from the label search:
in-kind labor income (`y0501` to `y0512`), money from relatives abroad (`yfa2`) and
vehicle ownership (`r14`). Those need the same check against the questionnaire.

This is why the Casen 2022 row shows the lowest availability score in `docs/results.md`.
Most of that disagreement comes from the reference, and the reviewed gold file settles it.
