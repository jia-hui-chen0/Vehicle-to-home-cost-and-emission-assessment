import pandas as pd 
import numpy as np
from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue

total = 0


def ICEV(num0, num1):
    import pandas as pd 
    import numpy as np
    from datetime import datetime
    import os
    basedir = r'C:\jiahuic\Dropbox (University of Michigan)\Ford_CC'

    outdir = basedir
    df_loc_1 = pd.read_csv(outdir + r'\\2020_Gaz_counties_national_0728_tempreg.csv')
    uqlst = np.unique(df_loc_1['tempreg'])
    
    for county_num in range(num0,num1):
        # if county_num not in [i for i in range(2310,2321)]:
        try: os.mkdir(outdir+r'\\Energy consumption_ICEV\\'+str(county_num))
        except:pass
        ind = df_loc_1.index[county_num]
        df_loc = df_loc_1[df_loc_1['tempreg']==uqlst[county_num]]
        region = df_loc['Region'].to_list()[0]
        driving_profile_foldername = basedir+r'\\Driving_profile_simu_trb\\Results\\'+region+'\\'
        outputdir = outdir+r'\\Energy consumption_ICEV\\'+str(county_num)+'\\'
        hr = pd.Timedelta(value=1,unit='hours')
        yr = pd.read_csv(outdir+r'\\tempAdjusted\\'+str(uqlst[county_num])+'.csv')['0']

        
        nlst = [i for i in os.listdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Driving_profile_simu_trb\Results\East North Central') 
            if '0_0_0_' in i]
        nlst = [i[:-4] for i in nlst]
        # MPGe fuel economy from fuel economy
        cty_lst = [1/43,1/25.4]
        hwy_lst = [1/36,1/31.3]
        # URB mix, city and hwy
        # temp function
        def tempimpact(tem1):
                                # temperature threshold cold
            TC = 15.5
            # temperature hot
            TH = 23.9
            if tem1 < TC:
                coeT1 = 0.0064*(TC-tem1) + 1
            elif TC <=tem1<=TH:
                coeT1 = 1
            elif TH <= tem1:
                coeT1 = 0.0129*(tem1-TH) + 1
            return coeT1
        for fname in nlst:
            df = pd.read_csv(driving_profile_foldername+fname+'.csv')
            trp_num = df.shape[0] # total trip number
            cari = int(fname[2])
            urbi = int(fname[0])
            urban = urbi
            #fe calculation
            # change MPGe to kWh/mile
            # change from lab to real-world (exclude temp impact)
            # if urban == 0:
            #     # hwyOR = 33.70/hwy_lst[cari]
            #     cityNT = 1/(0.00187+(1.134/(cty_lst[cari])) )
            #     comb = cityNT
            if urban ==0:
                hwyNT = 1/(0.00269+(1.235/(hwy_lst[cari])) )
                # hwyOR = 33.70/hwy_lst[cari]
                cityNT = 1/(0.00187+(1.134/(cty_lst[cari])) )
                comb = hwyNT*0.45+cityNT*0.55
            # elif urban ==2: # not in use
            #     cityOR = 33.70/cty_lst[cari]
            #     hwyOR = 33.70/hwy_lst[cari]
            #     cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
            #     hwyNT = 33.70/hwy_lst[cari]*0.7 + 0.87*(hwyOR - 33.70/hwy_lst[cari]*0.7)
            #     comb = 0.45* hwyNT + 0.55*cityNT
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
            try: os.mkdir(outdir+r'//Energy consumption_ICEV//')
            except: pass                
            try: os.mkdir(outdir+r'//Energy consumption_ICEV//'+str(county_num))
            except: pass
            outputdir = outdir+r'//Energy consumption_ICEV//'+str(county_num)+'//'
            df.to_csv(outputdir+fname[:-4]+'.csv')
            # print(str(county_num)+'_'+fname)
    
if __name__ == '__main__':
    # all processes
    # if rank <= 46:
    #     soc_drop(rank*5,rank*5+5)
    # else:
    #     soc_drop(230+(rank-46)*4,230+(rank-46)*4+4)
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(48):
        if i != 47:
            p = Process(target=ICEV, args=([i*9,i*9+9]))
        else:
            p = Process(target=ICEV,args=([i*9,433]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates

    