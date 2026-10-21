"""
Streamlit dashboard for Urban Queue Ontology.
Includes pipeline, advanced stats, optimizer, and Kalman + Monte Carlo.
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))

from queue_ontology.pipeline import run_pipeline
from queue_ontology.advanced_stats import (
    bootstrap_queue_metrics,
    waiting_time_percentiles,
    stochastic_green_optimizer,
)
from queue_ontology.advanced_models import (
    ArrivalRateKalman,
    monte_carlo_queue_simulation,
    kalman_then_monte_carlo,
)

st.set_page_config(page_title="Urban Queue Ontology", layout="wide")
st.title("Urban Queue Ontology")
st.markdown("**Ontology + Queue Theory + Advanced Statistics + Kalman & Monte Carlo**")

tab1, tab2, tab3, tab4 = st.tabs([
    "Pipeline Results",
    "Advanced Statistics",
    "Interactive Optimizer",
    "Kalman + Monte Carlo"
])

with tab1:
    st.subheader("End-to-end Pipeline")
    n_sensors = st.slider("Number of synthetic sensors", 4, 12, 6)
    if st.button("Run Pipeline"):
        with st.spinner("Building ontology..."):
            onto, results = run_pipeline(n_sensors)
        st.success(f"Ontology built with {len(onto.objects)} objects")
        rows = []
        for r in results:
            m = r["metrics"]
            rows.append({
                "Segment": r["segment_id"],
                "Road": r["road"],
                "Arrival": r["arrival_rate"],
                "Service": r["service_rate"],
                "Lanes": r["lanes"],
                "Wait (min)": round(m.get("avg_wait_system_min", 0), 2) if "error" not in m else None,
                "Utilization": f"{m.get('utilization', 0):.0%}" if "error" not in m else "UNSTABLE",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        valid = [r for r in results if "error" not in r["metrics"]]
        if valid:
            chart = pd.DataFrame({
                "Segment": [r["segment_id"] for r in valid],
                "Wait (min)": [r["metrics"].get("avg_wait_system_min", 0) for r in valid],
            })
            st.bar_chart(chart.set_index("Segment"))

with tab2:
    st.subheader("Advanced Statistical Analysis")
    c1, c2, c3 = st.columns(3)
    with c1:
        arr = st.number_input("Arrival rate (veh/h)", 400, 2500, 1200, key="arr2")
    with c2:
        arr_std = st.number_input("Arrival std", 50, 400, 180, key="std2")
    with c3:
        srv = st.number_input("Service rate (veh/h)", 800, 3000, 1600, key="srv2")
    if st.button("Run Advanced Analysis"):
        with st.spinner("Computing..."):
            rng = np.random.default_rng(42)
            samples = np.clip(rng.normal(arr, arr_std, 50), 300, 2500)
            boot = bootstrap_queue_metrics(samples, srv, 1, n_bootstrap=400)
            pcts = waiting_time_percentiles(arr, srv, 1, [0.5, 0.8, 0.9, 0.95])
        if "error" not in boot:
            st.metric("Mean Wait", f"{boot['mean_wait_point']:.2f} min")
            a, b, c = st.columns(3)
            a.metric("Mean Wait 95% CI", f"{boot['mean_wait_ci'][0]:.2f} – {boot['mean_wait_ci'][1]:.2f}")
            b.metric("Utilization CI", f"{boot['utilization_ci'][0]:.0%} – {boot['utilization_ci'][1]:.0%}")
            c.metric("P90 Wait CI", f"{boot['p90_wait_ci'][0]:.2f} – {boot['p90_wait_ci'][1]:.2f}")
        st.write("**Waiting time percentiles**")
        st.dataframe(pd.DataFrame([
            {"Percentile": f"P{int(p*100)}", "Wait (min)": round(v, 2)} for p, v in pcts.items()
        ]), use_container_width=True)

with tab3:
    st.subheader("Stochastic Green Time Optimizer")
    o1, o2 = st.columns(2)
    with o1:
        opt_arr = st.slider("Base arrival rate", 600, 2000, 1100)
        opt_std = st.slider("Arrival uncertainty", 50, 300, 160)
    with o2:
        opt_srv = st.slider("Base service capacity", 1000, 2500, 1500)
    if st.button("Optimize"):
        with st.spinner("Optimizing..."):
            opt = stochastic_green_optimizer(opt_arr, opt_std, opt_srv, c=1, n_samples=100)
        st.success(f"Optimal green fraction: **{opt['optimal_green_fraction']:.2f}**")
        st.metric("Expected P90 wait", f"{opt['expected_p90_wait_min']:.2f} min")
        eval_df = pd.DataFrame(opt["evaluated"], columns=["Green fraction", "Expected P90"])
        st.line_chart(eval_df.set_index("Green fraction"))

with tab4:
    st.subheader("Kalman Filter + Monte Carlo Simulation")
    st.markdown("Estimates true arrival rate from noisy observations, then simulates the queue.")

    k1, k2, k3 = st.columns(3)
    with k1:
        true_lam = st.number_input("True arrival rate", 600, 2000, 1250, key="true_lam")
    with k2:
        noise = st.number_input("Observation noise (std)", 50, 300, 120, key="noise")
    with k3:
        srv_mc = st.number_input("Service rate", 1000, 2500, 1600, key="srv_mc")

    n_obs = st.slider("Number of observations", 10, 60, 30)
    n_mc = st.slider("Monte Carlo simulations", 100, 800, 300)

    if st.button("Run Kalman + Monte Carlo"):
        with st.spinner("Filtering and simulating..."):
            rng = np.random.default_rng(42)
            observations = np.clip(rng.normal(true_lam, noise, n_obs), 300, 2500)
            result = kalman_then_monte_carlo(observations, service_rate=srv_mc, c=1, n_mc=n_mc)

        st.success(f"Kalman estimated arrival rate: **{result['estimated_arrival_rate']:.0f} veh/h**")

        mc = result["monte_carlo"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Mean wait", f"{mc['mean_wait_min']:.2f} min")
        m2.metric("Median wait", f"{mc['median_wait_min']:.2f} min")
        m3.metric("P90 wait", f"{mc['p90_wait_min']:.2f} min")
        m4.metric("P95 wait", f"{mc['p95_wait_min']:.2f} min")

        st.metric("Mean utilization", f"{mc['mean_utilization']:.0%}")
        st.write(f"Utilization 95% CI: [{mc['utilization_ci'][0]:.0%}, {mc['utilization_ci'][1]:.0%}]")

        filtered = result["filtered_series"]
        chart_df = pd.DataFrame({
            "Observation": observations,
            "Kalman estimate": filtered,
        })
        st.line_chart(chart_df)

st.markdown("---")
st.caption("Urban Queue Ontology · Kalman filter · Monte Carlo · Bootstrap · Stochastic optimization")