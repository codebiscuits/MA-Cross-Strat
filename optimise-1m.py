import backtrader as bt
import backtrader.feeds as btfeeds
import os
import datetime
import time
from sizers import PercentSizer
import strategies
import extensions as ex
import results_function as rf
from pathlib import Path

startcash = 1000
trading_pair = 'BTCUSDT'
strat = MaCross
s_n = strat.params.strat_name      # name of current strategy as a string for generating filenames etc
pnl_results = False
sqn_results = True
sig_or_risk = False                 # True if optimising signal params, False if optimising stoploss/size params
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2020, 1, 30)

### optimisation params
ma = (1, 1000)
sl = (1, 100)
size = (20, 40, 60, 80, 99)

cerebro = bt.Cerebro(
    stdstats=False,
    optreturn=True,
    optdatas=True,
    # exactbars=True            # This was the cause of the 'deque index out of range' issue
)

t_start = time.perf_counter()

if sig_or_risk:
    cerebro.optstrategy(strat,
                        ma_periods = range(ma[0], ma[1]),
                        start=t_start)
else:
    cerebro.optstrategy(strat,
                        sl=range(sl[0], sl[1]),
                        size=range(size[0], size[1]),
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

if sig_or_risk:
    rt = ma[1] - ma[0]
else:
    rt = (sl[1] - sl[0]) * len(size)
run_counter = 0
def cb(MaCross):
    global run_counter
    global t_start
    global rt
    run_counter += 1
    if run_counter%10 == 0:
        t_elapsed = time.perf_counter()
        elapsed = t_elapsed - t_start
        hours = elapsed // 3600
        minutes = elapsed // 60
        print(f'Runs completed: {run_counter}/{rt}, Time elapsed:{int(hours)}h {int(minutes % 60)}m')
        print(f'Estimated time left:{((rt/run_counter)*elapsed)//3600}h {(((rt/run_counter)*elapsed)//60) % 60}m')
        print('-')

cerebro.adddata(data)
cerebro.broker.setcash(startcash)
cerebro.addsizer(PercentSizer)
PercentSizer.params.percents = size
cerebro.broker.setcommission(commission=0.00075)
cerebro.optcallback(cb)

if pnl_results:
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
if sqn_results:
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')


if __name__ == '__main__':

    print(f'Running {trading_pair} tests')

    opt_runs = cerebro.run()
    
    a = strat.params.ma_periods
    b = strat.params.stop_loss_perc
    c = strat.params.pos_size
    
    if signal_or_sl:
        rf.array_func_sroc(opt_runs, s_n, trading_pair, a, b, c, pnl_results, sqn_results, start_date, end_date)
    else:
        rf.array_func_sl(opt_runs, s_n, trading_pair, a, b, c, pnl_results, sqn_results, start_date, end_date)
    
    t_end = time.perf_counter()
    t = t_end - t_start
    hours = t // 3600
    minutes = t // 60
    if int(hours) >0:
        print(f'Time elapsed:{int(hours)}h {int(minutes%60)}m')
    else:
        print(f'{int(minutes)}m')
