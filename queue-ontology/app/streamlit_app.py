import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "queue_ontology"))

from data_loader import load_and_prepare

st.set_page_config(page_title="Urban Queue Ontology", layout="wide")
st.title("Urban Queue Ontology")
st.caption("Datos de ejemplo de Madrid")

@st.cache_data
def load_data():
    return load_and_prepare()

observations = load_data()
df = pd.DataFrame(observations)

st.sidebar.header("Sensor")
sensor = st.sidebar.selectbox("Selecciona", sorted(df["sensor_id"].unique()))
sensor_df = df[df["sensor_id"] == sensor].sort_values("hour")

st.subheader(f"Intensidad observada — {sensor}")
fig = px.line(sensor_df, x="hour", y="intensity", markers=True, title="veh/h")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Datos")
st.dataframe(sensor_df, use_container_width=True)