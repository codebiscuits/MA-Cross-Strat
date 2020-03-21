import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
from sizers import PercentSizer
import strategies
import results_function_df as rf
from pathlib import Path
import math

trading_pair = 'ETHUSDT'
strat = strategies.MaCrossFracNew
s_n = strat.params.strat_name      # name of current strategy as a string for generating filenames etc
timescale = '1m'
start_date = datetime.datetime(2019, 12, 1)
end_date = datetime.datetime(2020, 2, 29)

### optimisation params
ma = (25, 2410)
sl = (25, 1060)
divisor = (2, 40)
step_size = 50
div_step = 4
pos_size = 25

cerebro = bt.Cerebro(
    stdstats=False,
    optreturn=True,
    optdatas=True,
    # exactbars=True            # This was the cause of the 'deque index out of range' issue
)

t_start = time.perf_counter()

cerebro.optstrategy(strat,
                    ma_periods = range(ma[0], ma[1], step_size),
                    vol_mult=range(sl[0], sl[1], step_size),
                    divisor=range(divisor[0], divisor[1], div_step),
                    start=t_start)


datapath = Path(f'V:/Data/{trading_pair}-{timescale}-data.csv')

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

rt = math.ceil((ma[1] - ma[0])/step_size) * math.ceil((sl[1] - sl[0])/step_size) * math.ceil((divisor[1] - divisor[0])/div_step)
run_counter = 0
print(rt)
def cb(strat):
    global run_counter
    global t_start
    global rt
    run_counter += 1
    modu = max(1, round(rt / 100))
    if run_counter % modu == 0:
        t_elapsed = time.perf_counter()
        elapsed = t_elapsed - t_start
        est_tot = ((rt / run_counter) * elapsed)
        est_rem = est_tot - elapsed
        hours = elapsed // 3600
        minutes = elapsed // 60
        print('-')
        # print(f'Runs completed: {run_counter}/{rt}')
        print(f'{int(run_counter/(rt/100))}% Complete')
        if hours == 0:
            print(f'Time elapsed: {int(minutes % 60)}m')
        else:
            print(f'Time elapsed: {int(hours)}h {int(minutes % 60)}m')
        if est_rem//3600 == 0:
            print(f'Estimated time left: {int(est_rem // 60)}m')
        else:
            print(f'Estimated time left: {int(est_rem // 3600)}h {int((est_rem // 60) % 60)}m')

PercentSizer.params.percents = pos_size

cerebro.adddata(data)
cerebro.broker.setcash(1000)
cerebro.addsizer(PercentSizer)
cerebro.broker.setcommission(commission=0.00075)
cerebro.optcallback(cb)

cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')


if __name__ == '__main__':

    print(f'Running {trading_pair} tests')

    opt_runs = cerebro.run()

    start = str(start_date)
    end = str(end_date)

    print('-')
    rf.array_func(opt_runs, start, end, s_n, trading_pair, ma, sl,
                  divisor,
                  pos_size, step_size, timescale)

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
