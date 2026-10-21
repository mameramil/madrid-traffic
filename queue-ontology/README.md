# Urban Queue Ontology

**Decision support for urban traffic queues using ontology modeling, queueing theory, and advanced statistics.**

This project models road segments and intersections as an ontology, estimates traffic intensity under uncertainty, and computes queue metrics (waiting times, utilization, percentiles) to support signal timing decisions.

It is designed to demonstrate end-to-end ownership of a data-to-decision pipeline — from raw sensor observations to quantified recommendations.

---

## Problem

Urban intersections suffer from variable demand. Fixed signal plans waste capacity or create queues. By combining:

- an **ontology** of sensors, road segments and intersections,
- analytical and simulated **queueing models**,
- and **uncertainty quantification** (Bayesian estimation, bootstrap, Kalman / particle filters),

we can identify bottlenecks and evaluate the impact of green-time changes with statistical confidence.

---

## Architecture


