import pandas as pd 
import numpy as np
from gams import *
from datetime import datetime
import os
from os import getpid
import time
from pandas.tseries.holiday import USFederalHolidayCalendar
import datetime
from multiprocessing import Pool
import time
from multiprocessing import Process, Queue
from multiprocessing import Pool
import time
from multiprocessing import Process, Queue
import pandas as pd 
import numpy as np
from gams import *

from datetime import datetime
import os
import time
def CC(num0,num1,years):

    def get_model_text():
        return '''
$GDXIN _gams_py_gdb0.gdx
Sets
    h   Hours;

Parameters
    sc_cr(h)   capacity of plant i in cases
    fc_cr(h)
    vIni
    sc_ec(h)   energy cost
    fc_ec(h)
    SDrop(h)   SOC drop at hour h;

$load h sc_cr fc_cr sc_ec fc_ec SDrop vIni 

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
    vSOC.fx(h) $ (ord(h) eq 1) = vIni;
Equations
    cost      define objective function
    cCapacity(h)   observe capacity limit at hour h;


cost ..        z  =e=  sum(h,sc(h)*sc_ec(h)/0.95+fc_ec(h)*fc(h)/0.95) ;
cCapacity(h).. vSOC(h)$(ord(h) gt 1) =e= vSOC(h-1) + sc(h) +fc(h) - SDrop(h);

Model SCS /all/ ;
Option LP = cplex;
Option threads = 1;
Solve SCS using lp minimizing z ;

execute_unload "results.gdx" sc fc vSOC; '''
    # root_loc = r'E:\Dropbox (University of Michigan)\Ford_CC'
    # root_loc = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
    # root_loc = r'G:\Dropbox (University of Michigan)\Ford_CC'
    root_loc = r'F:\University of Michigan Dropbox\Jiahui Chen\Ford_CC'
    # root_loc = r'E:\Dropbox (University of Michigan)\Ford_CC'
    
    outputdir = root_loc

    vEff = 0.95 # charging efficiency
    vCR = [10,10] # charging rate
    SOC = [82,153]
    faillst = []
    lst_vehnm = []

    
    # fnames = [i for i in fnames if i!='0_0_0_21_0_soc.csv']
    ctydf = pd.read_csv(outputdir+r'\\2020_Gaz_counties_national_0728_tempreg.csv')
    
    uqlst = np.unique(ctydf['tempreg'])
    for year in years:
        try: os.mkdir(outputdir+r'\\Result_cc\\')
        except:pass
        try:
            
            os.mkdir(outputdir+r'\\Result_cc\\Results_Y82_'+str(year)+'_rev')
            
        except:pass
    for year in years:
        ctydf.set_index(keys=ctydf['county_num'],inplace=True)
        num01 = num0
        for county_num in range(num01,num1):
            try: os.mkdir(outputdir+r'\\Result_cc\\Results_Y82_'+str(year)+'_rev\\'+str(county_num)+'_'+str(0)+'_'+str(0)+r'\\')
            except:pass
            # 1st submission
            # fnames = os.listdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82_db\1\FC_opp_SUV\\')
            # fnames = [i for i in fnames if i[:6]=='0_0_0_']
            # fnames = [i for i in fnames if i not in os.listdir(outputdir+r'\\Results\Results_80_82\\'+str(county_num)+r'\\')]
            # fnames = [i for i in fnames if r'.csv' in i]
            # 2nd submission
            fnames = ['0_0_0_0_0_soc.csv', '0_0_0_10_0_soc.csv', '0_0_0_11_0_soc.csv', '0_0_0_12_0_soc.csv', '0_0_0_13_0_soc.csv', '0_0_0_14_0_soc.csv', '0_0_0_15_0_soc.csv', '0_0_0_16_0_soc.csv', '0_0_0_17_0_soc.csv', '0_0_0_18_0_soc.csv', '0_0_0_19_0_soc.csv', '0_0_0_1_0_soc.csv', '0_0_0_20_0_soc.csv', '0_0_0_21_0_soc.csv', '0_0_0_22_0_soc.csv']
            import os
            result_dir = outputdir + r'\\Result_cc\\Results_Y82_' + str(year) + '_rev\\' + str(county_num) + '_' + str(0) + '_' + str(0) + r'\\'
            if os.path.exists(result_dir):
                files_in_dir = [f for f in os.listdir(result_dir) if os.path.isfile(os.path.join(result_dir, f))]
                # Only consider .csv files
                csv_files_in_dir = [f for f in files_in_dir if f.endswith('.csv')]
                # Check if all files in fnames are present as .csv in the directory, and there are no extra .csv files
                if set(csv_files_in_dir) == set(fnames) and len(csv_files_in_dir) == len(fnames):
                    continue
                else:
                    exec = 1
            else:
                exec = 1
            if exec == 1:   
                ctydf_1 = ctydf[ctydf['tempreg']==uqlst[county_num]]
                countyBA = ctydf_1['reeds_ba'].to_list()[0]
                for fname_i in range(len(fnames)):
                    fname = fnames[fname_i]
                    cari = int(fname[2])
                    tcnm = ['_SUV','_Truck'][cari]
                    sc_crarr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82_db\\"+str(county_num)+"\\SC_opp"+tcnm+'\\'+fname)['slowCR'].to_numpy()
                    fc_crarr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82_db\\"+str(county_num)+"\\FC_opp"+tcnm+'\\'+fname)['fastCR'].to_numpy()
                    # electricity price (supplier)
                    cambium_df = pd.read_csv(outputdir+r'\\Cambium\\hourly_balancingArea\\' + countyBA +'_'+str(year)+'.csv')
                    emission = cambium_df['srmer_co2e'].to_numpy()/1000
                    cost = cambium_df['total_cost_enduse'].to_numpy()/1000
                    cost = cost + emission*0.051

                    hr = [str(i+1) for i in range(8760)]
                    # slow charging fast charging decision variable domain
                    slowCR = dict(zip(hr,sc_crarr))
                    fastCR = dict(zip(hr,fc_crarr))
                    fastCR = dict(zip(hr,fc_crarr))
                    # energy cost slow charging and fast charging 
                    sc_ec = cost+0.075
                    slowEC = dict(zip(hr,sc_ec))
                    
                    fc_ec = sc_ec + 0.2
                    # fc_ec = cost/1000 + 0.1+0.075
                    fastEC = dict(zip(hr,fc_ec))
                    # slowCR = np.array([[hr, sc_crarr[i]] for i in range(len(hr))], dtype=object)
                    # fastCR = np.array([[hr, fc_crarr[i]] for i in range(len(hr))], dtype=object)
                    # hourly SOC drop
                    soc_drop = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82_db\\"+str(county_num)+"\\"+fname)['SOC'].to_numpy()
                    soc_drop = dict(zip(hr,soc_drop))
                    ttncycle = 36
                            
                    totalresults = [[],[],[],[]]
                    vIni_val = SOC[cari]*0.8
                    for cyclei in range(ttncycle):
                        # ws = GamsWorkspace(system_directory=r'/home/jiahuic/Downloads/gams43.4_linux_x64_64_sfx',debug=DebugLevel.KeepFiles)
                        # ws = GamsWorkspace(system_directory=r'E:\GAMS\41')
                        ws = GamsWorkspace(system_directory=r'F:\GAMS\44')
                        # ws = GamsWorkspace(system_directory=r'C:\GAMS\42')
                        
                        db = ws.add_database()
                        vIni = db.add_parameter('vIni',0,'Inivial SOC in kWh')
                        vIni.add_record().value=vIni_val
                        vCap = db.add_parameter('vCap',0,'Capacity')
                        vCap.add_record().value=SOC[cari]
                        if cyclei!=ttncycle-1:
                            hr1 = hr[cyclei*24*10:cyclei*24*10+24*14]
                        else:
                            hr1 = hr[cyclei*24*10:8760]
                            
                        h = db.add_set("h", 1, "Hours") # set h
                        sc_cr = db.add_parameter_dc("sc_cr", [h], "upper slow charging rate of hour h") # parameter sc_cr
                        fc_cr = db.add_parameter_dc("fc_cr", [h], "upper fast charging rate of hour h") # parameter fc_cr
                        sc_ec = db.add_parameter_dc("sc_ec", [h], "slow charging energy cost rate of hour h") # parameter sc_ec
                        fc_ec = db.add_parameter_dc("fc_ec", [h], "fast charging energy cost rate of hour h") # parameter fc_ec
                        SDrop = db.add_parameter_dc("SDrop", [h], "SOC drop in hour h") # parameter SDrop
                        sd_dr = db.add_parameter_dc("sd_dr",[h])
                        
                        for hour in hr1:
                            h.add_record(hour)
                            sc_cr.add_record(hour).value = slowCR[hour]
                            sd_dr.add_record(hour).value = 0
                            fc_cr.add_record(hour).value = fastCR[hour]
                            SDrop.add_record(hour).value = soc_drop[hour]
                            sc_ec.add_record(hour).value = slowEC[hour]
                            fc_ec.add_record(hour).value = fastEC[hour]
                        # method for single parameter (0d)
                        # f = db.add_parameter("f", 0, "freight in dollars per case per thousand miles")
                        # g2np.gmdFillSymbolStr(db, f, np.array([[90]]))
                        job = ws.add_job_from_string(get_model_text())
                        opt = ws.add_options()
                        opt.defines["gdxincname"] = db.name
                        # opt.defines["gdxincname"] = db.name
                        # opt.all_model_types = "cplex"

                        # try:
                        job.run(opt, databases = db)
                        results = []
                        symbs = ['sc','fc','vSOC','sd']
                        for symbi in range(3):
                            result = []
                            for ii in job.out_db[symbs[symbi]]: # slow charging rate
                                result.append(ii.level)
                            results.append(result)
                            if cyclei!=ttncycle-1:
                                totalresults[symbi] = np.concatenate((np.array(totalresults[symbi]),np.array(result[0:24*10])))
                                
                            else:
                                totalresults[symbi] = np.concatenate((np.array(totalresults[symbi]),np.array(result)))
                        totalresults[3]=np.zeros(8760)
                        if cyclei!=ttncycle-1: vIni_val = results[2][24*10-1]
                        else:pass
                        # print(cyclei)
                                
                    df_res = pd.DataFrame(totalresults,index=['slowCR','fastCR','vSOC','sd'],columns=[i for i in range(8760)])
                    df_res.T.to_csv(outputdir+r'\\Result_cc\\Results_Y82_'+str(year)+'_rev\\'+str(county_num)+'_'+str(0)+'_'+str(0)+r'\\'+fname)
                    print(str(county_num)+"_"+str(fname))
                        
                        # except:faillst.append([county_num,fnames])

    # faildf = pd.DataFrame(faillst,columns=['county_num','fnames'])
    # faildf.to_csv(outputdir+'\\failure_'+str(year)+str(num0)+'_'+str(num1)+'.csv')
if __name__ == '__main__':
    # all processes
            
    # CC(0,1,[2024])
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    a=16
    b=432//a
    for i in range(a):
        if i != a-1:
            p = Process(target=CC, args=([i*b,i*b+b,[2030]]))
        else:
            p = Process(target=CC,args=([i*b,432,[2030]]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates
    # import warnings
    # a = 48
    # b = 9
    # procs = []
    # for yea in [2024,2030,2040]:
    #     for i in range(a):
    #         if i != a-1:
    #             p = Process(target=CC, args=([i*b,i*b+b,yea]))
    #         else:
    #             p = Process(target=CC,args=([i*b,432,yea]))
    #         p.start()
    #         procs.append(p)
    #     for p in procs:
    #         p.join() 
