import os
from blast1 import models
from blast1 import utils
import numpy as np
import pandas as pd
for county_num in range(1,9): 
    root_dir = r'C:\Users\jiahuic\\'
    lifecty = [] # battery life in years of zone county_num
    qcallst = []
    qcyclst = []
    # if charging == 0: 
    location = 'Energy consumption_adjusted_1_2_Y82_db\\'
    flst = [i for i in os.listdir(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num))]
    flst = [i for i in flst if '.csv' in i]
    flst = [i for i in flst if '0_0_0_' in i]
    flst = [i[6:-10] for i in flst]
    yr = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\tempAdjusted\\'+str(county_num)+'.csv')['0'].to_list()*20
    yr = [i for i in yr]
    for  vi in range(1,10):
        vi = str(vi)
        location = ['Result_v2h\Results_80_Y82_2024_1\\','Result_v2h\Results_80_Y82_2030_1\\','Result_v2h\Results_80_Y82_2040_1\\']
        socdf = [pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_db\\'
                        +location[yri]+str(county_num)+'_0_0'+'\\0_0_0_'+vi+'_0_50.csv') for yri in range(3)]
        socar = np.array(socdf[0]['vSOC'].to_list()*6+socdf[1]['vSOC'].to_list()*6+socdf[2]['vSOC'].to_list()*8)/(60)
        data = {'Time_s': np.arange(8760*20)*3600,
                'SOC':np.array(socar),
                'Temperature_C':np.array(yr)
                }


        cell = models.NMC_Gr_50Ah_B1()
        cell.simulate_battery_life(data)