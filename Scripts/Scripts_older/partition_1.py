##This script partitions the original travel records
## into desired trip and household level records
import pandas as pd
import numpy as np
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
import random
import os
import warnings
warnings.filterwarnings("ignore")
from multiprocessing import Process
from multiprocessing import Pool
import random
import os
import requests
import warnings
warnings.filterwarnings("ignore")
cal = USFederalHolidayCalendar()
holidays = cal.holidays(start='2021-01-01', end='2021-12-31').to_pydatetime()
basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\\Ford_CC\\'
def funcs(region_num):
    region = ['Pacific',
    'East North Central',
    'Mountain',
    'Middle Atlantic',
    'South Atlantic',
    'East South Central',
    'West North Central',
    'New England',
    'West South Central'][region_num]
    
    try:os.mkdir(basedir+r'\Raw\trip_regions\\'+region)
    except: pass
    veh_fname = basedir + r'\Raw\veh_'+ region+'.csv'
    trip_fname = basedir + r'\Raw\trip_'+ region+'.csv'
    df_veh = pd.read_csv(veh_fname)
    df_trip = pd.read_csv(trip_fname)
    df_trip['HHEVTP'] = df_trip.apply(lambda x: str(x['HOUSEID'])+ '_' + str(x['VEHID'])+'_'+str(x['TDTRPNUM']),axis=1)
    
    df_trip['TRPMILES_1'] = df_trip['TRPMILES']
    df_trip['TRVLCMIN_1'] = df_trip['TRVLCMIN']
    df_trip['ENDTIME_1'] = df_trip['ENDTIME']
    df_trip['STRTTIME_1'] = df_trip['STRTTIME']

    df_trip['STRTTIME'] = df_trip.apply(lambda row: row['STRTTIME']+2400 if row['STRTTIME']<100 else row['STRTTIME'], axis=1)
    df_trip['ENDTIME'] = df_trip.apply(lambda row: row['ENDTIME']+2400 if row['ENDTIME']<100 else row['ENDTIME'], axis=1)

    df_trip['TRVLCMIN'] = df_trip.apply(lambda row: ((int(str(row['ENDTIME'])[:-2])-int(str(row['STRTTIME'])[-2:]))*60
                                        + (int(str(row['ENDTIME'])[-2:])-int(str(row['STRTTIME'])[-2:])))
                                        if row['TRVLCMIN_1']<=0
                                        else row['TRVLCMIN_1'],axis=1)
    df_trip['TRVLCMIN'] = df_trip.apply(lambda row: 1
                                        if row['TRVLCMIN'] == 0
                                        else row['TRVLCMIN'],axis=1)

    df_trip['TRPMILES'] = df_trip.apply(lambda row: 
                                        (int(row['TRVLCMIN'])/60)
                                        *20
                                        if row['TRPMILES_1']/(row['TRVLCMIN']/60)>=150
                                         else row['TRPMILES_1'],axis=1
    )
    df_trip['TRPMILES'] = df_trip.apply(lambda row: 
                                    (int(row['TRVLCMIN'])/60)
                                    *20
                                    if row['TRPMILES']<=0
                                        else row['TRPMILES'],axis=1
    )
    df_trip['Speed'] = df_trip.apply(lambda row: 
                                    row['TRPMILES']/(row['TRVLCMIN']/60),axis=1
    )
    # 1,3 car SUV 2,4 van truck
    # travel day of week TRAVDAY 1,2,3,4,5 weekday 6,7 weekends
    # URBRUR 1,2 urban 3,4 non urban
    urban_g1 = [1]
    urban_g2 = [2]
    TRAVDAY_g1 = [1,2,3,4,5]
    TRAVDAY_g2 = [6,7]
    car_group_1 = [1,3]
    car_group_2 = [2,4]
    lcc_1 = [-9,1,2]
    lcc_2 = [i for i in range(3,9)]
    lcc_3 = [9,10]
    veh_num_1 = df_veh[df_veh['VEHTYPE'].isin(car_group_1)]
    veh_num_2 = df_veh[df_veh['VEHTYPE'].isin(car_group_2)]
    urban_g = [urban_g1,urban_g2]
    TRAVDAY_g = [TRAVDAY_g1,TRAVDAY_g2]
    car_group = [car_group_1,car_group_2]
    lfcycle = [lcc_1,lcc_2,lcc_3]

    # 0 weekday 1 holiday/weekend
    def weekendfun(x):
        no = x.weekday()
        if no >= 5 or x in holidays:
            return 1
        else:
            return 0
    def whyfrom(x):
        if x in [1,2]:
            return 0
        elif x in [2,3,4,5]:
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

    # individual trip householdid_vehid
    # vehid_region shape 
    # 2,    2,      3,      2,          7,          7
    # urb,  car,    lcc,    weekend,    orig_home,  dest_home
    vehid_region = [[[[] for i in range(3)] for i in range(2)] for i in range(2)]

    for urbi in range(2):
        for cari in range(2):
            for lcci in range(3):
                for weekend_i in range(2):
                    df_trip_1 = df_trip[df_trip['URBRUR'].isin(urban_g[urbi])][df_trip['VEHTYPE'].isin(car_group[cari])][df_trip['LIF_CYC'].isin(lfcycle[lcci])][df_trip['TRAVDAY'].isin(TRAVDAY_g[weekend_i])]
                    df_indi_trp = df_trip_1

                    # draw household id and vehid
                    hhid = df_indi_trp['HOUSEID']
                    
                    # household org dest, [org home[[dest home],[dest non home]],[org non home[dest home],[dest non home]]]
                    vehid_org_dest = [[[] for i in range(7)] for i in range(7)]
                    for hh in [*set(df_indi_trp['HOUSEID'].to_list())]:
                        for vv in [*set(df_indi_trp[df_indi_trp['HOUSEID']==hh]['VEHID'].to_list())]:
                            df1 = df_indi_trp[df_indi_trp['HOUSEID']==hh][df_indi_trp['VEHID']==vv]
                            # org = df1['WHYFROM'][df1.index[0]]
                            # dest = df1['WHYTRP1S'][df1.index[-1]]
                            # loc1 = whyfrom(org)
                            # loc2 = whyto(dest)
                            # df1 = df_indi_trp[df_indi_trp['HOUSEID']==hh][df_indi_trp['VEHID']==vv]
                            # org = df1['WHYFROM'][df1.index[0]]
                            # dest = df1['WHYTRP1S'][df1.index[-1]]
                            # loc1 = whyfrom(org)
                            # loc2 = whyto(dest)
                            # df2 = df1.loc[df1['TDTRPNUM']==np.unique(df1['TDTRPNUM'])[0]]

                            # df2 = df2.loc[df2[:].index[np.where(df2['TRPMILES']==max(df2['TRPMILES']))[0][0]:np.where(df2['TRPMILES']==max(df2['TRPMILES']))[0][0]+1]]
                            # for tpid in np.unique(df1['HHEVTP'])[1:]:
                            #     df3 = df1.loc[df1['HHEVTP']==tpid]
                            #     df3 = df3.loc[df3[:].index[0:1]]
                            #     df2= pd.concat([df2,df3])                            
                            # vehid_org_dest[loc1][loc2].append(str(hh)+'_'+str(vv))
                            # df1 = df1[[]]
                            try:os.mkdir(basedir+r'\Raw\trip_regions\\'+region+r'\\')
                            except:pass
                            df1.to_csv(basedir+r'\Raw\trip_regions\\'+region+r'\\'+str(hh)+'_' + str(vv) +'.csv')
                    vehid_region[urbi][cari][lcci].append(vehid_org_dest)
if __name__ == "__main__":
    
    procs = []
    for iii in range(9):
        p = Process(target=funcs, args=([iii]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
    import winsound

    # frequency is set to 500Hz
    freq = 500

    # duration is set to 100 milliseconds
    dur = 100

    winsound.Beep(freq, dur)