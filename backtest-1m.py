import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import time
from sizers import PercentSizer
import strategies
from pathlib import Path
import matplotlib

startcash = 1000
trading_pair = 'BTCUSDT'
strat = strategies.MaCrossFrac
s_n = strat.params.strat_name      # name of current strategy as a string for generating filenames etc
ma = 1370
mult = 280
divisor = 10
pos_size = 25
timescale = '1m'
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2020, 1, 30)

t_start = time.perf_counter()

cerebro = bt.Cerebro(
    stdstats=False,
    optreturn=True,
    optdatas=True,
    # exactbars=True            # This was the cause of the 'deque index out of range' issue
)

cerebro.addstrategy(strat, ma_periods=ma, vol_mult=mult, divisor=divisor, pos_size=pos_size, start=t_start)


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

cerebro.adddata(data)
cerebro.broker.setcash(startcash)
cerebro.addsizer(PercentSizer)
cerebro.broker.setcommission(commission=0.00075)
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
PercentSizer.params.percents = pos_size


if __name__ == '__main__':

    print(f'Running {trading_pair} tests')

    strat_list = cerebro.run()
    results = strat_list[0]

    pnl_value = results.analyzers.ta.get_analysis()['pnl']['net']['average']
    sqn_result = results.analyzers.sqn.get_analysis()
    # .get_analysis() returns a dict so use dictionary .get method to retrieve sqn score
    # pnl_value = pnl_result.get(['pnl']['net']['average'])
    sqn_value = sqn_result.get('sqn')

    endcash = cerebro.broker.getvalue()
    pnl_tot = ((endcash-startcash)/startcash)*100
    print('-')
    print(f'Starting Balance: {startcash}')
    print(f'Final Balance: {endcash:.2f}')
    print('-')
    print(f'Net PnL: {pnl_tot:.2f}%')
    print(f'Avg Trade PnL: {pnl_value:.2f}%')
    print(f'SQN Score: {sqn_value:.1f}')
    
    print('-')
    t_end = time.perf_counter()
    t = t_end - t_start
    hours = t // 3600
    minutes = t // 60
    if int(hours) > 0:
        print(f'Time elapsed: {int(hours)}h {int(minutes%60)}m')
    elif int(minutes) > 0:
        print(f'Time elapsed: {int(minutes)}m')
    else:
        print(f'Time elapsed: {int(t)}s')

    cerebro.plot()