import time
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
# from st_screen_stats import ScreenData, StreamlitNativeWidgetScreen, WindowQuerySize, WindowQueryHelper
# from pytz import timezone
import talib

MA_COLOR = 'orange'
MA_COLOR2 = 'red'
PC_COLOR = 'grey'
# IN_DATA = {}
CALL_LIST = ['NQ=F', '^VIX', 'ZB=F', 'JPY=X', ]


# with st.spinner('Wait for it...'):
#     time.sleep(5)
def pre_load_data(call_list=None):
    if call_list is None:
        call_list = CALL_LIST

    def download_historical(coin: str, start_date, end_date, period=None, interval='1d'):
        ''' This function extracts data from yfinance API and returns a dataframe
          with information about historical prices according to the chosen crypto'''

        stock = yf.Ticker(coin)
        print(start_date, ' ~ ', end_date)
        historical = stock.history(period=period, start=start_date, end=end_date, interval=interval).reset_index()
        if "Datetime" in historical.columns:
            historical.rename({"Datetime": "Date"}, axis=1, inplace=True)
        historical.to_csv(f'./database/{coin}_historical.csv', index=False)

    for c in call_list:
        back_days = date.today() - timedelta(days=1095)  # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        download_historical(c, start_date, end_date)


def load_data(name, period=90, interval='1D'):
    # print('at yf2 ::: ', len(IN_DATA))
    # data = IN_DATA[name]

    if period < 150:
        period = 150
    back_days = date.today() - timedelta(days=period)
    start = pd.to_datetime(back_days)
    # end = pd.to_datetime('now')

    data = pd.read_csv(f'./database/{name}_historical.csv')
    data['Date'] = pd.to_datetime(data['Date'], utc=True)
    data = data[data['Date'] > f'{start.year}-{str(start.month).zfill(2)}-{str(start.day).zfill(2)}']
    return data


def get_historical(coin: str, start_date, end_date, period=None, interval='1d'):
    ''' This function extracts data from yfinance API and returns a dataframe
      with information about historical prices according to the chosen crypto'''

    # coin += "-USD"
    stock = yf.Ticker(coin)
    print(start_date, ' ~ ', end_date)
    historical = stock.history(period=period, start=start_date, end=end_date, interval=interval).reset_index()
    if "Datetime" in historical.columns:
        historical.rename({"Datetime": "Date"}, axis=1, inplace=True)

    return historical


def get_market(coin: str):
    '''This function extracts data from yfinance and returns a dataframe
    with insights according to the chosen crypto'''

    # coin += "-USD"
    stock = yf.Ticker(coin)

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


def normalize(df):
    # return (df - df.min())/(df.max() - df.min())
    return (df - df.mean()) / (df.std())*50
    # return np.log(df)


def pageII():
    start_proc = time.time()

    todate = pd.to_datetime('now', utc=True) - timedelta(days=1)
    last_date = load_data('BTC-USD')['Date'].iloc[-1]
    # print(todate, ' || ', last_date)
    if todate > last_date:
        print('Refresh data')
        pre_load_data(['BTC-USD'] + CALL_LIST)

    ct1, _ = st.columns(2)
    with ct1:
        st.title('Market Dashboard', anchor="title", help="This page shows major market indices.")
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

    period_dict = {'1MO':30, '3MO':90, '6MO':180, '1Y':365, '3Y':1095,}
    period_list = ['1MO', '3MO', '6MO', '1Y', '3Y', ]
    # check = st.sidebar.radio('Filter', period_list, horizontal=True, index=1)
    check = st.sidebar.select_slider('Period', options=period_list, value="1MO", key='allrresolution')

    btc_df = load_data(name='BTC-USD', period=period_dict[check], )
    btc_df = btc_df[-period_dict[check]:]

    close_df = pd.DataFrame({})
    close_df['BTC-USD'] = btc_df.reset_index(drop=True)['Close']
    for n in CALL_LIST:
        close_df[n] = load_data(name=n, period=period_dict[check], ).reset_index(drop=True)['Close']

    # c1, c2 = st.columns(2)
    def draw_chart(name, n, h=300, is_vol=False):
        # st.header('R1')
        coin = name#'BTC'
        # Page
        # col1, col2 = st.columns([1, 5])
        # coin_image = f'img/{coin.lower()}.png'
        # st.header(f'{coin}')
        # col2.image(coin_image, width=60)

        # Call Period Data
        coin_df = load_data(name=coin, period=period_dict[check], )
        curr_price = round(coin_df['Close'].iloc[-1], 1)
        prev_price = round(coin_df['Close'].iloc[-2], 1)

        # Metrics
        # while True:
        # col1, col2, col3 = st.columns([2, 2, 2])
        col1, col2, = st.columns([2, 2, ])
        # info = get_market(coin)
        info = {}
        info['price'] = curr_price
        info['prevClose'] = prev_price
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.header(f'{coin}', divider='gray')
        col2.metric('Current Price', f'{info["price"]:,}', f'{round(price_difference_24h, 1)}%')
        # col2.metric('Prev Close', f'{round(info["prevClose"], 1):,}')

        # Moving average - 60
        coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        coin_df['20MA'] = coin_df['Close'].rolling(20, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]
        coin_df = coin_df[-period_dict[check]:]


        # Candle and volume chart
        if is_vol:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, specs=[[{'secondary_y': True,}], [{'secondary_y': False,}]], row_heights = [100, 25])
        else:
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1, specs=[[{'secondary_y': True,}]], )
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
        fig.add_trace(
            go.Scatter(
                x=btc_df['Date'],
                y=btc_df['Close'],
                line=dict(color='violet', width=2, dash='dot'),
                name="BTC-USD"
            ), row=1, col=1, secondary_y=True
        )
        # fig.update_layout(xaxis_rangeslider_visible=False)
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
                y=coin_df['20MA'],
                line=dict(color=MA_COLOR2, width=2, dash='dot'),
                name="20MA"
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

        if is_vol:
            # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
            fig.add_trace(
                go.Bar(
                    x = coin_df['Date'],
                    y = coin_df['Volume'],
                    marker = dict(color = coin_df['Volume'], colorscale = 'aggrnyl_r'),
                    name = 'Volume'
                ), row=2, col=1
            )
        # fig['layout']['xaxis']['title'] = 'Date'
        fig['layout']['yaxis']['title'] = 'Price'
        # fig['layout']['yaxis2']['title'] = 'Volume'
        fig.update_layout(margin=dict(t=40, b=0), xaxis_rangeslider_visible=False, height=h)

        st.plotly_chart(fig, use_container_width=True, )#height=200)  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # # Show data
        # if st.checkbox(f'Show data{n}'):
        #     st.dataframe(coin_df)

    def draw_multi_chart(name, n, h=300):
        # st.header('R1')
        coin = name#'BTC'
        # Page
        # col1, col2 = st.columns([1, 5])
        # coin_image = f'img/{coin.lower()}.png'
        # st.header(f'{coin}')
        # col2.image(coin_image, width=60)

        # Call Period Data
        coin_df = load_data(name=coin, period=period_dict[check], )
        curr_price = round(coin_df['Close'].iloc[-1], 1)
        prev_price = round(coin_df['Close'].iloc[-2], 1)

        # Metrics
        # while True:
        # col1, col2, col3 = st.columns([2, 2, 2])
        col1, col2, = st.columns([2, 2, ])
        # info = get_market(coin)
        info = {}
        info['price'] = curr_price
        info['prevClose'] = prev_price
        price_difference_24h = (info['price'] - info['prevClose']) / info['price'] * 100
        col1.header(f'{coin} #Signals', divider='gray')
        col2.metric('Current Price', f'{info["price"]:,}', f'{round(price_difference_24h, 1)}%')
        # col1.divider()
        # col2.divider()

        # Moving average - 60
        # coin_df['60MA'] = coin_df['Close'].rolling(60, min_periods=1).mean()
        # variance = round(np.var(coin_df['Close']),3)
        coin_df['Prev_Close'] = info["prevClose"]

        coin_df['Close_Price'] = normalize(coin_df['Close'])
        coin_df['STOCH_RSI'] = normalize(talib.STOCHRSI())
        # coin_df['RSI'] = normalize(talib.RSI(coin_df.Close))
        # coin_df['MOMENTUM'] = normalize(talib.MOM(coin_df.Close))
        # coin_df['Chaikin-ADOSC'] = normalize(talib.ADOSC(coin_df.High, coin_df.Low, coin_df.Close, coin_df.Volume, ))
        coin_df = coin_df[-period_dict[check]:]

        # Candle and volume chart
        # fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights = [100, 100, 100, 100, 100])
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,)
                            #row_heights=[100, 50])

        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Close_Price'],
                name='ClosePrice',
                line=dict(color='blue', width=7, dash='solid'),
            ),

            row=1, col=1
        )
        fig['layout']['yaxis']['title'] = 'Price'


        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['RSI'],
                line=dict(color='red', width=2, dash='dot'),
                name="RSI"
            ), row=1, col=1
        )
        # fig['layout']['yaxis2']['title'] = 'RSI'

        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['MOMENTUM'],
                line=dict(color='beige', width=2, dash='dot'),
                name="MOMENTUM"
            ), row=1, col=1
        )
        # fig['layout']['yaxis3']['title'] = 'MOM'

        fig.add_trace(
            go.Scatter(
                x=coin_df['Date'],
                y=coin_df['Chaikin-ADOSC'],
                line=dict(color='lime', width=2, dash='dot'),
                name="Chaikin-ADOSC"
            ), row=1, col=1
        )
        # fig['layout']['yaxis4']['title'] = 'ADOSC'

        # # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
        # fig.add_trace(
        #     go.Bar(
        #         x=coin_df['Date'],
        #         y=coin_df['Volume'],
        #         marker=dict(color=coin_df['Volume'], colorscale='aggrnyl_r'),
        #         name = 'Volume'
        #     ), row=2, col=1
        # )
        # fig['layout']['yaxis2']['title'] = 'Volume'
        # fig['layout']['xaxis']['title'] = 'Date'
        fig.update_layout(margin=dict(t=40, b=0), height=h)

        st.plotly_chart(fig, use_container_width=False, )#height=300)  # theme=None)
        # st.plotly_chart(fig, use_container_width=True, )  # theme=None)

        # # Show data
        # if st.checkbox(f'Show data{n}'):
        #     st.dataframe(coin_df)

    c1, c2 = st.columns(2)
    with c1:
        draw_chart('BTC-USD', 5, 400, is_vol=True)
    with c2:
        # draw_multi_chart('BTC-USD', 6, 400)

        # plt.figure(figsize=(2, 4))
        # fig, ax = plt.subplots()
        # ax.hist(btc_df['Close'], bins=20, )
        # st.pyplot(fig, use_container_width=True)

        st.header(f'Asset Correlations', divider='gray')
        corrs = close_df.corr()
        fig = px.imshow(corrs, width=800, height=800, text_auto=True, aspect="auto", labels=dict(color="Correlation"), color_continuous_scale='gray')
        fig.update_layout(margin=dict(t=0, b=0), xaxis_rangeslider_visible=False, height=400)
        st.plotly_chart(fig, use_container_width=True, )

        # # Show data
        # if st.checkbox(f'Show data-c'):
        #     st.dataframe(close_df)

    st.divider()

    cs = st.columns(4)
    for i, c in enumerate(cs):
        with c:
            draw_chart(CALL_LIST[i], i+1)

    end_proc = time.time()
    print(f"run time : {end_proc - start_proc:.5f} sec")