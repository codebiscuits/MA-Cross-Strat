import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
from sizers import PercentSizer
import strategies
import results_function as rf
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
            if not (item['symbol'] in ['PAXUSDT', 'USDSBUSDT', 'BCHSVUSDT', 'BCHABCUSDT', 'VENUSDT', 'TUSDUSDT', 'USDCUSDT', 'USDSUSDT', 'BUSDUSDT', 'EURUSDT', 'BCCUSDT']):
                pairs_list.append(item['symbol'])

    return pairs_list

def opt_loop(pair):
    startcash = 1000
    trading_pair = pair
    strat = strategies.MaCross
    s_n = strat.params.strat_name      # name of current strategy as a string for generating filenames etc
    pnl_results = True
    sqn_results = True
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 1, 30)

    ### optimisation params
    ma = (100, 103) # for testing, use (100, 103) or higher to avoid empty autodict error
    sl = (100, 103) # for testing, use (100, 103) or higher to avoid empty autodict error
    pos_size = 25

    cerebro = bt.Cerebro(
        stdstats=False,
        optreturn=True,
        optdatas=True,
        # exactbars=True            # This was the cause of the 'deque index out of range' issue
    )

    t_start = time.perf_counter()

    cerebro.optstrategy(strat,
                        ma_periods = range(ma[0], ma[1]),
                        vol_mult=range(sl[0], sl[1]),
                        start=t_start)


    datapath = Path(f'Z:/Data/{trading_pair}-1m-data.csv')

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

    rt = (ma[1] - ma[0]) * (sl[1] - sl[0])
    run_counter = 0
    def cb(MaCross):
        global run_counter
        global t_start
        global rt
        run_counter += 1
        if run_counter%(rt/100) == 0:
            t_elapsed = time.perf_counter()
            elapsed = t_elapsed - t_start
            est_tot = ((rt / run_counter) * elapsed)
            est_rem = est_tot - elapsed
            hours = elapsed // 3600
            minutes = elapsed // 60
            print('-')
            # print(f'Runs completed: {run_counter}/{rt}')
            print(f'{run_counter/(rt/100)}% Complete')
            if hours == 0:
                print(f'Time elapsed: {int(minutes % 60)}m')
            else:
                print(f'Time elapsed: {int(hours)}h {int(minutes % 60)}m')
            if est_rem//3600 == 0:
                print(f'Estimated time left: {int(est_rem // 60)}m')
            else:
                print(f'Estimated time left: {int(est_rem // 3600)}h {int((est_rem // 60) % 60)}m')

    cerebro.adddata(data)
    cerebro.broker.setcash(startcash)
    cerebro.addsizer(PercentSizer)
    cerebro.broker.setcommission(commission=0.00075)
    # cerebro.optcallback(cb)
    PercentSizer.params.percents = pos_size

    if pnl_results:
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    if sqn_results:
        cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')


    if __name__ == '__main__':

        print(f'Running {trading_pair} tests')

        opt_runs = cerebro.run()

        a = strat.params.pos_size

        print('-')
        rf.array_func(opt_runs, s_n, trading_pair, ma, sl, a, pnl_results, sqn_results, start_date, end_date)

        print('-')
        t_end = time.perf_counter()
        t = t_end - t_start
        hours = t // 3600
        minutes = t // 60
        if int(hours) > 0:
            print(f'Time elapsed:{int(hours)}h {int(minutes % 60)}m')
        elif int(minutes) > 0:
            print(f'{int(minutes)}m')
        else:
            print(f'Time elapsed: {int(t)}s')
        print('----------------------------')


pairs = get_pairs('USDT')

for pair in pairs:
    if pair != 'BTCUSDT':
        opt_loop(pair)