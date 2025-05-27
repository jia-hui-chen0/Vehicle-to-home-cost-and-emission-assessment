import pandas as pd
import numpy as np
import os
# GREET 2023 
# 10.64 kg CO2e/gal 
# basedir = r'E:\Dropbox (University of Michigan)\Ford_CC\\'
basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\\'
outputdir = basedir
medians = [] #fuel-cycle emissions

for regi in range(432):
    lst = []
    for fnm in os.listdir(basedir+r'Energy consumption_ICEV_2\\'+str(regi)):
        df = pd.read_csv(basedir+r'Energy consumption_ICEV_2\\'+str(regi)+r'\\'+fnm)
        lst.append(np.sum(df['SDrop'])*10.64)
    df1 = pd.DataFrame(data=lst)
    df1.columns = ['Emissions']
    df1.to_csv(outputdir+r'\\Server_168h\csv_db\\'
                +str(regi)+'_'
                +str(0)+'_'+str(0)+'_'+str(0)+'_'+str(5)+'_hev.csv')