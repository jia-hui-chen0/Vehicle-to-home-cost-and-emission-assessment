# https://www.mdpi.com/1996-1073/17/1/158
# NREL 2023           
from blast import utils
import pandas as pd
from blast import models
import numpy as np
import pandas as pd 
import numpy as np
from gams import *

from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue

root_dir = r'F:\University of Michigan Dropbox\Jiahui Chen\\'

# Define the result location mapping
result_locations = {
    "UC": "Results\\Results_80_82_rev\\",
    "CC": "Result_cc\\Results_Y82_2024_nocarb\\",
    "CC_60": "Result_cc\\Results_Y60_2024_nocarb\\",
    "V2H": "Result_v2h\\Results_80_Y82_2024_nocarb\\",
    "V2H_cons": "Result_v2h\\Results_80_Y82_2024_cons_nocarb\\",
    "V2H_60": "Result_v2h\\Results_80_Y60_2024_nocarb\\",
    "V2H_cons_60": "Result_v2h\\Results_80_Y60_2024_cons_nocarb\\"
}

# For each location, define the file suffix and divisor for SOC
location_settings = {
    "UC": {"suffix": "_0_soc.csv"},
    "CC": {"suffix": "_0_soc.csv"},
    "CC_60": {"suffix": "_0_soc.csv"},
    "V2H": {"suffix": "_0_50.csv"},
    "V2H_cons": {"suffix": "_0_50.csv"},
    "V2H_60": {"suffix": "_0_50.csv"},
    "V2H_cons_60": {"suffix": "_0_50.csv"}
}

# List of battery chemistries and their model class names
battery_models = [
    ("NMC_Gr_75Ah_A", models.NMC_Gr_75Ah_A, "75AhA"),
    ("NMC_Gr_50Ah_B1", models.NMC_Gr_50Ah_B1, "B1"),
    ("NMC_Gr_50Ah_B2", models.NMC_Gr_50Ah_B2, "B2"),
    ("Lfp_Gr_250AhPrismatic", models.Lfp_Gr_250AhPrismatic, "LFP")
]

def deg(num0, num1):
    years = [2024, 2030, 2040]
    # Prepare output directory (create if not exists)
    output_dir = os.path.join(
        root_dir,
        r'Ford_CC\DegradationAssessment_revision\Deginterm_1'
    )
    os.makedirs(output_dir, exist_ok=True)
    # Loop through battery chemistries
    for batt_name, batt_class, batt_tag in battery_models:
        # Loop through capacity (60 and 82)
        for cap in [60, 82]:
            # For each result location
            for loc_key, loc_path in result_locations.items():
                settings = location_settings[loc_key]
                suffix = settings["suffix"]
                divisor = cap
                for county_num in range(num0, num1):
                    # Check if output file already exists, if so, skip this county_num
                    out_name = f"{county_num}_80Y{cap}_{loc_key}_{batt_tag}_nocarb.csv"
                    out_path = os.path.join(
                        output_dir,
                        out_name
                    )
                    if os.path.exists(out_path):
                        continue  # Output file exists, skip processing

                    ttlst = [[], [], []]
                    lifecty = []
                    qcallst = []
                    qcyclst = []
                    # List all files in the result directory for this county
                    result_dir = os.path.join(
                        root_dir,
                        r'Ford_CC\\',
                        loc_path,
                        f"{county_num}_0_0"
                    )
                    if not os.path.exists(result_dir):
                        continue
                    flst = [f'0_0_0_0{suffix}', f'0_0_0_10{suffix}', f'0_0_0_11{suffix}',
                            f'0_0_0_12{suffix}', f'0_0_0_13{suffix}', f'0_0_0_14{suffix}', f'0_0_0_15{suffix}',
                            f'0_0_0_16{suffix}', f'0_0_0_17{suffix}', f'0_0_0_18{suffix}', f'0_0_0_19{suffix}',
                            f'0_0_0_1{suffix}', f'0_0_0_20{suffix}', f'0_0_0_21{suffix}', f'0_0_0_22{suffix}']
                    # Read temperature profile and repeat for 20 years
                    yr = pd.read_csv(
                        os.path.join(
                            root_dir,
                            r'Ford_CC\\',
                            'tempAdjusted',
                            f"{county_num}.csv"
                        )
                    )['0'].to_list() * 20
                    yr = [i for i in yr]
                    for vi_idx in range(15):
                        vi = flst[vi_idx]
                        socdf_list = []
                        # For each year, read the corresponding file and repeat as needed
                        for yri, year in enumerate(years):
                            file_path = os.path.join(
                                root_dir,
                                r'Ford_CC',
                                loc_path,
                                f"{county_num}_0_0",
                                f"{vi}"
                            )
                            if not os.path.exists(file_path):
                                continue
                            socdf = pd.read_csv(file_path)
                            # For 2024, 6 years; 2030, 6 years; 2040, 8 years (total 20)
                            repeat = 5 if year in [2024, 2030] else 10
                            socdf_list.extend(socdf['vSOC'].to_list() * repeat)
                        if len(socdf_list) != 8760 * 20:
                            # If not enough data, skip this vi
                            continue
                        socar = np.array(socdf_list) / divisor
                        data = {
                            'Time_s': np.arange(8760 * 20) * 3600,
                            'SOC': np.array(socar),
                            'Temperature_C': np.array(yr)
                        }
                        cell = batt_class()
                        cell.simulate_battery_life(data)
                        h = 0
                        while cell.outputs['q'][h] > .7 and h < 365*15:
                            h += 1
                        lifecty.append(h / 365)
                        qcallst.append(1 - cell.outputs['q_t'][-1])
                        qcyclst.append(1 - cell.outputs['q_EFC'][-1])
                    # Save results for this county, location, battery, and capacity
                    pd.DataFrame([lifecty, qcallst, qcyclst]).to_csv(out_path)

if __name__ == '__main__':
    # deg(0,1)
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(48):
        if i != 47:
            p = Process(target=deg, args=(i * 9, i * 9 + 9))
        else:
            p = Process(target=deg, args=(i * 9, 432))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()  # this blocks until the process terminates