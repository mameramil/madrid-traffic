"""
Advanced models: Kalman filtering for arrival rate estimation,
Monte Carlo queue simulation, and enhanced statistical analysis.
"""

from __future__ import annotations
from typing import Dict, List
import numpy as np


class ArrivalRateKalman:
    def __init__(self, initial_lambda: float = 1000.0, process_var: float = 50.0, obs_var: float = 100.0):
        self.x = initial_lambda
        self.P = 200.0
        self.Q = process_var
        self.R = obs_var

    def update(self, observation: float) -> float:
        x_pred = self.x
        P_pred = self.P + self.Q
        K = P_pred / (P_pred + self.R)
        self.x = x_pred + K * (observation - x_pred)
        self.P = (1 - K) * P_pred
        return self.x

    def filter_series(self, observations: np.ndarray) -> np.ndarray:
        estimates = []
        for obs in observations:
            estimates.append(self.update(float(obs)))
        return np.array(estimates)


def monte_carlo_queue_simulation(
    arrival_rate: float,
    service_rate: float,
    c: int = 1,
    n_simulations: int = 500,
    duration_h: float = 1.0,
    seed: int = 42,
) -> Dict:
    rng = np.random.default_rng(seed)
    wait_times = []
    utilizations = []

    for _ in range(n_simulations):
        n_arrivals = rng.poisson(arrival_rate * duration_h)
        if n_arrivals == 0:
            wait_times.append(0.0)
            utilizations.append(0.0)
            continue

        interarrivals = rng.exponential(1.0 / arrival_rate, n_arrivals)
        arrival_times = np.cumsum(interarrivals)
        service_times = rng.exponential(1.0 / service_rate, n_arrivals)

        servers_free = np.zeros(c)
        waits = []
        for arr, svc in zip(arrival_times, service_times):
            earliest = np.min(servers_free)
            wait = max(0.0, earliest - arr)
            waits.append(wait)
            start = max(arr, earliest)
            finish = start + svc
            servers_free[np.argmin(servers_free)] = finish

        avg_wait = np.mean(waits) * 60 if waits else 0.0
        busy_time = np.sum(service_times)
        util = min(1.0, busy_time / (c * duration_h))
        wait_times.append(avg_wait)
        utilizations.append(util)

    wait_times = np.array(wait_times)
    utilizations = np.array(utilizations)

    return {
        "mean_wait_min": float(np.mean(wait_times)),
        "median_wait_min": float(np.median(wait_times)),
        "p90_wait_min": float(np.percentile(wait_times, 90)),
        "p95_wait_min": float(np.percentile(wait_times, 95)),
        "wait_std": float(np.std(wait_times)),
        "mean_utilization": float(np.mean(utilizations)),
        "utilization_ci": (
            float(np.percentile(utilizations, 2.5)),
            float(np.percentile(utilizations, 97.5)),
        ),
        "n_simulations": n_simulations,
    }


def kalman_then_monte_carlo(
    noisy_observations: np.ndarray,
    service_rate: float,
    c: int = 1,
    n_mc: int = 300,
) -> Dict:
    kf = ArrivalRateKalman(initial_lambda=float(np.mean(noisy_observations)))
    filtered = kf.filter_series(noisy_observations)
    estimated_lambda = float(filtered[-1])

    mc = monte_carlo_queue_simulation(
        arrival_rate=estimated_lambda,
        service_rate=service_rate,
        c=c,
        n_simulations=n_mc,
    )

    return {
        "estimated_arrival_rate": estimated_lambda,
        "filtered_series": filtered.tolist(),
        "monte_carlo": mc,
    }


def run_advanced_demo(seed: int = 42) -> None:
    print("=== Advanced Models Demo (Kalman + Monte Carlo) ===\n")
    rng = np.random.default_rng(seed)
    true_lambda = 1250
    observations = rng.normal(true_lambda, 120, size=30)
    observations = np.clip(observations, 400, 2000)

    print(f"True arrival rate: {true_lambda} veh/h")
    print(f"Noisy observations mean: {np.mean(observations):.0f} veh/h\n")

    result = kalman_then_monte_carlo(observations, service_rate=1600, c=1, n_mc=400)
    print(f"Kalman estimated λ: {result['estimated_arrival_rate']:.0f} veh/h")
    mc = result["monte_carlo"]
    print("\nMonte Carlo results (1 hour):")
    print(f"  Mean wait: {mc['mean_wait_min']:.2f} min")
    print(f"  Median wait: {mc['median_wait_min']:.2f} min")
    print(f"  P90 wait: {mc['p90_wait_min']:.2f} min")
    print(f"  P95 wait: {mc['p95_wait_min']:.2f} min")
    print(f"  Mean utilization: {mc['mean_utilization']:.0%}")
    print(f"  Utilization 95% CI: [{mc['utilization_ci'][0]:.0%}, {mc['utilization_ci'][1]:.0%}]")
    print("\nDone.")


if __name__ == "__main__":
    run_advanced_demo()