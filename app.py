import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# 1. 页面设置（宽屏模式与标题）
st.set_page_config(
    page_title="FleetPulse | Fleet & Supply Chain Analytics",
    page_icon="🚛",
    layout="wide"
)

# 2. 模拟数据加载（带缓存，提速）
@st.cache_data
def load_data():
    # 实际项目中可读取你的 CSV，这里构造一个高质量的数据集
    data = {
        "Vehicle_ID": [f"TRK-{i}" for i in range(101, 121)],
        "Region": ["Ontario", "Quebec", "Alberta", "BC"] * 5,
        "Fuel_Efficiency_MPG": [6.2, 5.8, 7.1, 6.5, 5.9, 6.8, 7.3, 5.5, 6.1, 6.7] * 2,
        "Maintenance_Cost_CAD": [1200, 3400, 800, 2100, 4500, 900, 1100, 5200, 1800, 2300] * 2,
        "Status": ["Active", "Maintenance Required", "Active", "Active", "Critical Warning"] * 4,
        "Part_Failure_Risk": [15, 85, 10, 45, 92, 12, 18, 88, 30, 50] * 2
    }
    return pd.DataFrame(data)

df = load_data()

# 3. 侧边栏交互过滤器（Sidebar Slicers）
st.sidebar.title("🚛 筛选控制台")
selected_region = st.sidebar.multiselect(
    "选择运营大区 (Region):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

selected_status = st.sidebar.multiselect(
    "车辆状态 (Status):",
    options=df["Status"].unique(),
    default=df["Status"].unique()
)

# 用 DuckDB 展现你在 Python 里跑 SQL 的实力
filtered_df = duckdb.query("""
    SELECT * FROM df 
    WHERE Region IN $selected_region 
      AND Status IN $selected_status
""", params={"selected_region": tuple(selected_region), "selected_status": tuple(selected_status)}).df()

# 4. 主界面抬头
st.title("🚛 FleetPulse: 智能车队运营与预警仪表板")
st.markdown("本系统利用 Python 数据管道实时监测车队燃油效率、高昂维修成本及高风险零部件。")
st.divider()

# 5. 核心 KPI 卡片展示（Metrics）
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

avg_mpg = filtered_df["Fuel_Efficiency_MPG"].mean() if not filtered_df.empty else 0
total_cost = filtered_df["Maintenance_Cost_CAD"].sum() if not filtered_df.empty else 0
critical_count = len(filtered_df[filtered_df["Status"] == "Critical Warning"])

kpi1.metric("监测车辆总数", len(filtered_df))
kpi2.metric("平均燃油效率 (MPG)", f"{avg_mpg:.2f}")
kpi3.metric("总维修支出 (CAD)", f"${total_cost:,.0f}")
kpi4.metric("紧急预警车辆数", critical_count, delta_color="inverse")

st.divider()

# 6. 图表区域（Plotly 动态交互图）
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 车辆油耗与维修成本散点分布")
    fig_scatter = px.scatter(
        filtered_df,
        x="Fuel_Efficiency_MPG",
        y="Maintenance_Cost_CAD",
        color="Status",
        size="Part_Failure_Risk",
        hover_name="Vehicle_ID",
        labels={"Fuel_Efficiency_MPG": "燃油效率 (MPG)", "Maintenance_Cost_CAD": "维修成本 (CAD)"},
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    st.subheader("🚩 高风险故障零部件预警 (Risk > 70%)")
    high_risk_df = filtered_df[filtered_df["Part_Failure_Risk"] > 70]
    fig_bar = px.bar(
        high_risk_df,
        x="Vehicle_ID",
        y="Part_Failure_Risk",
        color="Region",
        text_auto=True,
        labels={"Part_Failure_Risk": "零部件故障概率 (%)"},
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 7. 底层数据源透视与导出
with st.expander("🔍 查看并导出清洗后的明细数据 (Data Inspector)"):
    st.dataframe(filtered_df, use_container_width=True)
    # 允许客户一键下载 CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 下载当前筛选数据 (CSV)",
        data=csv_data,
        file_name="fleetpulse_filtered_data.csv",
        mime="text/csv"
    )