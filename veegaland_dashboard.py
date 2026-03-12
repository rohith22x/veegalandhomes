"""
Veegaland Homes — Data Analyst Interview Dashboard
====================================================
Run with:  streamlit run veegaland_dashboard.py
Requires:  pip install streamlit plotly pandas
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

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {BG};
    color: {LIGHT_GOLD};
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background: {DARK_GREEN} !important;
    border-right: 1px solid {GOLD}33;
  }}
  section[data-testid="stSidebar"] * {{ color: {LIGHT_GOLD} !important; }}
  section[data-testid="stSidebar"] .stRadio label {{
    font-size: 15px;
    padding: 6px 0;
    letter-spacing: 0.4px;
  }}

  /* KPI card */
  .kpi-card {{
    background: {DARK_GREEN};
    border: 1px solid {GOLD}44;
    border-left: 4px solid {GOLD};
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 4px;
  }}
  .kpi-label {{
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 4px;
  }}
  .kpi-value {{
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: {GOLD};
    line-height: 1.1;
  }}
  .kpi-sub {{
    font-size: 12px;
    color: {MUTED};
    margin-top: 4px;
  }}
  .kpi-up   {{ color: #4CAF50; }}
  .kpi-down {{ color: {RED}; }}

  /* Section header */
  .section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    color: {GOLD};
    border-bottom: 1px solid {GOLD}44;
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
  }}

  /* Insight callout */
  .insight {{
    background: {MID_GREEN}55;
    border-left: 4px solid {GOLD};
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 14px;
    color: {LIGHT_GOLD};
    margin: 12px 0;
  }}
  .insight strong {{ color: {GOLD}; }}

  /* Page title */
  .page-header {{
    background: linear-gradient(135deg, {DARK_GREEN}, {MID_GREEN}99);
    border: 1px solid {GOLD}33;
    border-radius: 10px;
    padding: 24px 30px;
    margin-bottom: 28px;
  }}
  .page-header h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    color: {GOLD};
    margin: 0 0 6px 0;
  }}
  .page-header p {{
    font-size: 14px;
    color: {MUTED};
    margin: 0;
  }}

  /* Hide default header */
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

periods     = ["FY2023", "FY2024", "FY2025", "H1 FY26"]
periods_short = ["FY23", "FY24", "FY25", "H1 FY26"]

df_fin = pd.DataFrame({
    "Period":        periods_short,
    "Revenue":       [10891, 11077, 19238, 12416],
    "EBITDA":        [2422,  1672,  3377,  1892],
    "PAT":           [1453,  787,   2043,  1153],
    "EBITDA_Margin": [22.00, 14.59, 17.21, 15.12],
    "PAT_Margin":    [13.20, 6.87,  10.41, 9.21],
    "Gross_Margin":  [30.51, 28.83, 27.56, 27.42],
    "Net_Worth":     [3724,  4507,  6544,  25173],
    "Debt":          [12215, 12023, 17697, 4857],
    "DE_Ratio":      [3.28,  2.67,  2.70,  0.19],
    "ROE":           [48.44, 19.12, 36.96, 7.27],
    "ROCE":          [14.88, 9.85,  13.75, 6.21],
})

df_sales = pd.DataFrame({
    "Period":       periods_short,
    "Sales_Value":  [10962, 18916, 34205, 18660],
    "Collections":  [15539, 12531, 20754, 11379],
    "Revenue":      [10891, 11077, 19238, 12416],
    "Units":        [111,   169,   273,   135],
    "Avg_Price":    [6674,  6937,  7245,  7598],
    "Area_SqFt":    [164260,272668,472108,245595],
})

df_projects = pd.DataFrame({
    "Project":    ["Green Heights","Maybell","Green Fort","Green Capitol","Queens Park","Casabella","Symphony","Flora","Elanza"],
    "City":       ["Kochi","Kochi","Kochi","Trivandrum","Kochi","Kochi","Kozhikode","Kochi","Thrissur"],
    "Segment":    ["Ultra-Premium","Premium","Mid-Premium","Premium","Ultra-Premium","Premium","Ultra-Premium","Luxe","Premium"],
    "Area_SqFt":  [277907, 148860, 61272, 151778, 89639, 170852, 121800, 94039, 151354],
    "Pct_Sold":   [97.68,  100.0,  100.0,  82.84,  65.0,   65.09,  53.39,  37.77,  32.39],
    "Completion": ["Aug 2028","Dec 2027","Aug 2027","Jun 2028","Oct 2028","Jun 2029","Jul 2027","Nov 2029","Nov 2026"],
    "Rev_H1FY26": [2916, 1114, 1141, 2587, 567, 1388, 1661, 49, 654],
})

df_segments = pd.DataFrame({
    "Period":        ["FY23","FY23","FY23","FY24","FY24","FY24","FY25","FY25","FY25","H1 FY26","H1 FY26","H1 FY26","H1 FY26"],
    "Segment":       ["Mid-Premium","Premium","Ultra-Premium","Mid-Premium","Premium","Ultra-Premium","Mid-Premium","Premium","Ultra-Premium","Mid-Premium","Premium","Ultra-Premium","Luxe"],
    "Revenue":       [1927, 9309, 0, 70, 10314, 693, 911, 11044, 6957, 1141, 6081, 5144, 49],
})

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 24px 0; border-bottom: 1px solid {GOLD}44; margin-bottom:20px;">
      <div style="font-family:'Playfair Display',serif; font-size:20px; color:{GOLD};">🏠 Veegaland Homes</div>
      <div style="font-size:11px; color:{MUTED}; margin-top:4px; letter-spacing:1px;">DRHP ANALYTICS · DEC 2025</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["📊  Overview", "🏗  Project Pipeline", "💰  Sales & Revenue"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:11px; color:{MUTED}; border-top:1px solid {GOLD}22; padding-top:16px;">
      <div style="margin-bottom:6px; color:{GOLD}; font-size:12px; letter-spacing:1px;">DATA SOURCE</div>
      Draft Red Herring Prospectus<br>
      Filed: December 30, 2025<br>
      Periods: FY23 – H1 FY26<br>
      Projects: 23 (10+9+4)
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER: KPI card
# ══════════════════════════════════════════════════════════════════════════════

def kpi(label, value, sub="", trend=""):
    trend_html = f'<span class="kpi-{"up" if trend=="up" else "down" if trend=="down" else ""}">{sub}</span>' if trend else f'<span class="kpi-sub">{sub}</span>'
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {trend_html}
    </div>
    """, unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)

