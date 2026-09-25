import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Vehicle Analytics Dashboard",
    page_icon="🚗",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------
st.title("🚗 Vehicle Analytics Dashboard")
st.markdown("Monitor vehicle speed, distance, fuel consumption and vehicle status.")

# -----------------------------
# CREATE SAMPLE DATA
# -----------------------------
random.seed(10)

vehicles = [
    "VH001", "VH002", "VH003", "VH004", "VH005",
    "VH006", "VH007", "VH008", "VH009", "VH010"
]

vehicle_types = [
    "Car", "Truck", "Bus", "Van", "Bike"
]

statuses = [
    "Active", "Idle", "Maintenance"
]

data = []

start_date = datetime(2026, 1, 1)

for i in range(300):

    vehicle = random.choice(vehicles)

    speed = random.randint(20, 120)
    distance = round(random.uniform(10, 500), 2)
    fuel = round(random.uniform(2, 50), 2)
    trips = random.randint(1, 8)

    if speed > 90:
        violation = "Yes"
    else:
        violation = "No"

    data.append({
        "Date": start_date + timedelta(days=random.randint(0, 270)),
        "Vehicle_ID": vehicle,
        "Vehicle_Type": random.choice(vehicle_types),
        "Speed_kmph": speed,
        "Distance_km": distance,
        "Fuel_Liters": fuel,
        "Trips": trips,
        "Status": random.choice(statuses),
        "Speed_Violation": violation
    })

df = pd.DataFrame(data)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Filters")

selected_vehicle = st.sidebar.multiselect(
    "Select Vehicle",
    options=sorted(df["Vehicle_ID"].unique()),
    default=sorted(df["Vehicle_ID"].unique())
)

selected_type = st.sidebar.multiselect(
    "Vehicle Type",
    options=sorted(df["Vehicle_Type"].unique()),
    default=sorted(df["Vehicle_Type"].unique())
)

selected_status = st.sidebar.multiselect(
    "Vehicle Status",
    options=sorted(df["Status"].unique()),
    default=sorted(df["Status"].unique())
)

# -----------------------------
# FILTER DATA
# -----------------------------
filtered_df = df[
    (df["Vehicle_ID"].isin(selected_vehicle)) &
    (df["Vehicle_Type"].isin(selected_type)) &
    (df["Status"].isin(selected_status))
]

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_vehicles = filtered_df["Vehicle_ID"].nunique()
total_trips = filtered_df["Trips"].sum()

average_speed = filtered_df["Speed_kmph"].mean()

total_distance = filtered_df["Distance_km"].sum()

total_fuel = filtered_df["Fuel_Liters"].sum()

violations = (filtered_df["Speed_Violation"] == "Yes").sum()

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🚗 Total Vehicles",
    total_vehicles
)

col2.metric(
    "🛣️ Total Trips",
    total_trips
)

col3.metric(
    "⚡ Average Speed",
    f"{average_speed:.1f} km/h"
)

col4.metric(
    "📍 Distance Travelled",
    f"{total_distance:,.0f} km"
)

st.divider()

# -----------------------------
# SECOND KPI ROW
# -----------------------------
col5, col6, col7 = st.columns(3)

col5.metric(
    "⛽ Fuel Consumed",
    f"{total_fuel:,.1f} L"
)

col6.metric(
    "⚠️ Speed Violations",
    violations
)

fuel_efficiency = (
    total_distance / total_fuel
    if total_fuel > 0
    else 0
)

col7.metric(
    "📊 Fuel Efficiency",
    f"{fuel_efficiency:.2f} km/L"
)

st.divider()

# -----------------------------
# DAILY VEHICLE ACTIVITY
# -----------------------------
daily_data = (
    filtered_df
    .groupby("Date")
    .agg({
        "Trips": "sum",
        "Distance_km": "sum"
    })
    .reset_index()
    .sort_values("Date")
)

fig1 = px.line(
    daily_data,
    x="Date",
    y="Distance_km",
    markers=True,
    title="📈 Daily Distance Travelled"
)

