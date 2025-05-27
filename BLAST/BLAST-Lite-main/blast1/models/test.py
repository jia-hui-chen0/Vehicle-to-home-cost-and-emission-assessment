from blast import utils
import pandas as pd
from blast import models
import numpy as np
# socdf = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Result_db\Results\Results_80_82_1\0\0_0_0_0_0_soc.csv')
socdf = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Result_db\Result_v2h\Results_80_Y82_2024\0_0_0\0_0_0_0_0_50.csv')
socar = np.array(socdf['vSOC'].to_list()*15)/(82)
yr = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\\tempAdjusted\\'+str(0)+'.csv')['0'].to_list()*15
data = {'Time_s': np.arange(8760*15)*3600,
        'SOC':np.array(socar),
        'Temperature_C':np.array(yr)
        }
cell = models.NMC_Gr_50Ah_B1()
cell.simulate_battery_life(data)
print(len(cell.outputs['q']))
print(cell.outputs['q'][-1],1-cell.outputs['q_t'][-1],1-cell.outputs['q_EFC'][-1])