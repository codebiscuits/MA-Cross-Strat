import os
import numpy as np
from pathlib import Path

def array_func(opt_runs, s_n, trading_pair, ma, sl, size, pnl_res, sqn_res, start, end):

    '''function to create a numpy array of appropriate size and populate it with results from the strategy object,
        then save the array with a procedurally generated path and filename'''

    range_a = ma[1] - ma[0]
    range_b = sl[1] - sl[0]
    range_str = f'ma{ma[0]}-{ma[1]}_sl{sl[0]}-{sl[1]}'

    start_date = str(start)
    end_date = str(end)
    date_range = f'{start_date[:10]}_{end_date[:10]}'

    if sqn_res:
        ### initialise an array for sqn stats
        sqn_array = np.zeros((range_a, range_b))

        for run in opt_runs:
            for strategy in run:
                period_a = strategy.params.ma_periods - ma[0]
                period_b = strategy.params.vol_mult - sl[0]
                sqn_result = strategy.analyzers.sqn.get_analysis()
                ### .get_analysis() returns a dict so use dictionary .get method to retrieve sqn score
                sqn_value = sqn_result.get('sqn')
                ### store all sqn scores from backtests in a numpy array
                sqn_array[period_a][period_b] = sqn_value


        ### save the array for future recall
        if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}/sqn')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}/sqn'))  # creates the folder if it doesn't

        try:
            np.save(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}/sqn/{trading_pair}_1m.npy'), sqn_array)
        except:
            np.save(Path(f'results/{s_n}/{range_str}/size-{size}/{date_range}/sqn/{trading_pair}_1m.npy'), sqn_array)
            print('Could not access NAS, results saved locally.')

        ### find index of result with highest score
        max = np.amax(sqn_array)
        ind_max = np.argwhere(sqn_array == max)
        avg = np.mean(sqn_array)

        print(f'Best SQN score: {max:.1f}, settings: {ind_max[0][0] + ma[0]}, {ind_max[0][1] + sl[0]}.\nMean SQN score for all settings: {avg:.2f}')

    if pnl_res:
        ### initialise an array for ta stats
        pnl_array = np.zeros((range_a, range_b))

        for run in opt_runs:
            for strategy in run:
                period_a = strategy.params.ma_periods - ma[0]
                period_b = strategy.params.vol_mult - sl[0]
                pnl_results = strategy.analyzers.ta.get_analysis()
                pnl_pnl = pnl_results.get('pnl')
                pnl_net = pnl_pnl.get('net')
                pnl_avg = pnl_net.get('average')
                ### store all pnl scores from backtests in a numpy array
                pnl_array[period_a][period_b] = pnl_avg

        ### save the array for future recall
        if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}/pnl')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}/pnl'))  # creates the folder if it doesn't

        try:
            np.save(Path(f'Z:/results/{s_n}/{range_str}/size-{size}/{date_range}/pnl/{trading_pair}_1m.npy'), pnl_array)
        except:
            np.save(Path(f'results/{s_n}/{range_str}/size-{size}/{date_range}/pnl/{trading_pair}_1m.npy'), pnl_array)
            print('Could not access NAS, results saved locally.')

        ### find index of result with highest score
        max = np.amax(pnl_array)
        ind_max = np.argwhere(pnl_array == max)
        avg = np.mean(pnl_array)

        print(f'Best PnL score: {max:.1f}, settings: {ind_max[0][0] + ma[0]}, {ind_max[0][1] + sl[0]}.\nMean PnL score for all settings: {avg:.2f}')
