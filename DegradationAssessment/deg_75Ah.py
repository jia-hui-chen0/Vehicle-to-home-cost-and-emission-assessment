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
# root_dir = 'G:\\'
 # uc 0 V2G 2
root_dir = r'C:\Users\jiahuic\\'
# root_dir = r'E:\\'

def deg(num0,num1,charging):
    for county_num in range(num0,num1):         
        ttlst = [[],[],[]]
        lifecty = [] # battery life in years of zone county_num
        qcallst = []
        qcyclst = []
        location = r'\\Result_v2h\Results_80_Y82_2040_cons\\'
        flst = [i for i in os.listdir(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num)+'_0_0\\')]
        flst = [i for i in flst if '.csv' in i]
        flst = [i for i in flst if '0_0_0_' in i]
        flst = [i[6:-9] for i in flst]
        yr = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\tempAdjusted\\'+str(county_num)+'.csv')['0'].to_list()*20
        yr = [i for i in yr]
        
        for  vi in range(15):
            vi = flst[vi]
            if charging ==0:
                location = 'Results\Results_80_60_1\\'
                socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num)+['','_0_0'][charging]+'\\0_0_0_'+vi+['_0_soc.csv','_0_50.csv'][charging])
                socar = np.array(socdf['vSOC'].to_list()*20)/(60)
            elif charging ==1:
                location = ['Result_cc\Results_Y60_2024\\','Result_cc\Results_Y60_2030\\','Result_cc\Results_Y60_2040\\']
                socdf = [pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'
                                +location[yri]+str(county_num)+'_0_0'+'\\0_0_0_'+vi+'_0_soc.csv') for yri in range(3)]
                socar = np.array(socdf[0]['vSOC'].to_list()*6+socdf[1]['vSOC'].to_list()*6+socdf[2]['vSOC'].to_list()*8)/(60)
            elif charging ==2:
                location = ['Result_v2h\Results_80_Y82_2024_cons\\','Result_v2h\Results_80_Y82_2030_cons\\','Result_v2h\Results_80_Y82_2040_cons\\']
                socdf = [pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'
                                +location[yri]+str(county_num)+'_0_0'+'\\0_0_0_'+vi+'_0_50.csv') for yri in range(3)]
                # socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_2024\\'+str(county_num)+'_0_0\\0_0_0_'+vi+'_0_50.csv')
                socar = np.array(socdf[0]['vSOC'].to_list()*6+socdf[1]['vSOC'].to_list()*6+socdf[2]['vSOC'].to_list()*8)/(82)
            data = {'Time_s': np.arange(8760*20)*3600,
                    'SOC':np.array(socar),
                    'Temperature_C':np.array(yr)
                    }
            cell = models.NMC_Gr_75Ah_A()
            cell.simulate_battery_life(data)
            h = 0
            while cell.outputs['q'][h] >.7 and h< 7007:
                h+=1
            
            lifecty.append(h/365)
            qcallst.append(1-cell.outputs['q_t'][-1])
            qcyclst.append(1-cell.outputs['q_EFC'][-1])
            # except:
            #     ttlst[0].append(county_num)
            #     ttlst[1].append(vi)
            #     ttlst[2].append(charging)
                # print(len(cell.outputs['q']))
            # print(cell.outputs['q'][-1],1-cell.outputs['q_t'][-1],1-cell.outputs['q_EFC'][-1])
        pd.DataFrame([lifecty,qcallst,qcyclst]).to_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Server_168h\Deginterm_1\\'+str(county_num)+'_80Y82_'+['uc','cc','v2h'][charging]+'_A'+'_cons.csv')
        # if len(ttlst[0]) != 0:
        #     df00 = pd.DataFrame(ttlst)
        #     df00.to_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Server_168h\testBLAST\errordoc\\'+str(county_num)+'.csv')
if __name__ == '__main__':
    # UC(18,21)

    import warnings
    warnings.filterwarnings("ignore")
    # for charging in range(1):
    #     for batteryi in range(1):
            
    #         deg(0,1,charging,batteryi)
    for charging in range(2,3):
        procs = []
        for i in range(48):
            if i != 47:
                p = Process(target=deg, args=([i*9,i*9+9,charging]))
            else:
                p = Process(target=deg,args=([i*9,432,charging]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join() # this blocks until the process terminates