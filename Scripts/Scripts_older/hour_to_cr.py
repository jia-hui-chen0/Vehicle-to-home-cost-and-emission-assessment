

import pandas as pd 
import numpy as np
from gams import *

from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
def CC(num0,num1,years):
    root_loc = r'G:\Dropbox (University of Michigan)\Ford_CC'
    # root_loc = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
    # root_loc = r'E:\\Dropbox (University of Michigan)\Ford_CC'
    outputdir = root_loc

    vCR = [10,10] # charging rate

    # fnames = [i for i in fnames if i!='0_0_0_21_0_soc.csv']
    ctydf = pd.read_csv(outputdir+r'\\2020_Gaz_counties_national_0728_tempreg.csv')
    uqlst = np.unique(ctydf['tempreg'])
    
    
    ctydf.set_index(keys=ctydf['county_num'],inplace=True)
    
    for county_num in range(num0,num1):
        try:
            os.mkdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\')
        except:pass
        try:
            os.mkdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\'+str(county_num))
        except:pass
        try:
            os.mkdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\FC_opp_SUV\\')
        except:pass
        try:
            os.mkdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\SC_opp_SUV\\')
        except:pass
        try:
            os.mkdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\FC_opp_Truck\\')
        except:pass
        try:
            os.mkdir(outputdir+r'\\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\SC_opp_Truck\\')
        except:pass
        fnames = os.listdir(outputdir+r'\\Energy consumption_adjusted_1_1_Y82\\'+str(county_num))
        fnames = [i for i in fnames if (r'.csv' in i)][:5]
        fnames = [i for i in fnames if i[0:6]=='0_0_0_']
        # fnames = [i for i in fnames if (r'.csv' in i) & (i[2]=='0' and i[0] =='0' and i[4]=='0')]
        ctydf_1 = ctydf[ctydf['tempreg']==uqlst[county_num]]
        countyBA = ctydf_1['reeds_ba'].to_list()[0]
        try:
            os.mkdir(r'E:\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2_Y82\\'+str(county_num))
            os.mkdir(r'E:\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\'+'FC_opp_SUV')
            os.mkdir(r'E:\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\'+'SC_opp_SUV')
        except:pass
        for fname in fnames:
            # veh_fname = fname[:-10]
            cari = int(fname[2])
            # vehi =int(veh_fname[6:])
            tcnm = ['_SUV','_Truck'][cari]
            df0 = pd.read_csv(outputdir+r'\\Energy consumption_adjusted_1_1_Y82\\'+str(county_num)+r'\\'+fname)
            sc_hr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\SC_opp"+tcnm+'\\'+fname)
            fc_hr = pd.read_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\FC_opp"+tcnm+'\\'+fname)
            for year in [years]:


                # electricity price (supplier)
                cambium_df = pd.read_csv(outputdir+r'\\Cambium\\hourly_balancingArea\\' + countyBA +'_'+str(year)+'.csv')
                emission = cambium_df['srmer_co2e'].to_numpy()
                cost = cambium_df['total_cost_enduse'].to_numpy()
                cost = cost + emission*0.051

                hr = [str(i+1) for i in range(8760)]
                # slow charging fast charging decision variable domain
                sc_crarr = np.zeros(8760)
                for i in sc_hr['Hours'].to_list():
                    sc_crarr[i-1] = vCR[cari]
                sc_crarr1 = np.zeros(4380)
                slowCR = dict(zip(hr,sc_crarr))
                fc_crarr = np.zeros(8760)
                for i in fc_hr['Hours'].to_list():
                    fc_crarr[i-1] = 150
                fc_crarr1 = np.zeros(4380)
                for i in range(4380):
                    sc_crarr1[i]=sum(sc_crarr[2*i:2*i+2])
                    fc_crarr1[i]=sum(fc_crarr[2*i:2*i+2])
                
                # hourly SOC drop
                soc_drop_df = df0
                soc_drop = np.zeros(8760)
                for i in range(soc_drop_df.shape[0]):
                    StrHr = soc_drop_df['StrHr'][i]
                    EndHr = soc_drop_df['EndHr'][i]
                    avg_drop = soc_drop_df['SDrop'][i]/max(EndHr+1-StrHr,1)
                    for Dh in range(StrHr,EndHr+1):
                        soc_drop[Dh] = avg_drop
                # soc_drop1 = np.zeros(8760)
                # for i in range(8760):
                #     sc_crarr1[i]=sum(sc_crarr[2*i:2*i+2])
                #     fc_crarr1[i]=sum(fc_crarr[2*i:2*i+2])
                #     soc_drop1[i]=sum(soc_drop[2*i:2*i+2])
                pd.DataFrame(fc_crarr,columns=['fastCR']).to_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\FC_opp"+tcnm+'\\'+fname)
                pd.DataFrame(sc_crarr,columns=['slowCR']).to_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\SC_opp"+tcnm+'\\'+fname)
                    
                pd.DataFrame(soc_drop,columns=['SOC']).to_csv(outputdir + r"\\Energy consumption_adjusted_1_2_Y82\\"+str(county_num)+"\\"+fname)
                
                soc_drop = dict(zip(hr,soc_drop))

if __name__ == '__main__':
    # CC(0,1,2040)
    for yr in [2024]:
        import warnings
        warnings.filterwarnings("ignore")
        procs = []
        for i in range(48):
            if i != 47:
                p = Process(target=CC, args=([i*9,i*9+9,yr]))
            else:
                p = Process(target=CC,args=([i*9,432,yr]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join() # this blocks until the process terminates
            

