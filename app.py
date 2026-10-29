import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from trading_strategy import run_strategy

st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")


def format_date(value):
    if pd.isna(value):
        return "-"
    return pd.to_datetime(value).strftime("%Y-%m-%d")


@st.cache_data
def load_data():
    data, positions, summary = run_strategy("MSFT")
    return data, positions, summary


data, positions, summary = load_data()

page = st.sidebar.radio(
    "Navigation",
    ["Price Chart", "Trade Statistics", "Detailed Trades"],
    index=0,
)

if page == "Price Chart":
    st.title("Price Chart")
    st.caption("MSFT stock price with 50-day and 200-day moving averages")

    chart_data = data.reset_index().rename(columns={"Date": "date"})
    chart_data = chart_data.rename(columns={"index": "Date"})

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_data["Date"],
            y=chart_data["Close"],
            mode="lines",
            name="Stock Price",
            line={"color": "#1f77b4", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_data["Date"],
            y=chart_data["MA50"],
            mode="lines",
            name="MA50",
            line={"color": "#ff7f0e", "width": 1.5},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_data["Date"],
            y=chart_data["MA200"],
            mode="lines",
            name="MA200",
            line={"color": "#2ca02c", "width": 1.5},
        )
    )

    buy_points = positions[["BuyDate", "BuyPrice"]].rename(columns={"BuyDate": "Date", "BuyPrice": "Close"})
    sell_points = positions[["SellDate", "SellPrice"]].rename(columns={"SellDate": "Date", "SellPrice": "Close"})

    fig.add_trace(
        go.Scatter(
            x=buy_points["Date"],
            y=buy_points["Close"],
            mode="markers",
            marker={"symbol": "circle", "size": 12, "color": "green"},
            name="Buy Point",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sell_points["Date"],
            y=sell_points["Close"],
            mode="markers",
            marker={"symbol": "circle-open", "size": 12, "color": "red"},
            name="Sell Point",
        )
    )

    fig.update_layout(
        title="MSFT Price and Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=700,
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Trade Statistics":
    st.title("Trade Statistics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", summary["total_trades"])
    c2.metric("Winning Trades", summary["win_trades"])
    c3.metric("Losing Trades", summary["loss_trades"])
    c4.metric("Win Rate", f"{summary['win_rate']:.2f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Average Profit", f"{summary['avg_profit']:.2f}%")
    c6.metric("Average Win", f"{summary['avg_win']:.2f}%")
    c7.metric("Average Loss", f"{summary['avg_loss']:.2f}%")
    c8.metric("Average Holding Days", f"{summary['avg_holding_days']:.1f}")

    st.subheader("Trade Summary")
    summary_df = pd.DataFrame(
        [
            {"Metric": "Total Trades", "Value": summary["total_trades"]},
            {"Metric": "Winning Trades", "Value": summary["win_trades"]},
            {"Metric": "Losing Trades", "Value": summary["loss_trades"]},
            {"Metric": "Win Rate (%)", "Value": round(summary["win_rate"], 2)},
            {"Metric": "Average Profit (%)", "Value": round(summary["avg_profit"], 2)},
            {"Metric": "Average Holding Days", "Value": round(summary["avg_holding_days"], 2)},
            {"Metric": "Target Reached", "Value": summary["target_reached"]},
            {"Metric": "Max Holding Period", "Value": summary["max_period"]},
        ]
    )
    st.dataframe(summary_df, use_container_width=True)

else:
    st.title("Detailed Trades")

    trade_table = positions.copy()
    trade_table["BuyDate"] = trade_table["BuyDate"].apply(format_date)
    trade_table["SellDate"] = trade_table["SellDate"].apply(format_date)
    trade_table["ProfitPct"] = trade_table["ProfitPct"].round(4)

    st.dataframe(trade_table, use_container_width=True)
