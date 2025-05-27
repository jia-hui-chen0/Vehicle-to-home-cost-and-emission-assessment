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
    
    SDrop(h)   SOC drop at hour h   ;

$load h sc_cr fc_cr sc_ec fc_ec SDrop
Variables
    sc(h)  slow charging rate at hour h 
    fc(h)  fast charging rate at hour h 
        vSOC(h)   vehicle SOC in kWh
        z         total costs;
        sc.lo(h) = 0;
        sc.up(h) = sc_cr(h);
        fc.lo(h) = 0;
        fc.up(h) = fc_cr(h);
        vSOC.lo(h) = 0.2 *82;
        vSOC.up(h) = 0.8 * 82;
        vSOC.fx(h) $ (ord(h) eq 1) = 0.8*82;
Equations
    cost      define objective function
    cCapacity(h)   observe capacity limit at hour h;


cost ..        z  =e=  sum(h,sc(h)*sc_ec(h)+fc_ec(h)*fc(h)) ;
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
    root_loc = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\\'
    # root_loc = r'G:\Dropbox (University of Michigan)\Ford_CC'
    outputdir = root_loc
    vEff = 0.95 # charging efficiency
    vCR = 10 # charging rate
    SOC = [82,153]
    fnames = os.listdir(outputdir+r'\\Energy consumption_adjusted_1_1_Y82_db\\0')
    fnames = [i for i in fnames if r'.csv' in i]
    fnames = [i for i in fnames if i[:6]=='0_0_0_']
    faillst = []
    for county_num in range(num0,num1):
        try:os.mkdir(outputdir+r'\\Result_db\\Results\Results_80_82_1\\')
        except:pass
        try:os.mkdir(outputdir+r'\\Result_db\\Results\Results_80_82_1\\'+str(county_num)+r'\\')
        except:pass
        for fname in fnames:
            cari = int(fname[2])
            urbi = int(fname[0])
            lcci = int(fname[4])

            if cari==0 and urbi ==0 and lcci==0:
                tcnm = ['_SUV','_Truck'][cari]
                df0 = pd.read_csv(outputdir+r'\\Energy consumption_adjusted_1_1_Y82_db\\'+str(county_num)+r'\\'+fname)

                vCap = SOC[cari]
                thresh = 8 # 8 hour parking

                # ws = GamsWorkspace(system_directory=r'E:\GAMS\41')
                # ws = GamsWorkspace(system_directory=r'E:\GAMS\41',debug=DebugLevel.KeepFiles)
                ws = GamsWorkspace(system_directory=r'C:\GAMS\42')
                ### Parameter prep 
                def whyto(x):
                    if x in [1,97]:
                        return 0
                    elif x == 10:
                        return 1
                    elif x == 20:
                        return 2
                    elif x == 30:
                        return 3
                    elif x in [40,70]:
                        return 4
                    elif x == 50:
                        return 5
                    elif x == 80:
                        return 6
                    else:
                        return 0
                def whyfrom(x):
                    if x in [1,2]:
                        return 0
                    elif x in [3,4,5]:
                        return 1
                    elif x in [8,9,10,19]:
                        return 2
                    elif x in [18]:
                        return 3
                    elif x in [6,11,12,14]:
                        return 4
                    elif x in [17,15,16]:
                        return 5
                    elif x in [13]:
                        return 6
                    else:
                        return 0
                trpnum = df0.shape[0]
                parkevt = [] # initial event
                strhr = 0
                endhr = df0['StrHr'][0]
                loc = whyfrom(df0['WHYFROM'][0])
                SOCDrop = df0['SDrop'][0]
                duration = endhr - strhr
                mile = df0['VMT_MILE'][0]
                if endhr != strhr:
                    parkevt.append([strhr,endhr,loc,SOCDrop,duration,mile])
                else:
                    pass
                # accumulated SOC drop
                acc_soc_drop = 0
                for i in range(trpnum):
                    strhr = df0['EndHr'][i]
                    if i != trpnum-1:
                        endhr = df0['StrHr'][i+1]
                    else:
                        endhr = 8759
                    loc = whyto(df0['WHYTRP1S'][i])
                    SOCDrop = df0['SDrop'][i]
                    acc_soc_drop += SOCDrop
                    duration = endhr - strhr
                    mile = df0['VMT_MILE'][i]
                    if acc_soc_drop >= 0.3 * vCap and duration >= thresh and loc in [0,1] :
                        parkevt.append([strhr,endhr,loc,SOCDrop,duration,mile,acc_soc_drop])
                        acc_soc_drop =0
                    else:
                        pass
                df = pd.DataFrame(parkevt,columns=['StrHr','EndHr','Location','SOCDrop','Duration','Mile','SOCDrop_acc'])

                lst_chg = [] # hours available for charging
                lst_index = df.index.to_list()
                for i in lst_index:
                    strhr = df['StrHr'][i]
                    endhr = df['EndHr'][i]
                    for k in range(strhr,endhr):
                        lst_chg.append(k+1)
                # UC charging demand, apply high penalty to fast charging
                fc_hr = pd.read_csv(outputdir+r'\\Energy consumption_adjusted_1_2_Y82_db\\'+str(county_num)+r'\\'+r'FC_opp'+tcnm+r'\\'+fname)
                hr = [str(i+1) for i in range(8760)]
                # slow charging fast charging decision variable domain
                sc_crarr = np.zeros(8760)
                sc_ecarr = np.zeros(8760)
                fc_crarr = np.ones(8760)*150
                for i in lst_chg:
                    sc_crarr[i-1] = vCR
                    sc_ecarr[i-1] = i
                    fc_crarr[i-1] = 0
                slowCR = dict(zip(hr,sc_crarr))
                # fc_crarr = fc_hr['fastCR'].to_numpy()
                fastCR = dict(zip(hr,fc_crarr))
                # energy cost slow charging and fast charging 
                sc_ec = sc_ecarr
                slowEC = dict(zip(hr,sc_ec))
                fc_ecarr = np.arange(8760) + 100000.5
                fc_ec = fc_ecarr
                fastEC = dict(zip(hr,fc_ec))
                #   hourly SOC drop
                soc_drop_df = pd.read_csv(outputdir+r'\\Energy consumption_adjusted_1_2_Y82_db\\'+str(county_num)+r'\\'+fname)
                soc_drop = soc_drop_df['SOC'].to_numpy()
                # soc_drop_df = df0
                # soc_drop = np.zeros(8760)
                # for i in range(soc_drop_df.shape[0]):
                #     StrHr = soc_drop_df['StrHr'][i]
                #     EndHr = soc_drop_df['EndHr'][i]
                #     avg_drop = soc_drop_df['SDrop'][i]/max(EndHr-StrHr,1)
                #     for Dh in range(StrHr,EndHr):
                #         soc_drop[Dh] = avg_drop
                soc_drop = dict(zip(hr,soc_drop))
                db = ws.add_database()

                h = db.add_set("h", 1, "Hours") # set h
                for hour in hr:
                    h.add_record(hour)
                sc_cr = db.add_parameter_dc("sc_cr", [h], "upper slow charging rate of hour h") # parameter sc_cr
                for hour in hr:
                    sc_cr.add_record(hour).value = slowCR[hour]
                fc_cr = db.add_parameter_dc("fc_cr", [h], "upper fast charging rate of hour h") # parameter fc_cr
                for hour in hr:
                    fc_cr.add_record(hour).value = fastCR[hour]
                sc_ec = db.add_parameter_dc("sc_ec", [h], "slow charging energy cost rate of hour h") # parameter sc_ec
                for hour in hr:
                    sc_ec.add_record(hour).value = slowEC[hour]
                fc_ec = db.add_parameter_dc("fc_ec", [h], "fast charging energy cost rate of hour h") # parameter fc_ec
                for hour in hr:
                    fc_ec.add_record(hour).value = fastEC[hour]
                SDrop = db.add_parameter_dc("SDrop", [h], "SOC drop in hour h") # parameter SDrop
                for hour in hr:
                    SDrop.add_record(hour).value = soc_drop[hour]

                # method for single parameter (0d)
                # f = db.add_parameter("f", 0, "freight in dollars per case per thousand miles")
                # g2np.gmdFillSymbolStr(db, f, np.array([[90]]))
                job = ws.add_job_from_string(get_model_text())
                opt = ws.add_options()
                opt.defines["gdxincname"] = db.name
                job.run(opt, databases = db)
                results = []
                symbs = ['sc','fc','vSOC']
                for symbi in range(3):
                    result = []
                    for ii in job.out_db[symbs[symbi]]: # slow charging rate
                        result.append(ii.level)
                    results.append(result)
                if results[2][1]!=82*0.3:
                    df_res = pd.DataFrame(results,index=['slowCR','fastCR','vSOC'],columns=[i for i in range(8760)])
                    try:os.mkdir(outputdir+r'\\Result_db\\Results\\Results_80_82_1\\')
                    except:pass
                    try:
                        os.mkdir(outputdir+r'\\Result_db\\Results\\Results_80_82_1\\'+str(county_num)+r'\\')
                    except:
                        pass
                    df_res.T.to_csv(outputdir+r'\\Result_db\\Results\\Results_80_82_1\\'+str(county_num)+r'\\'+fname)
                
if __name__ == '__main__':
    # UC(0,1)

    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(48):
        if i != 47:
            p = Process(target=UC, args=([i*9,i*9+9]))
        else:
            p = Process(target=UC,args=([i*9,432]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates