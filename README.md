# Epidemiological Rules Checker (MVP)

This is a minimal, production-friendly starter to evaluate late blight weather rules (Hutton, Smith, and a customizable local rule).
It reads hourly (or sub-hourly) weather, aggregates by day, and emits a JSON risk with an explanation.

## Quickstart
```bash
python -m epirules.cli --weather sample_data/sample_weather.csv --rules rules.yaml --rule-set Hutton --out out.json
cat out.json
```
- `--rule-set` can be `Hutton`, `Smith`, or `LocalAndes` (example to calibrate).
- Weather CSV requires columns: `timestamp` (ISO), `temp_c`, `rh` (0-100), optional `rain_mm`.

## Files
- `epirules/engine.py` : rule computations
- `epirules/io.py` : CSV ingestion & daily aggregation
- `epirules/cli.py` : command-line interface
- `rules.yaml` : rule parameters
- `sample_data/sample_weather.csv` : synthetic sample data (4 days)
- `tests/test_engine.py` : minimal tests (`pytest`)

## Notes
- Hutton and Smith definitions are implemented exactly as published.
- The `LocalAndes` rule is an **example** based on typical Andean expert heuristics and MUST be calibrated with local data and agronomist input.
