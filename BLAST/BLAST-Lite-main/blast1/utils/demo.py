"""Functions helpful for demonstrating the use of BLAST-Lite in Python."""

import numpy as np
import pandas as pd

from blast.utils.functions import assemble_one_year_input

def generate_sample_data(kind: str = "synthetic") -> dict:
    """
    Generate synthetic sample data for demonstration purposes.
    Options:

        1. Completely synthetic data
        2. Data from a small personal EV in Honolulu, Hawaii.
        3. Data from a large personal EV in Honolulu, Hawaii.
        4. Data from a commercial EV in Honolulu, Hawaii.

    Args:
        kind (str): One of 'synthetic', 'ev_smallbattery', 'ev_largebattery',
        'ev_commercial', 'ev_commercial_lowdod', 'ev_commercial_lowdod_lowsoc'

    Returns:
        dict:  Dictionary with keys {'Time_s', 'SOC', 'Temperature_C'}
    """

    _allowed_kinds = {
        "synthetic",
        "ev_smallbattery",
        "ev_largebattery",
        "ev_commercial",
        "ev_commercial_lowdod",
        "ev_commercial_lowdod_lowsoc",
    }

    root_dir = r'C:\Users\jiahuic\\'
    
    yr = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\tempAdjusted\\'+str(0)+'.csv')['0'].to_list()*20
    climate = pd.read_csv("examples/climates/nsrdb_honolulu.csv")
    ev_smallbattery = pd.read_csv(
        "examples/application profiles/personal_ev_smallbatt.csv"
    )
    ev_smallbattery = ev_smallbattery.iloc[
        np.linspace(0, 24 * 3600 * 7 - 1, 24 * 7)
    ]
    input = assemble_one_year_input(ev_smallbattery, climate)


    return input
