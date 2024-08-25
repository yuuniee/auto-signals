import yfinance as yf
from backtesting import Backtest, Strategy
import talib
import pandas as pd
import numpy as np

IS_LONG = True


class MovingAverageStrategy(Strategy):
    def init(self):
        self.ma = self.I(talib.SMA, self.data.Close, 60)*1.1

    def next(self):
        I_L = self.data.Close[-1] > self.ma[-1]
        O_L = self.data.Close[-1] <= self.ma[-1]
        I_S = False
        O_S = False
        is_position = self.position.is_long or self.position.is_short

        if not is_position:
            if I_L:
                self.buy()
            elif I_S:
                self.sell()
        else:
            if O_L:
                self.position.close()
            elif O_S:
                self.position.close()


class RelativeStrengthIndexStrategy(Strategy):
    n1 = 13
    n2 = 0
    n_enter = 31
    n_exit = 34
    my_name = 'RSI'

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.rsi = None
        self.enter = None
        self.exit = None

    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.n1)
        self.enter = self.n_enter
        self.exit = self.n_exit

    def next(self):
        if IS_LONG:
            I_L = self.enter > self.rsi[-1]
            O_L = self.exit < self.rsi[-1]
            I_S = False#75 < self.rsi[-1]
            O_S = False#60 > self.rsi[-1]
        else:
            I_L = False
            O_L = False
            I_S = self.enter < self.rsi[-1]
            O_S = self.exit > self.rsi[-1]

        is_position = self.position.is_long or self.position.is_short

        if not is_position:
            if I_L:
                self.buy()
            elif I_S:
                self.sell()
        else:
            if O_L:
                self.position.close()
            elif O_S:
                self.position.close()


class WilliamsPercentR(Strategy):
    n1 = 11
    n2 = 0
    n_enter = 17
    n_exit = 54

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.indicator = None
        self.long_in = None
        self.long_out = None

    def init(self):
        self.indicator = self.I(talib.WILLR, self.data.High, self.data.Low, self.data.Close, self.n1) + 100
        self.long_in = self.n_enter
        self.long_out = self.n_exit

    def next(self):
        I_L = self.long_in > self.indicator[-1]
        O_L = self.long_out < self.indicator[-1]
        I_S = False#75 < self.rsi[-1]
        O_S = False#60 > self.rsi[-1]
        is_position = self.position.is_long or self.position.is_short

        if not is_position:
            if I_L:
                self.buy()
            elif I_S:
                self.sell()
        else:
            if O_L:
                self.position.close()
            elif O_S:
                self.position.close()


class AroonOSCStrategy(Strategy):
    n1 = 9
    n2 = 0
    n_enter = 5
    n_exit = 22

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.aroon = None
        self.long_in = None
        self.long_out = None

    def init(self):
        # (talib.AROONOSC(df.High, df.Low, p1) + 100) / 2
        self.aroon = (self.I(talib.AROONOSC, self.data.High, self.data.Low, self.n1) + 100)/2
        self.long_in = self.n_enter
        self.long_out = self.n_exit

    def next(self):
        I_L = self.long_in > self.aroon[-1]
        O_L = self.long_out < self.aroon[-1]
        I_S = False#75 < self.rsi[-1]
        O_S = False#60 > self.rsi[-1]
        is_position = self.position.is_long or self.position.is_short

        if not is_position:
            if I_L:
                self.buy()
            elif I_S:
                self.sell()
        else:
            if O_L:
                self.position.close()
            elif O_S:
                self.position.close()


class MoneyFlowIndexStrategy(Strategy):
    n1 = 9
    n2 = 0
    n_enter = 19
    n_exit = 40

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.mfi = None
        self.long_in = None
        self.long_out = None

    def init(self):
        self.mfi = self.I(talib.MFI, np.array(self.data.High.astype(float)), np.array(self.data.Low.astype(float)), np.array(self.data.Close.astype(float)), np.array(self.data.Volume.astype(float)), self.n1)
        self.long_in = self.n_enter
        self.long_out = self.n_exit

    def next(self):
        I_L = self.long_in > self.mfi[-1]
        O_L = self.long_out < self.mfi[-1]
        I_S = False#75 < self.rsi[-1]
        O_S = False#60 > self.rsi[-1]
        is_position = self.position.is_long or self.position.is_short

        if not is_position:
            if I_L:
                self.buy()
            elif I_S:
                self.sell()
        else:
            if O_L:
                self.position.close()
            elif O_S:
                self.position.close()


