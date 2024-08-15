import time

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from st_screen_stats import ScreenData, StreamlitNativeWidgetScreen, WindowQuerySize, WindowQueryHelper
from pytz import timezone

MA_COLOR = 'orange'
PC_COLOR = 'grey'


def get_historical(coin: str, start_date, end_date, period = None, interval = '1d'):
    ''' This function extracts data from yfinance API and returns a dataframe
      with information about historical prices according to the chosen crypto'''

    # coin += "-USD"
    stock = yf.Ticker(coin)
    print(start_date, ' ~ ', end_date)
    historical = stock.history(period = period, start = start_date, end = end_date, interval = interval).reset_index()
    if "Datetime" in historical.columns:
        historical.rename({"Datetime": "Date"}, axis=1, inplace=True)

    return historical


def get_market(coin: str):
    '''This function extracts data from yfinance and returns a dataframe
    with insights according to the chosen crypto'''

    # coin += "-USD"
    stock = yf.Ticker(coin)
    print(' ::::::::::::::::::: ', ' called somthing')

    # yfinance info: can't find 'regularMarketPrice' replaced by 'regularMarketDayLow'
    # https://github.com/ranaroussi/yfinance/issues/1519
    
    info = {
        "priceHigh24h": stock.info.get('dayHigh', None),
        "priceLow24h": stock.info.get('dayLow', None),
        "volumeUsd24h": stock.info.get('volume24Hr', None),
        "prevClose": stock.info.get('previousClose', None),
        "price": stock.info.get('regularMarketDayLow', None)
    }
    
    return info


