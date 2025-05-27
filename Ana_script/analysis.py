from gams import *
import numpy as np
import sys
import pandas as pd
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
from analysis_func import ana_func
# check for 0.051 *f_emi
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for charge in range(2):
        if charge == 0:
            for yr in [2024,2030,2035,2040]:

        
                for i in range(48):
                    if i != 47:
                        p = Process(target=ana_func, args=([i*9,i*9+9,yr,charge,0,0,0]))
                    else:
                        p = Process(target=ana_func,args=([i*9,432,yr,charge,0,0,0]))
                    p.start()
                    procs.append(p)
                for p in procs:
                    p.join() # this blocks until the process terminates
        else: 
            for yr in [2024,2030,2035,2040]:
                for i in range(48):
                    if i != 47:
                        p = Process(target=ana_func, args=([i*9,i*9+9,yr,charge,0,0,0]))
                    else:
                        p = Process(target=ana_func,args=([i*9,432,yr,charge,0,0,0]))
                    p.start()
                    procs.append(p)
                for p in procs:
                    p.join() # this bl
        