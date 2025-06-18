from gams import *
import numpy as np
import sys
import pandas as pd
import os
from multiprocessing import Pool
from os import getpid
import time

# check for 0.051 *f_emi
# reworking median
# first with degradation time
def ana_func1(num0,num1):
    for county_num in range(num0,num1):
        flst = [i[6:-9] for i in os.listdir(r'E:\Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_2024\\'+str(county_num)+'_0_0')]
        uc = np.zeros(len(flst))
        v2g = np.zeros(len(flst))
        for vinum in range(len(flst)): # Degradation
            vi = flst[vinum]
            evec = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_3\\'+str(county_num)+'\\0_0_0_'+vi+'_0_soc.csv')
            driving=evec['SOC'].to_list()*15
            socdf = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Results\Results_2026\\'+str(county_num)+'\\0_0_0_'+vi+'_0_soc.csv')
            socar = socdf['vSOC'].to_list()*15
            deg=0
            deglst = []
            Degdet = 1
            h=0
            while h < 365/2 and Degdet>0.8:
                n_cycle=+sum(driving[0:h*24*15*2+24*15*2])/((28*3.3))/0.7
                SOC0 =np.mean(socar[0:h*24*15*2+24*15*2])
                v = (3.32 + (4.1-3.32)*(SOC0/(28*3.3)))
                alpha = (7.543*v-23.75)*10**6.*np.exp(-6976./298.15)
                beta=7.348/10**3 * (v-3.667)**2 + 7.6/10**4 + 4.081/10**3 * 0.8
                Degdet = 1-(alpha*(h*15*2)**0.75+beta*np.sqrt(n_cycle))
                deglst.append(Degdet)
                h+=1
            uc[vinum]=h/365*15*2
            socdf = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Result_v2h_no\Results_2024\\'+str(county_num)+'_0_0\\0_0_0_'+vi+'_0_50.csv')
            socar = socdf['vSOC'].to_list()*15
            disc = socdf['sd'].to_list()*15
            deg=0
            deglst = []
            Degdet = 1
            h=0
            while h < 365/2 and Degdet>0.8:
                n_cycle=+sum(driving[0:h*24*15*2+24*15*2])/((28*3.3))/0.7+sum(disc[1:h*24*15*2+24*15*2])/((28*3.3))
                SOC0 =np.mean( socar[0:h*24*15*2+24*15*2])
                v = (3.32 + (4.1-3.32)*(SOC0/(28*3.3)))
                alpha = (7.543*v-23.75)*10**6.*np.exp(-6976./298.15)
                beta=7.348/10**3 * (v-3.667)**2 + 7.6/10**4 + 4.081/10**3 * 0.8
                Degdet = 1-(alpha*(h*15*2)**0.75+beta*np.sqrt(n_cycle))
                deglst.append(Degdet)
                h+=1
            v2g[vinum]=h/365*15*2
                
        pd.DataFrame(uc).to_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Server_168h\intermediateresults\\uc_degradation_'+str(county_num)+'.csv')
        pd.DataFrame(v2g).to_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Server_168h\intermediateresults\\v2g_degradation_'+str(county_num)+'.csv')
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    b=15
    a = 432 //b
    for i in range(b):
        if i != b-1:
            p = Process(target=ana_func1, args=([i*a,i*a+a]))
        else:
            p = Process(target=ana_func1,args=([i*a,432]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates
    