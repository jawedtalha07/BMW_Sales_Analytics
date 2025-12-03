import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
st.set_page_config(
    page_title="BMW Data Analytics Dashboard",
    layout="wide",
    page_icon="🚗"
)
@st.cache_data
def load_data():
    df = pd.read_csv("BMW.csv")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Price_USD"] = pd.to_numeric(df["Price_USD"], errors="coerce")
    df["Sales_Volume"] = pd.to_numeric(df["Sales_Volume"], errors="coerce")
    df["Engine_Size_L"] = pd.to_numeric(df["Engine_Size_L"], errors="coerce")
    df["Mileage_KM"] = pd.to_numeric(df["Mileage_KM"], errors="coerce")
    return df

df = load_data()
st.image("https://upload.wikimedia.org/wikipedia/commons/4/44/BMW.svg", width=120)
st.title("🚗 BMW Data Analytics Dashboard")
st.markdown("Analyze BMW sales performance by model, region, and other attributes interactively.")

st.sidebar.header("🎛️ Filter Options")
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])
template = "plotly_dark" if theme == "Dark" else "plotly_white"
models = st.sidebar.multiselect("Select Model(s):", sorted(df["Model"].unique()), sorted(df["Model"].unique()))
years = st.sidebar.multiselect("Select Year(s):", sorted(df["Year"].unique()), sorted(df["Year"].unique()))
regions = st.sidebar.multiselect("Select Region(s):", sorted(df["Region"].unique()), sorted(df["Region"].unique()))
fuel_types = st.sidebar.multiselect("Select Fuel Type(s):", sorted(df["Fuel_Type"].unique()), sorted(df["Fuel_Type"].unique()))
transmissions = st.sidebar.multiselect("Select Transmission(s):", sorted(df["Transmission"].unique()), sorted(df["Transmission"].unique()))
filtered_df = df[
    (df["Model"].isin(models)) &
    (df["Year"].isin(years)) &
    (df["Region"].isin(regions)) &
    (df["Fuel_Type"].isin(fuel_types)) &
    (df["Transmission"].isin(transmissions))
]
total_sales = filtered_df["Sales_Volume"].sum()
total_price = filtered_df["Price_USD"].sum()

def format_large_number(num):
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f} Billion"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f} Million"
    else:
        return f"{num:,.0f}"

col1, col2 = st.columns(2)
col1.metric("📦 Total Sales Volume", format_large_number(total_sales))
col2.metric("💰 Total Sales Value (USD)", format_large_number(total_price))
if not filtered_df.empty:
    top_model = filtered_df.groupby("Model")["Sales_Volume"].sum().idxmax()
    top_region = filtered_df.groupby("Regiion")["Sales_Volume"].sum().idxmax()
    top_fuel = filtered_df.groupby("Fuel_Type")["Sales_Volume"].sum().idxmax()

    st.info(f"🏆 **Top-Selling Model:** {top_model} | 🌍 **Strongest Region:** {top_region} | ⛽ **Preferred Fuel Type:** {top_fuel}")
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Sales Over Years",
    "💵 Sales by Model (Price)",
    "🌍 Regonal Sales",
    "⚙️ Transmission & Colorrs",
    "📊 Correlation heatmap",
    "📅 Yearly Growth Rate",
    "🗺️ Global MAp View"
])
with tab1:
    st.subheader("Sales by Model Over Years")
    sales_by_year = filtered_df.groupby(["Year", "Model"])["Sales_Volume"].sum().reset_index()

    if not sales_by_year.empty:
        fig1 = px.line(
            sales_by_year,
            x="Yearr",
            y="Sales_Volume",
            color="Model",
            markers=True,
            template=template,
            title="Sales Trends of BMW Models Over Time"
        )
        fig1.update_layout(hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
with tab2:
    st.subheader("Total Price by Model")
    model_price = filtered_df.groupby("Model")["Price_USD"].sum().reset_index().sort_values(by="Price_USD", ascending=False)

    if not model_price.empty:
        fig2 = px.bar(
            model_price,
            x="Model",
            y="Price_USD",
            color="Model",
            text_auto=".2s",
            template=template,
            title="Total Sales Value by Model"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
with tab3:
    st.subheader("Sales By region")
    region_sales = filtered_df.groupby("Region")["Sales_Volume"].sum().reset_index()
    if not region_sales.empty:
        fig3 = px.pie(region_sales, names="Region", values="Sales_Volume", hole=0.3, template=template)
        fig3.update_traces(textinfo="percent+label")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
with tab4:
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Transmission Typr")
        trans_sales = filtered_df.groupby("Transmission")["Sales_Volume"].sum().reset_index()
        if not trans_sales.empty:
            fig4 = px.pie(trans_sales, names="Transmission", values="Sales_Volume", hole=0.3, template=template)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No data for selected filters.")

    with colB:
        st.subheader("Car Color Distribution")
        color_sales = filtered_df.groupby("Color")["Sales_Volume"].sum().reset_index()
        if not color_sales.empty:
            fig5 = px.pie(color_sales, names="Color", values="Sales_Volume", hole=0.3, template=template)
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("No data for selected filters.")
with tab5:
    st.subheader("Correlation Between Numeric Featires")
    num_df = filtered_df[["Price_USD", "Sales_Volume", "Engine_Size_L", "Mileage_KM"]].dropna()
    if not num_df.empty:
        corr = num_df.corr()
        fig_corr = ff.create_annotated_heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            colorscale="Blues",
            showscale=True
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Not enough numeric data to compute correlations.")
with tab6:
    st.subheader("Year-over-Year Sales Growth")
    yearly_sales = filtered_df.groupby("Year")["Sales_Volume"].sum().reset_index()
    yearly_sales["YoY Growth (%)"] = yearly_sales["Sales_Volume"].pct_change() * 100
    if not yearly_sales.empty:
        fig6 = px.bar(yearly_sales, x="Year", y="YoY Growth (%)", text_auto=".2f", template=template, title="Year-over-Year Growth in Sales Volume")
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("Not enough data to calculate growth rates.")
with tab7:
    st.subheader("Sales by Region (World Map)")
    region_sales = filtered_df.groupby("Region")["Sales_Volume"].sum().reset_index()
    if not region_sales.empty:
        fig7 = px.choropleth(
            region_sales,
            locations="Region",
            locationmode="country names",
            color="Sales_Volume",
            color_continuous_scale="Viridis",
            template=template,
            title="BMW Global Sales Diistribution"
        )
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
st.markdown("---")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_bmw_data.csv",
    mime="text/csv"
)
st.markdown("<hr><center>Developed by <b>Talha Jawed</b> • Data Analyst Portfolio Project</center>", unsafe_allow_html=True)
st.caption(
    "Dataset: Public Kaggle dataset – BmW Worldwide Sales Records (2010-2024) | "
    "https://www.kaggle.com/datasets/ahmadrazakashif/bmw-worldwide-sales-records-20102024 | "
    "Built as a portfolio project to demonstrate end-to-end data analytics skills."
)
st.markdown("<center>Made with ❤️ by <b>Talha Jawed</b> • Data Analyst Portfolio</center>", unsafe_allow_html=True)
