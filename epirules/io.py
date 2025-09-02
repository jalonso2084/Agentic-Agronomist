from __future__ import annotations
import pandas as pd

def read_weather_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if 'timestamp' not in df or 'temp_c' not in df or 'rh' not in df:
        raise ValueError("CSV must include 'timestamp', 'temp_c', 'rh' columns")
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    if df['timestamp'].isna().any():
        raise ValueError("Invalid timestamps in CSV")
    # Coerce RH bounds
    df['rh'] = df['rh'].clip(lower=0, upper=100)
    # Normalize to hourly; if sub-hourly present, keep native freq
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

def daily_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    # Compute daily stats needed for rules
    g = df.set_index('timestamp').groupby(pd.Grouper(freq='D'))
    agg = g.apply(lambda x: pd.Series({
        'min_temp_c': x['temp_c'].min(),
        'hours_rh_ge_90': (x['rh'] >= 90).sum(),
        'hours_rh_ge_80': (x['rh'] >= 80).sum(),
        'mean_temp_when_rh_ge_80': x.loc[x['rh'] >= 80, 'temp_c'].mean() if (x['rh'] >= 80).any() else float('nan'),
        'n_records': len(x),
    }))
    agg.index = agg.index.tz_localize(None)  # strip tz for cleaner keys
    return agg.reset_index().rename(columns={'timestamp':'day'})
