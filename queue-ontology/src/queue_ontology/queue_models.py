"""
Analytical and simulation models for queues.
Based on classical queueing theory (M/M/1, M/M/c, etc.).
"""

from __future__ import annotations
from typing import Dict, List, Optional
import math
import random


def mm1_wait_time(arrival_rate: float, service_rate: float) -> Dict[str, float]:
    """
    M/M/1 queue metrics.
    arrival_rate (λ) and service_rate (μ) in the same units (e.g. vehicles per hour).
    Returns average waiting time in system (W) and queue (Wq), utilization, etc.
    """
    if service_rate <= arrival_rate:
        return {"error": "Unstable queue (ρ >= 1)", "utilization": arrival_rate / service_rate}

    rho = arrival_rate / service_rate
    avg_in_system = rho / (1 - rho)
    avg_in_queue = rho ** 2 / (1 - rho)
    avg_wait_system = 1 / (service_rate - arrival_rate)
    avg_wait_queue = arrival_rate / (service_rate * (service_rate - arrival_rate))

    return {
        "utilization": round(rho, 4),
        "avg_in_system": round(avg_in_system, 4),
        "avg_in_queue": round(avg_in_queue, 4),
        "avg_wait_system_h": round(avg_wait_system, 4),
        "avg_wait_queue_h": round(avg_wait_queue, 4),
        "avg_wait_system_min": round(avg_wait_system * 60, 2),
    }


def mmc_wait_time(arrival_rate: float, service_rate: float, num_servers: int) -> Dict[str, float]:
    """
    M/M/c multi-server queue (Erlang-C based).
    """
    if num_servers <= 0 or service_rate <= 0:
        return {"error": "Invalid parameters"}

    rho = arrival_rate / (num_servers * service_rate)
    if rho >= 1:
        return {"error": "Unstable queue", "utilization": rho}

    # Probability of zero customers (Erlang-C formula components)
    def erlang_c_prob_wait(lambda_: float, mu: float, c: int) -> float:
        a = lambda_ / mu
        # Sum for P0
        sum_term = sum((a ** k) / math.factorial(k) for k in range(c))
        last_term = (a ** c) / (math.factorial(c) * (1 - rho))
        p0 = 1 / (sum_term + last_term)
        # Erlang C (probability of waiting)
        pc = (a ** c) * p0 / (math.factorial(c) * (1 - rho))
        return pc

    pc = erlang_c_prob_wait(arrival_rate, service_rate, num_servers)
    avg_wait_queue = pc / (num_servers * service_rate - arrival_rate)
    avg_wait_system = avg_wait_queue + 1 / service_rate

    return {
        "utilization": round(rho, 4),
        "prob_of_waiting": round(pc, 4),
        "avg_wait_queue_h": round(avg_wait_queue, 4),
        "avg_wait_system_h": round(avg_wait_system, 4),
        "avg_wait_system_min": round(avg_wait_system * 60, 2),
        "num_servers": num_servers,
    }


def estimate_arrival_rate_from_intensity(intensity_veh_per_h: float, peak_factor: float = 1.0) -> float:
    """Helper to convert sensor intensity to arrival rate λ."""
    return intensity_veh_per_h * peak_factor


# Example usage / simple simulation stub
def simple_simpy_example(arrival_rate: float, service_rate: float, sim_time: float = 1000.0) -> Dict[str, float]:
    """Minimal discrete-event simulation example (requires simpy)."""
    try:
        import simpy
    except ImportError:
        return {"error": "simpy not installed"}

    wait_times: List[float] = []

    def customer(env, name, server):
        arrive = env.now
        with server.request() as req:
            yield req
            wait = env.now - arrive
            wait_times.append(wait)
            service = random.expovariate(service_rate)
            yield env.timeout(service)

    def source(env, server):
        i = 0
        while True:
            yield env.timeout(random.expovariate(arrival_rate))
            i += 1
            env.process(customer(env, f"Cust{i}", server))

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)
    env.process(source(env, server))
    env.run(until=sim_time)

    if not wait_times:
        return {"avg_wait": 0.0}
    return {
        "avg_wait_h": round(sum(wait_times) / len(wait_times), 4),
        "num_customers": len(wait_times),
    }
