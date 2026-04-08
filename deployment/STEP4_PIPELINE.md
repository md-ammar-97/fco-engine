# Step 4 - Processing pipeline migration

## Included in this step
- input discovery and table loading
- mapping JSON application
- loads preprocessing
- city/state clustering with geocode cache + DBSCAN
- route aggregation
- fuel statement / fuel prices preprocessing
- workbook generation
- PDF generation
- heuristic scenario sheet generation
- manifest + callback integration

## Important note
This step is a strong processing scaffold, but it does **not** yet implement:
- full ORS corridor routing
- station candidate extraction
- PuLP-based lexicographic optimization
- detailed fuel-to-load assignment logic

Those can be added in a later hardening step while keeping this repo structure unchanged.
