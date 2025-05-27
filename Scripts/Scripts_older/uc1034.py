from gams import *
import numpy as np
import gams.numpy as gams2numpy
import sys
import pandas as pd
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
        vSOC.lo(h) = 0.2 *28*3.3;
        vSOC.up(h) = 1 * 28*3.3;
        vSOC.fx(h) $ (ord(h) eq 1) = 28*3.3;
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

lst_vehnm = []
root_loc = r'/home/jiahuic/Ford_CC'
outputdir = r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC'
vEff = 0.95 # charging efficiency
vCR = 10 # charging rate
SOC = [28*3.3,153]
def UC(num0,num1):
    faillst = []
    for county_num in range(num0,num1):
        if county_num not in range(2310,2322):
            fnames = os.listdir(outputdir+r'/Energy consumption/'+str(county_num))
            fnames = [i for i in fnames if r'.csv' in i and i[4]==i[2]==i[0]=='0']
            for fname in fnames:
                veh_fname = fname[:-10]
                cari = int(veh_fname[2])
                urbi = int(veh_fname[0])
                lcci = int(veh_fname[4])
                if cari==0 and urbi ==0 and lcci==0:
                    tcnm = ['_SUV','_Truck'][cari]
                    df0 = pd.read_csv(outputdir+r'/Energy consumption/'+str(county_num)+r'/'+veh_fname+'_0_soc.csv')

                    vCap = SOC[cari]
                    thresh = 8 # 8 hour parking
                    try:
                        ws = GamsWorkspace(system_directory=r'/home/jiahuic/Downloads/gams43.4_linux_x64_64_sfx')
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
                            if acc_soc_drop >= 0.5 * vCap and duration >= thresh:
                                parkevt.append([strhr,endhr,loc,SOCDrop,duration,mile,acc_soc_drop])
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
                        fc_hr = pd.read_csv(outputdir+r'/Energy consumption/'+str(county_num)+r'/'+r'FC_opp'+tcnm+r'/'+veh_fname+'_0_soc.csv.csv')
                        # # electricity price (supplier)
                        # cambium_df = pd.read_csv(r'E:\Dropbox (University of Michigan)\Backup\2022_UMich_Parth\Driving profile\Data\MEF\hourly_state\\' + state +'_'+str(year)+'.csv')
                        # cost = cambium_df['total_cost_enduse'].to_numpy()

                        hr = [str(i+1) for i in range(8760)]
                        hr_num = [i for i in range(8760)]
                        # slow charging fast charging decision variable domain
                        sc_crarr = np.zeros(8760)
                        sc_ecarr = np.zeros(8760)
                        for i in lst_chg:
                            sc_crarr[i-1] = vCR
                            sc_ecarr[i-1] = i
                        slowCR = dict(zip(hr,sc_crarr))
                        fc_crarr = np.zeros(8760)
                        fc_ecarr = np.zeros(8760)
                        for i in fc_hr['Hours'].to_list():
                            fc_crarr[i-1] = 150
                            fc_ecarr[i-1] = i + 10**4
                        fastCR = dict(zip(hr,fc_crarr))
                        # energy cost slow charging and fast charging 
                        sc_ec = sc_ecarr
                        slowEC = dict(zip(hr,sc_ec))
                        fc_ec = fc_ecarr
                        fastEC = dict(zip(hr,fc_ec))
                        # slowCR = np.array([[hr, sc_crarr[i]] for i in range(len(hr))], dtype=object)
                        # fastCR = np.array([[hr, fc_crarr[i]] for i in range(len(hr))], dtype=object)

                    #   hourly SOC drop
                        soc_drop_df = df0
                        soc_drop = np.zeros(8760)
                        for i in range(soc_drop_df.shape[0]):
                            StrHr = soc_drop_df['StrHr'][i]
                            EndHr = soc_drop_df['EndHr'][i]
                            avg_drop = soc_drop_df['SDrop'][i]/max(EndHr-StrHr,1)
                            for Dh in range(StrHr,EndHr):
                                soc_drop[Dh] += avg_drop
                        soc_drop = dict(zip(hr,soc_drop))
                        db = ws.add_database()
                        g2np = gams2numpy.Gams2Numpy(ws.system_directory)

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
                        # opt.all_model_types = "cplex"
                        # try:
                        
                        job.run(opt, databases = db)
                        result = [np.zeros(8760) for i in range(3)]
                        sc_res = g2np.gmdReadSymbolStr(job.out_db, "sc")
                        fc_res = g2np.gmdReadSymbolStr(job.out_db, "fc")
                        vSOC_res = g2np.gmdReadSymbolStr(job.out_db, "vSOC")
                        for ii in range(len(g2np.gmdReadSymbolStr(job.out_db, "sc"))): # slow charging rate
                            result[0][ii] = sc_res[ii][1]
                            result[1][ii] = fc_res[ii][1]
                            result[2][ii] = vSOC_res[ii][1]

                        df_res = pd.DataFrame(result,index=['slowCR','fastCR','vSOC'],columns=[i for i in range(8760)])
                        for year in [2024]:
                            df_res.T.to_csv(outputdir+r'/Results/Results_2024/'+str(county_num)+r'/'+veh_fname+'.csv')
                    except:
                        try:os.mkdir(r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC/Analysis/diagn/'+str(county_num)+'_'+str(veh_fname)+'_UC')
                        except:pass
                        ws = GamsWorkspace(debug=DebugLevel.KeepFiles,system_directory=r'/home/jiahuic/Downloads/gams43.4_linux_x64_64_sfx'
                            ,working_directory=r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC/Analysis/diagn'+str(county_num)+'_'+str(veh_fname)+'_UC')
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
                            if acc_soc_drop >= 0.8 * vCap and duration >= thresh:
                                parkevt.append([strhr,endhr,loc,SOCDrop,duration,mile,acc_soc_drop])
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
                        fc_hr = pd.read_csv(outputdir+r'/Energy consumption/'+str(county_num)+r'/'+r'FC_opp'+tcnm+r'/'+veh_fname+'_0_soc.csv.csv')
                        # # electricity price (supplier)
                        # cambium_df = pd.read_csv(r'E:\Dropbox (University of Michigan)\Backup\2022_UMich_Parth\Driving profile\Data\MEF\hourly_state\\' + state +'_'+str(year)+'.csv')
                        # cost = cambium_df['total_cost_enduse'].to_numpy()

                        hr = [str(i+1) for i in range(8760)]
                        hr_num = [i for i in range(8760)]
                        # slow charging fast charging decision variable domain
                        sc_crarr = np.zeros(8760)
                        sc_ecarr = np.zeros(8760)
                        for i in lst_chg:
                            sc_crarr[i-1] = vCR
                            sc_ecarr[i-1] = i
                        slowCR = dict(zip(hr,sc_crarr))
                        fc_crarr = np.zeros(8760)
                        fc_ecarr = np.zeros(8760)
                        for i in fc_hr['Hours'].to_list():
                            fc_crarr[i-1] = 150
                            fc_ecarr[i-1] = i + 10**4
                        fastCR = dict(zip(hr,fc_crarr))
                        # energy cost slow charging and fast charging 
                        sc_ec = sc_ecarr
                        slowEC = dict(zip(hr,sc_ec))
                        fc_ec = fc_ecarr
                        fastEC = dict(zip(hr,fc_ec))
                        # slowCR = np.array([[hr, sc_crarr[i]] for i in range(len(hr))], dtype=object)
                        # fastCR = np.array([[hr, fc_crarr[i]] for i in range(len(hr))], dtype=object)

                    #   hourly SOC drop
                        soc_drop_df = df0
                        soc_drop = np.zeros(8760)
                        for i in range(soc_drop_df.shape[0]):
                            StrHr = soc_drop_df['StrHr'][i]
                            EndHr = soc_drop_df['EndHr'][i]
                            avg_drop = soc_drop_df['SDrop'][i]/max(EndHr-StrHr,1)
                            for Dh in range(StrHr,EndHr):
                                soc_drop[Dh] += avg_drop
                        soc_drop = dict(zip(hr,soc_drop))
                        db = ws.add_database()
                        g2np = gams2numpy.Gams2Numpy(ws.system_directory)

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
                        # opt.all_model_types = "cplex"
                        # try:
                        
                        job.run(opt, databases = db)
                        result = [np.zeros(8760) for i in range(3)]
                        sc_res = g2np.gmdReadSymbolStr(job.out_db, "sc")
                        fc_res = g2np.gmdReadSymbolStr(job.out_db, "fc")
                        vSOC_res = g2np.gmdReadSymbolStr(job.out_db, "vSOC")
                        for ii in range(len(g2np.gmdReadSymbolStr(job.out_db, "sc"))): # slow charging rate
                            result[0][ii] = sc_res[ii][1]
                            result[1][ii] = fc_res[ii][1]
                            result[2][ii] = vSOC_res[ii][1]

                        print(str(county_num)+'_'+str(veh_fname)+'_UC')
                        faildf.append([county_num,fnames])
                        # except:
                        #     gams2np = gnp.Gams2Numpy(ws.system_directory)

                        #     result = [np.zeros(8760) for i in range(3)]
                        #     sc_res = gams2np.gdxReadSymbolRaw(ws.working_directory+r'\results.gdx','sc')
                        #     fc_res = gams2np.gdxReadSymbolRaw(ws.working_directory+r'\results.gdx','fc')
                        #     vSOC_res = gams2np.gdxReadSymbolRaw(ws.working_directory+r'\results.gdx','vSOC')

                        #     for ii in range(len(g2np.gmdReadSymbolStr(job.out_db, "sc"))): # slow charging rate
                        #         result[0][ii] = sc_res[ii][1]
                        #         result[1][ii] = fc_res[ii][1]
                        #         result[2][ii] = vSOC_res[ii][1]
                        #     print(veh_fname)
                        #     lst_vehnm.append(veh_fname)
                        #     df_res = pd.DataFrame(result,index=['slowCR','fastCR','vSOC'],columns=[i for i in range(8760)])
                        #     df_res.T.to_csv(r'E:\Dropbox (University of Michigan)\Backup\2022_UMich_Parth\Driving profile\Data\\Results'+tcnm1+'\Results_'+str(year)+'\\UC\\'+veh_fname+'.csv')
        faildf = pd.DataFrame(faillst,columns=['county_num','fnames'])
        faildf.to_csv(outputdir+'//failure//'+str(year)+str(num0)+'_'+str(num1)+'.csv')
UC(2064,2065)