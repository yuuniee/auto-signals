import time, random
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import talib
from . import dashboard_yf2, backtest


MA_COLOR = 'orange'
MA_COLOR2 = 'red'
MA_COLOR3 = 'purple'

PC_COLOR = 'grey'

STG_LIST = [['RSI', 14, 'blue'], ['AROON', 14, 'green'], ['MFI', 14, 'white'], ['WILLR', 14, 'violet'],]# ['HT_DCPERIOD', 0, 'lime']]


def normalize(df):
    # return (df - df.min())/(df.max() - df.min())
    return (df - df.mean()) / (df.std())*50
    # return np.log(df)


def style_dataframe(df):
    return df.style.set_table_styles(
        [{
            'selector': 'th',
            'props': [
                ('background-color', '#4CAF50'),
                ('color', 'white'),
                ('font-family', 'Arial, sans-serif'),
                ('font-size', '16px')
            ]
        },
        {
            'selector': 'td, th',
            'props': [
                ('border', '2px solid #4CAF50')
            ]
        }]
    )


# style
th_props = [
    ('font-size', '14px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#FF0000'),
    ('background-color', '#f7ffff')
]

td_props = [
    ('font-size', '16px'),
    ('color', '#FF0000'),
]

styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)
]


def get_indicator(df, name='MA', p1=14, p2=14):
    if name == 'MA':
        res = talib.MA(df.Close, p1)
    elif name == 'RSI':
        res = talib.RSI(df.Close, p1)
    elif name == 'AROON':
        res = (talib.AROONOSC(df.High, df.Low, p1) + 100) / 2
    elif name == 'MFI':
        res = talib.MFI(df.High, df.Low, df.Close, df.Volume, p1)
    elif name == 'WILLR':
        res = talib.WILLR(df.High, df.Low, df.Close, p1) + 100
    # elif name == 'STOCHRSI':
    #     res = talib.STOCHRSI()
    # elif name == 'HT_DCPERIOD':
    #     res = talib.HT_DCPERIOD(df.Close)
    else:
        res = talib.MA(df.Close, p1)

    return res


