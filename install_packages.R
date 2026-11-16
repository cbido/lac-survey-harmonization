# Paquetes de R que usan indicators/ y sae/
# versiones con las que se corrió: R 4.3.3, survey 4.2.1, convey 1.0.1, sae 1.4,
# nanoparquet 0.5.2, dplyr 1.1.4, ggplot2 3.4.4, sf 1.0.15, randomForest 4.7.1.1, chilemapas 0.4.1

packages <- c("survey", "convey", "sae", "nanoparquet", "dplyr", "ggplot2", "sf", "randomForest", "chilemapas")
missing  <- setdiff(packages, rownames(installed.packages()))
missing
if (length(missing) > 0) install.packages(missing, repos = "https://cloud.r-project.org")
