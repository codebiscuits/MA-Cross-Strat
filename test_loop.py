import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
from sizers import PercentSizer
from sizers import FixedReverser
import strategies
from pathlib import Path
import pandas as pd
import os
from binance.client import Client
import keys
from sigfig import round

op = {  # optimisation params dictionary
    'strat': strategies.MaCrossFracNew,
    'timescale': '1m',
    'start': datetime.datetime(2019, 12, 1),
    'end': datetime.datetime(2020, 2, 29),
    'dates': False,
    'ma': 1700,
    'mult': 750,
    'div': 2,
    'size': 90
}

def get_pairs(quote):
    binance_client = Client(api_key=keys.Pkey, api_secret=keys.Skey)
    info = binance_client.get_exchange_info()
    symbols = info['symbols']
    length = len(quote)
    pairs_list = []

    for item in symbols:
        if item['symbol'][-length:] == quote:
            if not (item['symbol'] in ['PAXUSDT', 'USDSBUSDT', 'BCHSVUSDT', 'BCHABCUSDT', 'VENUSDT', 'TUSDUSDT', 'USDCUSDT', 'USDSUSDT', 'BUSDUSDT', 'EURUSDT', 'BCCUSDT', 'IOTAUSDT']):
                pairs_list.append(item['symbol'])

    return pairs_list

def backtest(pair, op):
    startcash = 1000
    trading_pair = pair
    strat = op.get('strat')
    s_n = strat.params.strat_name      # name of current strategy as a string for generating filenames etc
    timescale = '1m'
    ma = op.get('ma')
    mult = op.get('mult')
    divisor = op.get('div')
    pos_size = op.get('size')

    inner_start = time.perf_counter()

    cerebro = bt.Cerebro(
        # stdstats=False,
        # optreturn=True,
        optdatas=True,
        # exactbars=True            # This was the cause of the 'deque index out of range' issue
    )

    cerebro.addstrategy(strat, ma_periods=ma, vol_mult=mult, divisor=divisor, start=t_start)


    datapath = Path(f'V:/Data/{trading_pair}-{timescale}-data.csv')

    # Create a data feed
    if op.get('dates'):
        data = btfeeds.GenericCSVData(
            dataname=datapath,
            fromdate=op.get('start'),
            todate=op.get('end'),
            dtformat=('%Y-%m-%d %H:%M:%S'),
            datetime=0, high=2, low=3, open=1, close=4, volume=5, openinterest=-1,
            timeframe=bt.TimeFrame.Minutes,
            compression=1
        )
    else:
        data = btfeeds.GenericCSVData(
            dataname=datapath,
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

        print(f'Running {trading_pair} - {s_n} tests')

        strat_list = cerebro.run()
        results = strat_list[0]

        inner_end = time.perf_counter()
        time_taken = inner_end - inner_start

        try:
            pnl_value = results.analyzers.ta.get_analysis()['pnl']['net']['average']
            total_closed = results.analyzers.ta.get_analysis()['total']['closed']
            total_won = results.analyzers.ta.get_analysis()['won']['total']
        except KeyError:
            pnl_value = 0
            total_closed = 0
            total_won = 0
        sqn_result = results.analyzers.sqn.get_analysis()
        sqn_value = sqn_result.get('sqn')

        endcash = cerebro.broker.getvalue()
        pnl_tot = ((endcash-startcash)/startcash)*100
        results_list = [pair, round(sqn_value, sigfigs=3), round(pnl_tot, sigfigs=3), round(pnl_value, sigfigs=3), total_closed, total_won, round(time_taken, sigfigs=3)]

        return results_list

pairs_list = get_pairs('USDT')
# print(pairs_list)
### short list for testing
# pairs_list = ['STPTUSDT', 'COTIUSDT', 'BNBBEARUSDT', 'BNBBULLUSDT', 'MBLUSDT', 'AIONUSDT']

big_list = []

t_start = time.perf_counter()

count = 0
for pair in pairs_list:
    results = backtest(pair, op)
    big_list.append(results)
    print(results)
    count += 1
    print(f'{count/len(pairs_list):.0%} completed')
    t_end = time.perf_counter()
    t = t_end - t_start
    hours = t // 3600
    minutes = t // 60
    if int(hours) > 0:
        print(f'Time elapsed: {int(hours)}h {int(minutes % 60)}m')
    elif int(minutes) > 0:
        print(f'Time elapsed: {int(minutes)}m')
    else:
        print(f'Time elapsed: {int(t)}s')
    print('-')

df = pd.DataFrame(big_list,
                   columns=['pair', 'sqn',
                            'total pnl', 'avg pnl',
                            'num trades', 'wins', 'time'])

### save the array for future recall
s_n = op.get('strat').params.strat_name
filename = f'ma-{op.get("ma")}mult-{op.get("mult")}div-{op.get("div")}.csv'
date_range = f'{str(op.get("start"))[:10]}_{str(op.get("end"))[:10]}'

if not os.path.isdir(Path(f'results')):
    os.mkdir(Path(f'results/{s_n}'))
if not os.path.isdir(Path(f'results')):
    os.mkdir(Path(f'results/{s_n}'))
if not os.path.isdir(Path(f'results/{s_n}/{op.get("timescale")}')):
    os.mkdir(Path(f'results/{s_n}/{op.get("timescale")}'))
if not os.path.isdir(Path(f'results/{s_n}/{op.get("timescale")}/size-{op.get("size")}')):
    os.mkdir(Path(f'results/{s_n}/{op.get("timescale")}/size-{op.get("size")}'))
if not os.path.isdir(Path(f'results/{s_n}/{op.get("timescale")}/size-{op.get("size")}/{date_range}')):
    os.mkdir(Path(f'results/{s_n}/{op.get("timescale")}/size-{op.get("size")}/{date_range}'))
df.to_csv(filename)
df.to_csv(Path(f'results/{s_n}/{op.get("timescale")}/size-{op.get("size")}/{date_range}/{filename}'))