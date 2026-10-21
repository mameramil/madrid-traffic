"""
Deep statistical methods for queue systems.
"""

from __future__ import annotations
from typing import Dict
import numpy as np
import math


def bayesian_arrival_estimate(observations: np.ndarray, prior_alpha: float = 2.0, prior_beta: float = 0.002) -> Dict:
    n = len(observations)
    sum_obs = float(np.sum(observations))
    post_alpha = prior_alpha + sum_obs
    post_beta = prior_beta + n
    mean = post_alpha / post_beta
    var = post_alpha / (post_beta ** 2)
    std = math.sqrt(var)
    ci = (mean - 1.96 * std, mean + 1.96 * std)
    return {
        "posterior_mean": mean,
        "posterior_var": var,
        "credible_interval_95": ci,
        "posterior_alpha": post_alpha,
        "posterior_beta": post_beta,
    }


class ParticleFilterArrival:
    def __init__(self, n_particles: int = 200, process_std: float = 40.0, obs_std: float = 100.0, seed: int = 42):
        self.n_particles = n_particles
        self.process_std = process_std
        self.obs_std = obs_std
        self.rng = np.random.default_rng(seed)
        self.particles = self.rng.normal(1000, 200, n_particles)
        self.weights = np.ones(n_particles) / n_particles

    def update(self, observation: float) -> float:
        self.particles += self.rng.normal(0, self.process_std, self.n_particles)
        self.particles = np.clip(self.particles, 200, 3000)
        log_lik = -0.5 * ((observation - self.particles) / self.obs_std) ** 2
        log_lik -= np.max(log_lik)
        weights = np.exp(log_lik)
        weights /= np.sum(weights)
        self.weights = weights
        ess = 1.0 / np.sum(weights ** 2)
        if ess < self.n_particles / 2:
            idx = self.rng.choice(self.n_particles, self.n_particles, p=weights)
            self.particles = self.particles[idx]
            self.weights = np.ones(self.n_particles) / self.n_particles
        return float(np.sum(self.particles * self.weights))

    def filter_series(self, observations: np.ndarray) -> np.ndarray:
        estimates = []
        for obs in observations:
            estimates.append(self.update(float(obs)))
        return np.array(estimates)


def pollaczek_khinchine_wait(arrival_rate: float, mean_service: float, service_cv: float) -> float:
    if arrival_rate * mean_service >= 1:
        return float("inf")
    rho = arrival_rate * mean_service
    var_service = (service_cv * mean_service) ** 2
    w_q = (arrival_rate * var_service + rho * mean_service) / (2 * (1 - rho))
    return w_q * 60


def monte_carlo_with_batch_means(
    arrival_rate: float,
    service_rate: float,
    c: int = 1,
    n_batches: int = 20,
    batch_size: int = 50,
    seed: int = 42,
) -> Dict:
    rng = np.random.default_rng(seed)
    batch_means = []
    for _ in range(n_batches):
        waits = []
        for _ in range(batch_size):
            n_arr = rng.poisson(arrival_rate)
            if n_arr == 0:
                waits.append(0.0)
                continue
            inter = rng.exponential(1 / arrival_rate, n_arr)
            arr_times = np.cumsum(inter)
            svc = rng.exponential(1 / service_rate, n_arr)
            free = np.zeros(c)
            batch_waits = []
            for a, s in zip(arr_times, svc):
                earliest = np.min(free)
                wait = max(0.0, earliest - a)
                batch_waits.append(wait)
                free[np.argmin(free)] = max(a, earliest) + s
            waits.append(np.mean(batch_waits) * 60 if batch_waits else 0.0)
        batch_means.append(np.mean(waits))
    batch_means = np.array(batch_means)
    overall_mean = float(np.mean(batch_means))
    se = float(np.std(batch_means) / math.sqrt(n_batches))
    return {
        "mean_wait_min": overall_mean,
        "standard_error": se,
        "ci_95": (overall_mean - 1.96 * se, overall_mean + 1.96 * se),
        "n_batches": n_batches,
    }


def compare_analytical_vs_mc(arrival_rate: float, service_rate: float, service_cv: float = 1.0) -> Dict:
    mean_service = 1.0 / service_rate
    analytical = pollaczek_khinchine_wait(arrival_rate, mean_service, service_cv)
    mc = monte_carlo_with_batch_means(arrival_rate, service_rate, c=1)
    diff = mc["mean_wait_min"] - analytical
    return {
        "analytical_wait_min": analytical,
        "mc_wait_min": mc["mean_wait_min"],
        "difference": diff,
        "mc_ci": mc["ci_95"],
        "agreement": abs(diff) < 2 * mc["standard_error"],
    }


def run_deep_analysis(seed: int = 42) -> None:
    print("=== Deep Statistical Analysis ===\n")
    rng = np.random.default_rng(seed)
    true_lam = 1300
    observations = np.clip(rng.normal(true_lam, 140, 40), 400, 2200)
    print(f"True λ: {true_lam} | Observations mean: {np.mean(observations):.0f}\n")

    bayes = bayesian_arrival_estimate(observations)
    print("Bayesian Gamma-Poisson:")
    print(f"  Posterior mean: {bayes['posterior_mean']:.0f} veh/h")
    print(f"  95% credible interval: [{bayes['credible_interval_95'][0]:.0f}, {bayes['credible_interval_95'][1]:.0f}]\n")

    pf = ParticleFilterArrival(n_particles=250)
    pf_est = pf.filter_series(observations)
    print(f"Particle Filter final estimate: {pf_est[-1]:.0f} veh/h\n")

    print("--- Analytical (Pollaczek-Khinchine) vs Monte Carlo ---")
    comp = compare_analytical_vs_mc(true_lam, 1650, service_cv=1.1)
    print(f"  Analytical wait: {comp['analytical_wait_min']:.2f} min")
    print(f"  Monte Carlo wait: {comp['mc_wait_min']:.2f} min")
    print(f"  Difference: {comp['difference']:.2f} min")
    print(f"  MC 95% CI: [{comp['mc_ci'][0]:.2f}, {comp['mc_ci'][1]:.2f}]")
    print(f"  Agreement within noise: {comp['agreement']}")
    print("\nDone.")


if __name__ == "__main__":
    run_deep_analysis()