def page3() -> None:
    start_proc = time.time()

    todate = pd.to_datetime('now', utc=True) - timedelta(days=1)
    last_date = dashboard_yf2.load_data('BTC-USD')['Date'].iloc[-1]
    # print(todate, ' || ', last_date)
    if todate > last_date:
        print('Refresh data')
        dashboard_yf2.pre_load_data(['BTC-USD'] + dashboard_yf2.CALL_LIST)

    # ct1, _ = st.columns(2)
    # with ct1:
    #     st.title('Market Dashboard', anchor="title", help="This page shows major market indices.")
    # cm1, cm2 = st.columns(2)
    # with cm2:
    # ctime = pd.to_datetime('now').tz_localize('Asia/Seoul').tz_convert('America/New_York')
    # st.sidebar.footer.metric('EDT (UTC-04:00)',
    #           f'{ctime.year}-{str(ctime.month).zfill(2)}-{str(ctime.day).zfill(2)} {str(ctime.hour).zfill(2)}:{str(ctime.minute).zfill(2)}')

    # Sidebar
    # tickers = ('BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'MATIC', 'EGLD', 'DOGE', 'XRP', 'BNB')
    # coin = st.sidebar.selectbox('Pick a coin from the list', tickers)
    # types = ('candle', 'line',)
    # type = st.sidebar.selectbox('Pick the chart type from the list', types, )
    type = 'candle'

    # Check periods
    # The code has been simplified by using a dictionary to store the resolution options and default values
    # for each filter option, instead of having multiple if conditionals for each option.

    period_dict = {'1MO': 30, '3MO': 90, '6MO': 180, '1Y': 365, '3Y': 1095, }
    period_list = ['1MO', '3MO', '6MO', '1Y', '3Y', ]
    # check = st.sidebar.radio('Filter', period_list, horizontal=True, index=1)
    check = st.sidebar.select_slider('Period', options=period_list, value="1Y", key='allrresolution')

    # btc_df = dashboard_yf2.load_data(name='BTC-USD', period=period_dict[check], )
    # btc_df = btc_df[-period_dict[check]:]

    # Call Period Data
    coin = 'BTC-USD'
    coin_df = dashboard_yf2.load_data(name=coin, period=period_dict[check], )
    curr_price = round(coin_df['Close'].iloc[-1], 1)
    prev_price = round(coin_df['Close'].iloc[-2], 1)

    # col1, col2, = st.columns([0.4, 0.2, ])
    # with col1:
    # Page
    # Metrics
    info = dict()
    info['price'] = curr_price
    info['prevClose'] = prev_price
    coin_df['Prev_Close'] = info["prevClose"]
    st.title(f'Technical Indicators', help='Indicator values are scaled as 0 to 100')#divider='gray')
    st.divider()

    # backtest
    temp_df = coin_df[-period_dict[check]:].copy()
    temp_df['Date'] = temp_df['Date'].astype(str).str.split(' ').str[0]
    temp_df['Date'] = pd.to_datetime(temp_df['Date'])
    temp_df = temp_df.set_index('Date')

    res = list()
    params = list()
    for id in STG_LIST:
        if id[0] == 'RSI':
            sg = backtest.RelativeStrengthIndexStrategy
        elif id[0] == 'MFI':
            sg = backtest.MoneyFlowIndexStrategy
        elif id[0] == 'AROON':
            sg = backtest.AroonOSCStrategy
        elif id[0] == 'WILLR':
            sg = backtest.WilliamsPercentR
        else:
            # res.append(backtest.run_test(data=temp_df, sg=sg))
            # params.append((sg.n_enter, sg.n_exit))
            continue
        id[1] = sg.n1
        res.append(backtest.run_test(data=temp_df, sg=sg))
        params.append((sg.n_enter, sg.n_exit))

    # Call Indicators
    ma_list = [('MA', 20, MA_COLOR), ('MA', 60, MA_COLOR2), ]
    for ma in ma_list:
        coin_df[f'{ma[0]}{ma[1]}'] = get_indicator(coin_df, name=ma[0], p1=ma[1], )
    # variance = round(np.var(coin_df['Close']),3)

    for id in STG_LIST:
        coin_df[f'{id[0]}{id[1]}'] = get_indicator(coin_df, name=id[0], p1=id[1], )

    coin_df = coin_df[-period_dict[check]:]
    coin_df['50'] = 50
    df = pd.DataFrame(
        {
            "name": [f'{n[0]} {n[1]}' for n in STG_LIST],
            "Long Enter": [n[0] for n in params],
            "Long Exit": [n[1] for n in params],
            "rate": [round(n['rate'],2) for n in res],
            "return": [round(n['return'],2) for n in res],
            "MDD(%)": [round(n['MDD'], 2) for n in res],
            "sharpe": [round(n['sharpe'], 2) for n in res],
            "trades": [n['trades'] for n in res],
            "PnL": [n['PnL'].values[:] for n in res],
        }
    )

    def trade_reco(d, enter, exit, ):

        return
    df2 = pd.DataFrame(
        {
            "name": [f'{n[0]} {n[1]}' for n in STG_LIST],
            "Status": ['Strong Buy' if n[1] >= coin_df[f'{n[0]}{n[1]}'].iloc[-1] else 'Neutral' for n in STG_LIST],
            "Current Value": [coin_df[f'{n[0]}{n[1]}'].iloc[-1] for n in STG_LIST],
            # "Long Enter": [n[0] for n in params],
            # "Long Exit": [n[1] for n in params],
        }
    )
    # df = df.style.set_properties(**{'font-size': '22pt', 'font-family': 'Calibri'})
    # df2 = df2.style.set_properties(**{'font-size': '22pt', 'font-family': 'Calibri'})
    # df2 = style_dataframe(df2)
    # df2 = df2.style.set_properties(**{'text-align': 'right'}).set_table_styles(styles)
    def left_align(s, props='text-align: right;'):
        return props

    df = df.style.applymap(left_align)
    # df2 = df2.style.applymap(left_align)
    cm1, cm2 = st.columns([1, 1, ])
    with cm1:
        st.header('Current Status')
        st.dataframe(
            df2.style.applymap(left_align).format({"Current Value": "{:.2f}".format, }),
            column_config={
                "name": st.column_config.Column("Strategy"),
                "Current Value": st.column_config.NumberColumn("Current Value"),
                "Status": st.column_config.Column("Status"),
                # "Long Enter": st.column_config.NumberColumn("📕 Long Enter"),
                # "Long Exit": st.column_config.NumberColumn("📘 Long Exit"),
            },
            hide_index=True,
            use_container_width=True,
        )
    with cm2:
        st.header('Backtesting Record')
        st.dataframe(
            df.format({"rate": "{:.2f}".format, "return": "{:.2f}".format, "MDD(%)": "{:.2f}".format, "sharpe": "{:.2f}".format}),
            column_config={
                "name": st.column_config.Column("Strategy"),
                "Long Enter": st.column_config.NumberColumn("📕 Long Enter"),
                "Long Exit": st.column_config.NumberColumn("📘 Long Exit"),
                "rate": st.column_config.NumberColumn(
                    "🎯 Win Rate(%)",
                    help="Win Rate",
                    format="{:.2f}",
                ),
                "MDD(%)": st.column_config.NumberColumn("💣 MDD(%)"),
                "return": st.column_config.NumberColumn("💰 Return(%)"),
                "sharpe": st.column_config.NumberColumn("🔪 Sharpe Ratio"),
                "trades": st.column_config.NumberColumn("🎮 Trade Count"),
                "PnL": st.column_config.LineChartColumn(
                    "📈 PnL", y_min=70, y_max=150
                ),
            },
            hide_index=True,
            # height=800,
            # width=1500,
            use_container_width=True,
        )

