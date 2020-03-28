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
import math

op = {  # optimisation params dictionary
    'pair': 'LTCUSDT',  # only used when a single opt_run is being done
    'strat': strategies.MaCrossFracNew,
    'timescale': '1m',
    'start': datetime.datetime(2019, 12, 1),
    'end': datetime.datetime(2020, 2, 29),
    'ma': (500, 2410),
    'risk': (150, 1060),
    'div': (2, 12),
    'step': 50,
    'div_step': 2,
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

def optimise(pair, op, loop):

    ### optimisation params
    trading_pair = pair
    strat = op.get('strat')
    s_n = strat.params.strat_name  # name of current strategy as a string for generating filenames etc
    timescale = op.get('timescale')
    start_date = op.get('start')
    end_date = op.get('end')
    ma = op.get('ma')
    sl = op.get('risk')
    step_size = op.get('step')
    divisor = op.get('div')
    div_step = op.get('div_step')
    pos_size = op.get('size')


    cerebro = bt.Cerebro(
        stdstats=False,
        optreturn=True,
        optdatas=True,
        # exactbars=True            # This was the cause of the 'deque index out of range' issue
    )

    t_start = time.perf_counter()

    cerebro.optstrategy(strat,
                        ma_periods=range(ma[0], ma[1], step_size),
                        vol_mult=range(sl[0], sl[1], step_size),
                        divisor=range(divisor[0], divisor[1], div_step),
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
    cerebro.broker.setcash(1000)
    cerebro.addsizer(PercentSizer)
    cerebro.broker.setcommission(commission=0.00075)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    # if not loop:
    #     rt = math.ceil((ma[1] - ma[0])/step_size) * math.ceil((sl[1] - sl[0])/step_size) * math.ceil((divisor[1] - divisor[0])/div_step)
    #     run_counter = 0
    #
    #     def cb(strat):
    #         global run_counter
    #         global t_start
    #         global rt
    #         run_counter += 1
    #         if run_counter % (rt / 100) == 0:
    #             t_elapsed = time.perf_counter()
    #             elapsed = t_elapsed - t_start
    #             est_tot = ((rt / run_counter) * elapsed)
    #             est_rem = est_tot - elapsed
    #             hours = elapsed // 3600
    #             minutes = elapsed // 60
    #             print('-')
    #             # print(f'Runs completed: {run_counter}/{rt}')
    #             print(f'{int(run_counter / (rt / 100))}% Complete')
    #             if hours == 0:
    #                 print(f'Time elapsed: {int(minutes % 60)}m')
    #             else:
    #                 print(f'Time elapsed: {int(hours)}h {int(minutes % 60)}m')
    #             if est_rem // 3600 == 0:
    #                 print(f'Estimated time left: {int(est_rem // 60)}m')
    #             else:
    #                 print(f'Estimated time left: {int(est_rem // 3600)}h {int((est_rem // 60) % 60)}m')
    #
    #     cerebro.optcallback(cb)

    if __name__ == '__main__':

        print(f'Running {trading_pair} tests')

        opt_runs = cerebro.run()

        start = str(start_date)
        end = str(end_date)

        rf.array_func(opt_runs, start, end, s_n, trading_pair, ma, sl,
                      divisor, div_step,
                      pos_size, step_size, timescale)

        x = time.time()
        y = time.gmtime(x)
        print(f'Completed at {y[3]}:{y[4]}')

        t_end = time.perf_counter()
        global t
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

pairs_list = get_pairs('USDT')

params = (f'ma{op.get("ma")[0]}-{op.get("ma")[1]}_sl{op.get("risk")[0]}-{op.get("risk")[1]}_step{op.get("step")}_div{op.get("div")[0]}-{op.get("div")[1]}_div-step{op.get("div_step")}')
folder = Path(f'Z:/results/{op.get("strat").params.strat_name}/{op.get("timescale")}/{params}/size-{op.get("size")}/{str(op.get("start"))[:10]}_{str(op.get("end"))[:10]}')

files_list = list(folder.glob('*.csv'))
done_list = [file.stem for file in files_list]
pairs = [x for x in pairs_list if not x in done_list]

### Run optimisation for all pairs in list
for pair in pairs:
    optimise(pair, op, True)

### Run optimisation for just one pair
# optimise('LTCUSDT', op, False)
