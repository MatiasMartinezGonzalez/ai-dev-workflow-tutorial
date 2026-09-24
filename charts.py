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
