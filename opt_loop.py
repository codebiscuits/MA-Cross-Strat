import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
from sizers import PercentSizer
import strategies
import results_function_df as rf
from pathlib import Path
from binance.client import Client
import keys

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

def opt_loop(pair):

    ### optimisation params
    trading_pair = pair
    strat = strategies.MaCrossFrac
    s_n = strat.params.strat_name  # name of current strategy as a string for generating filenames etc
    timescale = '5m'
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 1, 31)
    ma = (220, 420)
    risk = (500, 1000)
    divisor = (2, 20)
    step_size = 20
    pos_size = 25
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
                        divisor=range(divisor[0], divisor[1], 2),
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
        rf.array_func(opt_runs, start, end, s_n, trading_pair, ma, risk,
                      divisor,
                      pos_size, step_size, timescale)

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

for pair in pairs:
    opt_loop(pair)
