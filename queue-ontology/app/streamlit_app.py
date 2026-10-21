"""
Streamlit dashboard for Urban Queue Ontology.
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

st.set_page_config(page_title="Urban Queue Ontology", layout="wide")
st.title("Urban Queue Ontology")
st.markdown("**Ontology + Queue Theory + Advanced Statistics for traffic decision support**")

tab1, tab2, tab3 = st.tabs(["Pipeline Results", "Advanced Statistics", "Interactive Optimizer"])

with tab1:
    st.subheader("End-to-end Pipeline")
    n_sensors = st.slider("Number of synthetic sensors", 4, 12, 6)
    if st.button("Run Pipeline"):
        with st.spinner("Building ontology and computing metrics..."):
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
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        valid = [r for r in results if "error" not in r["metrics"]]
        if valid:
            chart_data = pd.DataFrame({
                "Segment": [r["segment_id"] for r in valid],
                "Wait (min)": [r["metrics"].get("avg_wait_system_min", 0) for r in valid],
            })
            st.bar_chart(chart_data.set_index("Segment"))

with tab2:
    st.subheader("Advanced Statistical Analysis")
    c1, c2, c3 = st.columns(3)
    with c1:
        arr = st.number_input("Arrival rate (veh/h)", 400, 2500, 1200)
    with c2:
        arr_std = st.number_input("Arrival std", 50, 400, 180)
    with c3:
        srv = st.number_input("Service rate (veh/h)", 800, 3000, 1600)
    if st.button("Run Advanced Analysis"):
        with st.spinner("Computing bootstrap CIs..."):
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
        pct_df = pd.DataFrame([{"Percentile": f"P{int(p*100)}", "Wait (min)": round(v, 2)} for p, v in pcts.items()])
        st.dataframe(pct_df, use_container_width=True)

with tab3:
    st.subheader("Stochastic Green Time Optimizer")
    st.markdown("Optimizes green ratio under arrival uncertainty (minimizes expected P90 wait).")
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

st.markdown("---")
st.caption("Urban Queue Ontology · Synthetic Madrid data · Queue theory + Bootstrap + Stochastic opt")
