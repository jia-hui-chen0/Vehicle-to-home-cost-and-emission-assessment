import pandas as pd
import numpy as np
from gams import *
from datetime import datetime
from multiprocessing import Pool
import time
from multiprocessing import Process, Queue
output = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Server_168h\Deginterm_2'
batmodlst = ['A','B1','B2','LFP250'] # 2121
caplst = ['60','82']
chargelst = ['uc','cc','v2h']
capi = 0
lst0 = [[] for i in range(4)]
for bati in range(4):
    for chargei in range(3):
        for county_num in range(432):
            df = pd.read_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Server_168h\Deginterm_1\\'
                                    +str(county_num)+'_80Y'+caplst[capi]+'_'+chargelst[chargei]+'_'+batmodlst[bati]+'.csv')
            # if batmodlst[bati] == 'B1' or batmodlst[bati] == 'LFP250':
            #     q = np.quantile(df.T[1][1:df.T[0].shape[0]],.85)
            # elif batmodlst[bati] != 'B1' and batmodlst[bati] != 'LFP250':
            q = np.quantile((df.T[1] + df.T[2])[1:df.T[0].shape[0]],.85)
            lst0[0].append(bati)
            lst0[1].append(chargei)
            lst0[2].append(q)
            lst0[3].append(county_num)
pd.DataFrame(lst0).to_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Server_168h\Deginterm_2\\degmid_'+caplst[capi]+'_60.csv')