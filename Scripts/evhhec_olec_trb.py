#  min of slowCR and household electricity consumption is the lower bound for v2h
import pandas as pd 
import numpy as np
import os
import time

import pandas as pd 
import numpy as np
from datetime import datetime
import os
from multiprocessing import Pool
import time
from multiprocessing import Process, Queue
def CC(num0,num1):
    for county_num in range(num0,num1):
        for i1 in range(1):
            for i2 in range(1):
                fnms = os.listdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\ResStock\indi_noelec_fossilfuel\\'+str(county_num)
                                +'_'+str(i1)+'_'+str(i2))
                fnms_ev = os.listdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\SC_opp_SUV')
                fnms_ev = [i for i in fnms_ev if i[-6:]!='sv.csv']
                fnms_ev = [i for i in fnms_ev if i not in os.listdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\\Results\Results_80_82\\'+str(county_num)+r'\\')]
                # print(fnms_ev,fnms)
                try:
                    os.mkdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\ResStock\dischargecons_oelec_Y82\\')
                except:pass
                try:
                    os.mkdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\ResStock\dischargecons_oelec_Y82\\'+str(county_num)+'_'+
                                                                str(i1)+'_'+str(i2)+'\\')
                except:pass
                for fnm in fnms:
                    hhec = pd.read_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\ResStock\indi_noelec_fossilfuel\\'+str(county_num)
                                +'_'+str(i1)+'_'+str(i2)+'\\'+fnm)['0'].to_numpy()
                    for fnm_ev in fnms_ev:
                        evcr = pd.read_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\SC_opp_SUV\\'+fnm_ev)['slowCR'].to_numpy()
                        cons = np.zeros(8760)
                        for i in range(8760):
                            cons[i] = min(evcr[i],hhec[i])
                        pd.DataFrame(cons,columns=['CR']).to_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\ResStock\dischargecons_oelec_Y82\\'+str(county_num)+'_'+
                                                                str(i1)+'_'+str(i2)+'\\'+
                                                                fnm_ev[:-8]+fnm[-7:])
        # print(county_num)
if __name__ == '__main__':
    # import warnings
    # warnings.filterwarnings("ignore")
    # if rank <= 46:
    #     Parkingrecog(rank*5,rank*5+5)
    # else:
    #     Parkingrecog(230+(rank-46)*4,230+(rank-46)*4+4)
    # CC(0,1)
    import warnings
    warnings.filterwarnings("ignore")
    # CC(0,1)
    procs = []
    for i in range(48):
        if i != 47:
            p = Process(target=CC, args=([i*9,i*9+9]))
        else:
            p = Process(target=CC,args=([i*9,432]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates 