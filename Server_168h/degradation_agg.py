# https://www.mdpi.com/1996-1073/17/1/158
# TUM 2024
import pandas as pd 
import numpy as np
from gams import *

from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
# root_dir = 'G:\\'
charging = 0 # uc 0 V2G 1
root_dir = r'C:\Users\jiahuic\\'
def qcomb(qcal0,qcyc0,n_cycle,v,T1,DOD,t):
    alpha = (7.543*v-23.75)*10**6.*np.exp(-6976./T1)
    beta=7.348/10**3 * (v-3.667)**2 + 7.6/10**4 + 4.081/10**3 * DOD
    q_cur = qcal0+qcyc0
    tvir = (qcal0/(alpha))**(4/3)
    qvir = (qcyc0/(beta))**2
    if q_cur != 0:
        qcal = (alpha*(tvir+t)**(0.75))
        qcyc =  (beta*np.sqrt(qvir+n_cycle))
    else:
        qcal = alpha*(t)**(.75)
        qcyc = beta*np.sqrt(n_cycle)

    return [qcal,qcyc]
life = [] # battery life in years of zone county_num
def deg(num0,num1):
    for county_num in range(num0,num1):
        lifecty = [] # battery life in years of zone county_num
        qcallst = []
        qcyclst = []
        flst = [i[6:-9] for i in os.listdir(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_80_2024\\'+str(county_num)+'_0_0')]
        yr = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\tempAdjusted\\'+str(county_num)+'.csv')['0'].to_list()*20
        yr = [25 if i<25 else i for i in yr ]
        for  vi in flst:
            evec = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2\\'+str(county_num)+'\\0_0_0_'+vi+'_0_soc.csv')
            driving=evec['SOC'].to_list()*20
            socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'
                                +['Results\Results_80\\','Result_v2h\Results_80_2024\\'][charging]+str(county_num)
                                +['','_0_0'][charging]+'\\0_0_0_'+vi+['_0_soc.csv','_0_50.csv'][charging])
            # socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_2024\\'+str(county_num)+'_0_0\\0_0_0_'+vi+'_0_50.csv')
            socar = np.array(socdf['vSOC'].to_list()*20)/(62)
            if charging == 1:
                disc = socdf['sd'].to_list()*20
            charg = list(socdf['slowCR'].to_numpy()+socdf['fastCR'].to_numpy())*20
            qcal0 = 0
            qcyc0 = 0
            h=0
            tt = 15
            while h < 4/3*365*tt and qcal0+qcyc0<0.3:
                socar_h = socar[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )]
                if charging ==1:
                    n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(62)+sum(disc[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((62))+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((62))
                elif charging ==0:
                    n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(62)+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((62))
                n_cycle = n_cycle*2.15
                T1 = np.mean(yr[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])+273.15
                SOC0 =np.mean( socar_h)
                DOD = max(socar_h)-min(socar_h)
                v = (3.32 + (4.1-3.32)*(SOC0))
                qcal,qcyc = qcomb(qcal0,qcyc0,n_cycle,v,T1,DOD,15/tt)
                qcal0 = qcal
                qcyc0 = qcyc
                h+=1
                # print(qcal0,qcyc0)
            lifecty.append(h/365*15/tt)
            qcallst.append(qcal0)
            qcyclst.append(qcyc0)
            # print(qcal0,qcyc0)
            # print(h/365)
        pd.DataFrame([lifecty,qcallst,qcyclst]).to_csv(
            r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Deginterm\\'+str(county_num)+'_80UC_15_62m3.csv')
if __name__ == '__main__':
    # UC(20,21)

    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(48):
        if i != 47:
            p = Process(target=deg, args=([i*9,i*9+9]))
        else:
            p = Process(target=deg,args=([i*9,432]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates