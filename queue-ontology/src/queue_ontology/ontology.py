"""
Ontology layer: objects, properties, links and actions
inspired by operational data platforms.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import networkx as nx


@dataclass
class Sensor:
    sensor_id: str
    latitude: float
    longitude: float
    road_name: Optional[str] = None
    intensity_series: Dict[str, float] = field(default_factory=dict)  # timestamp -> vehicles/h


@dataclass
class RoadSegment:
    segment_id: str
    name: str
    length_m: float
    capacity_veh_per_h: float
    sensors: List[str] = field(default_factory=list)


@dataclass
class Intersection:
    intersection_id: str
    name: str
    incoming_segments: List[str] = field(default_factory=list)
    outgoing_segments: List[str] = field(default_factory=list)
    signal_plan_id: Optional[str] = None


@dataclass
class SignalPlan:
    plan_id: str
    cycle_time_s: float
    green_splits: Dict[str, float]  # segment_id -> fraction of cycle


class Ontology:
    """Simple in-memory ontology using a directed graph + object store."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.objects: Dict[str, Any] = {}

    def add_sensor(self, sensor: Sensor) -> None:
        self.objects[sensor.sensor_id] = sensor
        self.graph.add_node(sensor.sensor_id, type="Sensor", **sensor.__dict__)

    def add_road_segment(self, segment: RoadSegment) -> None:
        self.objects[segment.segment_id] = segment
        self.graph.add_node(segment.segment_id, type="RoadSegment", **segment.__dict__)

    def add_intersection(self, intersection: Intersection) -> None:
        self.objects[intersection.intersection_id] = intersection
        self.graph.add_node(intersection.intersection_id, type="Intersection", **intersection.__dict__)

    def link_sensor_to_segment(self, sensor_id: str, segment_id: str) -> None:
        self.graph.add_edge(sensor_id, segment_id, link="measures")

    def link_segment_to_intersection(self, segment_id: str, intersection_id: str, direction: str = "incoming") -> None:
        self.graph.add_edge(segment_id, intersection_id, link=direction)

    def get_objects_by_type(self, type_name: str) -> List[Any]:
        return [obj for obj in self.objects.values() if type(obj).__name__ == type_name]

    def compute_metrics_action(self, intersection_id: str) -> Dict[str, float]:
        """Example action: compute queue metrics for an intersection."""
        # Placeholder – real implementation lives in queue_models
        return {"avg_wait_s": 0.0, "utilization": 0.0}
