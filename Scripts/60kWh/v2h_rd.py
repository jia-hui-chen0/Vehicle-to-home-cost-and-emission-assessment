# from mpi4py import MPI
# import time

# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()
# size = comm.Get_size()
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
    SDrop(h)   SOC drop at hour h   
    sd_dr(h) ;

$load h sc_cr fc_cr sc_ec fc_ec SDrop vIni sd_dr

Variables
    sc(h)  slow charging rate at hour h 
    fc(h)  fast charging rate at hour h 
    sd(h) 
    vSOC(h)   vehicle SOC in kWh
    z         total costs;
    sc.lo(h) = 0;
    sc.up(h) = sc_cr(h);
    fc.lo(h) = 0;
    fc.up(h) = fc_cr(h);
    sd.lo(h) = 0;
    sd.up(h) = sd_dr(h);
    vSOC.lo(h) = 0.2 *60;
    vSOC.up(h) = 0.8 * 60;
    vSOC.fx(h) $ (ord(h) eq 1) = vIni;
Equations
    cost      define objective function
    cCapacity(h)   observe capacity limit at hour h;


cost ..        z  =e=  sum(h,sc(h)*sc_ec(h)/0.95+fc_ec(h)*fc(h)/0.95-(sd(h)*sc_ec(h)*0.95)) ;
cCapacity(h).. vSOC(h)$(ord(h) gt 1) =e= vSOC(h-1) + sc(h) +fc(h) - SDrop(h)-sd(h);

Model SCS /all/ ;
Option LP = cplex;
Option threads = 19;
Solve SCS using lp minimizing z ;

