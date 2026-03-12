"""
Veegaland Homes — Updated DRHP Analytics Dashboard
====================================================
Improvements: 
- Dynamic data loading from CSVs
- Added Marketing & Sales Spend analysis
- Fixed table sorting and segment naming bugs
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veegaland Homes · DRHP Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
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

# ── Data Loading & Cleaning ───────────────────────────────────────────────────

@st.cache_data
def load_data():
    # Load CSVs
    df_fin_raw = pd.read_csv('1_financial_kpis.csv')
    df_sales_raw = pd.read_csv('2_sales_kpis.csv')
    df_segments_raw = pd.read_csv('4_segment_revenue.csv')
    df_portfolio_raw = pd.read_csv('5_project_portfolio.csv')
    df_marketing_raw = pd.read_csv('8_marketing_spend.csv')

    # Consistent Period Mapping
    period_map = {
        "FY2023": "FY23",
        "FY2024": "FY24",
        "FY2025": "FY25",
        "H1_FY2026": "H1 FY26"
    }
    
    # Process Financials
    df_fin = df_fin_raw.copy()
    df_fin['Period'] = df_fin['Period'].map(period_map)
    
    # Process Sales
    df_sales = df_sales_raw.copy()
    df_sales['Period'] = df_sales['Period'].map(period_map)
    
    # Process Segments
    df_segments = df_segments_raw.copy()
    df_segments['Period'] = df_segments['Period'].map(period_map)
    # Standardize segment names
    df_segments['Segment'] = df_segments['Segment'].replace({"Luxe-Series": "Luxe"})
    
    # Process Marketing
    df_marketing = df_marketing_raw.copy()
    df_marketing['Period'] = df_marketing['Period'].map(period_map)
    
    # Process Projects (Ongoing Only)
    df_projects = df_portfolio_raw[df_portfolio_raw['Status'] == 'Ongoing'].copy()
    df_projects['Segment'] = df_projects['Segment'].replace({"Luxe-Series": "Luxe"})
    
    # Project H1 FY26 Revenue Mapping (from previous dashboard data)
    project_rev_h1_26 = {
        "Green Heights": 2916, "Maybell": 1114, "Green Fort": 1141, 
        "Green Capitol": 2587, "Queens Park": 567, "Casabella": 1388, 
        "Symphony": 1661, "Flora": 49, "Elanza": 654
    }
    df_projects['Rev_H1FY26'] = df_projects['Project_Name'].map(project_rev_h1_26).fillna(0)
    
    return df_fin, df_sales, df_segments, df_projects, df_marketing

df_fin, df_sales, df_segments, df_projects, df_marketing = load_data()
periods_short = ["FY23", "FY24", "FY25", "H1 FY26"]

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');
  html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; background-color: {BG}; color: {LIGHT_GOLD}; }}
  section[data-testid="stSidebar"] {{ background: {DARK_GREEN} !important; border-right: 1px solid {GOLD}33; }}
  section[data-testid="stSidebar"] * {{ color: {LIGHT_GOLD} !important; }}
  .kpi-card {{ background: {DARK_GREEN}; border: 1px solid {GOLD}44; border-left: 4px solid {GOLD}; border-radius: 8px; padding: 18px 20px; margin-bottom: 4px; }}
  .kpi-label {{ font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: {MUTED}; margin-bottom: 4px; }}
  .kpi-value {{ font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700; color: {GOLD}; line-height: 1.1; }}
  .kpi-sub {{ font-size: 12px; color: {MUTED}; margin-top: 4px; }}
  .kpi-up   {{ color: #4CAF50; }}
  .kpi-down {{ color: {RED}; }}
  .section-title {{ font-family: 'Playfair Display', serif; font-size: 22px; color: {GOLD}; border-bottom: 1px solid {GOLD}44; padding-bottom: 8px; margin: 28px 0 16px 0; }}
  .insight {{ background: {MID_GREEN}55; border-left: 4px solid {GOLD}; border-radius: 4px; padding: 12px 16px; font-size: 14px; color: {LIGHT_GOLD}; margin: 12px 0; }}
  .page-header {{ background: linear-gradient(135deg, {DARK_GREEN}, {MID_GREEN}99); border: 1px solid {GOLD}33; border-radius: 10px; padding: 24px 30px; margin-bottom: 28px; }}
  .page-header h1 {{ font-family: 'Playfair Display', serif; font-size: 30px; color: {GOLD}; margin: 0; }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem; }}
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def kpi(label, value, sub="", trend=""):
    trend_class = "kpi-up" if trend == "up" else "kpi-down" if trend == "down" else "kpi-sub"
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="{trend_class}">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def chart_layout(fig, height=360):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=f"{DARK_GREEN}33",
        font=dict(family="DM Sans", color=LIGHT_GOLD, size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor=f"{MUTED}22", tickfont=dict(size=11)),
        yaxis=dict(gridcolor=f"{MUTED}22", tickfont=dict(size=11)),
    )
    return fig

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 24px 0; border-bottom: 1px solid {GOLD}44; margin-bottom:20px;">
      <div style="font-family:'Playfair Display',serif; font-size:20px; color:{GOLD};">🏠 Veegaland Homes</div>
      <div style="font-size:11px; color:{MUTED}; margin-top:4px; letter-spacing:1px;">DRHP ANALYTICS · UPDATED</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", ["📊 Overview", "🏗 Project Pipeline", "💰 Sales & Revenue"], label_visibility="collapsed")

# ── Logic ─────────────────────────────────────────────────────────────────────

if "Overview" in page:
    st.markdown('<div class="page-header"><h1>Business Overview</h1><p>Kerala\'s residential leader · ₹250 Cr IPO · FY23 – H1 FY26 Performance</p></div>', unsafe_allow_html=True)
    
    # Metrics for KPI Row
    fy25_rev = df_fin[df_fin['Period'] == 'FY25']['Revenue_from_Operations_Lakhs'].values[0]
    fy24_rev = df_fin[df_fin['Period'] == 'FY24']['Revenue_from_Operations_Lakhs'].values[0]
    rev_growth = ((fy25_rev/fy24_rev) - 1) * 100

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("FY25 Revenue", f"₹{fy25_rev/100:.1f} Cr", f"▲ {rev_growth:.0f}% YoY", "up")
    with c2: kpi("FY25 Sales", "₹342 Cr", "▲ 81% YoY", "up")
    with c3: kpi("FY25 PAT Margin", "10.4%", "Benchmark: 10%+", "up")
    with c4: kpi("Avg Price/sqft", "₹7,598", "H1 FY26 Peak", "up")
    with c5: kpi("Portfolio Sold", "73.6%", "Ongoing Area")
    with c6: kpi("Debt / Equity", "0.19×", "▼ De-leveraged", "up")

    st.markdown('<div class="section-title">Revenue · Bookings · Collections Gap</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight"><strong>Insight:</strong> Bookings (Sales Value) lead Revenue recognition by 12-18 months. The growing gap represents a healthy pipeline of locked-in future revenue.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = go.Figure()
        fig.add_bar(name="Revenue", x=df_sales["Period"], y=df_sales["Revenue_from_Operations_Lakhs" if "Revenue_from_Operations_Lakhs" in df_sales else "Revenue"], marker_color=MID_GREEN)
        fig.add_bar(name="Sales (Bookings)", x=df_sales["Period"], y=df_sales["Sales_Value_Lakhs_excl_GST"], marker_color=GOLD)
        fig.add_bar(name="Collections", x=df_sales["Period"], y=df_sales["Gross_Collections_Lakhs_excl_GST"], marker_color=BLUE)
        fig.update_layout(barmode="group", title="Revenue Metrics (₹ Lakhs)")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_scatter(x=df_fin["Period"], y=df_fin["EBITDA_Margin_Pct"], name="EBITDA %", line=dict(color=GOLD, width=3))
        fig2.add_scatter(x=df_fin["Period"], y=df_fin["PAT_Margin_Pct"], name="PAT %", line=dict(color=MID_GREEN, dash="dot"))
        fig2.update_layout(title="Margin Trends", yaxis_ticksuffix="%")
        st.plotly_chart(chart_layout(fig2), use_container_width=True)

elif "Pipeline" in page:
    st.markdown('<div class="page-header"><h1>Project Pipeline</h1><p>Status of 9 ongoing projects across Kerala</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 3])
    with col1:
        df_sorted = df_projects.sort_values("Pct_Sold", ascending=True)
        fig = px.bar(df_sorted, y="Project_Name", x="Pct_Sold", orientation='h', color="Pct_Sold", 
                     color_continuous_scale=[RED, GOLD, MID_GREEN], title="Absorption % by Project")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    with col2:
        # Table Fix: Sort before formatting
        df_display = df_projects[["Project_Name","City","Segment","Saleable_Area_SqFt","Pct_Sold","Rev_H1FY26"]].copy()
        df_display = df_display.sort_values("Rev_H1FY26", ascending=False) # FIX: Numeric sort
        
        # Now format for display
        df_display["Saleable_Area_SqFt"] = df_display["Saleable_Area_SqFt"].apply(lambda x: f"{x:,}")
        df_display["Pct_Sold"] = df_display["Pct_Sold"].apply(lambda x: f"{x:.1f}%")
        df_display["Rev_H1FY26"] = df_display["Rev_H1FY26"].apply(lambda x: f"₹{x:,} L")
        
        st.markdown('<div class="section-title">Project Details (H1 FY26 Contribution)</div>', unsafe_allow_html=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

elif "Sales" in page:
    st.markdown('<div class="page-header"><h1>Sales & Marketing</h1><p>Growth trajectory and Marketing Efficiency</p></div>', unsafe_allow_html=True)
    
    # NEW: Marketing Spend Section
    st.markdown('<div class="section-title">Marketing & Sales Efficiency</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight"><strong>Marketing ROI:</strong> Spend peaked in FY24 (7.96% of revenue) during major project launches and has since stabilized as brand awareness grew.</div>', unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        fig_m1 = go.Figure()
        fig_m1.add_bar(x=df_marketing["Period"], y=df_marketing["Marketing_Sales_Spend_Lakhs"], 
                       marker_color=GOLD, text=df_marketing["Marketing_Sales_Spend_Lakhs"].apply(lambda x: f"₹{x:.0f}L"),
                       textposition='outside', name="Marketing Spend")
        fig_m1.update_layout(title="Marketing Spend (₹ Lakhs)")
        st.plotly_chart(chart_layout(fig_m1), use_container_width=True)
    
    with m2:
        fig_m2 = go.Figure()
        fig_m2.add_scatter(x=df_marketing["Period"], y=df_marketing["Pct_of_Revenue"], 
                           line=dict(color=RED, width=4), marker=dict(size=10), name="% of Revenue")
        fig_m2.update_layout(title="Marketing Spend as % of Revenue", yaxis_ticksuffix="%")
        st.plotly_chart(chart_layout(fig_m2), use_container_width=True)

    # Segment Evolution
    st.markdown('<div class="section-title">Segment Mix Evolution</div>', unsafe_allow_html=True)
    seg_colors = {"Mid-Premium": BLUE, "Premium": MID_GREEN, "Ultra-Premium": GOLD, "Luxe": "#9C27B0"}
    
    c1, c2 = st.columns([3, 2])
    with c1:
        fig_seg = px.bar(df_segments, x="Period", y="Revenue_Lakhs", color="Segment", 
                         color_discrete_map=seg_colors, title="Revenue by Segment")
        st.plotly_chart(chart_layout(fig_seg), use_container_width=True)
    with c2:
        df_h1 = df_segments[df_segments["Period"] == "H1 FY26"]
        fig_pie = px.pie(df_h1, values="Revenue_Lakhs", names="Segment", 
                         color="Segment", color_discrete_map=seg_colors, hole=0.5, title="H1 FY26 Segment Split")
        st.plotly_chart(chart_layout(fig_pie), use_container_width=True)
