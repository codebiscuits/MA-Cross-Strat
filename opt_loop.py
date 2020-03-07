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

op = {  # optimisation params dictionary
    'pair': 'BTCUSDT',
    'strat': strategies.MaCrossFrac,
    'timescale': '5m',
    'start': datetime.datetime(2019, 12, 1),
    'end': datetime.datetime(2020, 2, 29),
    'ma': (10, 2010),
    'risk': (200, 1800),
    'div': (2, 20),
    'step': 20,
    'size': 25,
    'cash': 1000
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

def opt_loop(pair, op):

    ### optimisation params
    trading_pair = pair
    strat = op.get('strat')
    s_n = strat.params.strat_name  # name of current strategy as a string for generating filenames etc
    timescale = op.get('timescale')
    start_date = op.get('start')
    end_date = op.get('end')
    ma = op.get('ma')
    risk = op.get('risk')
    divisor = op.get('div')
    step_size = op.get('step')
    pos_size = op.get('size')
    startcash = op.get('cash')


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
                        # divisor=range(divisor[0], divisor[1], 2),
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
                      # divisor,
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

pairs_list = get_pairs('USDT')

params = (f'ma{op.get("ma")[0]}-{op.get("ma")[1]}_sl{op.get("risk")[0]}-{op.get("risk")[1]}_div10_step{op.get("step")}')
folder = Path(f'Z:/results/{op.get("strat").params.strat_name}/{op.get("timescale")}/{params}/size-{op.get("size")}/{str(op.get("start"))[:10]}_{str(op.get("end"))[:10]}')

files_list = list(folder.glob('*.csv'))
done_list = [file.stem for file in files_list]
pairs = [x for x in pairs_list if not x in done_list]

for pair in pairs:
    opt_loop(pair, op)