fig1.update_layout(
    xaxis_title="Date",
    yaxis_title="Distance (km)"
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# TWO COLUMN CHARTS
# -----------------------------
left, right = st.columns(2)

# Vehicle Performance
vehicle_performance = (
    filtered_df
    .groupby("Vehicle_ID")
    .agg({
        "Speed_kmph": "mean",
        "Distance_km": "sum"
    })
    .reset_index()
)

fig2 = px.bar(
    vehicle_performance,
    x="Vehicle_ID",
    y="Speed_kmph",
    title="🚘 Average Speed by Vehicle",
    text_auto=".1f"
)

fig2.update_layout(
    xaxis_title="Vehicle",
    yaxis_title="Average Speed (km/h)"
)

left.plotly_chart(fig2, use_container_width=True)

# Fuel Consumption
fuel_data = (
    filtered_df
    .groupby("Vehicle_ID")["Fuel_Liters"]
    .sum()
    .reset_index()
)

fig3 = px.bar(
    fuel_data,
    x="Vehicle_ID",
    y="Fuel_Liters",
    title="⛽ Fuel Consumption by Vehicle",
    text_auto=".1f"
)

fig3.update_layout(
    xaxis_title="Vehicle",
    yaxis_title="Fuel (Liters)"
)

right.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# VEHICLE TYPE DISTRIBUTION
# -----------------------------
left, right = st.columns(2)

type_data = (
    filtered_df["Vehicle_Type"]
    .value_counts()
    .reset_index()
)

type_data.columns = ["Vehicle_Type", "Count"]

fig4 = px.pie(
    type_data,
    names="Vehicle_Type",
    values="Count",
    title="🚙 Vehicle Type Distribution"
)

left.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# VEHICLE STATUS
# -----------------------------
status_data = (
    filtered_df["Status"]
    .value_counts()
    .reset_index()
)

status_data.columns = ["Status", "Count"]

fig5 = px.pie(
    status_data,
    names="Status",
    values="Count",
    title="🔧 Vehicle Status"
)

right.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# SPEED VIOLATIONS
# -----------------------------
st.subheader("⚠️ Speed Violation Analysis")

violation_df = filtered_df[
    filtered_df["Speed_Violation"] == "Yes"
].copy()

if len(violation_df) > 0:

    violation_display = violation_df[
        [
            "Date",
            "Vehicle_ID",
            "Vehicle_Type",
            "Speed_kmph",
            "Speed_Violation"
        ]
    ].sort_values(
        "Speed_kmph",
        ascending=False
    )

    st.dataframe(
        violation_display,
        use_container_width=True,
        hide_index=True
    )

else:
    st.success("✅ No speed violations found.")

# -----------------------------
# VEHICLE PERFORMANCE TABLE
# -----------------------------
st.subheader("📋 Vehicle Performance")

performance_table = (
    filtered_df
    .groupby("Vehicle_ID")
    .agg(
        Average_Speed=("Speed_kmph", "mean"),
        Total_Distance=("Distance_km", "sum"),
        Total_Fuel=("Fuel_Liters", "sum"),
        Total_Trips=("Trips", "sum")
    )
    .reset_index()
)

performance_table["Fuel_Efficiency"] = (
    performance_table["Total_Distance"] /
    performance_table["Total_Fuel"]
)

performance_table["Average_Speed"] = \
    performance_table["Average_Speed"].round(2)

performance_table["Total_Distance"] = \
    performance_table["Total_Distance"].round(2)

performance_table["Total_Fuel"] = \
    performance_table["Total_Fuel"].round(2)

performance_table["Fuel_Efficiency"] = \
    performance_table["Fuel_Efficiency"].round(2)

st.dataframe(
    performance_table,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# DOWNLOAD DATA
# -----------------------------
st.subheader("📥 Download Data")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Vehicle Data CSV",
    data=csv,
    file_name="vehicle_analytics_data.csv",
    mime="text/csv"
)

# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption(
    "Vehicle Analytics Dashboard | Built with Python, Pandas, Streamlit & Plotly"
)
