# Urban Queue Ontology

**Decision support for urban traffic queues using ontology modeling, queueing theory, and advanced statistics.**

This project models road segments and intersections as an ontology, estimates traffic intensity under uncertainty, and computes queue metrics (waiting times, utilization, percentiles) to support signal timing decisions.

It is designed to demonstrate end-to-end ownership of a data-to-decision pipeline — from raw sensor observations to quantified recommendations.

---

## Problem

Urban traffic congestion generates large economic losses, pollution, and time waste. Decision-makers need more than raw sensor counts: they need models that answer:

- Where are queues forming and why?
- What is the expected wait time under current conditions?
- Which interventions (changing green times, adding capacity, re-routing) produce the biggest reduction in delay?

This project decomposes the problem into a semantic model (ontology), analytical and simulated queue models, and uncertainty quantification, so that recommendations come with statistical confidence.

By combining:

- an **ontology** of sensors, road segments and intersections,
- analytical and simulated **queueing models**,
- and **uncertainty quantification** (Bayesian estimation, bootstrap, Kalman / particle filters),

we can identify bottlenecks and evaluate the impact of green-time changes with statistical confidence.

---

## ArchitectureSensor observations (noisy intensity)
↓
Ontology layer (Sensors, RoadSegments, Intersections)
↓
Estimation layer (Kalman / Particle Filter / Bayesian)
↓
Queue models (M/M/c, M/G/1 Pollaczek-Khinchine, Monte Carlo)
↓
Metrics + confidence intervals + recommendations
↓
Streamlit dashboardtext---

## Project Structurequeue-ontology/
├── src/queue_ontology/
│   ├── ontology.py          # Ontology objects and links
│   ├── queue_models.py      # Analytical M/M/1 and M/M/c
│   ├── pipeline.py          # End-to-end pipeline
│   ├── advanced_stats.py    # Bootstrap CIs, percentiles, stochastic optimizer
│   ├── advanced_models.py   # Kalman filter + Monte Carlo
│   └── deep_stats.py        # Bayesian estimation, Particle Filter, Pollaczek-Khinchine
├── app/
│   └── streamlit_app.py     # Interactive dashboard
├── data/
│   └── madrid_traffic_sample.csv
├── requirements.txt
└── README.mdtext---

## Key Capabilities

- **Ontology modeling** of sensors, segments and intersections
- Analytical queue metrics (M/M/c)
- **Bootstrap** confidence intervals and waiting-time percentiles
- **Kalman filter** and **Particle Filter** for arrival-rate estimation from noisy data
- **Bayesian** Gamma-Poisson estimation with credible intervals
- **M/G/1 Pollaczek-Khinchine** formula
- **Monte Carlo** simulation with batch means
- Stochastic green-time optimizer under uncertainty
- Interactive Streamlit dashboard

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/mameramil/madrid-traffic.git
cd madrid-traffic/queue-ontology
pip install -r requirements.txt
