import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
import os
from sizers import PercentSizer
import strategies
import results_function_df as rf
from pathlib import Path
from binance.client import Client
import pandas as pd
import keys

def get_pairs(quote):
    binance_client = Client(api_key=keys.Pkey, api_secret=keys.Skey)
    info = binance_client.get_exchange_info()
    symbols = info['symbols']
    length = len(quote)
    pairs_list = []

    for item in symbols:
        if item['symbol'][-length:] == quote:
            if not (item['symbol'] in ['PAXUSDT', 'USDSBUSDT', 'BCHSVUSDT', 'BCHABCUSDT', 'VENUSDT', 'TUSDUSDT', 'USDCUSDT', 'USDSUSDT', 'BUSDUSDT', 'EURUSDT', 'BCCUSDT', 'IOTA']):
                pairs_list.append(item['symbol'])

    return pairs_list

### optimisation params
strat = strategies.MaCross
s_n = strat.params.strat_name  # name of current strategy as a string for generating filenames etc
timescale = '5m'
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2020, 1, 31)
ma = (2, 102)
risk = (0, 80)
step_size = 10
pos_size = 25

range_str = f'ma{ma[0]}-{ma[1]}_risk{risk[0]}-{risk[1]}_step{step_size}'
date_range = f'{str(start_date)[:10]}_{str(end_date)[:10]}'

t = 0

def opt_loop(pair, strategy, timescale, start, end, ma, risk, step_size, pos_size):

    trading_pair = pair
    strat = strategy
    s_n = strat.params.strat_name
    timescale = timescale
    start_date = start
    end_date = end
    ma = ma
    risk = risk
    step_size = step_size
    pos_size = pos_size
    startcash = 1000


    cerebro = bt.Cerebro(
        stdstats=False,
        optreturn=True,
        optdatas=True,
        # exactbars=True            # This was the cause of the 'deque index out of range' issue
    )

    t_start = time.perf_counter()

    cerebro.optstrategy(strat,
                        ma_periods=range(ma[0], ma[1], step_size),
                        vol_mult=range(risk[0], risk[1], step_size),
                        start=t_start)

    datapath = Path(f'Z:/Data/{trading_pair}-{timescale}-data.csv')

    # Create a data feed
    data = btfeeds.GenericCSVData(
        dataname=datapath,
        fromdate=start_date,
        todate=end_date,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        datetime=0, high=2, low=3, open=1, close=4, volume=5, openinterest=-1,
        timeframe=bt.TimeFrame.Minutes,
        compression=1
    )


    PercentSizer.params.percents = pos_size

    cerebro.adddata(data)
    cerebro.broker.setcash(startcash)
    cerebro.addsizer(PercentSizer)
    cerebro.broker.setcommission(commission=0.00075)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    if __name__ == '__main__':

        print(f'Running {trading_pair} tests')

        opt_runs = cerebro.run()

        start = str(start_date)
        end = str(end_date)

        print('-')
        rf.array_func(opt_runs, start, end, s_n, trading_pair, ma, risk, pos_size, step_size, timescale)

        print('-')
        t_end = time.perf_counter()
        global t
        t = t_end - t_start
        hours = t // 3600
        minutes = t // 60
        if int(hours) > 0:
            print(f'Time elapsed:{int(hours)}h {int(minutes % 60)}m')
        elif int(minutes) > 0:
            print(f'{int(minutes)}m')
        else:
            print(f'Time elapsed: {int(t)}s')


pairs = get_pairs('USDT')

if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
    os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
    os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}')):  # checks that the relevant folder exists
    os.mkdir(Path(f'Z:/results/{s_n}/{timescale}'))  # creates the folder if it doesn't
if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}')):  # checks that the relevant folder exists
    os.mkdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}'))  # creates the folder if it doesn't
if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}')):  # checks that the relevant folder exists
    os.mkdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}'))  # creates the folder if it doesn't
if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}/{date_range}')):  # checks that the relevant folder exists
    os.mkdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}/{date_range}'))  # creates the folder if it doesn't

for pair in pairs:
    if os.path.isfile(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}/{date_range}/tests_started.csv')):
        tests_started = pd.read_csv(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}/{date_range}/tests_started.csv')
    else:
        tests_started = pd.DataFrame({'pair': [], 'time': []})

    started_list = list(tests_started['pair'])

    if not pair in started_list:
        tests_started = tests_started.append({'pair': pair, 'time': 0}, ignore_index=True)
        tests_started.to_csv(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}/{date_range}/tests_started.csv'))
        opt_loop(pair, strat, timescale, start_date, end_date, ma, risk, step_size, pos_size)
    tests_started.loc['pair' == pair, 'time'] = t
    tests_started.to_csv(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{pos_size}/{date_range}/tests_started.csv'))
