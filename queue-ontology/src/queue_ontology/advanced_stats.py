"""
Advanced statistical analysis for queue metrics.
"""

from __future__ import annotations
from typing import Dict, List
import numpy as np
import math


def mmc_waiting_time_cdf(t: float, arrival_rate: float, service_rate: float, c: int) -> float:
    if arrival_rate >= service_rate * c or c < 1:
        return 0.0
    rho = arrival_rate / (service_rate * c)
    sum_term = sum([(arrival_rate / service_rate)**k / math.factorial(k) for k in range(c)])
    p0 = 1.0 / (sum_term + (arrival_rate / service_rate)**c / (math.factorial(c) * (1 - rho)))
    prob_wait = (p0 * (arrival_rate / service_rate)**c / (math.factorial(c) * (1 - rho)))
    if t <= 0:
        return 1.0 - prob_wait
    rate = c * service_rate - arrival_rate
    return 1.0 - prob_wait * np.exp(-rate * t)


def waiting_time_percentiles(arrival_rate: float, service_rate: float, c: int,
                             percentiles: List[float] = [0.5, 0.9, 0.95]) -> Dict[float, float]:
    result = {}
    for p in percentiles:
        low, high = 0.0, 2.0
        for _ in range(40):
            mid = (low + high) / 2
            if mmc_waiting_time_cdf(mid, arrival_rate, service_rate, c) < p:
                low = mid
            else:
                high = mid
        result[p] = high * 60
    return result


def bootstrap_queue_metrics(arrival_samples: np.ndarray, service_rate: float, c: int,
                            n_bootstrap: int = 1000, seed: int = 42) -> Dict:
    rng = np.random.default_rng(seed)
    n = len(arrival_samples)
    mean_waits, utils, p90_waits = [], [], []

    for _ in range(n_bootstrap):
        sample = rng.choice(arrival_samples, size=n, replace=True)
        lam = float(np.mean(sample))
        if lam >= service_rate * c:
            continue
        rho = lam / (service_rate * c)
        if c == 1:
            w = 1 / (service_rate - lam) if service_rate > lam else 30
        else:
            w_q = max(0, rho**c / (c * service_rate - lam))
            w = w_q + 1 / service_rate
        mean_waits.append(w * 60)
        utils.append(rho)
        try:
            p90 = waiting_time_percentiles(lam, service_rate, c, [0.9]).get(0.9, 0)
            p90_waits.append(p90)
        except Exception:
            p90_waits.append(5.0)

    if not mean_waits:
        return {"error": "unstable"}

    return {
        "mean_wait_ci": (float(np.percentile(mean_waits, 2.5)), float(np.percentile(mean_waits, 97.5))),
        "utilization_ci": (float(np.percentile(utils, 2.5)), float(np.percentile(utils, 97.5))),
        "p90_wait_ci": (float(np.percentile(p90_waits, 2.5)), float(np.percentile(p90_waits, 97.5))),
        "mean_wait_point": float(np.mean(mean_waits)),
        "n_valid": len(mean_waits),
    }


def stochastic_green_optimizer(arrival_rate: float, arrival_std: float,
                               service_rate: float, c: int = 1,
                               n_samples: int = 150) -> Dict:
    best_green, best_cost = 0.5, float("inf")
    results = []
    for green in np.linspace(0.35, 0.65, 7):
        mu_eff = service_rate * green * 1.8
        costs = []
        for _ in range(n_samples):
            lam = max(200, np.random.normal(arrival_rate, arrival_std))
            if lam >= mu_eff * c:
                costs.append(25.0)
                continue
            try:
                p90 = waiting_time_percentiles(lam, mu_eff, c, [0.9]).get(0.9, 8)
                costs.append(p90)
            except Exception:
                costs.append(10.0)
        mean_cost = float(np.mean(costs))
        results.append((float(green), mean_cost))
        if mean_cost < best_cost:
            best_cost, best_green = mean_cost, float(green)
    return {
        "optimal_green_fraction": best_green,
        "expected_p90_wait_min": best_cost,
        "evaluated": results,
    }


def run_advanced_analysis(arrival_rate: float = 1200, arrival_std: float = 180,
                          service_rate: float = 1600, c: int = 1) -> None:
    print("=== Advanced Queue Statistics ===\n")
    rng = np.random.default_rng(42)
    samples = rng.normal(arrival_rate, arrival_std, size=50)
    samples = np.clip(samples, 400, 2200)
    print(f"Arrival rate estimate: {np.mean(samples):.0f} veh/h (±{arrival_std:.0f})")
    print(f"Service rate: {service_rate} veh/h | servers: {c}\n")

    boot = bootstrap_queue_metrics(samples, service_rate, c, n_bootstrap=600)
    if "error" not in boot:
        print("Bootstrap 95% CIs:")
        print(f"  Mean wait: {boot['mean_wait_point']:.2f} min  [{boot['mean_wait_ci'][0]:.2f} – {boot['mean_wait_ci'][1]:.2f}]")
        print(f"  Utilization: [{boot['utilization_ci'][0]:.0%} – {boot['utilization_ci'][1]:.0%}]")
        print(f"  P90 wait: [{boot['p90_wait_ci'][0]:.2f} – {boot['p90_wait_ci'][1]:.2f}] min\n")

    pcts = waiting_time_percentiles(arrival_rate, service_rate, c, [0.5, 0.8, 0.9, 0.95])
    print("Waiting time percentiles (in queue):")
    for p, val in pcts.items():
        print(f"  P{int(p*100)}: {val:.2f} min")

    print("\n--- Stochastic Green Optimization ---")
    opt = stochastic_green_optimizer(arrival_rate, arrival_std, service_rate, c)
    print(f"Optimal green fraction: {opt['optimal_green_fraction']:.2f}")
    print(f"Expected P90 wait: {opt['expected_p90_wait_min']:.2f} min")
    print("\nDone.")


if __name__ == "__main__":
    run_advanced_analysis()