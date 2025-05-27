
import pandas as pd 
import numpy as np
from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
start_time = time.time()
total = 0


def soc_drop(num0, num1,urbi,lcci):
    import pandas as pd 
    import numpy as np
    from datetime import datetime
    import os
    for county_num in range(num0,num1): # county num is now temp reg
        hr = pd.Timedelta(value=1,unit='hours')

        basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\\'

        outdir = basedir
        df_loc = pd.read_csv(outdir + r'2020_Gaz_counties_national_0728_tempreg.csv')
        uqlst = np.unique(df_loc['tempreg'])
        # ind = df_loc[df_loc['tempreg']==uqlst[county_num]]
        # 16-20 avg
        # lst_temp = []
        region = df_loc[df_loc['tempreg']==uqlst[county_num]]['Region'].to_list()[0]
        driving_profile_foldername = basedir+r'\\Driving_profile_simu_trb\\Results\\'+region+'\\'

        # MPGe fuel economy from fuel economy
        cty_lst = [127*82/28*100/330,78]
        hwy_lst = [117*82/28*100/330,63]
        yr = pd.read_csv(outdir+r'\\tempAdjusted\\'+str(county_num)+'.csv')['0'].to_numpy()
        # temp function
        def tempimpact(tem1):
            # temperature threshold cold
            TC = 15.5
            # temperature hot
            TH = 23.9
            if tem1 < TC:
                coeT1 = 0.0242*(TC-tem1) + 1
            elif TC <=tem1<=TH:
                coeT1 = 1
            elif TH <= tem1:
                coeT1 = 0.0210*(tem1-TH) + 1
            return coeT1
        for fname in [i for i in os.listdir(driving_profile_foldername) if i[0:6]==str(urbi)+'_0_'+str(lcci)+'_']:
        # for fname in [j for j in os.listdir(driving_profile_foldername) if j[0]==j[2]== '1' and j[4]=='0']:

            df = pd.read_csv(driving_profile_foldername+fname)
            df = df.loc[df['DAY']<=364]
            trp_num = df.shape[0] # total trip number

            cari = int(fname[2])
            urbi = int(fname[0])
            urban = urbi
            #fe calculation
            # change MPGe to kWh/mile
            # change from lab to real-world (exclude temp impact)
            if urban == 0:
                cityOR = 33.70/cty_lst[cari]
                # hwyOR = 33.70/hwy_lst[cari]
                cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
                hwyOR = 33.70/hwy_lst[cari]
                hwyNT = 33.70/hwy_lst[cari]*0.7 + 0.87*(hwyOR - 33.70/hwy_lst[cari]*0.7)
                comb = (hwyNT*0.45+cityNT*0.55)
            elif urban ==1:
                hwyOR = 33.70/hwy_lst[cari]
                hwyNT = 33.70/hwy_lst[cari]*0.7 + 0.87*(hwyOR - 33.70/hwy_lst[cari]*0.7)
                cityOR = 33.70/cty_lst[cari]
                # hwyOR = 33.70/hwy_lst[cari]
                cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
                comb = hwyNT*0.55+cityNT*0.45
            elif urban ==2: # not in use
                cityOR = 33.70/cty_lst[cari]
                hwyOR = 33.70/hwy_lst[cari]
                cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
                hwyNT = 33.70/hwy_lst[cari]*0.7 + 0.87*(hwyOR - 33.70/hwy_lst[cari]*0.7)
                comb = 0.45* hwyNT + 0.55*cityNT
            SDrops = []
            strhrs = []
            endhrs = []
            for ev_i in range(trp_num):
                # divide tripmiles equally to hours
                # tripmiles
                trpmile = df['TRPMILES'][ev_i]
                
                # trip time
                trpt = df['TRVLCMIN'][ev_i]
                # to deltatime hour
                trpt = hr * trpt/60

                starttime = str(df['STRTTIME'][ev_i])
                endtime = str(df['ENDTIME'][ev_i])
                day = df['DAY'][ev_i]
                if len(starttime)>=3:
                    strhr = int(starttime[:-2])
                    
                    strmin = int(starttime[-2:])
                    if len(endtime)>=3:
                        endhr = int(endtime[:-2])
                        endmin = int(endtime[-2:])
                    else:
                        endhr = 0
                        endmin = int(endtime)
                else:
                    strhr = 0
                    strmin = int(starttime)
                    if len(endtime)>=3:
                        endhr = int(endtime[:-2])
                        endmin = int(endtime[-2:])
                    else:
                        endhr = 0
                        endmin = int(endtime)
                # hour number (8760)
                strhrnum = day*24+int(strhr)
                endhrnum = day*24+int(endhr)
                
                if endhrnum >= 8760:
                    endhrnum = endhrnum % 24+8736
                    strhrnum = strhrnum % 24+8736
                else:
                    pass
                if endhrnum - strhrnum == 0:
                    # temperature of the hour
                    tem = yr[strhrnum]

                    
                    coeT = tempimpact(tem)
                    SDrop = trpmile * comb *coeT

                elif endhrnum - strhrnum >= 1:
                    # time percentage
                    time_perc = np.ones(int(endhrnum - strhrnum)+1)*60
                    time_perc[0]=60-strmin
                    time_perc[-1] = endmin
                    mile_perc = np.array([trpmile*time_perc[k]/np.sum(time_perc) for k in range(int(endhrnum - strhrnum)+1)])
                    # temperature of the hours
                    tem = [yr[strhrnum+k] for k in range(int(endhrnum - strhrnum)+1)]
                    coeT_lst = np.array([tempimpact(tem[k]) for k in range(int(endhrnum - strhrnum)+1)])
                    SDrop_sub = coeT_lst * mile_perc * comb
                    SDrop = np.sum(SDrop_sub)
                SDrops.append(SDrop)
                strhrs.append(strhrnum)
                endhrs.append(endhrnum)
            df['SDrop'] = SDrops
            df['EndHr'] = endhrs
            df['StrHr'] = strhrs
            # df.drop(df.loc[df['VMT_MILE']==-1].index, inplace=True)
            df.sort_values(by='StrHr',axis=0,inplace=True)
            # df.drop(df['Unnamed: 0'])
            df.reset_index(inplace=True)
            try: df.drop(columns=['Unnamed: 0','Unnamed: 0.1', 'Unnamed: 0.1.1','index'], inplace=True)
            except: pass
            try: df.drop(columns=['Unnamed: 0'], inplace=True)
            except: pass
            try: os.mkdir(outdir+r'\\Energy consumption_adjusted_1_1_Y82_db\\')
            except: pass                
            try: os.mkdir(outdir+r'\\Energy consumption_adjusted_1_1_Y82_db\\'+str(county_num))
            except: pass
            outputdir = outdir+r'\\Energy consumption_adjusted_1_1_Y82_db\\'+str(county_num)+'\\'
            df.to_csv(outputdir+fname[:-4]+'_0'+'_soc.csv')
# if __name__ == '__main__':
#     # all processes
#     if rank <= 46:
#         soc_drop(rank*5,rank*5+5)
#     else:
#         soc_drop(230+(rank-46)*4,230+(rank-46)*4+4)
if __name__ == '__main__':
    # all processes
    # if rank <= 46:
    #     soc_drop(rank*5,rank*5+5)
    # else:
    #     soc_drop(230+(rank-46)*4,230+(rank-46)*4+4)
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    a=19
    b=432//a
    for urbi in range(1):
        for lcci in range(1):
            for i in range(a):
                if i != a-1:
                    p = Process(target=soc_drop, args=([i*b,i*b+b,urbi,lcci]))
                else:
                    p = Process(target=soc_drop,args=([i*b,432,urbi,lcci]))
                p.start()
                procs.append(p)
            for p in procs:
                p.join() # this blocks until the process terminates


    