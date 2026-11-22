import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="E-Commerce 360 | Analytics",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PROFESSIONAL LIGHT THEME
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"],
[data-testid="stSidebar"], button, input, textarea, select {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #F5F7FA !important;
    color: #172033 !important;
}

.block-container {
    max-width: 1500px !important;
    padding: 2rem 2rem 3rem !important;
}

/* Main title */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 36px !important;
    font-weight: 700 !important;
    letter-spacing: -1px !important;
    line-height: 1.2 !important;
    color: #172033 !important;
}

/* Section titles */
h2 {
    font-size: 28px !important;
    font-weight: 650 !important;
    letter-spacing: -0.6px !important;
    color: #172033 !important;
    line-height: 1.3 !important;
}

h3 {
    font-size: 19px !important;
    font-weight: 600 !important;
    letter-spacing: -0.2px !important;
    color: #263449 !important;
}

/* Body text */
p, li, label {
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 1.65 !important;
    color: #64748B !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5EAF1 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #172033 !important;
    font-weight: 650 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #64748B !important;
}

/* Sidebar dropdown */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 1px solid #D8E1EC !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #263449 !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E5EAF1 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.035) !important;
}

[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] {
    color: #172033 !important;
    font-size: 26px !important;
    font-weight: 650 !important;
    letter-spacing: -0.5px !important;
}

/* Charts */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF !important;
    border: 1px solid #E5EAF1 !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

/* Subtitle */
.dashboard-subtitle {
    font-size: 14px !important;
    color: #64748B !important;
    font-weight: 400 !important;
}

/* Dividers */
hr {
    border-color: #E5EAF1 !important;
}

/* Footer */
.dashboard-footer {
    color: #64748B !important;
    font-size: 12px !important;
    line-height: 1.7 !important;
    text-align: center !important;
    padding-top: 24px !important;
    margin-top: 30px !important;
    border-top: 1px solid #E5EAF1 !important;
}

/* Spacing */
[data-testid="stVerticalBlock"] {
    gap: 1rem !important;
}

/* Responsive */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }

    h1 {
        font-size: 29px !important;
    }

    h2 {
        font-size: 24px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 22px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA LOADING
# =========================================================
DATA_DIR = Path(__file__).parent / "powerbi" / "data"

@st.cache_data
def load_data():
    files = {
        "sales": "sales_analytics.csv",
        "customers": "customer_analytics.csv",
        "products": "product_analytics.csv",
        "payments": "payment_analytics.csv",
        "reviews": "reviews_analytics.csv",
        "delivery": "delivery_analytics.csv",
        "seasonal": "seasonal_analytics_fixed.csv",
    }

    result = {}

    for key, filename in files.items():
        filepath = DATA_DIR / filename

        if not filepath.exists():
            st.error(f"Missing file: {filename}")
            return None

        result[key] = pd.read_csv(filepath)

    return result


data = load_data()

if data is None:
    st.stop()

sales = data["sales"].copy()
customers = data["customers"].copy()
products = data["products"].copy()
payments = data["payments"].copy()
reviews = data["reviews"].copy()
delivery = data["delivery"].copy()
seasonal = data["seasonal"].copy()

# =========================================================
# DATA PREPARATION
# =========================================================
for df in [sales, seasonal]:
    for column in ["purchase_year", "purchase_month"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

if "purchase_date" in sales.columns:
    sales["purchase_date"] = pd.to_datetime(
        sales["purchase_date"], errors="coerce"
    )

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def numeric(df, column):
    if column not in df.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(df[column], errors="coerce")


def safe_sum(df, column):
    return numeric(df, column).fillna(0).sum()


def safe_mean(df, column):
    return numeric(df, column).mean()


def chart_style(fig, height=420):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, sans-serif",
            color="#334155",
            size=13
        ),
        title=dict(
            font=dict(size=18, color="#172033"),
            x=0.02,
            xanchor="left"
        ),
        margin=dict(l=55, r=30, t=65, b=55),
        height=height,
        legend=dict(
            title=None,
            font=dict(
                color="#334155",
                size=12
            ),
            bgcolor="rgba(255,255,255,0)"
        ),
        hoverlabel=dict(
            bgcolor="#172033",
            font=dict(color="#FFFFFF")
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E8EEF5",
        zeroline=False,
        color="#475569",
        tickfont=dict(color="#475569", size=12),
        title_font=dict(color="#334155", size=13),
        linecolor="#E2E8F0"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E8EEF5",
        zeroline=False,
        color="#475569",
        tickfont=dict(color="#475569", size=12),
        title_font=dict(color="#334155", size=13),
        linecolor="#E2E8F0"
    )

    # Explicitly force readable text colors on all chart traces
    fig.update_traces(
        textfont=dict(color="#FFFFFF"),
        
    )

    return fig


def show_chart(fig, height=420):
    st.plotly_chart(
        chart_style(fig, height),
        width='stretch'
    )


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## E-Commerce 360")
st.sidebar.markdown("Sales Intelligence")
st.sidebar.markdown("---")
st.sidebar.markdown("### Dashboard Filters")

years = []

if "purchase_year" in sales.columns:
    years = sorted(
        sales["purchase_year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + years
)

st.sidebar.caption(
    "Select a year to filter sales and seasonal analytics."
)

# =========================================================
# FILTER DATA
# =========================================================
filtered_sales = sales.copy()
filtered_seasonal = seasonal.copy()

if selected_year != "All":

    filtered_sales = filtered_sales[
        filtered_sales["purchase_year"] == selected_year
    ]

    if "purchase_year" in filtered_seasonal.columns:
        filtered_seasonal = filtered_seasonal[
            filtered_seasonal["purchase_year"] == selected_year
        ]

# =========================================================
# HEADER
# =========================================================
st.title("E-Commerce 360")

st.markdown(
    '<div class="dashboard-subtitle">'
    'Customer Behaviour & Sales Intelligence Platform'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Brazilian e-commerce data | Sales, customers, products and operations"
)

st.markdown("---")

# =========================================================
# KPI METRICS
# =========================================================
total_revenue = safe_sum(filtered_sales, "total_revenue")

total_orders = (
    filtered_sales["order_id"].nunique()
    if "order_id" in filtered_sales.columns
    else len(filtered_sales)
)

total_items = safe_sum(filtered_sales, "total_items")

if total_items == 0:
    total_items = safe_sum(filtered_sales, "total_items_sold")

average_order_value = (
    total_revenue / total_orders
    if total_orders else 0
)

delivery_rate = 0

if not delivery.empty and "delivery_performance" in delivery.columns:

    on_time_data = delivery[
        delivery["delivery_performance"]
        .astype(str)
        .str.contains("on time", case=False, na=False)
    ]

    on_time_orders = safe_sum(on_time_data, "total_orders")
    all_delivery_orders = safe_sum(delivery, "total_orders")

    if all_delivery_orders:
        delivery_rate = (
            on_time_orders / all_delivery_orders * 100
        )

average_review = 0

if not reviews.empty and "review_score" in reviews.columns:

    review_scores = numeric(reviews, "review_score")
    weights = numeric(reviews, "total_reviews")

    if weights.notna().any() and weights.sum():
        average_review = (
            (review_scores.fillna(0) * weights.fillna(0)).sum()
            / weights.sum()
        )
    else:
        average_review = review_scores.mean()

# KPI ROW 1
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
k2.metric("Total Orders", f"{total_orders:,}")
k3.metric("Items Sold", f"{total_items:,.0f}")
k4.metric("Average Order Value", f"R$ {average_order_value:,.2f}")

# KPI ROW 2
k5, k6 = st.columns(2)

k5.metric("On-Time Delivery", f"{delivery_rate:.2f}%")
k6.metric("Average Review Score", f"{average_review:.2f} / 5")

st.markdown("---")

# =========================================================
# SALES PERFORMANCE
# =========================================================
st.header("Sales Performance")

st.caption(
    "Revenue trends and order status overview."
)

# MONTHLY SALES
if {
    "purchase_year",
    "purchase_month",
    "total_revenue"
}.issubset(filtered_sales.columns):

    monthly = (
        filtered_sales
        .groupby(
            ["purchase_year", "purchase_month"],
            as_index=False
        )["total_revenue"]
        .sum()
    )

    monthly["month_date"] = pd.to_datetime(
        monthly["purchase_year"].astype(int).astype(str)
        + "-"
        + monthly["purchase_month"].astype(int).astype(str)
        + "-01"
    )

    monthly = monthly.sort_values("month_date")

    fig = px.line(
        monthly,
        x="month_date",
        y="total_revenue",
        markers=True
    )

    fig.update_traces(
        line=dict(color="#2563EB", width=3),
        marker=dict(color="#2563EB", size=7),
        hovertemplate=(
            "<b>%{x|%B %Y}</b><br>"
            "Revenue: R$ %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_xaxes(
        title="Month",
        tickformat="%b %Y",
        tickangle=-35
    )

    fig.update_yaxes(
        title="Revenue (BRL)",
        tickprefix="R$ ",
        tickformat=",.0f"
    )

    show_chart(fig, 400)

# ORDER STATUS + YEARLY REVENUE
col1, col2 = st.columns(2, gap="large")

with col1:

    if "order_status" in filtered_sales.columns:

        status_data = (
            filtered_sales["order_status"]
            .value_counts()
            .reset_index()
        )

        status_data.columns = ["order_status", "orders"]

        fig = px.pie(
            status_data,
            names="order_status",
            values="orders",
            hole=0.62
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(
                line=dict(color="white", width=2)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Orders: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            legend=dict(orientation="h", y=-0.12)
        )

        show_chart(fig, 400)

with col2:

    if {
        "purchase_year",
        "total_revenue",
        "order_id"
    }.issubset(filtered_sales.columns):

        yearly = (
            filtered_sales
            .groupby("purchase_year", as_index=False)
            .agg(
                revenue=("total_revenue", "sum"),
                orders=("order_id", "nunique")
            )
        )

        yearly["purchase_year"] = (
            yearly["purchase_year"].astype(int).astype(str)
        )

        fig = px.bar(
            yearly,
            x="purchase_year",
            y="revenue"
        )

        fig.update_traces(
            marker_color="#2563EB",
            hovertemplate=(
                "<b>Year %{x}</b><br>"
                "Revenue: R$ %{y:,.2f}"
                "<extra></extra>"
            )
        )

        fig.update_xaxes(
            title="Year",
            type="category"
        )

        fig.update_yaxes(
            title="Revenue (BRL)",
            tickprefix="R$ ",
            tickformat=",.0s"
        )

        show_chart(fig, 400)

# =========================================================
# CUSTOMER ANALYTICS
# =========================================================
st.markdown("---")
st.header("Customer Analytics")

st.caption(
    "Customer segments, spending patterns and geographic contribution."
)

col1, col2 = st.columns(2, gap="large")

# SEGMENTATION
with col1:

    if "customer_segment" in customers.columns:

        segment_data = (
            customers["customer_segment"]
            .value_counts()
            .reset_index()
        )

        segment_data.columns = ["segment", "customers"]

        fig = px.pie(
            segment_data,
            names="segment",
            values="customers",
            hole=0.62
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(
                line=dict(color="white", width=2)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Customers: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            legend=dict(orientation="h", y=-0.12)
        )

        show_chart(fig, 400)

# SPENDING DISTRIBUTION
with col2:

    if "total_spending" in customers.columns:

        spending = customers.copy()

        spending["total_spending"] = numeric(
            spending, "total_spending"
        )

        spending = spending.dropna(
            subset=["total_spending"]
        )

        fig = px.histogram(
            spending,
            x="total_spending",
            nbins=40
        )

        fig.update_traces(
            marker_color="#0D9488",
            marker_line_color="white",
            marker_line_width=0.5,
            hovertemplate=(
                "Spending: R$ %{x:,.2f}<br>"
                "Customers: %{y:,}"
                "<extra></extra>"
            )
        )

        fig.update_xaxes(
            title="Customer Spending (BRL)",
            tickprefix="R$ ",
            tickformat=",.0f"
        )

        fig.update_yaxes(
            title="Number of Customers"
        )

        show_chart(fig, 400)

# STATES
if {
    "customer_state",
    "total_spending"
}.issubset(customers.columns):

    state_data = (
        customers
        .groupby("customer_state", as_index=False)
        ["total_spending"]
        .sum()
        .sort_values(
            "total_spending",
            ascending=False
        )
        .head(15)
        .sort_values(
            "total_spending",
            ascending=True
        )
    )

    fig = px.bar(
        state_data,
        x="total_spending",
        y="customer_state",
        orientation="h"
    )

    fig.update_traces(
        marker_color="#2563EB",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Spending: R$ %{x:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_yaxes(title="")

    fig.update_xaxes(
        title="Customer Spending (BRL)",
        tickprefix="R$ ",
        tickformat=",.0s"
    )

    show_chart(fig, 520)

st.caption(
    "Customer analytics use the customer identifier available in the Gold dataset. "
    "They should not be interpreted as verified unique repeat-customer behaviour."
)

# =========================================================
# PRODUCT ANALYTICS
# =========================================================
st.markdown("---")
st.header("Product Analytics")

st.caption(
    "Category revenue, product volume and average pricing."
)

category_col = "product_category_name_english"

if category_col not in products.columns:
    category_col = "product_category_name"

# CATEGORY REVENUE
if (
    category_col in products.columns
    and "total_revenue" in products.columns
):

    category_revenue = (
        products
        .groupby(category_col, as_index=False)
        ["total_revenue"]
        .sum()
        .sort_values(
            "total_revenue",
            ascending=False
        )
        .head(15)
        .sort_values(
            "total_revenue",
            ascending=True
        )
    )

    fig = px.bar(
        category_revenue,
        x="total_revenue",
        y=category_col,
        orientation="h"
    )

    fig.update_traces(
        marker_color="#2563EB",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Revenue: R$ %{x:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_yaxes(title="")

    fig.update_xaxes(
        title="Revenue (BRL)",
        tickprefix="R$ ",
        tickformat=",.0s"
    )

    show_chart(fig, 600)

# ITEMS + PRICE
col1, col2 = st.columns(2, gap="large")

with col1:

    if (
        category_col in products.columns
        and "total_items_sold" in products.columns
    ):

        top_items = (
            products
            .groupby(category_col, as_index=False)
            ["total_items_sold"]
            .sum()
            .sort_values(
                "total_items_sold",
                ascending=False
            )
            .head(10)
            .sort_values(
                "total_items_sold",
                ascending=True
            )
        )

        fig = px.bar(
            top_items,
            x="total_items_sold",
            y=category_col,
            orientation="h"
        )

        fig.update_traces(
            marker_color="#0D9488",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Items Sold: %{x:,.0f}"
                "<extra></extra>"
            )
        )

        fig.update_yaxes(title="")

        fig.update_xaxes(
            title="Items Sold",
            tickformat=","
        )

        show_chart(fig, 470)

with col2:

    if (
        category_col in products.columns
        and "average_price" in products.columns
    ):

        price_data = (
            products
            .groupby(category_col, as_index=False)
            ["average_price"]
            .mean()
            .sort_values(
                "average_price",
                ascending=False
            )
            .head(10)
            .sort_values(
                "average_price",
                ascending=True
            )
        )

        fig = px.bar(
            price_data,
            x="average_price",
            y=category_col,
            orientation="h"
        )

        fig.update_traces(
            marker_color="#D97706",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Average Price: R$ %{x:,.2f}"
                "<extra></extra>"
            )
        )

        fig.update_yaxes(title="")

        fig.update_xaxes(
            title="Average Price (BRL)",
            tickprefix="R$ ",
            tickformat=",.0f"
        )

        show_chart(fig, 470)

# =========================================================
# PAYMENT ANALYTICS
# =========================================================
st.markdown("---")
st.header("Payment Analytics")

st.caption(
    "Payment method contribution by value and transaction volume."
)

if "payment_type" in payments.columns:

    col1, col2 = st.columns(2, gap="large")

    with col1:

        if "total_payment_value" in payments.columns:

            payment_value = payments.sort_values(
                "total_payment_value",
                ascending=False
            )

            fig = px.pie(
                payment_value,
                names="payment_type",
                values="total_payment_value",
                hole=0.62
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                marker=dict(
                    line=dict(color="white", width=2)
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Value: R$ %{value:,.2f}<br>"
                    "Share: %{percent}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                legend=dict(orientation="h", y=-0.12)
            )

            show_chart(fig, 400)

    with col2:

        if "total_orders" in payments.columns:

            payment_orders = payments.sort_values(
                "total_orders",
                ascending=True
            )

            fig = px.bar(
                payment_orders,
                x="total_orders",
                y="payment_type",
                orientation="h"
            )

            fig.update_traces(
                marker_color="#2563EB",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Orders: %{x:,}"
                    "<extra></extra>"
                )
            )

            fig.update_yaxes(title="")

            fig.update_xaxes(
                title="Number of Orders",
                tickformat=","
            )

            show_chart(fig, 400)

# =========================================================
# REVIEW ANALYTICS
# =========================================================
st.markdown("---")
st.header("Customer Reviews")

st.caption(
    "Customer feedback distribution and overall review performance."
)

if {
    "review_score",
    "total_reviews"
}.issubset(reviews.columns):

    review_data = reviews.copy()

    review_data["review_score"] = numeric(
        review_data, "review_score"
    )

    review_data["total_reviews"] = numeric(
        review_data, "total_reviews"
    )

    review_data = review_data.dropna(
        subset=["review_score", "total_reviews"]
    )

    total_reviews = review_data["total_reviews"].sum()

    average_rating = (
        (
            review_data["review_score"]
            * review_data["total_reviews"]
        ).sum() / total_reviews
        if total_reviews else 0
    )

    positive_reviews = review_data.loc[
        review_data["review_score"] >= 4,
        "total_reviews"
    ].sum()

    positive_percentage = (
        positive_reviews / total_reviews * 100
        if total_reviews else 0
    )

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Total Reviews",
        f"{total_reviews:,.0f}"
    )

    r2.metric(
        "Average Rating",
        f"{average_rating:.2f} / 5"
    )

    r3.metric(
        "4–5 Star Reviews",
        f"{positive_percentage:.1f}%"
    )

    review_data = review_data.sort_values(
        "review_score"
    )

    fig = px.bar(
        review_data,
        x="review_score",
        y="total_reviews"
    )

    fig.update_traces(
        marker_color="#D97706",
        texttemplate="%{y:,}",
        textposition="outside",
        hovertemplate=(
            "<b>%{x} Stars</b><br>"
            "Reviews: %{y:,}"
            "<extra></extra>"
        )
    )

    fig.update_xaxes(
        title="Review Score",
        tickmode="linear",
        dtick=1
    )

    fig.update_yaxes(
        title="Number of Reviews",
        tickformat=","
    )

    show_chart(fig, 430)

else:
    st.warning("Review analytics data unavailable.")

# =========================================================
# DELIVERY ANALYTICS
# =========================================================
st.markdown("---")
st.header("Delivery Performance")

st.caption(
    "Delivery outcomes and average delivery duration."
)

if {
    "delivery_performance",
    "total_orders"
}.issubset(delivery.columns):

    delivery_data = delivery.copy()

    delivery_data["total_orders"] = numeric(
        delivery_data, "total_orders"
    )

    delivery_data = delivery_data.dropna(
        subset=[
            "delivery_performance",
            "total_orders"
        ]
    )

    total_deliveries = delivery_data["total_orders"].sum()

    on_time_orders = delivery_data.loc[
        delivery_data["delivery_performance"] == "On Time",
        "total_orders"
    ].sum()

    late_orders = delivery_data.loc[
        delivery_data["delivery_performance"] == "Late",
        "total_orders"
    ].sum()

    on_time_percentage = (
        on_time_orders / total_deliveries * 100
        if total_deliveries else 0
    )

    d1, d2, d3, d4 = st.columns(4)

    d1.metric(
        "Total Deliveries",
        f"{total_deliveries:,.0f}"
    )

    d2.metric(
        "On-Time Deliveries",
        f"{on_time_orders:,.0f}"
    )

    d3.metric(
        "Late Deliveries",
        f"{late_orders:,.0f}"
    )

    d4.metric(
        "On-Time Rate",
        f"{on_time_percentage:.2f}%"
    )

    st.caption(
        "Delivery metrics represent the complete dataset "
        "and are not affected by the selected year filter."
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:

        fig = px.pie(
            delivery_data,
            names="delivery_performance",
            values="total_orders",
            hole=0.62
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(
                line=dict(color="white", width=2)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Orders: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            legend=dict(orientation="h", y=-0.12)
        )

        show_chart(fig, 400)

    with col2:

        comparison = delivery_data.sort_values(
            "total_orders",
            ascending=True
        )

        fig = px.bar(
            comparison,
            x="total_orders",
            y="delivery_performance",
            orientation="h"
        )

        fig.update_traces(
            marker_color="#2563EB",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Orders: %{x:,}"
                "<extra></extra>"
            )
        )

        fig.update_yaxes(title="")

        fig.update_xaxes(
            title="Number of Orders",
            tickformat=","
        )

        show_chart(fig, 400)

    # DELIVERY TIME
    if "average_delivery_days" in delivery_data.columns:

        delivery_data["average_delivery_days"] = numeric(
            delivery_data,
            "average_delivery_days"
        )

        fig = px.bar(
            delivery_data,
            x="delivery_performance",
            y="average_delivery_days"
        )

        fig.update_traces(
            marker_color="#0D9488",
            texttemplate="%{y:.2f} days",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Delivery: %{y:.2f} days"
                "<extra></extra>"
            )
        )

        fig.update_xaxes(
            title="Delivery Status"
        )

        fig.update_yaxes(
            title="Average Delivery Days"
        )

        show_chart(fig, 380)

else:
    st.warning("Delivery analytics data unavailable.")

# =========================================================
# SEASONAL ANALYTICS
# =========================================================
st.markdown("---")
st.header("Seasonal & Weather Analytics")

st.caption(
    "Monthly revenue patterns alongside temperature and holiday indicators."
)

if {
    "purchase_year",
    "purchase_month",
    "total_revenue"
}.issubset(filtered_seasonal.columns):

    seasonal_data = filtered_seasonal.copy()

    seasonal_data["month_date"] = pd.to_datetime(
        seasonal_data["purchase_year"].astype(int).astype(str)
        + "-"
        + seasonal_data["purchase_month"].astype(int).astype(str)
        + "-01"
    )

    seasonal_data = seasonal_data.sort_values(
        "month_date"
    )

    # MONTHLY REVENUE
    fig = px.line(
        seasonal_data,
        x="month_date",
        y="total_revenue",
        markers=True
    )

    fig.update_traces(
        line=dict(color="#2563EB", width=3),
        marker=dict(color="#2563EB", size=7),
        hovertemplate=(
            "<b>%{x|%B %Y}</b><br>"
            "Revenue: R$ %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_xaxes(
        title="Month",
        tickformat="%b %Y",
        tickangle=-35
    )

    fig.update_yaxes(
        title="Revenue (BRL)",
        tickprefix="R$ ",
        tickformat=",.0f"
    )

    show_chart(fig, 430)

    col1, col2 = st.columns(2, gap="large")

    # TEMPERATURE
    with col1:

        if {
            "avg_temperature",
            "total_revenue"
        }.issubset(seasonal_data.columns):

            size_column = (
                "total_orders"
                if "total_orders" in seasonal_data.columns
                else None
            )

            fig = px.scatter(
                seasonal_data,
                x="avg_temperature",
                y="total_revenue",
                size=size_column,
                hover_data=[
                    "purchase_year",
                    "purchase_month"
                ]
            )

            fig.update_traces(
                marker=dict(
                    color="#0D9488",
                    opacity=0.8,
                    line=dict(width=1, color="white")
                ),
                hovertemplate=(
                    "Temperature: %{x:.2f}°C<br>"
                    "Revenue: R$ %{y:,.2f}"
                    "<extra></extra>"
                )
            )

            fig.update_xaxes(
                title="Average Temperature (°C)"
            )

            fig.update_yaxes(
                title="Revenue (BRL)",
                tickprefix="R$ ",
                tickformat=",.0f"
            )

            show_chart(fig, 400)

    # HOLIDAYS
    with col2:

        if {
            "total_holidays",
            "total_revenue"
        }.issubset(seasonal_data.columns):

            size_column = (
                "total_orders"
                if "total_orders" in seasonal_data.columns
                else None
            )

            fig = px.scatter(
                seasonal_data,
                x="total_holidays",
                y="total_revenue",
                size=size_column,
                hover_data=[
                    "purchase_year",
                    "purchase_month"
                ]
            )

            fig.update_traces(
                marker=dict(
                    color="#D97706",
                    opacity=0.8,
                    line=dict(width=1, color="white")
                ),
                hovertemplate=(
                    "Holidays: %{x}<br>"
                    "Revenue: R$ %{y:,.2f}"
                    "<extra></extra>"
                )
            )

            fig.update_xaxes(
                title="Number of Holidays",
                tickmode="linear",
                dtick=1
            )

            fig.update_yaxes(
                title="Revenue (BRL)",
                tickprefix="R$ ",
                tickformat=",.0f"
            )

            show_chart(fig, 400)


else:
    st.warning("Seasonal analytics data unavailable.")

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="dashboard-footer">
    <strong>E-Commerce 360</strong><br>
    Customer Behaviour & Sales Intelligence Platform<br>
    Big Data Analytics Project · Data Engineering · Analytics · Visualization<br>
    Data Sources: Olist Brazilian E-Commerce Dataset |
    Open-Meteo Weather API | BrasilAPI Holidays<br>
    Revenue is reported in Brazilian Real (BRL). Weather and holiday
    relationships are exploratory correlations and do not imply causation.
</div>
""", unsafe_allow_html=True)
