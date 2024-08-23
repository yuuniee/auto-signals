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


def normalize(df):
    # return (df - df.min())/(df.max() - df.min())
    return (df - df.mean()) / (df.std())*50
    # return np.log(df)


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
    types = ('candle', 'line',)
    type = st.sidebar.selectbox('Pick the chart type from the list', types, )

    # Check periods
    # The code has been simplified by using a dictionary to store the resolution options and default values
    # for each filter option, instead of having multiple if conditionals for each option.

    period_dict = {'1MO': 30, '3MO': 90, '6MO': 180, '1Y': 365, '3Y': 1095, }
    period_list = ['1MO', '3MO', '6MO', '1Y', '3Y', ]
    # check = st.sidebar.radio('Filter', period_list, horizontal=True, index=1)
    check = st.sidebar.select_slider('Period', options=period_list, value="1Y", key='allrresolution')

    btc_df = dashboard_yf2.load_data(name='BTC-USD', period=period_dict[check], )
    btc_df = btc_df[-period_dict[check]:]

    # close_df = pd.DataFrame({})
    # close_df['BTC-USD'] = btc_df.reset_index(drop=True)['Close']
    # for n in dashboard_yf2.CALL_LIST:
    #     close_df[n] = dashboard_yf2.load_data(name=n, period=period_dict[check], ).reset_index(drop=True)['Close']

    col1, col2, = st.columns([0.4, 0.2, ])
    with col1:
        # st.header('R1')
        coin = 'BTC-USD'
        # Page
        c1, c2 = st.columns([1, 1])
        # coin_image = f'img/{coin.lower()}.png'
        # st.header(f'{coin}')
        # col2.image(coin_image, width=60)

        # Call Period Data
        coin_df = dashboard_yf2.load_data(name=coin, period=period_dict[check], )
        curr_price = round(coin_df['Close'].iloc[-1], 1)
        prev_price = round(coin_df['Close'].iloc[-2], 1)

        # Metrics
        # while True:
        # col1, col2, col3 = st.columns([2, 2, 2])
        # col1, col2, = st.columns([2, 2, ])
        # info = get_market(coin)
        info = {}
        info['price'] = curr_price
        info['prevClose'] = prev_price
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        c1.title(f'{coin} & Technical Indicators', )#divider='gray')
        # c2.metric('Current Price', f'{info["price"]:,}', f'{round(price_difference_24h, 1)}%')
        st.divider()
        # col2.metric('Prev Close', f'{round(info["prevClose"], 1):,}')

        # Moving average -
        coin_df['20MA'] = coin_df['Close'].rolling(20, min_periods=1).mean()
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        coin_df['150MA'] = coin_df['Close'].rolling(150, min_periods=1).mean()

        indicat_list = ['RSI', 'WILLR', 'MFI', 'AROONOSC', ]
        coin_df[indicat_list[0]] = talib.RSI(coin_df.Close, 14)
        coin_df[indicat_list[1]] = talib.WILLR(coin_df.High, coin_df.Low, coin_df.Close, 14) + 100
        coin_df[indicat_list[2]] = talib.MFI(coin_df.High, coin_df.Low, coin_df.Close, coin_df.Volume, 14)
        coin_df[indicat_list[3]] = talib.AROONOSC(coin_df.High, coin_df.Low, 14)
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]
        coin_df = coin_df[-period_dict[check]:]


        # Candle and volume chart
        fig = make_subplots(rows=6, cols=1, shared_xaxes=True, vertical_spacing=0.025, horizontal_spacing=0.5, # specs=[[{'secondary_y': True,}], [{'secondary_y': False,}]],
                            specs=[[{'secondary_y': True, }], [{'secondary_y': True, }], [{'secondary_y': True, }], [{'secondary_y': True, }], [{'secondary_y': True, }], [{'secondary_y': False, }]],
                            row_heights=[100, 25, 25, 25, 25, 25])

        if type == 'line':
            fig.add_trace(
                go.Scatter(x=coin_df['Date'], y=coin_df['Close'], name='ClosePrice'),
                row=1, col=1
            )
        if type == 'candle':
            fig.add_trace(
                # go.Scatter(x = coin_df['Date'],  y = coin_df['Close'], name='ClosePrice'),
                go.Candlestick(x=coin_df['Date'],
                               open=coin_df['Open'], high=coin_df['High'],
                               low=coin_df['Low'], close=coin_df['Close'],
                               name='BTC Candle',
                               ),
                row=1, col=1
            )
        # fig.add_trace(
        #     go.Scatter(
        #         x=btc_df['Date'],
        #         y=btc_df['Close'],
        #         line=dict(color='violet', width=2, dash='dot'),
        #         name="BTC-USD"
        #     ), row=1, col=1, # secondary_y=True
        # )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Prev_Close'],
                line=dict(color=PC_COLOR, width=2, dash='dot'),
                name="Prev_Close"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['20MA'],
                line=dict(color=MA_COLOR, width=2, dash='dot'),
                name="20MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['60MA'],
                line=dict(color=MA_COLOR2, width=2, dash='dot'),
                name="60MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['150MA'],
                line=dict(color=MA_COLOR3, width=2, dash='dot'),
                name="150MA"
            ), row=1, col=1
        )

        # fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df[indicat_list[0]],
                line=dict(color='red', width=2, dash='dot'),
                name=indicat_list[0]
            ), row=2, col=1, secondary_y=True
        )
        fig.add_trace(
            go.Scatter(
                x=btc_df['Date'],
                y=btc_df['Close'],
                line=dict(color='violet', width=2, dash='dot'),
                name="BTC-USD"
            ), row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df[indicat_list[1]],
                line=dict(color='blue', width=2, dash='dot'),
                name=indicat_list[1]
            ), row=3, col=1, secondary_y=True
        )
        fig.add_trace(
            go.Scatter(
                x=btc_df['Date'],
                y=btc_df['Close'],
                line=dict(color='violet', width=2, dash='dot'),
                name="BTC-USD"
            ), row=3, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df[indicat_list[2]],
                line=dict(color='orange', width=2, dash='dot'),
                name=indicat_list[2]
            ), row=4, col=1, secondary_y=True
        )
        fig.add_trace(
            go.Scatter(
                x=btc_df['Date'],
                y=btc_df['Close'],
                line=dict(color='violet', width=2, dash='dot'),
                name="BTC-USD"
            ), row=4, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df[indicat_list[3]],
                line=dict(color='maroon', width=2, dash='dot'),
                name=indicat_list[3]
            ), row=5, col=1, secondary_y=True
        )
        fig.add_trace(
            go.Scatter(
                x=btc_df['Date'],
                y=btc_df['Close'],
                line=dict(color='violet', width=2, dash='dot'),
                name="BTC-USD"
            ), row=5, col=1
        )
        #
        # fig.add_trace(
        #     go.Scatter(x=coin_df['Date'], y=coin_df['Close'], name='ClosePrice'),
        #     # go.Candlestick(x = coin_df['Date'],
        #     #                 open = coin_df['Open'], high = coin_df['High'],
        #     #                 low = coin_df['Low'], close = coin_df['Close'],
        #     #                 name = 'Candlestick',
        #     #                 ),
        #     row=1, col=2
        # )
        # fig.update_layout(xaxis_rangeslider_visible=False)
        # fig.add_trace(
        #     go.Scatter(
        #         x=coin_df['Date'],
        #         y=coin_df['60MA'],
        #         line=dict(color='#e0e0e0', width=2, dash='dot'),
        #         name="60MA"
        #     ), row=1, col=2
        # )


        # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        fig.add_trace(
            go.Bar(
                x = coin_df['Date'],
                y = coin_df['Volume'],
                marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
                name = 'Volume'
            ), row=6, col=1
        )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        fig['layout']['yaxis3']['title'] = indicat_list[0]
        fig['layout']['yaxis5']['title'] = indicat_list[1]
        fig['layout']['yaxis7']['title'] = indicat_list[2]
        fig['layout']['yaxis9']['title'] = indicat_list[3]

        # fig['layout']['yaxis4']['title'] = indicat_list[0]
        # fig['layout']['yaxis6']['title'] = indicat_list[1]
        # fig['layout']['yaxis8']['title'] = indicat_list[2]
        # fig['layout']['yaxis10']['title'] = indicat_list[3]

        fig['layout']['yaxis11']['title'] = 'Volume'
        fig.update_layout(margin=dict(t=50, b=0), xaxis_rangeslider_visible=False, height=800)
        # fig.update_traces(mode="markers+lines", hovertemplate=None)
        fig.update_layout(hovermode="x unified")

        st.plotly_chart(fig, use_container_width=True, )#height=200)  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # # Show data
        # if st.checkbox(f'Show data{n}'):
        #     st.dataframe(coin_df)
    with col2:
        st.title('PnL Table View')
        st.divider()

        coin_df['Date'] = coin_df['Date'].astype(str).str.split(' ').str[0]
        coin_df['Date'] = pd.to_datetime(coin_df['Date'])
        coin_df = coin_df.set_index('Date')
        res = backtest.run_test(coin_df)
        # st.dataframe(coin_df, height=800)
        df = pd.DataFrame(
            {
                "name": ["RSI", ],
                "rate": [res['rate'], ],
                "return": [res['return'], ],
                "PnL": [res['PnL'].values[:], ],
            }
        )
        st.dataframe(
            df,
            column_config={
                "name": "Strategy",
                "rate": st.column_config.NumberColumn(
                    "Win Rate",
                    help="Win Rate",
                    format="%d 🎯",
                ),
                "return": st.column_config.NumberColumn("return"),
                "PnL": st.column_config.LineChartColumn(
                    "PnL", y_min=70, y_max=150
                ),
            },
            hide_index=True,
            # height=800, width=600
        )

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