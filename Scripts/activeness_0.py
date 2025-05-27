import pandas as pd
import numpy as np
import pandas as pd 
import numpy as np
from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
from soc_drop_func import *
basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
def actvness(region_num):
    region = ['Pacific',
    'East North Central',
    'Mountain',
    'Middle Atlantic',
    'South Atlantic',
    'East South Central',
    'West North Central',
    'New England',
    'West South Central'][region_num]
    veh_fname =basedir+ r'\Raw\veh_'+ region+'.csv'
    trip_fname = basedir+r'\Raw\trip_'+ region+'_1.csv'
    df_veh = pd.read_csv(veh_fname)
    """[df_veh['BESTMILE']<=0]"""
    df_veh=df_veh.loc[df_veh['BESTMILE']>500]
    df_veh=df_veh.loc[df_veh['VEHAGE']<=20]
    # vehicle side id
    df_veh = df_veh[df_veh['VEHID'].isin([i for i in range(1,13)])]
    hhvv = []
    hhlst = [*set(df_veh[df_veh['VEHTYPE'].isin([1,2,3,4])]['HOUSEID'].to_list())]
    for hi in hhlst:
        df1 = df_veh[df_veh['HOUSEID']==hi]
        for vi in df1['VEHID'].to_list():
            hhvv.append(str(hi) + '_' + str(vi))
    df_trip = pd.read_csv(trip_fname)
    df_trip['HHVV'] = df_trip.apply(lambda x: str(x['HOUSEID'])+ '_' + str(x['VEHID']),axis=1)

    # trip side id
    df_trip = df_trip[df_trip['VEHID'].isin([i for i in range(1,13)])]
    df_trip = df_trip[df_trip['HHVV'].isin(hhvv)]
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
    # total vehicle count
    lst = []
    for ii in range(2):
        for jj in range(2) :
            for kk in range(2) :
                for ll in range(3):
                    i = [urban_g1,urban_g2][ii]
                    j = [TRAVDAY_g1,TRAVDAY_g2][jj]
                    k = [car_group_1, car_group_2][kk]
                    l = lfcycle[ll]
                    lst.append(df_veh[df_veh['VEHTYPE'].isin(k)][df_veh['URBRUR'].isin(i)][df_veh['TRAVDAY'].isin(j)][df_veh['LIF_CYC'].isin(l)].shape[0])
    # total vehicle count
    lst = []

    # driver count
    # DRVRCNT, vehicle record
    driver_num = 0

    # filtered with Urb car lcc
    hhvv_1 = []
    for ii in range(2):
        for jj in range(2) :
            for kk in range(2):
                for ll in range(3):
                    i = [urban_g1,urban_g2][ii]
                    k = [car_group_1, car_group_2][kk]
                    j = TRAVDAY_g[jj]
                    l = lfcycle[ll]
                    df_1 = df_veh[df_veh['VEHTYPE'].isin(k)][df_veh['URBRUR'].isin(i)][df_veh['LIF_CYC'].isin(l)][df_veh['TRAVDAY'].isin(j)]
                    lst.append(df_1.shape[0])
                    
                    for hid in [*set(df_1['HOUSEID'].to_list())]:
                        df_2 = df_1[df_1['HOUSEID']==hid]
                        vlst = df_2['VEHID'].to_list()
                        driver_num += df_2['DRVRCNT'][df_2.index[0]]
                        for vid in vlst:
                            hhvv_1.append(str(hid)+'_'+str(vid))
    # vehicles that have trips
    # veh_region URBRUR TRAVDAY VEHTYPE TRPTRANS
    # filter out the vehicles 
    hh_veh_lst = [[],[],[],[],[],[],[],[],[],[]]
    hh_veh_num = []
    hh_adult_num = []
    hh_driver_num = []
    for hi in hhlst:
        df1 = df_trip[df_trip['HOUSEID']==hi]
        vehid = [*set(df1['VEHID'].to_list())]
        for vi in vehid:
            hh_veh_lst[0].append(str(hi)+'_'+str(vi))
            # df3 vehicle record
            df3 = df_veh[df_veh['HOUSEID']==hi][df_veh['VEHID']==vi]
            # df33 trip record
            df33 = df1[df1['VEHID']==vi]
            hh_veh_lst[1].append(df3['URBRUR'][df3['URBRUR'].index[0]])
            hh_veh_lst[2].append(df3['TRAVDAY'][df3['TRAVDAY'].index[0]])
            hh_veh_lst[3].append(df3['VEHTYPE'][df3['VEHTYPE'].index[0]])
            hh_veh_lst[4].append(df33['TRPTRANS'][df33['TRPTRANS'].index[0]])
            hh_veh_lst[5].append(df3['ANNMILES'][df3['ANNMILES'].index[0]])
            hh_veh_lst[6].append(df3['BESTMILE'][df3['BESTMILE'].index[0]])
            hh_veh_lst[7].append(df3['LIF_CYC'][df3['LIF_CYC'].index[0]])
            hh_veh_lst[9].append(sum(df33['TRPMILES'].to_list()))
    df_veh_trp = pd.DataFrame(hh_veh_lst)
    df4 = df_veh_trp.transpose()
    df4[0].tolist()
    lst_1 = []
    for ii in range(2):
        for jj in range(2) :
            for kk in range(2) :
                for ll in range(3):
                    i = [urban_g1,urban_g2][ii]
                    j = [TRAVDAY_g1,TRAVDAY_g2][jj]
                    k = [car_group_1, car_group_2][kk]
                    l = lfcycle[ll]
                    lst_1.append(df4[df4[3].isin(k)][df4[1].isin(i)][df4[2].isin(j)][df4[7].isin(l)].shape[0])
    if region_num == 5:
        df0 = pd.DataFrame([lst,lst_1,[lst_1[i]/lst[i] for i in range(len(lst))]])
    else:
        df0 = pd.DataFrame([lst,lst_1,[lst_1[i]/lst[i] for i in range(len(lst))]])

    df0.to_csv(r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Driving_profile_simu\activeness_'+region+'.csv')
if __name__ == '__main__':
    # soc_drop(93,3108)
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(9):
        p = Process(target=actvness, args=([i]))
        
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks unt