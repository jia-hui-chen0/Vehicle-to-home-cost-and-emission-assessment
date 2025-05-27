#  min of slowCR and household electricity consumption is the lower bound for v2h
import pandas as pd 
import numpy as np
import os
import time

import pandas as pd 
import numpy as np
from datetime import datetime
import os
from mpi4py import MPI
import time
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def CC(num0,num1):
    for county_num in range(num0,num1):
        for i1 in range(1):
            for i2 in range(1):
                fnms = os.listdir(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC//indi_Hourly//'+str(county_num)
                                +'_'+str(i1)+'_'+str(i2))
                fnms = [i for i in fnms if i[-6:-4]=='50']
                fnms_ev = os.listdir(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC//Energy consumption_v2h_ol//'+str(county_num)+'//SC_opp_SUV')
                try:
                    os.mkdir(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC//ResStock//dischargecons_2//'+str(county_num)+'_'+
                                                                str(i1)+'_'+str(i2)+'//')
                except:pass
                for fnm in fnms:
                    hhec = pd.read_csv(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC//indi_Hourly//'+str(county_num)
                                +'_'+str(i1)+'_'+str(i2)+'//'+fnm)['0'].to_numpy()
                    for fnm_ev in fnms_ev:
                        evcr = pd.read_csv(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC//Energy consumption_v2h_ol//'+str(county_num)+'//SC_opp_SUV//'+fnm_ev)['slowCR'].to_numpy()
                        cons = np.zeros(8760)
                        for i in range(8760):
                            cons[i] = min(evcr[i],hhec[i])
                        pd.DataFrame(cons,columns=['CR']).to_csv(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC//ResStock//dischargecons_2//'+str(county_num)+'_'+
                                                                str(i1)+'_'+str(i2)+'//'+
                                                                fnm_ev[:-8]+fnm[-7:])
if __name__ == '__main__':
    import warnings
    CC(rank*4,(rank+1)*4,2024)

    # CC(rank*,(rank+1)*4,2024)
    # import warnings
    # warnings.filterwarnings("ignore")
    # procs = []
    # for i in range(48):
    #     if i != 47:
    #         p = Process(target=CC, args=([i*9,i*9+9]))
    #     else:
    #         p = Process(target=CC,args=([i*9,432]))
    #     p.start()
    #     procs.append(p)
    # for p in procs:
    #     p.join() # this blocks until the process terminates
    /nfs/turbo/seas-parthtv/jiahuic/Ford_CC/Energy consumption_adjusted_3/116
    /nfs/turbo/seas-parthtv/jiahuic/Ford_CC/Energy consumption_3//108//SC_opp_SUV