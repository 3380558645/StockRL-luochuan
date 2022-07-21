from typing import List
import pandas as pd
from pyfolio import timeseries
import pyfolio
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils.pull_data import Pull_data
from utils import config

def get_daily_return(
    df: pd.DataFrame,
    value_col_name: str = "account_value"
) -> pd.Series:
    """获取每天的涨跌值"""
    df = deepcopy(df)
    df["daily_return"] = df[value_col_name].pct_change(1)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True, drop=True)
    df.index = df.index.tz_localize("UTC")

    return pd.Series(df["daily_return"], index = df.index)

def backtest_stats(
    account_value: pd.DataFrame, 
    value_col_name: str = "account_value"
) -> pd.Series:
    """对回测数据进行分析"""
    dr_test = get_daily_return(account_value, value_col_name=value_col_name)
    perf_stats_all = timeseries.perf_stats(
        returns=dr_test,
        positions=None,
        transactions=None,
        turnover_denom="AGB"
    )
    print(perf_stats_all)

    return perf_stats_all

def backtest_plot(
    account_value: pd.DataFrame,
    baseline_start: str = config.End_Trade_Date,
    baseline_end: str = config.End_Test_Date,
    baseline_ticker: List = config.SSE_50_INDEX,
    value_col_name: str = "account_value"
) -> None:
    """对回测数据进行分析并画图"""
    df = deepcopy(account_value)
    test_returns = get_daily_return(df, value_col_name=value_col_name)

    baseline_df = get_baseline(
        ticker=baseline_ticker,
        start=baseline_start,
        end=baseline_end
    )

    baseline_returns = get_daily_return(baseline_df, value_col_name="close")
    with pyfolio.plotting.plotting_context(font_scale=1.1):
        pyfolio.create_full_tear_sheet(
            returns=test_returns,
            benchmark_rets=baseline_returns,
            set_context=False

        )

def get_baseline(
    ticker: List, start: str, end: str
    ) -> pd.DataFrame:
    """获取指数的行情数据"""
    baselines = Pull_data(
        ticker_list=ticker,
        start_date=start,
        end_date=end,
        pull_index=True
    ).pull_data()

    return baselines

def trx_plot(df_trade, df_actions, ticker_list):  #绘制对股票的具体操作行为
    df_trx = pd.DataFrame(np.array(df_actions["transactions"].to_list()))
    print(df_trx)
    df_trx.columns = ticker_list
    df_trx.index = df_actions["date"]
    df_trx.index.name = ""

    for i in range(df_trx.shape[1]):
        df_trx_temp = df_trx.iloc[:, i]
        df_trx_temp_sign = np.sign(df_trx_temp)
        buying_signal = df_trx_temp_sign.apply(lambda x: x > 0)
        selling_signal = df_trx_temp_sign.apply(lambda x: x < 0)

        tic_plot = df_trade[
            (df_trade["tic"] == df_trx_temp.name)
            & (df_trade["date"].isin(df_trx.index))
            ]["close"]
        tic_plot.index = df_trx_temp.index

        plt.figure(figsize=(10, 8))
        plt.plot(tic_plot, color="g", lw=2.0)
        plt.plot(
            tic_plot,
            "^",
            markersize=10,
            color="m",
            label="buying signal",
            markevery=buying_signal,
        )
        plt.plot(
            tic_plot,
            "v",
            markersize=10,
            color="k",
            label="selling signal",
            markevery=selling_signal,
        )
        plt.title(
            f"{df_trx_temp.name} Num Transactions: {len(buying_signal[buying_signal == True]) + len(selling_signal[selling_signal == True])}"
        )
        plt.legend()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=25))
        plt.xticks(rotation=45, ha="right")
        plt.show()


def plot(tradedata, actionsdata, ticker):
    # the first plot is the actual close price with long/short positions
    # 绘制实际的股票收盘数据
    df_plot = pd.merge(left=tradedata, right=actionsdata, on='date', how='inner')
    plot_df = df_plot.loc[df_plot['tic'] == ticker].loc[:, ['date', 'tic', 'close', ticker]].reset_index()
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.plot(plot_df.index, plot_df['close'], label=ticker)
    # 只显示时刻点，不显示折线图 => 设置 linewidth=0
    ax.plot(plot_df.loc[plot_df[ticker] > 0].index, plot_df['close'][plot_df[ticker] > 0], label='Buy', linewidth=0,
            marker='^', c='g')
    ax.plot(plot_df.loc[plot_df[ticker] < 0].index, plot_df['close'][plot_df[ticker] < 0], label='Sell', linewidth=0,
            marker='v', c='r')

    plt.legend(loc='best')
    plt.grid(True)
    plt.title(ticker + '__' + plot_df['date'].min() + '___' + plot_df['date'].max())
    plt.show()
    print(plot_df.loc[df_plot[ticker] > 0])