def run_test(data, sg=RelativeStrengthIndexStrategy, in_cash=10000*10000, ):
    bt = Backtest(data, sg, exclusive_orders=True, cash=in_cash, commission=.002)
    # Backtest.optimize()
    results = bt.run()
    # # Print all performance metrics
    # print(results._equity_curve['Equity'] / in_cash)
    # print(results['Return [%]'], results['Sharpe Ratio'])
    # print(results['Win Rate [%]'], results['# Trades'], results['Max. Drawdown [%]'])

    # # Plot backtesting result

    res = {
        'PnL': results._equity_curve['Equity'] / in_cash * 100,
        'params': (sg.n1, sg.n2, sg.n_enter, sg.n_exit),
        'return': results['Return [%]'],
        'sharpe': results['Sharpe Ratio'],
        'rate': results['Win Rate [%]'],
        'trades': results['# Trades'],
        'MDD': results['Max. Drawdown [%]'],
    }
    # bt.plot()
    return res


# opt_params = {'RSI': [range(5, 35, 2), [0], range(20, 40, 2), range(25, 60, 2)]}
long_opt_params = {'RSI': [range(5, 35, 2),
                           [0],
                           range(5, 40, 2),
                           range(10, 60, 2)], }
short_opt_params = {'RSI': [range(5, 35, 2),
                            [0],
                            range(90, 70, -2),
                            range(85, 60, -2)], }


def run_optimizing(data, sg, in_cash=10000*10000, ):
    backtest = Backtest(data, sg, cash=in_cash, commission=.002)
    if IS_LONG:
        results, heatmap = backtest.optimize(
            n1=long_opt_params['RSI'][0],
            n2=long_opt_params['RSI'][1],
            n_enter=long_opt_params['RSI'][2],
            n_exit=long_opt_params['RSI'][3],
            constraint=lambda p: p.n_exit > p.n_enter,
            maximize='Sharpe Ratio', # 'Equity Final [$]',
            max_tries=5000,
            random_state=42,
            return_heatmap=True,
        )
    else:
        results, heatmap = backtest.optimize(
            n1=short_opt_params['RSI'][0],
            n2=short_opt_params['RSI'][1],
            n_enter=short_opt_params['RSI'][2],
            n_exit=short_opt_params['RSI'][3],
            constraint=lambda p: p.n_exit < p.n_enter,
            maximize='Sharpe Ratio', # 'Equity Final [$]',
            max_tries=5000,
            random_state=42,
            return_heatmap=True,
        )
    backtest.plot()
    heatmap.values[np.isnan(heatmap.values)] = 0
    max_val = np.max(heatmap.values)
    target_index = np.where(heatmap.values == max_val)
    if len(target_index[0]) > 1:
        target_index = target_index[0][0]
    best_opt = heatmap.index.values[target_index]
    # print(best_opt, max_val)

    res = {
        'PnL': results._equity_curve['Equity'] / in_cash * 100,
        'params': best_opt[0],
        'return': results['Return [%]'],
        'sharpe': results['Sharpe Ratio'],
        'rate': results['Win Rate [%]'],
        'trades': results['# Trades'],
        'MDD': results['Max. Drawdown [%]'],
    }
    return res, best_opt


def get_strategy(name='RSI'):
    if name == 'RSI':
        return RelativeStrengthIndexStrategy
    elif name == 'MFI':
        return MoneyFlowIndexStrategy
    elif name == 'AROON':
        return AroonOSCStrategy
    elif name == 'WILLR':
        return WilliamsPercentR
    else:
        return None


if __name__ == '__main__':
    # ticker = yf.Ticker("AAPL")
    # start_date = "2022-01-01"
    # end_date = "2022-12-31"
    # ohlcv = ticker.history(start=start_date, end=end_date)
    ohlcv = pd.read_csv(f'../database/BTC-USD_historical.csv')
    ohlcv['Date'] = ohlcv['Date'].astype(str).str.split(' ').str[0]
    ohlcv['Date'] = pd.to_datetime(ohlcv['Date'])
    ohlcv = ohlcv.set_index('Date')

    res = run_optimizing(data=ohlcv, sg=WilliamsPercentR)
    print(res)

    # res = run_test(data=ohlcv, st=MoneyFlowIndexStrategy)
    # print(res)