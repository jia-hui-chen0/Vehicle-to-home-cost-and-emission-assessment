from random import randrange
import os
from multiprocessing import Process, Queue
from multiprocessing import Pool
import pandas as pd
import requests
climatezs = ['Cold','Hot-Dry','Hot-Humid','Marine','Mixed-Dry','Mixed-Humid','Very Cold']
def dataaq(ind,metdf,czs):
    try:os.mkdir('Individuals_noelec\\'+czs)
    except:pass
    state = metdf['in.state'][ind]
    building_id = metdf['bldg_id'][ind]
    url = "https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/timeseries_individual_buildings/by_state/upgrade=0/state="+state+"/"+str(building_id)+ "-7"+ ".parquet"
    query_parameters = {"downloadformat": "parquet"}
    response = requests.get(url, params=query_parameters)
    with open(r"E:\Dropbox (University of Michigan)\Ford_CC\ResStock\Individuals_noelec\\"+czs+'\\'+state+str(building_id)+r".parquet", mode="wb") as file:
        file.write(response.content)
if __name__ == '__main__':
    metdf0 = pd.read_csv(r"E:\Dropbox (University of Michigan)\Ford_CC\ResStock\Aggregate.csv",low_memory=False)
    
    for climatezsi in range(7):
        czs = climatezs[climatezsi]

        try:os.mkdir('Individuals_noelec\\'+czs)
        except:pass
        
        metdf = metdf0.loc[metdf0['in.building_america_climate_zone']==czs]
        tthnm = metdf.shape[0]
        # list of buildings to download
        lst = [metdf.index[randrange(tthnm)] for i in range(400)]
        procs = []
        for ind in lst:
            p = Process(target=dataaq, args=([ind,metdf,czs]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join() # this blocks until the process terminates

    