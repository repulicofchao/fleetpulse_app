import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import duckdb

# ==========================================
# 1. Page Configuration & Custom CSS Styling
# ==========================================
st.set_page_config(
    page_title="FleetPulse Enterprise | Advanced Logistics Telematics",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished metric cards
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #0066CC;
        padding: 12px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Advanced Multi-Factor Mock Dataset Generator
# ==========================================
@st.cache_data
def load_enterprise_telematics_data():
    np.random.seed(42)
    n_records = 150
    
    vehicle_types = ["Heavy Duty Semi", "Medium Delivery Truck", "Electric Fleet Van", "Refrigerated Carrier"]
    engine_types = ["Diesel", "Hybrid", "Fully Electric"]
    regions = ["Ontario", "Quebec", "Alberta", "British Columbia"]
    statuses = ["Active Operations", "Scheduled Service", "Critical Warning", "Out of Service"]
    
    data = {
        "Vehicle_ID": [f"TRK-{1000 + i}" for i in range(n_records)],
        "Vehicle_Type": np.random.choice(vehicle_types, n_records),
        "Engine_Type": np.random.choice(engine_types, n_records),
        "Region": np.random.choice(regions, n_records),
        "Status": np.random.choice(statuses, n_records, p=[0.6, 0.2, 0.1, 0.1]),
        "Odometer_KM": np.random.randint(20000, 350000, n_records),
        "Fuel_Efficiency_MPG": np.round(np.random.uniform(4.5, 9.5, n_records), 2),
        "Maintenance_Cost_CAD": np.round(np.random.uniform(500, 12000, n_records), 2),
        "Part_Failure_Risk_Pct": np.random.randint(5, 98, n_records),
        "Driver_Safety_Score": np.random.randint(60, 100, n_records),
        "CO2_Emissions_Tons": np.round(np.random.uniform(1.2, 8.5, n_records), 2)
    }
    return pd.DataFrame(data)

raw_df = load_enterprise_telematics_data()

# ==========================================
# 3. Sidebar: Multi-Parameter Control Panel
# ==========================================
st.sidebar.title("🎛️ Enterprise Control Panel")
st.sidebar.markdown("Filter and stress-test fleet telemetry metrics:")

# Multi-select filters
selected_regions = st.sidebar.multiselect(
    "1. Operating Regions:",
    options=raw_df["Region"].unique(),
    default=raw_df["Region"].unique()
)

selected_vtypes = st.sidebar.multiselect(
    "2. Vehicle Classification:",
    options=raw_df["Vehicle_Type"].unique(),
    default=raw_df["Vehicle_Type"].unique()
)

selected_engines = st.sidebar.multiselect(
    "3. Powertrain / Engine:",
    options=raw_df["Engine_Type"].unique(),
    default=raw_df["Engine_Type"].unique()
)

# Numeric Range Sliders
min_risk, max_risk = st.sidebar.slider(
    "4. Component Failure Risk Threshold (%):",
    min_value=0, max_value=100, value=(0, 100)
)

max_maintenance = st.sidebar.slider(
    "5. Max Maintenance Expense Budget (CAD):",
    min_value=1000, max_value=15000, value=15000, step=500
)

# Querying via DuckDB for SQL demonstration
filtered_df = duckdb.query("""
    SELECT * FROM raw_df 
    WHERE Region IN $selected_regions
      AND Vehicle_Type IN $selected_vtypes
      AND Engine_Type IN $selected_engines
      AND Part_Failure_Risk_Pct BETWEEN $min_risk AND $max_risk
      AND Maintenance_Cost_CAD <= $max_maintenance
""", params={
    "selected_regions": tuple(selected_regions),
    "selected_vtypes": tuple(selected_vtypes),
    "selected_engines": tuple(selected_engines),
    "min_risk": min_risk,
    "max_risk": max_risk,
    "max_maintenance": max_maintenance
}).df()

# ==========================================
# 4. Main Header & Top Executive KPIs
# ==========================================
st.title("🚛 FleetPulse Enterprise: Advanced Fleet & Supply Chain Analytics")
st.markdown("Integrated IoT Telematics Portal evaluating fuel efficiency, predictive maintenance risk, and driver safety compliance.")
st.divider()

# KPI Row
k1, k2, k3, k4, k5 = st.columns(5)

total_units = len(filtered_df)
avg_mpg = filtered_df["Fuel_Efficiency_MPG"].mean() if total_units > 0 else 0
total_maint = filtered_df["Maintenance_Cost_CAD"].sum() if total_units > 0 else 0
avg_safety = filtered_df["Driver_Safety_Score"].mean() if total_units > 0 else 0
critical_alerts = len(filtered_df[filtered_df["Part_Failure_Risk_Pct"] > 75])

k1.metric("Monitored Units", f"{total_units} / {len(raw_df)}")
k2.metric("Avg Fuel Efficiency", f"{avg_mpg:.2f} MPG")
k3.metric("Total Maint. Expense", f"${total_maint:,.0f} CAD")
k4.metric("Avg Driver Safety Score", f"{avg_safety:.1f} / 100")
k5.metric("High Risk Alerts (>75%)", critical_alerts, delta_color="inverse")

st.divider()

# ==========================================
# 5. Tabbed Multi-Chart Layout
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📊 Operational Efficiency & Risk", 
    "📈 Powertrain & Emissions Breakdown", 
    "🔍 Interactive Data Explorer"
])

