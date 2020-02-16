import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
from sizers import PercentSizer
import strategies
from pathlib import Path

startcash = 1000
trading_pair = 'BNBUSDT'
strat = strategies.MaCross
s_n = strat.params.strat_name      # name of current strategy as a string for generating filenames etc
ma = 50
mult = 10
pos_size = 99
pnl_results = True
sqn_results = False
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2020, 1, 30)

cerebro = bt.Cerebro(
    stdstats=False,
    optreturn=True,
    optdatas=True,
    # exactbars=True            # This was the cause of the 'deque index out of range' issue
)

t_start = time.perf_counter()

cerebro.addstrategy(strat, ma_periods=ma, vol_mult=mult, start=t_start)


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

cerebro.adddata(data)
cerebro.broker.setcash(startcash)
cerebro.addsizer(PercentSizer)
cerebro.broker.setcommission(commission=0.00075)
if pnl_results:
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
if sqn_results:
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
PercentSizer.params.percents = pos_size


if __name__ == '__main__':

    print(f'Running {trading_pair} tests')

    strat_list = cerebro.run()
    results = strat_list[0]

    if pnl_results:
        pnl_value = results.analyzers.ta.get_analysis()['pnl']['net']['average']
    if sqn_results:
        sqn_result = results.analyzers.sqn.get_analysis()
        # .get_analysis() returns a dict so use dictionary .get method to retrieve sqn score
        # pnl_value = pnl_result.get(['pnl']['net']['average'])
        sqn_value = sqn_result.get('sqn')

    print(f'Starting Balance: {startcash}')
    print('Final Balance: %.2f' % cerebro.broker.getvalue())
    if pnl_results:
        print(f'PNL Average: {pnl_value}')
    if sqn_results:
        print(f'SQN Score: {sqn_value:.1f}')
    
    t_end = time.perf_counter()
    t = t_end - t_start
    hours = t // 3600
    minutes = t // 60
    if int(hours) > 0:
        print(f'Time elapsed:{int(hours)}h {int(minutes%60)}m')
    elif int(minutes) > 0:
        print(f'{int(minutes)}m')
    else:
        print(f'Time elapsed: {int(t)}s')
