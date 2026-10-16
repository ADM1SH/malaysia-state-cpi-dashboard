import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.cpi_model import compute_state_cpi_and_rpi, get_hygr_regional_pressure_summary

st.set_page_config(page_title="Malaysia State CPI & Retail Pressure Dashboard", layout="wide")
st.title("STATE-LEVEL CPI & RETAIL PRESSURE INDEX")
st.caption("Ministry of Finance Malaysia Economic Outlook 2027 (Table 3.16)")

records = compute_state_cpi_and_rpi()
df_all = pd.DataFrame([r.model_dump() for r in records])
df_hygr = get_hygr_regional_pressure_summary()

cols = st.columns(4)
for idx, row in df_hygr.iterrows():
    with cols[idx % 4]:
        st.metric(
            label=f"{row['region_group']} RPI",
            value=f"{row['retail_pressure_index']:.2f}",
            delta=f"CPI '26: {row['cpi_2026']:.1f}% | Food: {row['food_2026']:.1f}%"
        )

c1, c2 = st.columns(2)
with c1:
    df_sorted = df_all[df_all["state"] != "Malaysia"].sort_values("retail_pressure_index", ascending=True)
    fig1 = go.Figure(go.Bar(
        x=df_sorted["retail_pressure_index"],
        y=df_sorted["state"],
        orientation="h",
        marker_color=["#D92B2B" if rg in ["Klang Valley", "Penang", "Sabah", "Sarawak"] else "#1D4ED8" for rg in df_sorted["region_group"]]
    ))
    fig1.update_layout(title="Retail Pressure Index by State", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Headline CPI 2026", x=df_hygr["region_group"], y=df_hygr["cpi_2026"], marker_color="#1D4ED8"))
    fig2.add_trace(go.Bar(name="Food CPI 2026", x=df_hygr["region_group"], y=df_hygr["food_2026"], marker_color="#EAB308"))
    fig2.add_trace(go.Bar(name="Retail Pressure Index", x=df_hygr["region_group"], y=df_hygr["retail_pressure_index"], marker_color="#D92B2B"))
    fig2.update_layout(title="HYGR Focus Regions: Cost Pressure Comparison", barmode="group", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("HYGR Core Regions Summary")
st.dataframe(df_hygr, use_container_width=True)
st.subheader("Complete State Dataset (Table 3.16)")
st.dataframe(df_all, use_container_width=True)
