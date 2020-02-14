import os
import numpy as np
from pathlib import Path

def array_func_signal(opt_runs, s_n, trading_pair, ma, b, c, pnl_res, sqn_res, start, end):

    '''function to create a numpy array of appropriate size and populate it with results from the strategy object,
        then save the array with a procedurally generated path and filename'''

    range = ma[1] - ma[0]
    range_str = f'ma{ma[0]}-{ma[1]}'

    start_date = str(start)
    end_date = str(end)
    date_range = f'{start_date[:10]}_{end_date[:10]}'

    if sqn_res:
        ### initialise an array for sqn stats
        sqn_array = np.zeros((range))

        for run in opt_runs:
            for strategy in run:
                period = strategy.params.ma_periods - ma[0]
                sqn_result = strategy.analyzers.sqn.get_analysis()
                ### .get_analysis() returns a dict so use dictionary .get method to retrieve sqn score
                sqn_value = sqn_result.get('sqn')
                ### store all sqn scores from backtests in a numpy array
                sqn_array[period] = sqn_value


        ### save the array for future recall
        if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}/sqn')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}/sqn'))  # creates the folder if it doesn't

        np.save(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}/sqn/{trading_pair}_1m.npy'), sqn_array)

        ### find index of result with highest score
        max = np.amax(sqn_array)
        ind_max = np.argwhere(sqn_array == max)
        avg = np.mean(sqn_array)

        print(f'Best SQN score: {max:.1f}, settings: {ind_max[0][0] + ma[0]}.\nMean SQN score for all settings: {avg:.2f}')

    if pnl_res:
        ### initialise an array for ta stats
        pnl_array = np.zeros((range))

        for run in opt_runs:
            for strategy in run:
                period = strategy.params.ma_periods - ma[0]
                pnl_value = strategy.analyzers.ta.get_analysis()['pnl']['net']['average']
                ### store all pnl scores from backtests in a numpy array
                pnl_array[period] = pnl_value

        ### save the array for future recall
        if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}/pnl')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}/pnl'))  # creates the folder if it doesn't

        np.save(Path(f'Z:/results/{s_n}/{range_str}/mult-{b}-size-{c}/{date_range}/pnl/{trading_pair}_1m.npy'), pnl_array)

        ### find index of result with highest score
        max = np.amax(pnl_array)
        ind_max = np.argwhere(pnl_array == max)
        avg = np.mean(pnl_array)

        print(f'Best PnL score: {max:.1f}, settings: {ind_max[0][0] + ma[0]}.\nMean PnL score for all settings: {avg:.2f}')

def array_func_risk(opt_runs, s_n, trading_pair, a, sl, pos_size, pnl_res, sqn_res, start, end):

    '''function to create a numpy array of appropriate size and populate it with results from the strategy object,
        then save the array with a procedurally generated path and filename'''

    range_b = sl[1] - sl[0]
    range_c = 1     # len(pos_size)
    range_str = f'mult{sl[0]}-{sl[1]},size{pos_size[0]}-{pos_size[-1]}'

    start_date = str(start)
    end_date = str(end)
    date_range = f'{start_date[:10]}_{end_date[:10]}'

    if sqn_res:
        ### initialise an array for sqn stats
        sqn_array = np.zeros((range_b, range_c))

        for run in opt_runs:
            for strategy in run:
                period1 = strategy.params.vol_mult - b[0]
                period2 = round(strategy.params.size / 20) - 1      # if size != (20, 40, 60, 80, 99) this line needs to be changed
                sqn_result = strategy.analyzers.sqn.get_analysis()
                ### .get_analysis() returns a dict so use dictionary .get method to retrieve sqn score
                sqn_value = sqn_result.get('sqn')
                # print(f'SQN Value:{sqn_value}')
                ### store all sqn scores from backtests in a numpy array
                sqn_array[period1][period2] = sqn_value


        ### save the array for future recall
        if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}/sqn')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}/sqn'))  # creates the folder if it doesn't

        np.save(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}/sqn/{trading_pair}_1m.npy'), sqn_array)

        ### find index of result with highest score
        max = np.amax(sqn_array)
        ind_max = np.argwhere(sqn_array == max)
        avg = np.mean(sqn_array)

        print(f'Best SQN score: {max:.1f}, settings: {ind_max[0][0] + sl[0]}, {ind_max[0][1] + pos_size[0]}.\nMean SQN score for all settings: {avg:.2f}')

    if pnl_res:
        ### initialise an array for ta stats
        pnl_array = np.zeros((range_b, range_c))

        for run in opt_runs:
            for strategy in run:
                period1 = strategy.params.vol_mult - b[0]
                period2 = round(strategy.params.size / 20) - 1  # if size != (20, 40, 60, 80, 99) this line needs to be changed
                pnl_value = strategy.analyzers.ta.get_analysis()['pnl']['net']['average']
                ### store all pnl scores from backtests in a numpy array
                pnl_array[period1][period2] = pnl_value

        ### save the array for future recall
        if not os.path.isdir(Path(f'Z:/results')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}'))  # creates the folder if it doesn't
        if not os.path.isdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}/pnl')):  # checks that the relevant folder exists
            os.mkdir(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}/pnl'))  # creates the folder if it doesn't

        np.save(Path(f'Z:/results/{s_n}/{range_str}/ma-{a}/{date_range}/pnl/{trading_pair}_1m.npy'), pnl_array)

        ### find index of result with highest score
        max = np.amax(pnl_array)
        ind_max = np.argwhere(pnl_array == max)
        avg = np.mean(pnl_array)

        print(f'Best PnL score: {max:.1f}, settings: {ind_max[0][0] + sl[0]}, {ind_max[0][1] + pos_size[0]}.\nMean PnL score for all settings: {avg:.2f}')