def pageII():
    start_proc = time.time()

    ct1, _ = st.columns(2)
    with ct1 :
        st.title('Market Dashboard', anchor="title", help="This page shows major market indices.")
    cm1, cm2 = st.columns(2)

    # with cm1:
    #     ctime = pd.to_datetime('now')
    #     st.metric('KST (UTC+09:00)',
    #               f'{ctime.year}-{str(ctime.month).zfill(2)}-{str(ctime.day).zfill(2)} {str(ctime.hour).zfill(2)}:{str(ctime.minute).zfill(2)}')
    #     # st.write(f':blue[{ctime.year}-{str(ctime.month).zfill(2)}-{str(ctime.day).zfill(2)} {str(ctime.hour).zfill(2)}:{str(ctime.minute).zfill(2)} EDT (UTC−04:00)]')
    with cm2:
        ctime = pd.to_datetime('now').tz_localize('Asia/Seoul').tz_convert('America/New_York')
        print('ctime : ', ctime)
        st.metric('EDT (UTC-04:00)',
                  f'{ctime.year}-{str(ctime.month).zfill(2)}-{str(ctime.day).zfill(2)} {str(ctime.hour).zfill(2)}:{str(ctime.minute).zfill(2)}')

    # Sidebar
    tickers = ('BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'MATIC', 'EGLD', 'DOGE', 'XRP', 'BNB')
    coin = st.sidebar.selectbox('Pick a coin from the list', tickers)
    types = ('line', 'candle', )
    type = st.sidebar.selectbox('Pick the chart type from the list', types)

    # Check periods
    # The code has been simplified by using a dictionary to store the resolution options and default values
    # for each filter option, instead of having multiple if conditionals for each option.

    check = st.radio('Filter', ['1D', '5D', '1MO', '3MO', '6MO', '1Y', '2Y', 'All', ], horizontal=True, index=5)
    resolution_options = {
        '1D': (["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d"], "5m"),
        '5D': (["30m", "60m", "90m", "1d"], "30m"),
        '1MO': (["1d", "5d", "1wk", "1mo"], "1d"),
        '3MO': (["1d", "5d", "1wk", "1mo"], "1d"),
        '6MO': (["1d", "5d", "1wk", "1mo", "3mo"], "1d"),
        '1Y': (["1d", "5d", "1wk", "1mo", "3mo"], "1d"),
        '2Y': (["1d", "5d", "1wk", "1mo", "3mo"], "1d")
    }
    if check == 'All':
        resolution = st.select_slider('Resolution', options=["1d", "5d", "1wk", "1mo", "3mo"], value="1d", key='allrresolution')
    else:
        options, default_value = resolution_options[check]
        period = check.lower()
        resolution = st.select_slider('Resolution', options=options, value=default_value, key=f'{period}resolution')


    cc = st.empty()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # st.header('R1')
        # Page
        # col1, col2 = st.columns([1, 5])
        # coin_image = f'img/{coin.lower()}.png'
        st.header(f'{coin}-USD')
        # col2.image(coin_image, width=60)

        back_days = date.today() - timedelta(days=2)  # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        coin_df_0 = get_historical(coin + '-USD', start_date=start_date, end_date=end_date, interval='1d')
        curr_price = round(coin_df_0['Close'].iloc[-1], 1)

        # Metrics
        # while True:
        # col1, col2, col3 = st.columns([2, 2, 2])
        col1, col2, col3 = st.columns([2, 2, 2])
        info = get_market(coin + '-USD')
        info['price'] = curr_price
        print(info)
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.metric('Price', f'{info["price"]:,}', f'{round(price_difference_24h, 1)}%')
        # col2.metric('24h High', f'{info["priceHigh24h"]:,}')
        # col3.metric('24h Low', f'{info["priceLow24h"]:,}')
        col2.metric('Prev Close', f'{round(info["prevClose"], 1)}')
        # time.sleep(10)

        # if check == 'None':
        #     start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2022-01-01'), key='dstart_date')
        #     end_date = st.sidebar.date_input('End Date', value=pd.to_datetime('now'), key='dend_date')
        #     resolution = st.select_slider('Resolution', options=["1d", "5d", "1mo"], value="1d", key='Nresolution')
        #     coin_df = get_historical(coin, start_date, end_date, interval=resolution)
        if check == 'All':
            back_days = date.today() - timedelta(days=1095)  # 3 years
            start_date = pd.to_datetime(back_days)
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=["1d", "5d", "1wk", "1mo", "3mo"], value="1d", key='allrresolution')
            coin_df = get_historical(coin + '-USD', start_date=start_date, end_date=end_date, interval=resolution)
        else:
            # options, default_value = resolution_options[check]
            period = check.lower()
            # resolution = st.select_slider('Resolution', options=options, value=default_value, key=f'{period}resolution')
            end_date = pd.to_datetime('now')
            print('::::ED DATE ', end_date)
            coin_df = get_historical(coin + '-USD', period=period, start_date=None, end_date=end_date, interval=resolution)
        # coin_df.index = coin_df.index.tz_localize(None)
        if check in ['1D', '5D']:
            coin_df['Date'] = pd.DatetimeIndex(coin_df['Date']).tz_convert('America/New_York')
            todate = coin_df['Date'].iloc[-1]
            coin_df = coin_df[coin_df['Date'] >= f'{todate.year}-{todate.month}-{todate.day}']
        # Moving average - 60
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]

        # Candle and volume chart
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,  )#row_heights = [100, 50])
        if type == 'line':
            fig.add_trace(
                go.Scatter(x = coin_df['Date'],  y = coin_df['Close'], name='ClosePrice'),
                row=1, col=1
            )
        if type == 'candle':
            fig.add_trace(
                # go.Scatter(x = coin_df['Date'],  y = coin_df['Close'], name='ClosePrice'),
                go.Candlestick(x=coin_df['Date'],
                               open=coin_df['Open'], high=coin_df['High'],
                               low=coin_df['Low'], close=coin_df['Close'],
                               name='Candlestick',
                               ),
                row=1, col=1
            )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['60MA'],
                line=dict(color=MA_COLOR, width=2, dash='dot'),
                name="60MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Prev_Close'],
                line=dict(color=PC_COLOR, width=2, dash='dot'),
                name="Prev_Close"
            ), row=1, col=1
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

        # # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        # fig.add_trace(
        #     go.Bar(
        #         x = coin_df['Date'],
        #         y = coin_df['Volume'],
        #         marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
        #         name = 'Volume'
        #     ), row = 2, col = 1
        # )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        # fig['layout']['yaxis2']['title'] = 'Volume'
        st.plotly_chart(fig, use_container_width=True, height=200)#theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # Show data
        if st.checkbox('Show data'):
            st.dataframe(coin_df)

    with c2:
        # st.header('R2')
        tk = 'NQ=F'
        # Page
        # col1, col2 = st.columns([1, 5])
        # coin_image = f'img/{coin.lower()}.png'
        st.header(tk)
        # col2.image(coin_image, width=60)

        back_days = date.today() - timedelta(days=2)  # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        coin_df_0 = get_historical(tk, start_date=start_date, end_date=end_date, interval='1d')
        curr_price = round(coin_df_0['Close'].iloc[-1], 2)

        # Metrics
        # while True:
        col1, col2, col3 = st.columns([2, 2, 2])
        info = get_market(tk)
        info['price'] = curr_price
        print(info)
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.metric('Price', f'{info["price"]:,}', f'{round(price_difference_24h, 2)}%')
        # col2.metric('24h High', f'{info["priceHigh24h"]:,}')
        # col3.metric('24h Low', f'{info["priceLow24h"]:,}')
        col2.metric('Prev Close', f'{info["prevClose"]:,}')
        # st.metric('24h Volume', f'{info["volumeUsd24h"]:,}')
        # time.sleep(10)

        if check == 'All':
            back_days = date.today() - timedelta(days=1095)  # 3 years
            start_date = pd.to_datetime(back_days)
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=["1d", "5d", "1wk", "1mo", "3mo"], value="1d", key='allrresolution')
            coin_df = get_historical(tk, start_date=start_date, end_date=end_date, interval=resolution)
        else:
            # options, default_value = resolution_options[check]
            period = check.lower()
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=options, value=default_value, key=f'{period}resolution')
            coin_df = get_historical(tk, period=period, start_date=None, end_date=end_date, interval=resolution)
        # coin_df.index = coin_df.index.tz_localize(None)
        coin_df['Date'] = pd.DatetimeIndex(coin_df['Date']).tz_convert('America/New_York')
        # Moving average - 60
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]

        # Candle and volume chart
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1, )  # row_heights = [100,25])
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
                               name='Candlestick',
                               ),
                row=1, col=1
            )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['60MA'],
                line=dict(color=MA_COLOR, width=2, dash='dot'),
                name="60MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Prev_Close'],
                line=dict(color=PC_COLOR, width=2, dash='dot'),
                name="Prev_Close"
            ), row=1, col=1
        )

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

        # # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        # fig.add_trace(
        #     go.Bar(
        #         x = coin_df['Date'],
        #         y = coin_df['Volume'],
        #         marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
        #         name = 'Volume'
        #     ), row = 2, col = 1
        # )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        # fig['layout']['yaxis2']['title'] = 'Volume'
        st.plotly_chart(fig, use_container_width=True, height=200)  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )#theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # Show data
        if st.checkbox('Show data2'):
            st.dataframe(coin_df)


    with c3:
        # st.header('R2')
        tk = 'NKD=F'
        # Page
        # col1, col2 = st.columns([1, 5])
        # coin_image = f'img/{coin.lower()}.png'
        st.header(tk)
        # col2.image(coin_image, width=60)

        back_days = date.today() - timedelta(days=2)  # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        coin_df_0 = get_historical(tk, start_date=start_date, end_date=end_date, interval='1d')
        curr_price = round(coin_df_0['Close'].iloc[-1], 2)

        # Metrics
        # while True:
        col1, col2, col3 = st.columns([2, 2, 2])
        info = get_market(tk)
        info['price'] = curr_price
        print(info)
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.metric('Price', f'{info["price"]:,}', f'{round(price_difference_24h, 2)}%')
        # col2.metric('24h High', f'{info["priceHigh24h"]:,}')
        # col3.metric('24h Low', f'{info["priceLow24h"]:,}')
        col2.metric('Prev Close', f'{info["prevClose"]:,}')
        # st.metric('24h Volume', f'{info["volumeUsd24h"]:,}')
        # time.sleep(10)

        if check == 'All':
            back_days = date.today() - timedelta(days=1095)  # 3 years
            start_date = pd.to_datetime(back_days)
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=["1d", "5d", "1wk", "1mo", "3mo"], value="1d", key='allrresolution')
            coin_df = get_historical(tk, start_date=start_date, end_date=end_date, interval=resolution)
        else:
            # options, default_value = resolution_options[check]
            period = check.lower()
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=options, value=default_value, key=f'{period}resolution')
            coin_df = get_historical(tk, period=period, start_date=None, end_date=end_date, interval=resolution)
        # coin_df.index = coin_df.index.tz_localize(None)
        coin_df['Date'] = pd.DatetimeIndex(coin_df['Date']).tz_convert('America/New_York')
        # Moving average - 60
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]

        # Candle and volume chart
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1, )  # row_heights = [100,25])
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
                               name='Candlestick',
                               ),
                row=1, col=1
            )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['60MA'],
                line=dict(color=MA_COLOR, width=2, dash='dot'),
                name="60MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Prev_Close'],
                line=dict(color=PC_COLOR, width=2, dash='dot'),
                name="Prev_Close"
            ), row=1, col=1
        )

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

        # # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        # fig.add_trace(
        #     go.Bar(
        #         x = coin_df['Date'],
        #         y = coin_df['Volume'],
        #         marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
        #         name = 'Volume'
        #     ), row = 2, col = 1
        # )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        # fig['layout']['yaxis2']['title'] = 'Volume'
        st.plotly_chart(fig, use_container_width=True, height=200)  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )#theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # Show data
        if st.checkbox('Show data3'):
            st.dataframe(coin_df)

    with c4:
        # st.header('R2')
        tk = 'ZB=F'
        # Page
        # col1, col2 = st.columns([1, 5])
        # coin_image = f'img/{coin.lower()}.png'
        st.header(tk)
        # col2.image(coin_image, width=60)

        back_days = date.today() - timedelta(days=2)  # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        coin_df_0 = get_historical(tk, start_date=start_date, end_date=end_date, interval='1d')
        curr_price = round(coin_df_0['Close'].iloc[-1], 2)

        # Metrics
        # while True:
        col1, col2, col3 = st.columns([2, 2, 2])
        info = get_market(tk)
        info['price'] = curr_price
        print(info)
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.metric('Price', f'{info["price"]:,}', f'{round(price_difference_24h, 2)}%')
        # col2.metric('24h High', f'{info["priceHigh24h"]:,}')
        # col3.metric('24h Low', f'{info["priceLow24h"]:,}')
        col2.metric('Prev Close', f'{info["prevClose"]:,}')
        # st.metric('24h Volume', f'{info["volumeUsd24h"]:,}')
        # time.sleep(10)

        if check == 'All':
            back_days = date.today() - timedelta(days=1095)  # 3 years
            start_date = pd.to_datetime(back_days)
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=["1d", "5d", "1wk", "1mo", "3mo"], value="1d", key='allrresolution')
            coin_df = get_historical(tk, start_date=start_date, end_date=end_date, interval=resolution)
        else:
            # options, default_value = resolution_options[check]
            period = check.lower()
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=options, value=default_value, key=f'{period}resolution')
            coin_df = get_historical(tk, period=period, start_date=None, end_date=end_date, interval=resolution)
        # coin_df.index = coin_df.index.tz_localize(None)
        coin_df['Date'] = pd.DatetimeIndex(coin_df['Date']).tz_convert('America/New_York')
        # Moving average - 60
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]

        # Candle and volume chart
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1, )  # row_heights = [100,25])
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
                               name='Candlestick',
                               ),
                row=1, col=1
            )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['60MA'],
                line=dict(color=MA_COLOR, width=2, dash='dot'),
                name="60MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Prev_Close'],
                line=dict(color=PC_COLOR, width=2, dash='dot'),
                name="Prev_Close"
            ), row=1, col=1
        )

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

        # # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        # fig.add_trace(
        #     go.Bar(
        #         x = coin_df['Date'],
        #         y = coin_df['Volume'],
        #         marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
        #         name = 'Volume'
        #     ), row = 2, col = 1
        # )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        # fig['layout']['yaxis2']['title'] = 'Volume'
        st.plotly_chart(fig, use_container_width=True, height=200)  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )#theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # Show data
        if st.checkbox('Show data4'):
            st.dataframe(coin_df)

    with cc:
        # st.header('R1')
        st.header(f'{coin}-USD')
        # col2.image(coin_image, width=60)

        back_days = date.today() - timedelta(days=2)  # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        coin_df_0 = get_historical(coin + '-USD', start_date=start_date, end_date=end_date, interval='1d')
        curr_price = round(coin_df_0['Close'].iloc[-1], 2)

        # Metrics
        col1, col2, col3 = st.columns([2, 2, 2])
        info = get_market(coin + '-USD')
        info['price'] = curr_price
        print(info)
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.metric('Price', f'{info["price"]:,}', f'{round(price_difference_24h, 2)}%')
        # col2.metric('24h High', f'{info["priceHigh24h"]:,}')
        # col3.metric('24h Low', f'{info["priceLow24h"]:,}')
        col2.metric('Prev Close', f'{info["prevClose"]:,}')

        if check == 'All':
            back_days = date.today() - timedelta(days=1095)  # 3 years
            start_date = pd.to_datetime(back_days)
            end_date = pd.to_datetime('now')
            # resolution = st.select_slider('Resolution', options=["1d", "5d", "1wk", "1mo", "3mo"], value="1d", key='allrresolution')
            coin_df = get_historical(coin + '-USD', start_date=start_date, end_date=end_date, interval=resolution)
        else:
            # options, default_value = resolution_options[check]
            period = check.lower()
            # resolution = st.select_slider('Resolution', options=options, value=default_value, key=f'{period}resolution')
            end_date = pd.to_datetime('now')
            print('::::ED DATE ', end_date)
            coin_df = get_historical(coin + '-USD', period=period, start_date=None, end_date=end_date, interval=resolution)
        # coin_df.index = coin_df.index.tz_localize(None)
        if check in ['1D', '5D']:
            coin_df['Date'] = pd.DatetimeIndex(coin_df['Date']).tz_convert('America/New_York')
            todate = coin_df['Date'].iloc[-1]
            coin_df = coin_df[coin_df['Date'] >= f'{todate.year}-{todate.month}-{todate.day}']
        # Moving average - 60
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]

        # Candle and volume chart
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,  )#row_heights = [100, 50])
        if type == 'line':
            fig.add_trace(
                go.Scatter(x = coin_df['Date'],  y = coin_df['Close'], name='ClosePrice'),
                row=1, col=1
            )
        if type == 'candle':
            fig.add_trace(
                # go.Scatter(x = coin_df['Date'],  y = coin_df['Close'], name='ClosePrice'),
                go.Candlestick(x=coin_df['Date'],
                               open=coin_df['Open'], high=coin_df['High'],
                               low=coin_df['Low'], close=coin_df['Close'],
                               name='Candlestick',
                               ),
                row=1, col=1
            )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['60MA'],
                line=dict(color=MA_COLOR, width=2, dash='dot'),
                name="60MA"
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Prev_Close'],
                line=dict(color=PC_COLOR, width=2, dash='dot'),
                name="Prev_Close"
            ), row=1, col=1
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

        # # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        # fig.add_trace(
        #     go.Bar(
        #         x = coin_df['Date'],
        #         y = coin_df['Volume'],
        #         marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
        #         name = 'Volume'
        #     ), row = 2, col = 1
        # )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        # fig['layout']['yaxis2']['title'] = 'Volume'
        st.plotly_chart(fig, use_container_width=True, height=200)#theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

    end_proc = time.time()
    print(f"run time : {end_proc - start_proc:.5f} sec")