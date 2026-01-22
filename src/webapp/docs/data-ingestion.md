# Data Ingestion Guide

Baller Hub supports two primary ingestion paths:

1. **CSV ingestion** for bulk, historical data stored under `raw-data/`
2. **Scraper seeding** for targeted seasons or daily box scores

## CSV Ingestion (Bulk)

CSV ingestion loads historical datasets into staging tables and upserts into
production tables. Use the seed script to run this end-to-end.

```bash
cd src/webapp
python -m scripts.seed_db --csv
```

To include the play-by-play dataset (large):

```bash
python -m scripts.seed_db --csv --csv-play-by-play
```

What happens:

- CSVs are copied into staging tables
- Validation checks run for numeric/date fields
- Production tables are upserted
- Materialized views are refreshed

## Scraper Seeding (Targeted)

Scraper seeding pulls data from basketball-reference.com for specific needs.
This is slower but useful for the current season.

```bash
# Seed a single season
python -m scripts.seed_db --season 2024

# Seed yesterday's games
python -m scripts.seed_db --yesterday

# Seed a specific date
python -m scripts.seed_db --daily 2024-01-15
```

## Search Indexing

After data is ingested, rebuild search indices:

```bash
python -m scripts.seed_db --index
```

Or run both CSV ingestion and indexing:

```bash
python -m scripts.seed_db --bootstrap
```

## Notes

- CSV ingestion expects the datasets to exist under `raw-data/`.
- Play-by-play ingestion is optional due to size.
- Scraper seeding respects rate limits and can be slow for large seasons.
