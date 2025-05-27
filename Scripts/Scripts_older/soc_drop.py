import pandas as pd 
import numpy as np
from datetime import datetime
from meteostat import Stations, Point, Hourly,Normals
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue

def soc_drop(num0, num1):
    import pandas as pd 
    import numpy as np
    from datetime import datetime
    from meteostat import Stations, Point, Hourly,Normals
    import os
    for county_num in range(num0,num1):
        if county_num not in [i for i in range(2310,2321)]:

            basedir = '/home/jiahuic/Ford_CC'
            outdir = '/nfs/turbo/seas-parthtv/jiahuic/Ford_CC'
            df_loc = pd.read_csv(basedir + r'//Server/2020_Gaz_counties_national.csv')
            ind = df_loc.index[county_num]
            locla = df_loc['INTPTLAT'][ind]
            loclong = df_loc['INTPTLONG'][ind]
            region = df_loc['Region'][ind]
            # temperature
            # 16-20 avg
            # lst_temp = []
            pt = Point(locla, loclong)
            stations = Stations()
            stations = stations.nearby(locla, loclong)
            station = stations.fetch(20)
            start = datetime(2011, 12, 31, 23, 59)
            end = datetime(2020, 1, 2, 00, 1)
            success = 0
            station_i = 0
            while success ==0:
                try:
                    data = Hourly(station.index[station_i],start,end)

                    data = data.fetch()
                    data = data.loc[:,['temp']]
                    data.interpolate(inplace=True)

                    hr = pd.Timedelta(value=1,unit='hours')
                    yr = np.zeros(8760)
                    yr[0] = 1
                    # find hourly average by hour
                    for h in range(8760):
                        temps = []
                        for a in range(7):
                            # find the temperature for the timeslot
                            # if failed, pass
                            time = datetime(2013+a, 1, 1, 0, 0) + (h+1) * hr
                            try:
                                temps.append(data['temp'][time])
                            except:
                                pass
                        temps = [i for i in temps if np.isnan(i)==False]
                        try:
                            temp_avg = sum(temps)/len(temps)
                            if np.isnan(temp_avg) == True:
                                if h >= 24:
                                    temp_avg = yr[h-24]
                                    print('h prevday')
                                    print(loclong,locla)
                                else:
                                    print('h < 24')
                                    print(loclong,locla)
                            yr[h] = temp_avg
                            success = 1
                        except:pass
                    
                except:
                    station_i +=1
            driving_profile_foldername = basedir+r'//Driving_profile_simu//Results//'+region+'//'
            # MPGe fuel economy from fuel economy
            cty_lst = [129,78]
            hwy_lst = [116,63]
            # URB mix, city and hwy
            urbmix = [0.55,0.45]

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
            for fname in os.listdir(driving_profile_foldername):
                df = pd.read_csv(driving_profile_foldername+fname)
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
                    comb = cityNT
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
                    

                    if endhr - strhr == 0:
                        # temperature of the hour
                        tem = yr[strhrnum]
                        coeT = tempimpact(tem)
                        SDrop = trpmile * comb *coeT

                    elif endhr - strhr >= 1:
                        # time percentage
                        time_perc = np.ones(int(endhr - strhr)+1)*60
                        time_perc[0]=60-strmin
                        time_perc[-1] = endmin
                        mile_perc = np.array([trpmile*time_perc[k]/np.sum(time_perc) for k in range(int(endhr - strhr)+1)])
                        # temperature of the hours
                        tem = [yr[strhrnum+k] for k in range(int(endhr - strhr)+1)]
                        coeT_lst = np.array([tempimpact(tem[k]) for k in range(int(endhr - strhr)+1)])
                        SDrop_sub = coeT_lst * mile_perc * comb
                        SDrop = np.sum(SDrop_sub)
                    SDrops.append(SDrop)
                    strhrs.append(strhrnum)
                    endhrs.append(strhrnum+endhr-strhr)
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
                try: os.mkdir(outdir+r'//Energy consumption//')
                except: pass                
                try: os.mkdir(outdir+r'//Energy consumption//'+str(county_num))
                except: pass
                outputdir = outdir+r'//Energy consumption//'+str(county_num)+'//'
                df.to_csv(outputdir+fname[:-4]+'_0'+'_soc.csv')

if __name__ == '__main__':
    # soc_drop(93,3108)
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(36):
        if i != 35:
            p = Process(target=soc_drop, args=([i*86,i*86+86]))
        else:
            p = Process(target=soc_drop,args=([i*86,3108]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates

    