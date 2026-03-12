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
    
    # Process Financials
    df_fin = data['fin'].copy()
    df_fin['Period'] = df_fin['Period'].map(period_map)
    
    # Process Sales and detect Revenue column
    df_sales = data['sales'].copy()
    df_sales['Period'] = df_sales['Period'].map(period_map)
    
    # FIX: Robust Column Detection
    possible_rev_cols = ['Revenue_from_Operations_Lakhs', 'Revenue_Recognised_Lakhs', 'Revenue']
    found_col = next((c for c in possible_rev_cols if c in df_sales.columns), None)
    
    if found_col:
        df_sales['Display_Revenue'] = df_sales[found_col]
    else:
        # Fallback merge if column is missing from sales file
        df_sales = df_sales.merge(df_fin[['Period', 'Revenue_from_Operations_Lakhs']], on='Period', how='left')
        df_sales['Display_Revenue'] = df_sales['Revenue_from_Operations_Lakhs']

    # Process Segments
    df_segments = data['segments'].copy()
    df_segments['Period'] = df_segments['Period'].map(period_map)
    df_segments['Segment'] = df_segments['Segment'].replace({"Luxe-Series": "Luxe"})
    
    # Process Marketing
    df_marketing = data['marketing'].copy()
    df_marketing['Period'] = df_marketing['Period'].map(period_map)
    
    # Process Projects
    df_projects = data['portfolio'][data['portfolio']['Status'] == 'Ongoing'].copy()
    project_rev_h1_26 = {
        "Green Heights": 2916, "Maybell": 1114, "Green Fort": 1141, 
        "Green Capitol": 2587, "Queens Park": 567, "Casabella": 1388, 
        "Symphony": 1661, "Flora": 49, "Elanza": 654
    }
    df_projects['Rev_H1FY26'] = df_projects['Project_Name'].map(project_rev_h1_26).fillna(0)
    
    return df_fin, df_sales, df_segments, df_projects, df_marketing

df_fin, df_sales, df_segments, df_projects, df_marketing = load_data()

# ── The Fixed Chart Layout Function ───────────────────────────────────────────

def chart_layout(fig, height=360):
    """
    FIX: Direct variable usage. 
    The strings are constructed using f-strings inside the function 
    so Plotly receives a valid hex/rgba value.
    """
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=LIGHT_GOLD, size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(
            gridcolor=f"{MUTED}33",  # Correctly evaluates to #6B8C7333
            tickfont=dict(size=11),
            showgrid=True
        ),
        yaxis=dict(
            gridcolor=f"{MUTED}33",  # Correctly evaluates to #6B8C7333
            tickfont=dict(size=11),
            showgrid=True
        ),
    )
    return fig

# ── Sidebar & UI ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"<h2 style='color:{GOLD};'>🏠 Veegaland Homes</h2>", unsafe_allow_html=True)
    page = st.radio("Navigate", ["📊 Overview", "🏗 Projects", "💰 Marketing"])

# ── Page Content ──────────────────────────────────────────────────────────────

if "Overview" in page:
    st.title("Business Overview")
    
    # KPI Row
    c1, c2, c3 = st.columns(3)
    latest = df_fin.iloc[-1]
    c1.metric("Revenue (H1 FY26)", f"₹{latest['Revenue_from_Operations_Lakhs']:,.0f} L")
    c2.metric("EBITDA Margin", f"{latest['EBITDA_Margin_Pct']}%")
    c3.metric("Debt/Equity", f"{latest['Debt_Equity_Ratio']}x")

    # Grouped Bar Chart
    fig = go.Figure()
    fig.add_bar(name="Revenue Recognized", x=df_sales["Period"], y=df_sales["Display_Revenue"], marker_color=MID_GREEN)
    fig.add_bar(name="Sales Value", x=df_sales["Period"], y=df_sales["Sales_Value_Lakhs_excl_GST"], marker_color=GOLD)
    fig.update_layout(barmode='group', title="Revenue vs. Sales Bookings")
    st.plotly_chart(chart_layout(fig), use_container_width=True)

elif "Projects" in page:
    st.title("Project Pipeline")
    df_p = df_projects.sort_values("Rev_H1FY26", ascending=True)
    fig_p = px.bar(df_p, x="Rev_H1FY26", y="Project_Name", orientation='h', color_discrete_sequence=[GOLD])
    st.plotly_chart(chart_layout(fig_p), use_container_width=True)
    st.dataframe(df_projects[['Project_Name', 'City', 'Pct_Sold', 'Rev_H1FY26']], use_container_width=True)

elif "Marketing" in page:
    st.title("Marketing Spend")
    
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(df_marketing, x="Period", y="Marketing_Sales_Spend_Lakhs", title="Spend (₹ Lakhs)", color_discrete_sequence=[MID_GREEN])
        st.plotly_chart(chart_layout(fig1), use_container_width=True)
    with c2:
        fig2 = px.line(df_marketing, x="Period", y="Pct_of_Revenue", title="Spend as % of Revenue", markers=True)
        fig2.update_traces(line_color=GOLD)
        st.plotly_chart(chart_layout(fig2), use_container_width=True)
