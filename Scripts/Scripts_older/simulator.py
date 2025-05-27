from multiprocessing import Process
basedir = '/home/jiahuic/Ford_CC'
import pandas as pd
import numpy as np
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
from multiprocessing import Pool
import random
import os
import requests
import warnings
warnings.filterwarnings("ignore")
def simulator(region_num,start):
    coelst = [0.8813149497306003,
 0.848345059783396,
 0.8347526017917626,
 0.8148986143832327,
 0.8598851930889437,
 1.1265153174481006,
 0.8671760359285938,
 0.8062908883545367,
 0.8110228934530891]
    coe = [1*coelst[i] for i in range(9)][region_num]
    basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\\'
    veh = 0
    vehnm = ['','_truck']
    simu = 1
    cal = USFederalHolidayCalendar()
    # the number of driving profiles to be simulated, simulate 1 to test
    region = ['Pacific',
    'East North Central',
    'Mountain',
    'Middle Atlantic',
    'South Atlantic',
    'East South Central',
    'West North Central',
    'New England',
    'West South Central'][region_num]
    try:os.mkdir(basedir+r'\\Driving_profile_simu\\Results'+vehnm[veh]+'\\'+region+'\\')
    except: pass
    veh_fname = basedir+r'\Raw\veh_'+ region+'.csv'
    trip_fname = basedir+r'\Raw\trip_'+ region+'.csv'
    df_veh = pd.read_csv(veh_fname)
    df_trip = pd.read_csv(trip_fname)
    df_veh['HHEVID'] = df_veh.apply(lambda x: str(x['HOUSEID'])+ '_' + str(x['VEHID']),axis=1)
    allowedvehid = os.listdir(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Raw\trip_regions\\'+region)
    allowedvehid = [i[:-4] for i in allowedvehid]
    holidays = cal.holidays(start='2021-01-01', end='2021-12-31').to_pydatetime()
    # 1,3 car SUV 2,4 van truck
    # travel day of week TRAVDAY 1,2,3,4,5 weekday 6,7 weekends
    # URBRUR 1,2 urban 3,4 non urban
    urban_g1 = [1]
    urban_g2 = [2]
    TRAVDAY_g1 = [1,2,3,4,5]
    TRAVDAY_g2 = [6,7]
    car_group_1 = [1,3]
    car_group_2 = [2,4]
    lcc_1 = [-9,1,2] # no child
    lcc_2 = [i for i in range(3,9)] # with child
    lcc_3 = [9,10] # retired
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
        elif x in [3,4,5]:
            return 1
        elif x in [8,9,10,19]:
            return 2
        elif x in [18]:
            return 2
        elif x in [6,11,12,14]:
            return 2
        elif x in [17,15,16]:
            return 2
        elif x in [13]:
            return 2
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
            return 2
        elif x in [40,70]:
            return 2
        elif x == 50:
            return 2
        elif x == 80:
            return 2
        else:
            return 0

    # individual trip householdid_vehid
    # vehid_region shape 
    # 2,    2,      3,      2,          7,          7
    # urb,  car,    lcc,    weekend,    orig_home,  dest_home
    vehid_region = [[[[] for i in range(3)] for i in range(2)] for i in range(2)]

    for urbi in range(2):
        for cari in range(1):
            for lcci in [2]:
            # for lcci in range(3):
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
                            org = df1['WHYFROM'][df1.index[0]]
                            dest = df1['WHYTRP1S'][df1.index[-1]]
                            loc1 = whyfrom(org)
                            loc2 = whyto(dest)
                            vehid_org_dest[loc1][loc2].append(str(hh)+'_'+str(vv))
                    vehid_region[urbi][cari][lcci].append(vehid_org_dest)
    df_act = pd.read_csv(basedir+r'\\Driving_profile_simu\activeness_'+region+'.csv')
    # for each household and vehicle type, draw driving profiles
    # append profile to lst

    # function: judge if from/to home, return 0 if to/from home 
    def dest_home(x):
        if x ==1:
            return 0
        else:
            return 1
    # 0 trips
    lst_0tp = []
    # use one dataframe to store the driving profile of one car 
    dflst = [[[[] for i in range(3)] for j in range(2)] for k in range(2)]

    ## draw samples
    for urbi in range(2):
        for cari in range(1):
            for lcci in [2]:
            # for lcci 
                for i in range(simu):
                    
                    # set the date of the first day
                    date1 = datetime.date(2021,1,1)
                    # assume start from home
                    start_loc = 0
                    fname0 = os.listdir(basedir+r'\Raw\trip_regions\\'+region+'\\')[0]
                    df_head = pd.read_csv(basedir+r'\Raw\trip_regions\\'+region+'\\'+fname0)
                    df_head['DAY'] = 1
                    df = df_head[0:0]
                    for dayi in range(365):
                        
                        weekend_i = weekendfun(date1)
                        # is it active? 
                        weekend_i_1 = weekendfun(date1 + datetime.timedelta(days=1))
                        # if random.uniform(0,1) <= [22328/30407,8359/12006][weekend_i]:
                        if random.uniform(0,1) <= df_act.transpose()[1:][2][urbi*12+weekend_i*6+cari*3+lcci]/coe:
                            vehid = []
                            for grp_i in range(3):
                                vehid = vehid+ vehid_region[urbi][cari][lcci][weekend_i][start_loc][grp_i]
                            if len(vehid) ==0:
                                lst_0tp.append([urbi,cari,lcci,weekend_i,start_loc])
                                start_loc = 0
                            else: pass
                            vehid = []
                            for grp_i in range(3):
                                vehid = vehid+ vehid_region[urbi][cari][lcci][weekend_i][start_loc][grp_i]
                            # uniformly draw random sample 
                            vehid = [i for i in vehid if i in allowedvehid]
                            a = int(random.uniform(0, len(vehid)))
                            try:
                                vehid_sam = vehid[a]
                            except:
                                print([urbi,cari,lcci,weekend_i,start_loc,region_num])
                                print(len(vehid))
                            vehid_sam = vehid[a]
                                
                            df_new = pd.read_csv(basedir+r'\Raw\trip_regions\\'+region+'\\'+vehid_sam+'.csv')
                            df_new['DAY'] = dayi
                            df = pd.concat([df,df_new])
                            # destination of trip so far
                            df.reset_index(drop=True,inplace=True)
                            start_loc = whyto(df['WHYTRP1S'][df.index[-1]]) 

                        else:
                            pass
                        date1+=datetime.timedelta(days=1)
                        
                    dflst[urbi][cari][lcci].append(df)

    ## store the samples

    for urbi in range(2):
        for cari in range(1):
            for lcci in [2]:
                for veh_i in range(len(dflst[urbi][cari][lcci])):
                    df_dflst = pd.DataFrame(dflst[urbi][cari][lcci][veh_i])
                    df_dflst = df_dflst[["TRPMILES", "TRVLCMIN","STRTTIME",
                                         'ENDTIME','WHYFROM','WHYTRP1S','DAY','VMT_MILE'
                                         ]]
                    id = str(urbi) + '_' + str(cari) + '_' + str(lcci) + '_' +str(veh_i+start)
                    try:os.mkdir(basedir+r'\\Driving_profile_simu\\Results\\'+region+'\\')
                    except:pass
                    df_dflst.to_csv(basedir+r'\\Driving_profile_simu\\Results\\'+region+'\\'+ id+ '.csv')
if __name__ == "__main__":
    # simulator(0,0)
    for regi in range(9):
        procs = []
        for iii in range(10):
            p = Process(target=simulator, args=([regi,iii]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join()