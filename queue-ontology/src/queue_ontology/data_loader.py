from pathlib import Path
from typing import List, Dict
import pandas as pd


def load_madrid_sample(csv_path=None):
    if csv_path is None:
        csv_path = Path(__file__).resolve().parents[2] / "data" / "madrid_traffic_sample.csv"
    df = pd.read_csv(csv_path)
    return df


def load_and_prepare(csv_path=None):
    df = load_madrid_sample(csv_path)
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