def chart_layout(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=f"{DARK_GREEN}55",
        font=dict(family="DM Sans", color=LIGHT_GOLD, size=12),
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor=f"{MUTED}33", tickfont=dict(size=11)),
        yaxis=dict(gridcolor=f"{MUTED}33", tickfont=dict(size=11)),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if "Overview" in page:

    st.markdown("""
    <div class="page-header">
      <h1>Business Overview</h1>
      <p>Kerala's fastest-growing residential developer · ₹250 Cr IPO · 23 projects across 4 cities</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("FY25 Revenue", "₹192 Cr", "▲ 73% YoY", "up")
    with c2: kpi("FY25 Sales", "₹342 Cr", "▲ 81% YoY", "up")
    with c3: kpi("FY25 PAT", "₹20.4 Cr", "10.4% margin", "up")
    with c4: kpi("Avg Price/sqft", "₹7,598", "▲ from ₹6,674 in FY23", "up")
    with c5: kpi("Portfolio Sold", "73.6%", "Ongoing projects")
    with c6: kpi("Debt / Equity", "0.19×", "▼ from 2.70× in FY25", "up")

    st.markdown('<div class="section-title">Revenue · Bookings · Collections Gap</div>', unsafe_allow_html=True)

    insight("<strong>Key Insight:</strong> Bookings (₹342 Cr FY25) far exceed recognised Revenue (₹192 Cr) — the ₹150 Cr gap is locked-in future revenue under POCM accounting. This is a leading indicator of financial health, not a problem.")

    col1, col2 = st.columns([3, 2])

    with col1:
        fig = go.Figure()
        fig.add_bar(name="Revenue Recognised", x=periods_short, y=df_sales["Revenue"],
                    marker_color=MID_GREEN, text=df_sales["Revenue"].apply(lambda x: f"₹{x/100:.0f}Cr"),
                    textposition="outside", textfont=dict(size=10))
        fig.add_bar(name="Sales (Bookings)", x=periods_short, y=df_sales["Sales_Value"],
                    marker_color=GOLD, text=df_sales["Sales_Value"].apply(lambda x: f"₹{x/100:.0f}Cr"),
                    textposition="outside", textfont=dict(size=10))
        fig.add_bar(name="Gross Collections", x=periods_short, y=df_sales["Collections"],
                    marker_color=BLUE, text=df_sales["Collections"].apply(lambda x: f"₹{x/100:.0f}Cr"),
                    textposition="outside", textfont=dict(size=10))
        fig.update_layout(barmode="group", title="₹ Lakhs · Three Revenue Metrics")
        st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_scatter(x=periods_short, y=df_fin["EBITDA_Margin"],
                         name="EBITDA Margin", mode="lines+markers",
                         line=dict(color=GOLD, width=3), marker=dict(size=8))
        fig2.add_scatter(x=periods_short, y=df_fin["PAT_Margin"],
                         name="PAT Margin", mode="lines+markers",
                         line=dict(color=MID_GREEN, width=3, dash="dot"), marker=dict(size=8))
        fig2.add_scatter(x=periods_short, y=df_fin["Gross_Margin"],
                         name="Gross Margin", mode="lines+markers",
                         line=dict(color=BLUE, width=3, dash="dash"), marker=dict(size=8))
        fig2.update_layout(title="Margin Trends (%)", yaxis_ticksuffix="%")
        st.plotly_chart(chart_layout(fig2, 380), use_container_width=True)

    # Net worth vs debt
    st.markdown('<div class="section-title">Balance Sheet Transformation</div>', unsafe_allow_html=True)

    insight("<strong>Key Insight:</strong> Net Worth jumped from ₹65 Cr (FY25) to ₹252 Cr in H1 FY26 after promoter loans were converted to equity. Debt/Equity collapsed from 2.70× to 0.19× — the balance sheet is now very clean heading into the IPO.")

    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure()
        fig3.add_bar(name="Net Worth", x=periods_short, y=df_fin["Net_Worth"],
                     marker_color=GOLD)
        fig3.add_bar(name="Total Debt", x=periods_short, y=df_fin["Debt"],
                     marker_color=RED)
        fig3.update_layout(barmode="group", title="Net Worth vs Debt (₹ Lakhs)")
        st.plotly_chart(chart_layout(fig3, 320), use_container_width=True)

    with col4:
        fig4 = go.Figure()
        fig4.add_scatter(x=periods_short, y=df_fin["DE_Ratio"],
                         mode="lines+markers+text",
                         text=[f"{v:.2f}×" for v in df_fin["DE_Ratio"]],
                         textposition="top center",
                         line=dict(color=GOLD, width=3), marker=dict(size=10))
        fig4.update_layout(title="Debt / Equity Ratio", yaxis_title="D/E Ratio")
        st.plotly_chart(chart_layout(fig4, 320), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PROJECT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

elif "Pipeline" in page:

    st.markdown("""
    <div class="page-header">
      <h1>Project Pipeline</h1>
      <p>9 ongoing projects · 12.67 lakh sqft · 73.6% average absorption · as of Oct 31, 2025</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Ongoing Projects", "9", "12.67L sqft pipeline")
    with c2: kpi("Avg Absorption", "73.6%", "Sold of total area")
    with c3: kpi("Fully Sold", "2 projects", "Maybell + Green Fort")
    with c4: kpi("Concern Project", "Elanza", "Only 32.4% sold")

    insight("<strong>Green Heights & Maybell sold before completion</strong> — best-in-class execution. <strong>Elanza (Thrissur)</strong> at 32% is the outlier to watch — only JDA project still active, completion Nov 2026.")

    col1, col2 = st.columns([2,3])

    with col1:
        # Absorption bar chart
        df_sorted = df_projects.sort_values("Pct_Sold", ascending=True)
        colors = [
            "#4CAF50" if v >= 90 else GOLD if v >= 60 else RED
            for v in df_sorted["Pct_Sold"]
        ]
        fig = go.Figure(go.Bar(
            y=df_sorted["Project"],
            x=df_sorted["Pct_Sold"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}%" for v in df_sorted["Pct_Sold"]],
            textposition="outside",
            textfont=dict(size=11)
        ))
        fig.update_layout(
            title="Sales Absorption % (🟢>90  🟡60-90  🔴<60)",
            xaxis=dict(range=[0, 115], ticksuffix="%")
        )
        st.plotly_chart(chart_layout(fig, 400), use_container_width=True)

    with col2:
        # Scatter: Area vs Absorption
        seg_colors = {
            "Ultra-Premium": GOLD,
            "Premium": MID_GREEN,
            "Mid-Premium": BLUE,
            "Luxe": "#9C27B0"
        }
        fig2 = go.Figure()
        for seg, color in seg_colors.items():
            df_seg = df_projects[df_projects["Segment"] == seg]
            if not df_seg.empty:
                fig2.add_scatter(
                    x=df_seg["Area_SqFt"],
                    y=df_seg["Pct_Sold"],
                    mode="markers+text",
                    name=seg,
                    text=df_seg["Project"],
                    textposition="top center",
                    textfont=dict(size=9),
                    marker=dict(size=df_seg["Area_SqFt"]/5000, color=color,
                                line=dict(width=1, color="white"), opacity=0.85)
                )
        fig2.update_layout(
            title="Project Size vs Absorption (bubble = area)",
            xaxis_title="Saleable Area (sqft)",
            yaxis_title="% Sold",
            yaxis=dict(ticksuffix="%", range=[0, 115])
        )
        st.plotly_chart(chart_layout(fig2, 400), use_container_width=True)

    # Detailed table
    st.markdown('<div class="section-title">Ongoing Projects — Detail</div>', unsafe_allow_html=True)

    def color_absorption(val):
        if val >= 90:   return "color: #4CAF50; font-weight:600"
        elif val >= 60: return f"color: {GOLD}; font-weight:600"
        else:           return f"color: {RED}; font-weight:600"

    df_display = df_projects[["Project","City","Segment","Area_SqFt","Pct_Sold","Completion","Rev_H1FY26"]].copy()
    df_display.columns = ["Project","City","Segment","Area (sqft)","% Sold","Completion","H1 FY26 Rev (₹L)"]
    df_display["Area (sqft)"] = df_display["Area (sqft)"].apply(lambda x: f"{x:,}")
    df_display["% Sold"] = df_display["% Sold"].apply(lambda x: f"{x:.1f}%")
    df_display["H1 FY26 Rev (₹L)"] = df_display["H1 FY26 Rev (₹L)"].apply(lambda x: f"₹{x:,}")
    df_display = df_display.sort_values("H1 FY26 Rev (₹L)", ascending=False)

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=360,
    )

    # City breakdown
    st.markdown('<div class="section-title">Portfolio by City</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        city_area = df_projects.groupby("City")["Area_SqFt"].sum().reset_index()
        fig3 = px.pie(city_area, values="Area_SqFt", names="City",
                      color_discrete_sequence=[GOLD, MID_GREEN, BLUE, MUTED],
                      hole=0.45)
        fig3.update_traces(textfont_size=12, textposition="outside")
        fig3.update_layout(title="Area by City")
        st.plotly_chart(chart_layout(fig3, 320), use_container_width=True)

    with col4:
        city_rev = df_projects.groupby("City")["Rev_H1FY26"].sum().reset_index().sort_values("Rev_H1FY26", ascending=True)
        fig4 = go.Figure(go.Bar(
            y=city_rev["City"], x=city_rev["Rev_H1FY26"],
            orientation="h", marker_color=GOLD,
            text=[f"₹{v:,}L" for v in city_rev["Rev_H1FY26"]],
            textposition="outside"
        ))
        fig4.update_layout(title="H1 FY26 Revenue by City (₹ Lakhs)")
        st.plotly_chart(chart_layout(fig4, 320), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — SALES & REVENUE
# ══════════════════════════════════════════════════════════════════════════════

elif "Sales" in page:

    st.markdown("""
    <div class="page-header">
      <h1>Sales & Revenue</h1>
      <p>Sales CAGR 76.6% (FY23–FY25) · Deliberate shift to Ultra-Premium · Pricing power intact</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("FY25 Sales Value", "₹342 Cr", "▲ 81% vs FY24", "up")
    with c2: kpi("FY25 Units Sold", "273 units", "▲ 62% vs FY24", "up")
    with c3: kpi("H1 FY26 Avg Price", "₹7,598/sqft", "▲ from ₹6,674 in FY23", "up")
    with c4: kpi("Sales CAGR FY23–25", "76.6%", "Best-in-class growth")

    col1, col2 = st.columns(2)

    with col1:
        # Units sold
        fig = go.Figure(go.Bar(
            x=periods_short, y=df_sales["Units"],
            marker_color=[MUTED, BLUE, GOLD, MID_GREEN],
            text=df_sales["Units"], textposition="outside",
            textfont=dict(size=13, color=LIGHT_GOLD)
        ))
        fig.update_layout(title="Units Sold per Period", yaxis_title="Units")
        st.plotly_chart(chart_layout(fig, 340), use_container_width=True)

    with col2:
        # Avg price trend
        fig2 = go.Figure()
        fig2.add_scatter(x=periods_short, y=df_sales["Avg_Price"],
                         mode="lines+markers+text",
                         text=[f"₹{v:,}" for v in df_sales["Avg_Price"]],
                         textposition="top center",
                         line=dict(color=GOLD, width=3),
                         marker=dict(size=10, color=GOLD),
                         fill="tozeroy", fillcolor=f"{GOLD}15")
        fig2.update_layout(title="Average Selling Price (₹/sqft)",
                           yaxis=dict(tickprefix="₹", range=[6000, 8500]))
        st.plotly_chart(chart_layout(fig2, 340), use_container_width=True)

    # Segment evolution
    st.markdown('<div class="section-title">Segment Mix Evolution</div>', unsafe_allow_html=True)
    insight("<strong>Strategic shift:</strong> In FY23, 85% of revenue was Premium. By H1 FY26, Ultra-Premium is 41% and Luxe-Series has launched. Veegaland is deliberately moving upmarket — improving margins and brand positioning.")

    col3, col4 = st.columns([3,2])

    with col3:
        seg_order = ["Mid-Premium","Premium","Ultra-Premium","Luxe"]
        seg_colors_map = {"Mid-Premium": BLUE, "Premium": MID_GREEN, "Ultra-Premium": GOLD, "Luxe": "#9C27B0"}
        fig3 = go.Figure()
        for seg in seg_order:
            df_s = df_segments[df_segments["Segment"] == seg]
            if not df_s.empty:
                fig3.add_bar(name=seg, x=df_s["Period"], y=df_s["Revenue"],
                             marker_color=seg_colors_map.get(seg, MUTED))
        fig3.update_layout(barmode="stack", title="Revenue by Segment (₹ Lakhs, Stacked)")
        st.plotly_chart(chart_layout(fig3, 360), use_container_width=True)

    with col4:
        # H1 FY26 donut
        df_h1 = df_segments[df_segments["Period"] == "H1 FY26"].copy()
        df_h1 = df_h1[df_h1["Revenue"] > 0]
        fig4 = px.pie(df_h1, values="Revenue", names="Segment",
                      color_discrete_sequence=[GOLD, MID_GREEN, BLUE, "#9C27B0"],
                      hole=0.5)
        fig4.update_traces(textfont_size=11)
        fig4.update_layout(title="H1 FY26 Segment Split")
        st.plotly_chart(chart_layout(fig4, 360), use_container_width=True)

    # Project-wise revenue H1 FY26
    st.markdown('<div class="section-title">Project-wise Revenue — H1 FY26</div>', unsafe_allow_html=True)

    df_rev = df_projects[["Project","Segment","Rev_H1FY26"]].sort_values("Rev_H1FY26", ascending=True)
    bar_colors = [seg_colors_map.get(s, MUTED) for s in df_rev["Segment"]]
    fig5 = go.Figure(go.Bar(
        y=df_rev["Project"], x=df_rev["Rev_H1FY26"],
        orientation="h", marker_color=bar_colors,
        text=[f"₹{v:,}L" for v in df_rev["Rev_H1FY26"]],
        textposition="outside"
    ))
    fig5.update_layout(title="Revenue Contribution per Project · H1 FY26 (₹ Lakhs) · Colour = Segment",
                       height=320)
    st.plotly_chart(chart_layout(fig5, 340), use_container_width=True)

    insight("<strong>Green Heights alone = ₹29 Cr</strong> in H1 FY26, more than double any other project. It is 97.7% sold and the biggest single revenue driver. Ultra-Premium projects are carrying the growth story.")
