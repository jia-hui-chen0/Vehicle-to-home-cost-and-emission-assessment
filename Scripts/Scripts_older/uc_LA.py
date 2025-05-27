

import pandas as pd 
import numpy as np
from gams import *

from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
def get_model_text():
    return '''
$GDXIN _gams_py_gdb0.gdx
Sets
    h   Hours;

Parameters
    sc_cr(h)   capacity of plant i in cases
    fc_cr(h)
    sc_ec(h)   energy cost
    fc_ec(h)
    vIni
    
    SDrop(h)   SOC drop at hour h   ;

$load h sc_cr fc_cr vIni sc_ec fc_ec SDrop
Variables
    sc(h)  slow charging rate at hour h 
    fc(h)  fast charging rate at hour h 
        vSOC(h)   vehicle SOC in kWh
        z         total costs;
        sc.lo(h) = 0;
        sc.up(h) = sc_cr(h);
        fc.lo(h) = 0;
        fc.up(h) = fc_cr(h);
        vSOC.lo(h) = 0.2 *28*3.3;
        vSOC.up(h) = 1 * 28*3.3;
        vSOC.fx(h) $ (ord(h) eq 1) = vIni;
Equations
    cost      define objective function
    cCapacity(h)   observe capacity limit at hour h;


cost ..        z  =e=  sum(h,sc(h)*sc_ec(h)/0.95+fc_ec(h)*fc(h)/0.95) ;
cCapacity(h).. vSOC(h)$(ord(h) gt 1) =e= vSOC(h-1) + sc(h) +fc(h) - SDrop(h);

Model SCS /all/ ;
Option LP = cplex;
Option threads = 36;

Solve SCS using lp minimizing z ;

execute_unload "results.gdx" sc fc vSOC; '''

## uncontrolled charging


# fnames = [i for i in fnames if i!='0_0_0_21_0_soc.csv']
def UC(num0,num1):
    lst_vehnm = []
    root_loc = r'E:\Dropbox (University of Michigan)\Ford_CC\\'
    outputdir = root_loc
    vEff = 0.95 # charging efficiency
    vCR = 10 # charging rate
    SOC = [28*3.3,153]
    for county_num in range(num0,num1):
        fnames = ['20_0_0_0_20','50_0_0_0_22','80_0_0_0_47']
        fnames = [i +'_0_soc.csv' for i in fnames]
        for fname in fnames:
            cari = int(fname[2+3])

            tcnm = ['_SUV','_Truck'][cari]
            df0 = pd.read_csv(outputdir+r'\\Energy consumption_adjusted_2\\'+str(county_num)+r'\\'+fname)
            hr = [str(i+1) for i in range(8760)]

            sc_crarr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_2\\"+str(county_num)+"\\SC_opp"+tcnm+'\\'+fname)['slowCR'].to_numpy()
            fc_crarr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_2\\"+str(county_num)+"\\FC_opp"+tcnm+'\\'+fname)['fastCR'].to_numpy()
            
            slowCR = dict(zip(hr,sc_crarr))
            fastCR = dict(zip(hr,fc_crarr))
            sc_ecarr = np.arange(8760)
            # energy cost slow charging and fast charging 
            sc_ec = sc_ecarr
            slowEC = dict(zip(hr,sc_ec))
            fc_ec = sc_ecarr +10000
            fastEC = dict(zip(hr,fc_ec))
            # slowCR = np.array([[hr, sc_crarr[i]] for i in range(len(hr))], dtype=object)
            # fastCR = np.array([[hr, fc_crarr[i]] for i in range(len(hr))], dtype=object)
            soc_drop = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_2\\"+str(county_num)+"\\"+fname)['SOC'].to_numpy()

        #   hourly SOC drop
            soc_drop = dict(zip(hr,soc_drop))
            totalresults = [[],[],[]]
            ttncycle = 73
            vIni_val = SOC[cari]
            
            for cyclei in range(ttncycle):
            
                ws = GamsWorkspace(system_directory=r'E:\GAMS\44')
                
                db = ws.add_database()
                vIni = db.add_parameter('vIni',0,'Inivial SOC in kWh')
                vIni.add_record().value=vIni_val
                if cyclei!=ttncycle-1:
                    hr1 = hr[cyclei*24*5:cyclei*24*5+168]
                else:
                    hr1 = hr[cyclei*24*5:8760]
                h = db.add_set("h", 1, "Hours") # set h
                SDrop = db.add_parameter_dc("SDrop", [h], "SOC drop in hour h") # parameter SDrop
                fc_cr = db.add_parameter_dc("fc_cr", [h], "upper fast charging rate of hour h") # parameter fc_cr
                sc_ec = db.add_parameter_dc("sc_ec", [h], "slow charging energy cost rate of hour h") # parameter sc_ec
                fc_ec = db.add_parameter_dc("fc_ec", [h], "fast charging energy cost rate of hour h") # parameter fc_ec
                sc_cr = db.add_parameter_dc("sc_cr", [h], "upper slow charging rate of hour h") # parameter sc_cr
                for hour in hr1:
                    h.add_record(hour)
                    sc_cr.add_record(hour).value = slowCR[hour]
                    fc_cr.add_record(hour).value = fastCR[hour]
                    SDrop.add_record(hour).value = soc_drop[hour]
                    sc_ec.add_record(hour).value = int(slowEC[hour])
                    fc_ec.add_record(hour).value = int(fastEC[hour])
                job = ws.add_job_from_string(get_model_text())
                opt = ws.add_options()
                opt.defines["gdxincname"] = db.name
                # opt.all_model_types = "cplex"
                # try:
                
                job.run(opt, databases = db)
                results = []
                symbs = ['sc','fc','vSOC']
                for symbi in range(3):
                    result = []
                    for ii in job.out_db[symbs[symbi]]: # slow charging rate
                        result.append(ii.level)
                    results.append(result)
                    if cyclei!=ttncycle-1:
                        totalresults[symbi] = np.concatenate((np.array(totalresults[symbi]),np.array(result[0:24*5])))
                        
                    else:
                        totalresults[symbi] = np.concatenate((np.array(totalresults[symbi]),np.array(result)))
                        
                if cyclei!=ttncycle-1: vIni_val = results[2][24*5-1]
                else:pass
                print(cyclei)

            df_res = pd.DataFrame(totalresults,index=['slowCR','fastCR','vSOC'],columns=[i for i in range(8760)])

            df_res.T.to_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Case studies\\'+fname)
                
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    UC(20,21)
    # procs = []
    # for i in range(48):
    #     if i != 47:
    #         p = Process(target=UC, args=([i*9,i*9+9]))
    #     else:
    #         p = Process(target=UC,args=([i*9,432]))
    #     p.start()
    #     procs.append(p)
    # for p in procs:
    #     p.join() # this blocks until the process terminates