import plotly.express as px


def trend_chart(monthly_series):
    df = monthly_series.reset_index()
    df.columns = ["month", "total_amount"]
    df["month"] = df["month"].astype(str)

    fig = px.line(
        df,
        x="month",
        y="total_amount",
        markers=True,
        labels={"month": "Month", "total_amount": "Sales ($)"},
        title="Sales Trend Over Time",
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    return fig


def category_chart(category_series):
    df = category_series.reset_index()
    df.columns = ["category", "total_amount"]

    fig = px.bar(
        df,
        x="category",
        y="total_amount",
        labels={"category": "Category", "total_amount": "Sales ($)"},
        title="Sales by Category",
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    return fig


def region_chart(region_series):
    df = region_series.reset_index()
    df.columns = ["region", "total_amount"]

    fig = px.bar(
        df,
        x="region",
        y="total_amount",
        labels={"region": "Region", "total_amount": "Sales ($)"},
        title="Sales by Region",
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    return fig
