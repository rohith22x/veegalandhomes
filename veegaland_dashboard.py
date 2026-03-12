import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veegaland Homes · DRHP Analytics",
    page_icon="🏠",
    layout="wide",
)

# ── Brand colours ─────────────────────────────────────────────────────────────
DARK_GREEN  = "#1A3A2A"
MID_GREEN   = "#2A5A3A"
GOLD        = "#C8973A"
LIGHT_GOLD  = "#F5EDD8"
MUTED       = "#6B8C73"
RED         = "#C84A3A"
BLUE        = "#2F5597"
BG          = "#0D1F14"

# ── Robust Data Loading ──────────────────────────────────────────────────────

@st.cache_data
def load_data():
    def get_path(filename):
        for root, dirs, files in os.walk("."):
            if filename in files:
                return os.path.join(root, filename)
        return None

    files_to_load = {
        'fin': '1_financial_kpis.csv',
        'sales': '2_sales_kpis.csv',
        'segments': '4_segment_revenue.csv',
        'portfolio': '5_project_portfolio.csv',
        'marketing': '8_marketing_spend.csv'
    }

    data = {}
    for key, fname in files_to_load.items():
        path = get_path(fname)
        if path:
            data[key] = pd.read_csv(path)
        else:
            st.error(f"Missing File: {fname}")
            st.stop()

    period_map = {
        "FY2023": "FY23", "FY2024": "FY24", "FY2025": "FY25", "H1_FY2026": "H1 FY26"
    }
    
    # Process Dataframes
    df_fin = data['fin'].copy()
    df_fin['Period'] = df_fin['Period'].map(period_map)
    
    df_sales = data['sales'].copy()
    df_sales['Period'] = df_sales['Period'].map(period_map)
    
    # FIX for Error 1: Ensure Revenue column is identified correctly
    if 'Revenue_from_Operations_Lakhs' in df_sales.columns:
        df_sales['Display_Revenue'] = df_sales['Revenue_from_Operations_Lakhs']
    elif 'Revenue_Recognised_Lakhs' in df_sales.columns:
        df_sales['Display_Revenue'] = df_sales['Revenue_Recognised_Lakhs']
    else:
        # Fallback to revenue from the financial sheet if needed
        df_sales = df_sales.merge(df_fin[['Period', 'Revenue_from_Operations_Lakhs']], on='Period', how='left')
        df_sales['Display_Revenue'] = df_sales['Revenue_from_Operations_Lakhs']

    df_segments = data['segments'].copy()
    df_segments['Period'] = df_segments['Period'].map(period_map)
    df_segments['Segment'] = df_segments['Segment'].replace({"Luxe-Series": "Luxe"})
    
    df_marketing = data['marketing'].copy()
    df_marketing['Period'] = df_marketing['Period'].map(period_map)
    
    df_projects = data['portfolio'][data['portfolio']['Status'] == 'Ongoing'].copy()
    
    project_rev_h1_26 = {
        "Green Heights": 2916, "Maybell": 1114, "Green Fort": 1141, 
        "Green Capitol": 2587, "Queens Park": 567, "Casabella": 1388, 
        "Symphony": 1661, "Flora": 49, "Elanza": 654
    }
    df_projects['Rev_H1FY26'] = df_projects['Project_Name'].map(project_rev_h1_26).fillna(0)
    
    return df_fin, df_sales, df_segments, df_projects, df_marketing

df_fin, df_sales, df_segments, df_projects, df_marketing = load_data()

# ── FIX for Error 2 & 3: Standardize Plotly Layout ────────────────────────────

def chart_layout(fig, height=350):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=LIGHT_GOLD),
        title_font=dict(color=GOLD, size=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='#333333'),
        yaxis=dict(showgrid=True, gridcolor='#333333')
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stMetric {{ background-color: {DARK_GREEN}; padding: 15px; border-radius: 10px; border-left: 5px solid {GOLD}; }}
    [data-testid="stMetricLabel"] {{ color: {MUTED} !important; text-transform: uppercase; }}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🏠 Veegaland Analytics")
    page = st.selectbox("Menu", ["Overview", "Projects", "Marketing"])

if page == "Overview":
    st.header("Financial Performance")
    
    # KPI metrics
    latest = df_fin.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue (H1 FY26)", f"₹{latest['Revenue_from_Operations_Lakhs']:,.0f} L")
    c2.metric("PAT Margin", f"{latest['PAT_Margin_Pct']}%")
    c3.metric("D/E Ratio", f"{latest['Debt_Equity_Ratio']}x")

    # Fixed Bar Chart
    fig = go.Figure()
    fig.add_bar(name="Revenue Recognized", x=df_sales["Period"], y=df_sales["Display_Revenue"], marker_color=MID_GREEN)
    fig.add_bar(name="Sales Bookings", x=df_sales["Period"], y=df_sales["Sales_Value_Lakhs_excl_GST"], marker_color=GOLD)
    fig.update_layout(barmode='group', title="Revenue vs Bookings")
    st.plotly_chart(chart_layout(fig), use_container_width=True)

elif page == "Projects":
    st.header("Project Portfolio")
    df_p_sorted = df_projects.sort_values("Rev_H1FY26", ascending=True)
    fig_p = px.bar(df_p_sorted, x="Rev_H1FY26", y="Project_Name", orientation='h', color_discrete_sequence=[GOLD])
    st.plotly_chart(chart_layout(fig_p), use_container_width=True)
    st.dataframe(df_projects[['Project_Name', 'City', 'Pct_Sold', 'Rev_H1FY26']], use_container_width=True)

elif page == "Marketing":
    st.header("Marketing Spend Analysis")
    
    # Fixed Marketing Charts
    fig_m1 = px.bar(df_marketing, x="Period", y="Marketing_Sales_Spend_Lakhs", title="Spend per Period", color_discrete_sequence=[MID_GREEN])
    st.plotly_chart(chart_layout(fig_m1), use_container_width=True)
    
    fig_m2 = px.line(df_marketing, x="Period", y="Pct_of_Revenue", title="Efficiency (% of Revenue)", markers=True)
    fig_m2.update_traces(line_color=GOLD)
    st.plotly_chart(chart_layout(fig_m2), use_container_width=True)
