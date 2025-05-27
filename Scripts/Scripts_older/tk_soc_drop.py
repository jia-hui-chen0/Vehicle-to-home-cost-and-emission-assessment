# tk SOC
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
        lst_cty = []
        basedir = '/home/jiahuic/Ford_CC'
        outdir = '/nfs/turbo/seas-parthtv/jiahuic/Ford_CC'
        df_loc = pd.read_csv(basedir + r'//Server/2020_Gaz_counties_national.csv')
        ind = df_loc.index[county_num]
        ansi_dr = df['ANSICODE'][ind]
        df_ana = pd.read_csv(basedir+r'//Server/2020_Gaz_counties_national_0728.csv')
        ansi_ana = df_ana['ANSICODE'][ind]
        # locla = df_loc['INTPTLAT'][ind]
        # loclong = df_loc['INTPTLONG'][ind]
        region = df_loc['Region'][ind]
        # temperature
        # 16-20 avg
        # lst_temp = []
        
        driving_profile_foldername = basedir+r'//Driving_profile_simu//Results//'+region+'//'
        # MPGe fuel economy from fuel economy

        # temp function
        for fname in os.listdir(driving_profile_foldername):


            
            outputdir = outdir+r'//Energy consumption//'+str(county_num)+'//'
            lst_cty.append([str(county_num),fname[:-4],region,ansi_dr,ansi_ana])
        (pd.DataFrame(lst_cty,columns=['county_num','fname','region','ansi_dr','ansi_ana'])).to_csv(
            r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC/Diagnostics/SOC//'+str(county_num)
            +'.csv'
        )
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

    