import pandas as pd
import numpy as np
import os
vmt=[]
basedir = r'/home/jiahuic/Ford_CC/Driving_profile_simu/Results/Mountain/'
fnames = os.listdir(basedir)
fnames = [i for i in fnames if i[0]=='0' and i[2]=='0' and i[4]=='0' and]
for fname in fnames:
    df = pd.read_csv(basedir+fname)
    vmt.append(sum(df['TRPMILES']))
print(sum(vmt)/len(vmt))
