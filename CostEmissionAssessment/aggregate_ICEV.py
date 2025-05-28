import pandas as pd
import numpy as np
import os
emi = []
basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
# basedir = r'E:\Dropbox (University of Michigan)\Ford_CC'
for i in range(432):
    df = pd.read_csv(basedir+r'\\Server_168h\\csv_db\\'+str(i)+r'_0_0_0_5_hev.csv')
    emi.append(np.median(df['Emissions']))
print(emi)
df = pd.DataFrame(emi)
df.to_csv(basedir + r'\\Server_168h\res_trb\HEV.csv')