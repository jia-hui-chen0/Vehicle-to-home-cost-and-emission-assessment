# https://www.mdpi.com/1996-1073/17/1/158
# TUM 2024
import pandas as pd
import numpy as np
import os
import pandas as pd 
import numpy as np

from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
root_dir = 'G:\\'
# root_dir = 'C:\Users\jiahuic\\' 
def qcomb(qcal0,qcyc0,n_cycle,v,T1,DOD,t):
    kscale = 1
    alpha = (7.543*v-23.75)*10**6*np.exp(-6976./T1)
    beta=7.348/10**3 * (v-3.667)**2 + 7.6/10**4 + 4.081/10**3 * DOD
    q_cur = qcal0+qcyc0
    tvir = (qcal0/(alpha)/kscale)**(4/3)
    qvir = (qcyc0/(beta)/kscale)**2
    if q_cur != 0:
        qcal = kscale*(alpha*(tvir+t)**(0.75))
        qcyc =  kscale*(beta*np.sqrt(qvir+n_cycle))
    else:
        qcal = kscale*alpha*(t)**(.75)
        qcyc = kscale*beta*np.sqrt(n_cycle)

    return [qcal,qcyc]
def deg(num0,num1,charging):
    t25 = False
    for county_num in range(num0,num1):         
        lifecty = [] # battery life in years of zone county_num
        qcallst = []
        qcyclst = []
        # if charging == 0: 
        location = 'Energy consumption_adjusted_1_2_Y82\\'
        flst = [i for i in os.listdir(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num))]
        flst = [i for i in flst if '.csv' in i]
        flst = [i[6:-10] for i in flst]
        # if charging ==1 or charging==2:
        flst = flst[:5]
        if charging == 1:
            location = 'Result_cc\Results_Y82_2024\\'
            flst = [i[6:-10] for i in os.listdir(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num)+'_0_0')]
        # elif charging ==2:
        #     location = 'Result_v2h\Results_80_Y82_2024\\'
        #     flst = [i[6:-9] for i in os.listdir(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num)+'_0_0')]
        yr = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\tempAdjusted\\'+str(county_num)+'.csv')['0'].to_list()*20
        yr = [i for i in yr]
        if t25 == True:
            yr = [25 if i<25 else i for i in yr ]
        else:
            pass
        for  vi in flst:
            evec = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_1_2_Y82\\'+str(county_num)+'\\0_0_0_'+vi+'_0_soc.csv')
            driving=evec['SOC'].to_list()*20
            if charging ==0:
                location = 'Results\Results_80_82\\'
                socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'+location+str(county_num)+['','_0_0'][charging]+'\\0_0_0_'+vi+['_0_soc.csv','_0_50.csv'][charging])
                # socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_2024\\'+str(county_num)+'_0_0\\0_0_0_'+vi+'_0_50.csv')
                socar = np.array(socdf['vSOC'].to_list()*20)/(82)
                
                if charging == 1:
                    disc = socdf['sd'].to_list()*20
                charg = list(socdf['slowCR'].to_numpy()+socdf['fastCR'].to_numpy())*20
                qcal0 = 0
                qcyc0 = 0
                h=0
                tt = 15
                while h < 365*tt and qcal0+qcyc0<0.3:
                    socar_h = socar[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )]
                    if charging ==1:
                        n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(82)+sum(disc[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))
                    elif charging ==0:
                        n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(82)+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))
                    n_cycle = n_cycle*2.15
                    T1 = np.mean(yr[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])+273.15
                    SOC0 =np.mean( socar_h)
                    if charging ==1:
                        DOD = max(socar_h)-min(socar_h)
                    else:
                        DOD = 0.6
                    v = (3.32 + (4.1-3.32)*(SOC0))
                    qcal,qcyc = qcomb(qcal0,qcyc0,n_cycle,v,T1,DOD,15/tt)
                    qcal0 = qcal
                    qcyc0 = qcyc
                    h+=1
                # print(qcal0,qcyc0)
            elif charging ==1:
                location = ['Result_cc\Results_Y82_2024\\','Result_cc\Results_Y82_2030\\','Result_cc\Results_Y82_2040\\']
                socdf = [pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'
                                +location[yri]+str(county_num)+'_0_0'+'\\0_0_0_'+vi+'_0_soc.csv') for yri in range(3)]
                # socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_2024\\'+str(county_num)+'_0_0\\0_0_0_'+vi+'_0_50.csv')
                socar = np.array(socdf[0]['vSOC'].to_list()*6+socdf[1]['vSOC'].to_list()*6+socdf[2]['vSOC'].to_list()*6)/(82)
                charg = list(socdf[0]['slowCR'].to_numpy()+socdf[0]['fastCR'].to_numpy())*6+list(socdf[1]['slowCR'].to_numpy()+socdf[1]['fastCR'].to_numpy())*6+list(socdf[2]['slowCR'].to_numpy()+socdf[2]['fastCR'].to_numpy())*6
                qcal0 = 0
                qcyc0 = 0
                h=0
                tt = 15
                while h < 365*tt and qcal0+qcyc0<0.3:
                    socar_h = socar[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )]
                    if charging ==2:
                        n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(82)+sum(disc[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))
                    elif charging ==0 or charging ==1:
                        n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(82)+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))
                    n_cycle = n_cycle*2.15
                    T1 = np.mean(yr[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])+273.15
                    SOC0 =np.mean( socar_h)
                    if charging ==2:
                        DOD = max(socar_h)-min(socar_h)
                    else:
                        DOD = 0.6
                    v = (3.32 + (4.1-3.32)*(SOC0))
                    qcal,qcyc = qcomb(qcal0,qcyc0,n_cycle,v,T1,DOD,15/tt)
                    qcal0 = qcal
                    qcyc0 = qcyc
                    h+=1
            elif charging ==2:
                location = ['Result_v2h\Results_80_Y82_2024\\','Result_v2h\Results_80_Y82_2030\\','Result_v2h\Results_80_Y82_2040\\']
                socdf = [pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\\'
                                +location[yri]+str(county_num)+'_0_0'+'\\0_0_0_'+vi+'_0_50.csv') for yri in range(3)]
                # socdf = pd.read_csv(root_dir+r'Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_2024\\'+str(county_num)+'_0_0\\0_0_0_'+vi+'_0_50.csv')
                socar = np.array(socdf[0]['vSOC'].to_list()*6+socdf[1]['vSOC'].to_list()*6+socdf[2]['vSOC'].to_list()*6)/(82)
                disc = np.array(socdf[0]['sd'].to_list()*6+socdf[1]['sd'].to_list()*6+socdf[2]['sd'].to_list()*6)/(82)
                charg = list(socdf[0]['slowCR'].to_numpy()+socdf[0]['fastCR'].to_numpy())*6+list(socdf[1]['slowCR'].to_numpy()+socdf[1]['fastCR'].to_numpy())*6+list(socdf[2]['slowCR'].to_numpy()+socdf[2]['fastCR'].to_numpy())*6
                qcal0 = 0
                qcyc0 = 0
                h=0
                tt = 15
                while h < 365*tt and qcal0+qcyc0<0.3:
                    socar_h = socar[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )]
                    n_cycle=sum(driving[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/(82)+sum(disc[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))+sum(charg[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])/((82))
                    n_cycle = n_cycle*2.15
                    T1 = np.mean(yr[int(h*24*15/tt):int(h*24*15/tt +24*15/tt )])+273.15
                    SOC0 =np.mean( socar_h)
                    DOD = max(socar_h)-min(socar_h)
                    v = (3.32 + (4.1-3.32)*(SOC0))
                    qcal,qcyc = qcomb(qcal0,qcyc0,n_cycle,v,T1,DOD,15/tt)
                    qcal0 = qcal
                    qcyc0 = qcyc
                    h+=1
            lifecty.append(h/365*15/tt)
            qcallst.append(qcal0)
            qcyclst.append(qcyc0)
        pd.DataFrame([lifecty,qcallst,qcyclst]).to_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\Deginterm\\'+str(county_num)+'_80Y82_'+['uc','cc','v2h'][charging]+'_15_no25.csv')
        # pd.DataFrame([lifecty,qcallst,qcyclst]).to_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\Deginterm\\'+str(county_num)+'_80_uc_15_no25.csv')
        # pd.DataFrame([lifecty,qcallst,qcyclst]).to_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\Deginterm\\'+str(county_num)+'_100_uc_15_t2_no25.csv')
# f, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(6, 5), sharex=True, sharey=False)
# ax.hist(x=life,bins=5)
if __name__ == '__main__':
    # deg(182,183)
    for charging in range(3): # uc
    

        import warnings
        warnings.filterwarnings("ignore")
        procs = []
        for i in range(48):
            if i != 47:
                p = Process(target=deg, args=([i*9,i*9+9,charging]))
            else:
                p = Process(target=deg,args=([i*9,432,charging]))
            p.start()
            procs.append(p)
        for p in procs:
            p.join() # this blocks until the process terminates