# with cm2:
    # Candle and volume chart
    fig = make_subplots(rows=2+len(STG_LIST), cols=1, shared_xaxes=True, vertical_spacing=0.025, horizontal_spacing=0.5,
                        specs=[[{'secondary_y': True, }] for i in range(2+len(STG_LIST))],
                        row_heights=[100, 25] + [25 for i in range(len(STG_LIST))]
                        )
    fig.add_trace(
        go.Candlestick(x=coin_df['Date'],
                       open=coin_df['Open'], high=coin_df['High'],
                       low=coin_df['Low'], close=coin_df['Close'],
                       name='BTC Candle',
                       ), row=1, col=1
    )
    # # In Momentum
    # for i, id in enumerate(STG_LIST):
    #     fig.add_trace(
    #         go.Scatter(
    #             x=coin_df['Date'],
    #             y=coin_df[f'{id[0]}{id[1]}'],
    #             line=dict(color=id[2], width=2, dash='dot'),
    #             name=f'{id[0]}{id[1]}'
    #         ), row=1, col=1, secondary_y=True
    #     )
    # In Moving Average
    for i, ma in enumerate(ma_list):
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df[f'{ma[0]}{ma[1]}'],
                line=dict(color=ma[2], width=2, dash='dot'),
                name=f'{ma[0]}{ma[1]}'
            ), row=1, col=1
        )

    # Out Momentum
    for i, id in enumerate(STG_LIST):
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df[f'{id[0]}{id[1]}'],
                line=dict(color=id[2], width=2, dash='dot'),
                name=f'{id[0]}{id[1]}'
            ), row=2+i, col=1, # secondary_y=True
        )
        fig['layout'][f'yaxis{3+i*2}']['title'] = f'{id[0]}{id[1]}'

    fig.update_layout(xaxis_rangeslider_visible=False)

    # Bar chart
    # https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
    fig.add_trace(
        go.Bar(
            x=coin_df['Date'],
            y=coin_df['Volume'],
            marker=dict(color=coin_df['Volume'], colorscale='aggrnyl_r'),
            name='Volume'
        ), row=2+len(STG_LIST), col=1
    )
    # fig['layout']['xaxis']['title'] = 'Date'
    fig['layout']['yaxis']['title'] = 'Price'
    fig.update_layout(margin=dict(t=50, b=0), xaxis_rangeslider_visible=False, height=600)
    # fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, )  # height=200)  # theme=None)
    # st.plotly_chart(fig, use_container_width=True, )  # theme=None)
    # temp_df = coin_df[-period_dict[check]:]

    # with col2:
    #     st.title('PnL Table View')
    #     st.divider()




        # df = pd.DataFrame(
        #     {
        #         "name": ["Roadmap", "Extras", "Issues"],
        #         "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app",
        #                 "https://issues.streamlit.app"],
        #         "stars": [random.randint(0, 1000) for _ in range(3)],
        #         "views_history": [[random.randint(0, 5000) for _ in range(30)] for _ in range(3)],
        #     }
        # )
        # st.dataframe(
        #     df,
        #     column_config={
        #         "name": "App name",
        #         "stars": st.column_config.NumberColumn(
        #             "Github Stars",
        #             help="Number of stars on GitHub",
        #             format="%d ⭐",
        #         ),
        #         "url": st.column_config.LinkColumn("App URL"),
        #         "views_history": st.column_config.LineChartColumn(
        #             "Views (past 30 days)", y_min=0, y_max=5000
        #         ),
        #     },
        #     hide_index=True,
        # )

    end_proc = time.time()
    print(f"run time : {end_proc - start_proc:.5f} sec")