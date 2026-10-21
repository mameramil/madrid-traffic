from __future__ import annotations
from typing import Dict, List, Tuple
import random

from .ontology import Ontology, Sensor, RoadSegment, Intersection
from .queue_models import mm1_wait_time, mmc_wait_time


def generate_synthetic_madrid_data(num_sensors: int = 8, seed: int = 42) -> Dict:
    random.seed(seed)
    sensors = []
    for i in range(num_sensors):
        base = random.randint(600, 1600)
        sensors.append({
            "sensor_id": f"S{i+1:03d}",
            "latitude": 40.4168 + random.uniform(-0.05, 0.05),
            "longitude": -3.7038 + random.uniform(-0.05, 0.05),
            "road_name": f"Calle Principal {i+1}",
            "intensity_veh_h": base,
            "capacity_veh_h": random.choice([1200, 1500, 1800, 2000]),
        })
    return {"sensors": sensors}


def build_ontology_from_data(data: Dict) -> Ontology:
    onto = Ontology()
    for s in data["sensors"]:
        sensor = Sensor(
            sensor_id=s["sensor_id"],
            latitude=s["latitude"],
            longitude=s["longitude"],
            road_name=s["road_name"],
            intensity_series={"peak": s["intensity_veh_h"]},
        )
        onto.add_sensor(sensor)

        segment_id = f"SEG_{s['sensor_id']}"
        segment = RoadSegment(
            segment_id=segment_id,
            name=s["road_name"],
            length_m=random.randint(200, 800),
            capacity_veh_per_h=s["capacity_veh_h"],
            sensors=[s["sensor_id"]],
        )
        onto.add_road_segment(segment)
        onto.link_sensor_to_segment(s["sensor_id"], segment_id)

        if len(onto.get_objects_by_type("RoadSegment")) % 2 == 0:
            inter_id = f"INT_{len(onto.get_objects_by_type('Intersection'))+1}"
            inter = Intersection(
                intersection_id=inter_id,
                name=f"Intersección {inter_id}",
                incoming_segments=[segment_id],
            )
            onto.add_intersection(inter)
            onto.link_segment_to_intersection(segment_id, inter_id, "incoming")

    return onto


def compute_queue_metrics(onto: Ontology) -> List[Dict]:
    results = []
    segments = onto.get_objects_by_type("RoadSegment")

    for seg in segments:
        sensor_id = seg.sensors[0] if seg.sensors else None
        if not sensor_id or sensor_id not in onto.objects:
            continue

        sensor = onto.objects[sensor_id]
        arrival_rate = sensor.intensity_series.get("peak", 800)
        service_rate = seg.capacity_veh_per_h
        num_lanes = 2 if service_rate > 1500 else 1

        if num_lanes == 1:
            metrics = mm1_wait_time(arrival_rate, service_rate)
        else:
            metrics = mmc_wait_time(arrival_rate, service_rate / num_lanes, num_lanes)

        results.append({
            "segment_id": seg.segment_id,
            "road": seg.name,
            "arrival_rate": arrival_rate,
            "service_rate": service_rate,
            "lanes": num_lanes,
            "metrics": metrics,
        })

    return results


def run_pipeline(num_sensors: int = 6):
    print("=== Urban Queue Ontology Pipeline ===\n")

    data = generate_synthetic_madrid_data(num_sensors)
    print(f"Generated {len(data['sensors'])} synthetic sensors (Madrid-calibrated).")

    onto = build_ontology_from_data(data)
    print(f"Ontology built: {len(onto.objects)} objects.")

    results = compute_queue_metrics(onto)
    print(f"Computed queue metrics for {len(results)} segments.\n")

    print("--- Results (peak hour) ---")
    for r in results:
        m = r["metrics"]
        if "error" in m:
            print(f"  {r['segment_id']}: UNSTABLE")
        else:
            wait = m.get("avg_wait_system_min", 0)
            util = m.get("utilization", 0)
            print(f"  {r['segment_id']} ({r['road']}): wait={wait:.1f} min | util={util:.0%}")

    valid = [r for r in results if "error" not in r["metrics"]]
    if valid:
        worst = max(valid, key=lambda x: x["metrics"].get("avg_wait_system_min", 0))
        print(f"\nBottleneck: {worst['segment_id']} → {worst['metrics']['avg_wait_system_min']:.1f} min average wait")

    return onto, results


if __name__ == "__main__":
    run_pipeline()