import os
import pandas as pd
from pathlib import Path

def array_func(opt_runs, start, end, s_n, trading_pair, ma, sl,
               divisor,
               size, step_size, timescale):

    '''function to create a numpy array of appropriate size and populate it with results from the strategy object,
        then save the array with a procedurally generated path and filename'''

    range_str = f'ma{ma[0]}-{ma[1]}_sl{sl[0]}-{sl[1]}_div{divisor[0]}-{divisor[1]}_step{step_size}'
    # range_str = f'ma{ma[0]}-{ma[1]}_sl{sl[0]}-{sl[1]}_div10_step{step_size}'

    start_date = start
    end_date = end
    date_range = f'{start_date[:10]}_{end_date[:10]}'

    ### initialise a dataframe for sqn stats
    df_list = []

    for run in opt_runs:
        for strategy in run:
            period_a = strategy.params.ma_periods
            period_b = strategy.params.vol_mult
            divisor = strategy.params.divisor
            sqn_result = strategy.analyzers.sqn.get_analysis()
            sqn_value = round(sqn_result.get('sqn'), 2)
            try:
                pnl_results = strategy.analyzers.ta.get_analysis()
                pnl_net = round((pnl_results.get('pnl'))['net']['total'], 2)
                pnl_avg = (pnl_results.get('pnl'))['net']['average']
                total_open = (pnl_results.get('total'))['open']
                total_closed = (pnl_results.get('total'))['closed']
                total_won = (pnl_results.get('won'))['total']
                total_lost = (pnl_results.get('lost'))['total']
                strike_rate = round((total_won / total_closed) * 100)
            except TypeError:
                pnl_net = 0
                pnl_avg = 0
                total_open = 0
                total_closed = 0
                total_won = 0
                total_lost = 0
                strike_rate = 0
            df_list.append([period_a, period_b,
                            divisor,
                            sqn_value, strike_rate,
                            pnl_avg, pnl_net,
                            total_open, total_closed, total_won, total_lost])

    ### more efficient to build a list of lists and then turn that into a dataframe, rather than build the dataframe iteratively
    df = pd.DataFrame(df_list,
                   columns=['ma', 'risk',
                            'divisor',
                            'sqn', 'strike_rate',
                            'pnl_avg', 'pnl_net',
                            'total_open', 'total_closed', 'total_won', 'total_lost'])



    ### save the array for future recall
    if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
        os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
    if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
        os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
    if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}')):  # checks that the relevant folder exists
        os.mkdir(Path(f'Z:/results/{s_n}/{timescale}'))  # creates the folder if it doesn't
    if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}')):  # checks that the relevant folder exists
        os.mkdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}'))  # creates the folder if it doesn't
    if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{size}')):  # checks that the relevant folder exists
        os.mkdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{size}'))  # creates the folder if it doesn't
    if not os.path.isdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{size}/{date_range}')):  # checks that the relevant folder exists
        os.mkdir(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{size}/{date_range}'))  # creates the folder if it doesn't

    try:
        df.to_csv(Path(f'Z:/results/{s_n}/{timescale}/{range_str}/size-{size}/{date_range}/{trading_pair}.csv'))
    except:
        df.to_csv(Path(f'results/{s_n}/{timescale}/{range_str}/size-{size}/{date_range}/{trading_pair}.csv'))
        print('Could not access NAS, results saved locally.')

    # print(df.head())
