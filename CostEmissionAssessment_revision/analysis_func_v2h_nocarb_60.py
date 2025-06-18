# no missing 0613
from gams import *
import numpy as np
# import gams.numpy as gams2numpy
import sys
import pandas as pd
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
# from analysis_func import ana_func
def ana_func(num0,num1,year,cc_ip,urb,car,lcc):
# num0,num1,year,cc_ip,urb,car,lcc=0,1,2024,0,0,0,0
    # outputdir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
    outputdir = r'F:\University of Michigan Dropbox\Jiahui Chen\Ford_CC'
    # outputdir = r'G:\\Dropbox (University of Michigan)\Ford_CC'
    ctydf = pd.read_csv(outputdir + r'\\2020_Gaz_counties_national_0728_tempreg.csv')
    ctydf.set_index(keys=ctydf['county_num'],inplace=True)
    # number of columns:
    lenc = 4
    # UC urb car lcc
    lst = [[] for i in range(lenc)]
    cc_hand = ['s','_cc','_v2h'][cc_ip]
    county_num_lst = [i for i in range(num0,num1) if i in ctydf['county_num'].to_list()]
    for county_numi in range(len(county_num_lst)):
        county_num = county_num_lst[county_numi]
        countyBA = ctydf.loc[ctydf['tempreg']==county_num]['reeds_ba'].to_list()[0]
        yr = year
        for building in ['_0_0']:
            fnames = ['0_0_0_0_0_soc.csv', '0_0_0_10_0_soc.csv', '0_0_0_11_0_soc.csv', '0_0_0_12_0_soc.csv', '0_0_0_13_0_soc.csv', '0_0_0_14_0_soc.csv', '0_0_0_15_0_soc.csv', '0_0_0_16_0_soc.csv', '0_0_0_17_0_soc.csv', '0_0_0_18_0_soc.csv', '0_0_0_19_0_soc.csv', '0_0_0_1_0_soc.csv', '0_0_0_20_0_soc.csv', '0_0_0_21_0_soc.csv', '0_0_0_22_0_soc.csv']
            # fnames = os.listdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82_db\\'+str(county_num))
            # fnames = [i for i in fnames if i[:6]=='0_0_0_']
            fnames = [f[:-8]+'_50'+f[-4:] for f in fnames if r'.csv' in f]
            cambium_df = pd.read_csv(outputdir+r'\\Cambium\\hourly_balancingArea\\' + countyBA +'_'+yr+'.csv')
            f_cost = cambium_df['total_cost_enduse'].to_numpy()/1000
            f_emi = cambium_df['srmer_co2e'].to_numpy()/1000
            f_AER = cambium_df['aer_load_co2e'].to_numpy()/1000
            # print(len(fnames))

            if len(fnames) > 0:
                c_lst = [[],[],[]]
                
                for fname in fnames:
                    res = pd.read_csv(outputdir+r'\\Result'+cc_hand+r'\\Results_'+'80_Y60_'+year+r'_nocarb\\'+str(county_num)+building+'\\'+fname)
                    sc = res['slowCR'].to_numpy()
                    fc = res['fastCR'].to_numpy()
                    if cc_ip ==2:
                        sd = res['sd'].to_numpy()
                    else:
                        sd = 0
                    carbprice = 0*f_emi #0.051*f_emi
                    
                    # aggregate
                    # if sum(sc)+sum(fc)>1300:
                    c_lst[0].append(np.sum((f_cost+carbprice+0.075)*(sc/0.95-sd*0.95)+(f_cost+0.2+carbprice+0.075)*fc/0.95))
                    # c_lst[1].append(np.sum((f_cost+0.1+carbprice+0.075)*fc))
                    c_lst[1].append(np.sum(f_emi*(sc/0.95-sd*0.95)+f_emi*fc/0.95))#kg
                    c_lst[2].append(np.sum(f_AER*(sc/0.95-sd*0.95)+f_AER*fc/0.95))#kg
                    # c_lst[3].append(np.sum(f_emi*fc))#kg
                    # else:
                        # pass
                for k in range(3):
                    # print(c_lst[k])
                    
                    lst[k].append(np.median(c_lst[k]))
                lst[3].append(county_num)
    df1 = pd.DataFrame(data=lst)
    df2 = df1.transpose()
    df2.columns = ['Cost','Emissions','Emissions_AER','county_num']
    df2.to_csv(outputdir+r'\\CostEmissionAssessment_revision\csv_trb\\'
                +str(num0)+'_'+str(num1)+'_'+str(year)+'_'
                +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_60.csv')
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    a=48
    b=9
    charge =2
    for yr in [2024,2030,2040]:
        yr = str(yr)
        for i in range(a):
            if i != a-1:
                p = Process(target=ana_func, args=([i*b,i*b+b,yr,charge,0,0,0]))
            else:
                p = Process(target=ana_func,args=([i*b,432,yr,charge,0,0,0]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join() # this blocks until the process terminates