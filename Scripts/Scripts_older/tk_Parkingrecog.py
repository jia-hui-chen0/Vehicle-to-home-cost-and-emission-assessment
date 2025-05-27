# recognize charging opportunities, document in csvs
# 8760 1d 
# slow and fast charging opportunties 
import pandas as pd 
import numpy as np
from datetime import datetime
from meteostat import Stations, Point, Hourly,Normals
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
def Parkingrecog(num0, num1):
    basedir = '/home/jiahuic/Ford_CC'
    outdir = '/nfs/turbo/seas-parthtv/jiahuic/Ford_CC'
    
    thresh = 8
    # 0 home 1 work 2 other
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
    def whyfrom(x):
        if x in [1,2]:
            return 0
        elif x in [3,4,5]:
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


    for county_num in range(num0,num1):
        for fname in os.listdir(outdir+r'//Energy consumption//'+str(county_num)+'//'):
            cari = int(fname[2])
            urbi = int(fname[0])
            trucknm = ['SUV','Truck'][cari]

            df0 = pd.read_csv(outdir+r'//Energy consumption//'+str(county_num)+'//'+fname)
            # by driving event, create parking event
            trpnum = df0.shape[0]
            parkevt = []
            strhr = 0
            endhr = df0['StrHr'][0]
            loc = whyfrom(df0['WHYFROM'][0])
            SOCDrop = df0['SDrop'][0]
            duration = endhr - strhr
            mile = df0['VMT_MILE'][0]
            # range
            # 0 car 1 van
            # car 2022 Tesla Model Y Long Range AWD 28kWh/100mi, 330 mi
            # City 127 Hwy 117
            # van/truck 2022 Ford F-150 Lightning 4WD
            SOC = [28*3.3,153]
            SOC = SOC[cari]
            # hour index of charging windows
            lst_chg = []

            if endhr != strhr:
                parkevt.append([strhr,endhr,loc,SOCDrop,duration,mile])
            else:
                pass
            for i in range(trpnum):
                strhr = df0['EndHr'][i]
                if i != trpnum-1:
                    endhr = df0['StrHr'][i+1]
                else:
                    endhr = 8759
                loc = whyto(df0['WHYTRP1S'][i])
                SOCDrop = df0['SDrop'][i]
                duration = endhr - strhr
                mile = df0['VMT_MILE'][i]
                parkevt.append([strhr,endhr,loc,SOCDrop,duration,mile])
            df = pd.DataFrame(parkevt,columns=['StrHr','EndHr','Location','SOCDrop','Duration','Mile'])

            # recognize charging opportunities
            # list of index in the parking event dataframe
            # df1 = df[df['Duration'] >= thresh][df['Location'].isin([1,0])]
            df1 = df[df['Duration'] >= thresh]
            lst_index = df1.index.to_list()
            for i in lst_index:
                strhr = df1['StrHr'][i]
                endhr = df1['EndHr'][i]
                for k in range(strhr,endhr):
                    lst_chg.append(k+1)
            df2 = pd.DataFrame(lst_chg,columns=['Hours'])
            try:
                os.mkdir(outdir + r"/Energy consumption/"+str(county_num)+"/SC_opp_"+trucknm)
                os.mkdir(outdir + r"/Energy consumption/"+str(county_num)+"/FC_opp_"+trucknm)
            except:
                pass
            df2.to_csv(outdir + r"/Energy consumption/"+str(county_num)+"/SC_opp_"+trucknm+'//'+fname+'.csv')
            lst_fc = [i+1 for i in range(8760) if i+1 not in lst_chg]
            df3 = pd.DataFrame(lst_fc,columns=['Hours'])
            df3.to_csv(outdir + r"/Energy consumption/"+str(county_num)+"/FC_opp_"+trucknm+'//'+fname+'.csv')
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(36):
        if i != 35:
            p = Process(target=Parkingrecog, args=([i*86,i*86+86]))
        else:
            p = Process(target=Parkingrecog,args=([i*86,3108]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates