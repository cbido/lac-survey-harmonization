# Pobreza comunal con Fay-Herriot, Casen 2022 armonizada
# compara contra las estimaciones SAE oficiales del MDSF
# entra: data/harmonized/CHL_2022.parquet
#        data/aux/official_comuna_poverty.csv   (sae/prepare_aux.py)
# sale:  sae/output/CHL_2022_comuna_estimates.csv
#        sae/output/CHL_2022_comparison.csv
#        docs/img/sae_vs_official.png, docs/img/poverty_map.png

library(nanoparquet)
library(dplyr)
library(survey)
library(sae)
library(randomForest)
library(ggplot2)
library(sf)
library(chilemapas)

set.seed(2022)

d <- read_parquet("data/harmonized/CHL_2022.parquet")
nrow(d)
length(unique(d$comuna_raw))

# la variable a estimar es la pobreza oficial, para poder contrastar con el ministerio
d <- d %>%
  filter(!is.na(pobreza_oficial_raw)) %>%
  mutate(poor = as.numeric(pobreza_oficial_raw %in% c(1, 2)))

# 1. estimación directa por comuna, con factor de expansión comunal
options(survey.lonely.psu = "adjust")
des <- svydesign(ids = ~upm_ci, strata = ~estrato_ci, weights = ~factor_comuna_raw, data = d, nest = TRUE)

direct <- svyby(~poor, ~comuna_raw, des, svymean, deff = TRUE)
direct <- as.data.frame(direct)
names(direct) <- c("comuna", "p_direct", "se_direct", "deff")

size <- d %>%
  group_by(comuna = comuna_raw) %>%
  summarise(n = n(), n_psu = n_distinct(upm_ci), n_poor = sum(poor))
direct <- left_join(direct, size, by = "comuna")

nrow(direct)
summary(direct$n)
summary(direct$se_direct / direct$p_direct)
table(direct$n_poor == 0)

# 2. varianza suavizada en escala arcoseno
# el deff comunal es muy ruidoso, se usa la mediana de las comunas con muestra suficiente
deff_ok <- direct$deff[direct$n >= 100 & direct$n_poor >= 5 & is.finite(direct$deff)]
summary(deff_ok)
deff_med <- median(deff_ok)
deff_med

direct <- direct %>%
  mutate(
    n_eff = n / deff_med,
    z     = asin(sqrt(p_direct)),
    var_z = 1 / (4 * n_eff)
  )

# 3. variables auxiliares públicas
# ojo: el ministerio usa registros administrativos. Aquí van la estimación oficial 2020,
# la población proyectada y la región, que es lo que está publicado a nivel comunal
aux <- read.csv("data/aux/official_comuna_poverty.csv")
nrow(aux)
aux <- aux %>%
  mutate(
    z_2020  = asin(sqrt(p_official_2020)),
    log_pop = log(population_2022),
    region  = factor(region)
  )

all_comunas <- left_join(aux, direct, by = "comuna")
table(is.na(all_comunas$p_direct))

# comunas que entran al ajuste: muestra suficiente y más de una UPM
fit_set <- all_comunas %>% filter(!is.na(p_direct), n >= 50, n_psu >= 2)
nrow(fit_set)

# 4. modelo de área
fit <- mseFH(z ~ z_2020 + log_pop + region, vardir = var_z, data = fit_set, method = "REML")
fit$est$fit$estcoef[1:3, ]
fit$est$fit$refvar

fit_set$z_fh  <- as.numeric(fit$est$eblup)
fit_set$mse_z <- fit$mse
fit_set$gamma <- fit$est$fit$refvar / (fit$est$fit$refvar + fit_set$var_z)
summary(fit_set$gamma)

# sintética para todas las comunas, con los coeficientes del modelo
X <- model.matrix(~ z_2020 + log_pop + region, data = all_comunas)
all_comunas$z_syn <- as.numeric(X %*% fit$est$fit$estcoef$beta)

est <- all_comunas %>%
  left_join(fit_set %>% dplyr::select(comuna, z_fh, mse_z, gamma), by = "comuna") %>%
  mutate(
    type   = ifelse(is.na(z_fh), "synthetic", "fay-herriot"),
    z_hat  = ifelse(is.na(z_fh), z_syn, z_fh),
    p_fh   = sin(z_hat)^2,
    p_syn  = sin(z_syn)^2
  )
table(est$type)
summary(est$p_fh)

# 5. comparación con un bosque aleatorio sobre las mismas variables
rf <- randomForest(z ~ z_2020 + log_pop + region, data = fit_set, ntree = 500)
rf
est$p_rf <- sin(as.numeric(predict(rf, newdata = est)))^2
# para las comunas del ajuste se usa la predicción fuera de la bolsa, que no vio su propio dato
est$p_rf[match(fit_set$comuna, est$comuna)] <- sin(as.numeric(rf$predicted))^2

