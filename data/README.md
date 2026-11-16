# data/

Nothing in this folder is committed except this note.

```
python scripts/download_data.py     # open files listed in config/sources.yml
python ingest/unpack.py             # archives into data/raw/<survey>/unpacked/
```

| Folder | Contents |
|---|---|
| `raw/<survey>/` | Microdata as downloaded from the statistics office, and `unpacked/` |
| `questionnaires/<survey>/` | Questionnaires and codebooks |
| `metadata/` | DDI codebooks from the ANDA and PAD catalogs |
| `parquet/` | One Parquet file per survey, written by `ingest/to_parquet.py` |
| `dictionaries/` | One data dictionary per survey (variables, labels, codes, question text) |
| `checksums.csv` | SHA-256 of every downloaded file |

Microdata that needs a registered account (Bolivia, Costa Rica) is downloaded by hand
and placed in `raw/<survey>/`. The download script prints the page to visit.

For Chile the files are the databases as originally released. The ministry also
publishes an updated series with current methodological definitions. Record which
version was used whenever results are reported.
