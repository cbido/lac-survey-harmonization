# Pobreza y desigualdad con diseño muestral, Casen 2022 armonizada
# entra: data/harmonized/CHL_2022.parquet
# sale:  indicators/output/CHL_2022_indicators.csv
#        indicators/output/CHL_2022_poverty_by_region.csv

library(nanoparquet)
library(dplyr)
library(survey)
library(convey)

survey_id <- "CHL_2022"

d <- read_parquet(file.path("data", "harmonized", paste0(survey_id, ".parquet")))
nrow(d)
summary(d$factor_ci)

# ingreso del hogar: laboral monetario + laboral en especie + no laboral monetario
# ojo: ynlm_ci ya trae pensiones y subsidios (sale del ingreso autónomo), no sumar ypen_ci
d <- d %>%
  mutate(y_person = coalesce(ylm_ci, 0) + coalesce(ylnm_ci, 0) + coalesce(ynlm_ci, 0)) %>%
  group_by(idh_ch) %>%
  mutate(
    n_members = n(),
    y_hh      = sum(y_person),
    y_pc      = y_hh / n_members
  ) %>%
  ungroup()

summary(d$y_pc)
table(is.na(d$lp_ci))

# línea oficial: es por persona equivalente, con escala n^0.7
# se calculan dos versiones para ver cuánto pesa la escala
lp  <- unique(d$lp_ci)
lpe <- unique(d$lpe_ci)
lp
lpe

d <- d %>%
  group_by(idh_ch) %>%
  mutate(y_hh_corrected = sum(coalesce(ynlm_ci, 0) + coalesce(ytrabajocor_raw, 0))) %>%
  ungroup() %>%
  mutate(
    official_poor    = ifelse(is.na(pobreza_oficial_raw), NA, as.numeric(pobreza_oficial_raw %in% c(1, 2))),
    official_extreme = ifelse(is.na(pobreza_oficial_raw), NA, as.numeric(pobreza_oficial_raw == 1)),
    poor_pc          = as.numeric(y_pc < lp),
    # escalera hacia la cifra oficial, siempre por persona equivalente
    poor_eq          = as.numeric(y_hh / n_members^0.7 < lp),
    poor_eq_rent     = as.numeric((y_hh + rentaimp_ch) / n_members^0.7 < lp),
    poor_eq_rent_cor = as.numeric((y_hh_corrected + rentaimp_ch) / n_members^0.7 < lp),
    poor_formula     = as.numeric(ytotcorh_raw / numper_raw^0.7 < lp)
  )

table(d$official_poor, useNA = "ifany")

# diseño: upm + estrato + factor de expansión
options(survey.lonely.psu = "adjust")
des <- svydesign(ids = ~upm_ci, strata = ~estrato_ci, weights = ~factor_ci, data = d, nest = TRUE)
des <- convey_prep(des)

# 1. cifra oficial como control (variable del ministerio, sin tocar)
official <- svymean(~official_poor + official_extreme, des, na.rm = TRUE)
official
confint(official)

# 2. pobreza con el ingreso armonizado
harmonized <- svymean(~poor_pc + poor_eq + poor_eq_rent + poor_eq_rent_cor + poor_formula, des, na.rm = TRUE)
harmonized

fgt0 <- svyfgt(~y_pc, des, g = 0, abs_thresh = lp, na.rm = TRUE)
fgt1 <- svyfgt(~y_pc, des, g = 1, abs_thresh = lp, na.rm = TRUE)
fgt2 <- svyfgt(~y_pc, des, g = 2, abs_thresh = lp, na.rm = TRUE)
fgt0
fgt1
fgt2

# 3. desigualdad
gini <- svygini(~y_pc, des, na.rm = TRUE)
gini

# 4. por región y zona
by_region <- svyby(~official_poor + poor_pc, ~region_c, des, svymean, na.rm = TRUE)
by_region
by_zone <- svyby(~official_poor + poor_pc, ~zona_c, des, svymean, na.rm = TRUE)
by_zone

# salida
row <- function(name, est, definition) {
  data.frame(
    indicator = name, estimate = as.numeric(coef(est))[1], se = as.numeric(SE(est))[1],
    definition = definition
  )
}
out <- bind_rows(
  row("official_poverty",         svymean(~official_poor, des, na.rm = TRUE),    "Ministry's classification, carried from the raw file"),
  row("official_extreme_poverty", svymean(~official_extreme, des, na.rm = TRUE), "Ministry's classification, carried from the raw file"),
  row("official_formula_check",   svymean(~poor_formula, des, na.rm = TRUE),     "Ministry's total household income per equivalent person (n^0.7) below the line"),
  row("harmonized_poverty_per_capita", svymean(~poor_pc, des, na.rm = TRUE),     "Harmonized household income per capita below the official line"),
  row("harmonized_poverty_equivalised", svymean(~poor_eq, des, na.rm = TRUE),    "Harmonized household income per equivalent person (n^0.7) below the line"),
  row("harmonized_plus_imputed_rent", svymean(~poor_eq_rent, des, na.rm = TRUE), "Same, adding the harmonized imputed rent"),
  row("harmonized_rent_corrected_labor", svymean(~poor_eq_rent_cor, des, na.rm = TRUE), "Same, with the ministry's corrected labor income in place of the raw components"),
  row("fgt1_per_capita", fgt1, "Poverty gap, harmonized income per capita"),
  row("fgt2_per_capita", fgt2, "Poverty severity, harmonized income per capita"),
  row("gini_per_capita", gini, "Gini of harmonized household income per capita")
) %>%
  mutate(cv = se / estimate, lower = estimate - 1.96 * se, upper = estimate + 1.96 * se)
out

dir.create(file.path("indicators", "output"), showWarnings = FALSE, recursive = TRUE)
write.csv(out, file.path("indicators", "output", paste0(survey_id, "_indicators.csv")), row.names = FALSE)

region_out <- as.data.frame(by_region)
names(region_out) <- c("region_c", "official_poor", "harmonized_poor_pc", "se_official", "se_harmonized")
write.csv(region_out, file.path("indicators", "output", paste0(survey_id, "_poverty_by_region.csv")), row.names = FALSE)

# pendiente: Alkire-Foster con las privaciones armonizadas (vivienda, educación, trabajo)
