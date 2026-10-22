# Urban Queue Ontology

**Ontology-based decision support for urban traffic queues.**

This project models road infrastructure as an ontology and applies queueing theory together with advanced statistical methods to estimate waiting times, identify bottlenecks, and support signal timing decisions under uncertainty.

It demonstrates a complete data-to-decision pipeline: from noisy sensor observations to quantified recommendations with confidence intervals.

---

## Problem

Fixed traffic signal plans cannot adapt to variable demand. The result is either wasted capacity or growing queues. By representing the road network as an ontology and combining it with analytical and simulation-based queue models, it becomes possible to:

- Estimate true arrival rates from noisy sensor data
- Compute waiting times and utilization with uncertainty quantification
- Identify the most congested segments
- Evaluate the impact of green-time changes before applying them

---

## Architecture