# 6. contraste con las cifras oficiales 2022
err <- function(estimate, reference) {
  ok <- !is.na(estimate) & !is.na(reference)
  c(n = sum(ok), correlation = cor(estimate[ok], reference[ok]),
    mean_abs_diff = mean(abs(estimate[ok] - reference[ok])),
    share_inside_official_ci = NA)
}
inside <- function(estimate) mean(estimate >= est$lower_2022 & estimate <= est$upper_2022, na.rm = TRUE)

in_fit <- est$type == "fay-herriot"
comparison <- rbind(
  "direct, comunas in the model"       = err(est$p_direct[in_fit], est$p_official_2022[in_fit]),
  "fay-herriot, comunas in the model"  = err(est$p_fh[in_fit], est$p_official_2022[in_fit]),
  "random forest, comunas in the model" = err(est$p_rf[in_fit], est$p_official_2022[in_fit]),
  "official 2020 carried forward, comunas in the model" = err(est$p_official_2020[in_fit], est$p_official_2022[in_fit]),
  "synthetic, comunas outside the model" = err(est$p_fh[!in_fit], est$p_official_2022[!in_fit]),
  "fay-herriot or synthetic, all comunas" = err(est$p_fh, est$p_official_2022)
)
comparison <- as.data.frame(comparison)
comparison$share_inside_official_ci <- c(
  mean((est$p_direct >= est$lower_2022 & est$p_direct <= est$upper_2022)[in_fit], na.rm = TRUE),
  mean((est$p_fh >= est$lower_2022 & est$p_fh <= est$upper_2022)[in_fit]),
  mean((est$p_rf >= est$lower_2022 & est$p_rf <= est$upper_2022)[in_fit]),
  mean((est$p_official_2020 >= est$lower_2022 & est$p_official_2020 <= est$upper_2022)[in_fit]),
  mean((est$p_fh >= est$lower_2022 & est$p_fh <= est$upper_2022)[!in_fit]),
  inside(est$p_fh)
)
comparison

# precisión: error estándar directo contra raíz del ECM del modelo, escala arcoseno
summary(sqrt(fit_set$var_z))
summary(sqrt(fit_set$mse_z))
mean(sqrt(fit_set$mse_z) < sqrt(fit_set$var_z))

# salidas
dir.create(file.path("sae", "output"), showWarnings = FALSE, recursive = TRUE)
dir.create(file.path("docs", "img"), showWarnings = FALSE, recursive = TRUE)

out <- est %>%
  dplyr::select(comuna, comuna_name, region, population_2022, n, n_psu, p_direct, se_direct,
         gamma, type, p_fh, p_syn, p_rf, p_official_2022, lower_2022, upper_2022, p_official_2020)
write.csv(out, file.path("sae", "output", "CHL_2022_comuna_estimates.csv"), row.names = FALSE)
comparison$estimate <- rownames(comparison)
write.csv(comparison[, c("estimate", "n", "correlation", "mean_abs_diff", "share_inside_official_ci")],
          file.path("sae", "output", "CHL_2022_comparison.csv"), row.names = FALSE)

# figura 1: estimación propia contra oficial
plot_data <- bind_rows(
  est %>% filter(in_fit) %>% transmute(official = p_official_2022, own = p_direct, kind = "Direct estimate"),
  est %>% transmute(official = p_official_2022, own = p_fh, kind = "Fay-Herriot (this repo)")
)
g1 <- ggplot(plot_data, aes(official, own)) +
  geom_abline(slope = 1, intercept = 0, colour = "grey50") +
  geom_point(alpha = 0.5, size = 1.2, colour = "#1f4e79") +
  facet_wrap(~kind) +
  scale_x_continuous(labels = function(x) paste0(round(100 * x), "%")) +
  scale_y_continuous(labels = function(x) paste0(round(100 * x), "%")) +
  labs(x = "Official small-area estimate (MDSF)", y = "This repo",
       title = "Income poverty by comuna, Casen 2022",
       subtitle = "Each point is a comuna. The line marks equality with the official estimate.") +
  theme_minimal(base_size = 11)
ggsave(file.path("docs", "img", "sae_vs_official.png"), g1, width = 8, height = 4.2, dpi = 150)

# figura 2: mapa (sin Isla de Pascua ni Juan Fernández, que distorsionan la escala)
map <- chilemapas::mapa_comunas %>%
  mutate(comuna = as.integer(codigo_comuna)) %>%
  filter(!comuna %in% c(5201, 5104)) %>%
  left_join(est %>% dplyr::select(comuna, p_fh), by = "comuna") %>%
  st_as_sf()
table(is.na(map$p_fh))

g2 <- ggplot(map) +
  geom_sf(aes(fill = p_fh), colour = NA) +
  scale_fill_viridis_c(option = "magma", direction = -1, labels = function(x) paste0(round(100 * x), "%"),
                       name = "Poverty rate") +
  labs(title = "Income poverty by comuna, 2022", subtitle = "Fay-Herriot estimates from this repo") +
  theme_void(base_size = 10) +
  theme(legend.position = "right")
ggsave(file.path("docs", "img", "poverty_map.png"), g2, width = 3.6, height = 9, dpi = 150)
