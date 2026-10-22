"""
Data loader for the Urban Queue Ontology.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import pandas as pd


def load_madrid_sample(csv_path: str | Path | None = None) -> pd.DataFrame:
    if csv_path is None:
        csv_path = Path(__file__).resolve().parents[2] / "data" / "madrid_traffic_sample.csv"
    df = pd.read_csv(csv_path)
    required = {"sensor_id", "road_name", "hour", "intensity_veh_h", "lanes", "service_rate_veh_h"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df


def observations_from_dataframe(df: pd.DataFrame) -> List[Dict]:
    records = []
    for _, row in df.iterrows():
        records.append({
            "sensor_id": str(row["sensor_id"]),
            "road_name": str(row["road_name"]),
            "hour": int(row["hour"]),
            "intensity": float(row["intensity_veh_h"]),
            "lanes": int(row["lanes"]),
            "service_rate": float(row["service_rate_veh_h"]),
        })
    return records


def load_and_prepare(csv_path: str | Path | None = None) -> List[Dict]:
    df = load_madrid_sample(csv_path)
    return observations_from_dataframe(df)


if __name__ == "__main__":
    obs = load_and_prepare()
    print(f"Loaded {len(obs)} observations from sample CSV.")
    for o in obs[:3]:
        print(f"  {o['sensor_id']} | {o['road_name']} | hour={o['hour']} | {o['intensity']:.0f} veh/h")