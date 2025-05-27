import pandas as pd 
import numpy as np
from gams import *

from datetime import datetime
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
outputdir = r'E:\Dropbox (University of Michigan)\Ford_CC'
def goi(i):
    try:
        os.mkdir(outputdir+r'\\Energy consumption_adjusted_1\\'+str(i))
        os.mkdir(outputdir+r'\\Energy consumption_adjusted_1\\'+str(i)+'\\FC_opp_SUV\\')
        os.mkdir(outputdir+r'\\Energy consumption_adjusted_1\\'+str(i)+'\\SC_opp_SUV\\')

    except:pass
    fnames = os.listdir(outputdir+r'\\Energy consumption_adjusted\\'+str(i))
    fnames = [i for i in fnames if r'.csv' in i]
    fnames = [i for i in fnames if i[0]==i[2]==i[4]=='0']
    socs = []
    for fnm in fnames:
        socs.append(sum(pd.read_csv(outputdir+r'\\Energy consumption_adjusted\\'+str(i)+'\\'+fnm)['SDrop'].to_list()))
    positions = []
    qts = [20,35,50,65,80]
    for qt in qts:
        positions.append(np.where(socs==np.quantile(socs,qt/100,method='inverted_cdf'))[0][0])
    for posi in range(len(qts)):
        pos = positions[posi]
        pd.read_csv(outputdir+r'\\Energy consumption_adjusted\\'+str(i)+'\\'+fnames[pos]).to_csv(
            outputdir+r'\\Energy consumption_adjusted_1\\'+str(i)+'\\'+str(qts[posi])+'_'+fnames[pos]
        )
        pd.read_csv(outputdir+r'\\Energy consumption_adjusted\\'+str(i)+r'\\SC_opp_SUV\\'+fnames[pos]+'.csv').to_csv(
            outputdir+r'\\Energy consumption_adjusted_1\\'+str(i)+'\\SC_opp_SUV\\'+str(qts[posi])+'_'+fnames[pos]
        )
        pd.read_csv(outputdir+r'\\Energy consumption_adjusted\\'+str(i)+'\\FC_opp_SUV\\'+fnames[pos]+'.csv').to_csv(
            outputdir+r'\\Energy consumption_adjusted_1\\'+str(i)+'\\FC_opp_SUV\\'+str(qts[posi])+'_'+fnames[pos]
        )
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(432):
        p = Process(target=goi, args=([i]))
        
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates