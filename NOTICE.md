# Notice

This repository holds two kinds of material under different terms.

## Original work: MIT License

The code, configuration, tests and documentation written for this project are licensed
under the MIT License (`LICENSE`), except for the material listed below.

## Material derived from the IDB harmonization programs

The reference mappings were extracted from the Stata programs in the Inter-American
Development Bank's repository
[armonizacion_microdatos_encuestas_hogares_scl](https://github.com/EL-BID/armonizacion_microdatos_encuestas_hogares_scl).
Those programs are not included here. The files that reproduce information taken from
them are:

- `validate/gold/` (reference mappings, draft and reviewed)
- `validate/review/` and `validate/reports/` (which list those mappings beside the model's)
- `docs/reference_across_rounds.md` and `docs/gold_review_notes.md`
- the harmonized variable names in `config/target_schema.yml`

These files are made available under the terms of the IDB Open-Source Software License,
a copy of which is in `LICENSE-IDB.md`, and carry its statement:

> Copyright © 2020. Inter-American Development Bank ("IDB"). Authorized Use. The
> procedures and results obtained based on the execution of this software are those
> programmed by the developers and do not necessarily reflect the views of the IDB, its
> Board of Executive Directors or the countries it represents.

This project is independent. It is not affiliated with, endorsed by or reviewed by the
IDB, and any error in the extracted mappings is the author's.

## Survey data

No microdata, questionnaire or codebook is included. The results in this repository are
aggregates computed from public files of the statistical offices listed in the README,
each of which sets its own terms of use.