execute_unload "results.gdx" sc fc vSOC sd; '''
    # root_loc = r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC'
    # root_loc = r'G:\Dropbox (University of Michigan)\Ford_CC'
    root_loc = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
    outputdir = root_loc

    vEff = 0.95 # charging efficiency
    vCR = [10,10] # charging rate
    SOC = [60,153]
    faillst = []
    lst_vehnm = []

    # fnames = [i for i in fnames if i!='0_0_0_21_0_soc.csv']
    ctydf = pd.read_csv(outputdir+r'\\2020_Gaz_counties_national_0728_tempreg.csv')
    uqlst = np.unique(ctydf['tempreg'])
    # try:
        
    #     os.mkdir(outputdir+r'\\Result_v2h\\')
    # except:pass
    # try:
        
    #     os.mkdir(outputdir+r'\\Result_v2h\\Results_'+str(year))
    #     # try: os.mkdir(outputdir+r'\\Result_v2h\\Results_'+str(year)+'\\'+str(county_num)+r'\\')
    #     # except:pass
    # except:pass
    ctydf.set_index(keys=ctydf['county_num'],inplace=True)

    for county_num in range(num0,num1):
        fnames = os.listdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\'+str(county_num))
        fnames = [i for i in fnames if i[:6]=='0_0_0_']
        fnames = [i for i in fnames if r'.csv' in i][:5]

        
        ctydf_1 = ctydf[ctydf['tempreg']==uqlst[county_num]]
        countyBA = ctydf_1['reeds_ba'].to_list()[0]
        for fname_i in range(len(fnames)):
            costttl = 0

            fname = fnames[fname_i]
            cari = int(fname[2])
            tcnm = ['_SUV','_Truck'][cari]
            sc_crarr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\SC_opp"+tcnm+'\\'+fname)['slowCR'].to_numpy()
            fc_crarr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\FC_opp"+tcnm+'\\'+fname)['fastCR'].to_numpy()
            for year in [years]:
                # electricity price (supplier)
                cambium_df = pd.read_csv(outputdir+r'\\Cambium\\hourly_balancingArea\\' + countyBA +'_'+str(year)+'.csv')
                emission = cambium_df['srmer_co2e'].to_numpy()
                cost = cambium_df['total_cost_enduse'].to_numpy()
                cost = cost + emission*0.051

                hr = [str(i+1) for i in range(8760)]
                # slow charging fast charging decision variable domain
                slowCR = dict(zip(hr,sc_crarr))
                fastCR = dict(zip(hr,fc_crarr))
                fastCR = dict(zip(hr,fc_crarr))
                # energy cost slow charging and fast charging 
                sc_ec = cost/1000+0.075
                slowEC = dict(zip(hr,sc_ec))
                fc_ec = cost/1000 + 0.2+0.075
                fastEC = dict(zip(hr,fc_ec))
                # slowCR = np.array([[hr, sc_crarr[i]] for i in range(len(hr))], dtype=object)
                # fastCR = np.array([[hr, fc_crarr[i]] for i in range(len(hr))], dtype=object)

                # hourly SOC drop
                soc_drop = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\"+fname)['SOC'].to_numpy()
                soc_drop = dict(zip(hr,soc_drop))
                fname_evhh = fname[:-8]+'_50'+fname[-4:]

                ttncycle = 36
                for i1 in range(1):
                    for i2 in range(1):
                        sd_drarr = pd.read_csv(outputdir +r'\\ResStock\\dischargecons_Y82\\'+str(county_num)+'_'+str(i1)+'_'+str(i2)+'\\'+fname_evhh)['CR'].to_numpy()
                        CR = dict(zip(hr,sd_drarr))
                        totalresults = [[],[],[],[]]
                        vIni_val = SOC[cari]*0.8
                        for cyclei in range(ttncycle):
                            # ws = GamsWorkspace(system_directory=r'/home/jiahuic/Downloads/gams43.4_linux_x64_64_sfx')
                            # ws = GamsWorkspace(system_directory=r'E:\GAMS\41',debug=DebugLevel.KeepFiles)
                            ws = GamsWorkspace(system_directory=r'C:\GAMS\42')


                            db = ws.add_database()
                            vIni = db.add_parameter('vIni',0,'Inivial SOC in kWh')
                            vIni.add_record().value=vIni_val
                            if cyclei!=ttncycle-1:
                                hr1 = hr[cyclei*24*10:cyclei*24*10+24*20]
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
                                sd_dr.add_record(hour).value = CR[hour]
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
                            for symbi in range(4):
                                result = []
                                for ii in job.out_db[symbs[symbi]]: # slow charging rate
                                    result.append(ii.level)
                                results.append(result)
                                if cyclei!=ttncycle-1:
                                    totalresults[symbi] = np.concatenate((np.array(totalresults[symbi]),np.array(result[0:24*10])))
                                    
                                else:
                                    totalresults[symbi] = np.concatenate((np.array(totalresults[symbi]),np.array(result)))
                                    
                            if cyclei!=ttncycle-1: vIni_val = results[2][24*10-1]
                            else:pass
                            if cyclei!=ttncycle-1:costttl+=(sum(np.array(results[0])[0:24*10]*(cost/1000+0.075)[cyclei*24*10:cyclei*24*10+24*10])/0.95+
                                  sum(np.array(results[1])[0:24*10]*(cost/1000+0.275)[cyclei*24*10:cyclei*24*10+24*10])/0.95-
                                  sum(np.array(results[3])[0:24*10]*(cost/1000+0.075)[cyclei*24*10:cyclei*24*10+24*10])*0.95)
                            else: costttl+=(sum(np.array(results[0])*(cost/1000+0.075)[cyclei*24*10:8760])/0.95+
                                  sum(np.array(results[1])*(cost/1000+0.275)[cyclei*24*10:8760])/0.95-
                                  sum(np.array(results[3])*(cost/1000+0.075)[cyclei*24*10:8760])*0.95)
                        df_res = pd.DataFrame(totalresults,index=['slowCR','fastCR','vSOC','sd'],columns=[i for i in range(8760)])
                        # try: 
                        #     os.mkdir(outputdir+r'\\Result_v2h\\')
                        # except: pass
                        try: 
                        #     # os.mkdir(outputdir+r'\\Results_opt_3\\')
                            os.mkdir(outputdir+r'\\Result_v2h\\Results_80_Y60_'+str(year)+r'_1\\')
                        except: pass
                        try: os.mkdir(outputdir+r'\\Result_v2h\\Results_80_Y60_'+str(year)+r'_1\\'+str(county_num)+'_'+str(i1)+'_'+str(i2)+r'\\')
                        except: pass
                        df_res.T.to_csv(outputdir+r'\\Result_v2h\\Results_80_Y60_'+str(year)+r'_1\\'+str(county_num)+'_'+str(i1)+'_'+str(i2)+r'\\'+fname_evhh)
                        # except:faillst.append([county_num,fnames])
            print(costttl)
    # faildf = pd.DataFrame(faillst,columns=['county_num','fnames'])
    # faildf.to_csv(outputdir+'\\failure_'+str(year)+str(num0)+'_'+str(num1)+'.csv')
if __name__ == '__main__':
    # all processes
    import warnings
    warnings.filterwarnings("ignore")
    a = 48
    b = 9
    procs = []
    for yea in [2024,2030,2040]:
        for i in range(a):
            if i != a-1:
                p = Process(target=CC, args=([i*b,i*b+b,yea]))
            else:
                p = Process(target=CC,args=([i*b,432,yea]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join() 

            

