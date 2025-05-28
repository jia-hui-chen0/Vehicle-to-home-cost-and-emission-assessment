import os
from random import randrange
import pandas as pd
import requests
import numpy as np
def func(num0,num1):
    areasl = [0,2500]
    areasu = [2500,5000]
    vintgrp = [['<1940','1940-59','1960-79','1980-99'],['2000-09','2010s']]
    quantilepcts = [.495 + i * 0.001 for i in range(10)]
    quantilepctsstr = [str(100*i) for i in quantilepcts]
    metdf1 = pd.read_csv(r"C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\ResStock\Aggregate_vintage_01.csv")
    metdf1['latlon'] = metdf1.apply(lambda x: str(x['in.weather_file_latitude'])+'_'+str(x['in.weather_file_longitude']), axis=1)
    latlon1 = [ii.split('_', 2) for ii in np.unique(metdf1['latlon'])]
    latlon = [(float(i[0]),float(i[1])) for i in latlon1]
    import geopy.distance
    df = pd.read_csv(r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\Server_168h\results_median_tempreg.csv')
    numtempreg = len(np.unique(df['tempreg']))
    metdf1['latlon'] = metdf1.apply(lambda x: str(x['in.weather_file_latitude'])+'_'+str(x['in.weather_file_longitude']), axis=1)
    latlon1 = [ii.split('_', 2) for ii in np.unique(metdf1['latlon'])]
    latlon = [(float(i[0]),float(i[1])) for i in latlon1]
    # weather file number
    weatnum = [np.zeros(432) for i in range(4)]
    for regi in range(432):
        df1 = df.loc[df['tempreg']==np.unique(df['tempreg'])[regi]]
        lon = np.mean(df1['INTPTLONG'].to_numpy())
        lat = np.mean(df1['INTPTLAT'].to_numpy())
        dist = np.array([geopy.distance.geodesic((lat,lon), i).km for i in latlon])
        for i in range(4):
            weatnum[i][regi]=np.where(dist==sorted(dist)[i])[0][0]

    for regi in range(num0,num1):
        metdf2 = metdf1.loc[metdf1['latlon']==np.unique(metdf1['latlon'])[int(weatnum[3][regi])]]
        for i in range(3):
            metdf20 = metdf1.loc[metdf1['latlon']==np.unique(metdf1['latlon'])[int(weatnum[i][regi])]]
            metdf2 = pd.concat([metdf2,metdf20])

        for vini in [1]:
            for areai in [0]:
                try:os.mkdir(r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\ResStock\\Individuals_noelec_10homes\\'+str(regi)+'_'+str(vini)+'_'+str(areai))
                except:pass
                try:os.mkdir(r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\ResStock\\Individuals_10homes\\'+str(regi)+'_'+str(vini)+'_'+str(areai))
                except:pass
                metdf3 = metdf2.loc[(metdf2['in.sqft']>=areasl[areai])&(metdf2['in.sqft']<=areasu[areai])]
                metdf3 = metdf3.loc[metdf3['in.vintage_acs'].isin(vintgrp[vini])]
                # indices = [metdf3.loc[metdf3['out.electricity.total.energy_consumption.kwh']
                        #    ==np.quantile(metdf3['out.electricity.total.energy_consumption.kwh'].to_numpy(),quantilepcts[ii],method='inverted_cdf')].index for ii in range(10)]
                metdf3['abs_diff'] = abs(metdf3['out.electricity.total.energy_consumption.kwh'] - 
                                        np.median(metdf3['out.electricity.total.energy_consumption.kwh']))
                indices = metdf3.nsmallest(10, 'abs_diff').index
                metdf3.drop(columns=['abs_diff'], inplace=True)
                percentiles = [round(metdf3['out.electricity.total.energy_consumption.kwh'].rank(pct=True)[index],4) * 10000 for index in indices]
                for indi in range(len(percentiles)):
                    ind = indices[indi]
                    state = metdf3['in.state'][ind]
                    building_id = metdf3['bldg_id'][ind]
                    # noelec
                    url = "https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/timeseries_individual_buildings/by_state/upgrade=0/state="+state+"/"+str(building_id)+ "-0"+ ".parquet"
                    query_parameters = {"downloadformat": "parquet"}
                    response = requests.get(url, params=query_parameters)
                    with open(r"Individuals_noelec_10homes\\"+str(regi)+'_'+str(vini)+'_'+str(areai)
                            +'\\'+state+str(building_id)+'_'+str(percentiles[indi])+r".parquet", mode="wb") as file:
                        file.write(response.content)
                    # elec
                    url = "https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/timeseries_individual_buildings/by_state/upgrade=7/state="+state+"/"+str(building_id)+ "-7"+ ".parquet"
                    query_parameters = {"downloadformat": "parquet"}
                    response = requests.get(url, params=query_parameters)
                    with open(r"Individuals_10homes\\"+str(regi)+'_'+str(vini)+'_'+str(areai)
                            +'\\'+state+str(building_id)+'_'+str(round(percentiles[indi],0))+r".parquet", mode="wb") as file:
                        file.write(response.content)
from multiprocessing import Pool
import time
from multiprocessing import Process, Queue
if __name__ == '__main__':
    # all processes
    import warnings
    warnings.filterwarnings("ignore")
    # CC(216,217,2024)
    a = 48
    b = 9
    procs = []
    # CC(12,13,2024)
    for i in range(a):
        if i != a-1:
            p = Process(target=func, args=([i*b,i*b+b]))
        else:
            p = Process(target=func,args=([i*b,432]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() 