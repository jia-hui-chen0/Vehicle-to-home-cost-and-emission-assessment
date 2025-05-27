from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
import pandas as pd 
import numpy as np
from datetime import datetime
from meteostat import Stations, Point, Hourly,Normals
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
from soc_drop_func import *
total = 0
if __name__ == '__main__':
    # soc_drop(93,3108)
    import warnings
    warnings.filterwarnings("ignore")
    procs = []
    for i in range(36):
        if i != 35:
            p = Process(target=soc_drop_func, args=([i*43+1504,i*43+43+1504]))
        else:
            p = Process(target=soc_drop_func,args=([i*43+1504,3108]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates

    