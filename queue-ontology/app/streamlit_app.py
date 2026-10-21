"""
Simple Streamlit demo for the Queue Ontology project.
"""

import streamlit as st
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from queue_ontology.queue_models import mm1_wait_time, mmc_wait_time

st.set_page_config(page_title="Urban Queue Ontology", layout="wide")

st.title("Urban Queue Ontology")
st.markdown("**Decision support for traffic queues using analytical models.**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Parameters")
    arrival = st.slider("Arrival rate λ (vehicles/h)", 100, 2000, 800)
    service = st.slider("Service rate μ (vehicles/h per server)", 100, 2000, 1000)
    servers = st.slider("Number of servers / lanes", 1, 6, 2)

with col2:
    st.subheader("Results")
    if servers == 1:
        result = mm1_wait_time(arrival, service)
    else:
        result = mmc_wait_time(arrival, service, servers)

    if "error" in result:
        st.error(result["error"])
    else:
        st.metric("Utilization (ρ)", f"{result['utilization']:.1%}")
        st.metric("Avg wait in system", f"{result['avg_wait_system_min']:.1f} min")
        if "prob_of_waiting" in result:
            st.metric("Prob. of waiting", f"{result['prob_of_waiting']:.1%}")

st.markdown("---")
st.caption("Extend this dashboard with real Madrid sensor data, ontology graph visualization, and optimization results.")