# ---------------- TAB 1: Efficiency & Risk ----------------
with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("1. Maintenance Expense vs. Fuel Efficiency vs. Mileage")
        st.caption("Bubble Size = Driver Safety Score | Color = Operating Status")
        fig_bubble = px.scatter(
            filtered_df,
            x="Fuel_Efficiency_MPG",
            y="Maintenance_Cost_CAD",
            size="Odometer_KM",
            color="Status",
            hover_name="Vehicle_ID",
            hover_data=["Vehicle_Type", "Driver_Safety_Score"],
            labels={"Fuel_Efficiency_MPG": "Fuel Efficiency (MPG)", "Maintenance_Cost_CAD": "Maintenance Cost (CAD)"},
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col_b:
        st.subheader("2. Component Risk Distribution Across Regions (Boxplot)")
        st.caption("Identify regional risk outliers requiring fleet inspection")
        fig_box = px.box(
            filtered_df,
            x="Region",
            y="Part_Failure_Risk_Pct",
            color="Vehicle_Type",
            labels={"Part_Failure_Risk_Pct": "Failure Risk (% )"},
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_box, use_container_width=True)

# ---------------- TAB 2: Powertrain & Emissions ----------------
with tab2:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("3. Total Maintenance Expenditure by Vehicle Class")
        vtype_summary = filtered_df.groupby(["Vehicle_Type", "Engine_Type"])["Maintenance_Cost_CAD"].sum().reset_index()
        fig_bar_group = px.bar(
            vtype_summary,
            x="Vehicle_Type",
            y="Maintenance_Cost_CAD",
            color="Engine_Type",
            barmode="group",
            text_auto="$.2s",
            labels={"Maintenance_Cost_CAD": "Total Cost (CAD)"},
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_bar_group, use_container_width=True)
        
    with col_d:
        st.subheader("4. Fleet Operational Status Funnel Breakdown")
        status_counts = filtered_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_funnel = px.funnel(
            status_counts,
            x="Count",
            y="Status",
            color="Status",
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

# ---------------- TAB 3: Data Inspector & Export ----------------
with tab3:
    st.subheader("🔍 Real-Time Query Results & Data Export")
    st.markdown("Filter and inspect the underlying SQL dataset directly in the matrix below:")
    
    # Allow column selection for customized export
    selected_cols = st.multiselect(
        "Select columns to display/export:",
        options=list(filtered_df.columns),
        default=["Vehicle_ID", "Vehicle_Type", "Region", "Status", "Maintenance_Cost_CAD", "Part_Failure_Risk_Pct"]
    )
    
    st.dataframe(filtered_df[selected_cols], use_container_width=True)
    
    csv = filtered_df[selected_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Selected Query Dataset (CSV)",
        data=csv,
        file_name="fleetpulse_filtered_query.csv",
        mime="text/csv"
    )