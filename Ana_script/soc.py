import pandas as pd
import numpy as np
import os
vmt=[]
basedir = r'/nfs/turbo/seas-parthtv/jiahuic/Ford_CC/Energy consumption/'
df0728 = pd.read_csv(r'/home/jiahuic/Ford_CC/Server/2020_Gaz_counties_national_0728.csv')
ctynmlst = df0728['county_num'][df0728['Region']=='Mountain'].to_list()

for cty in ctynmlst:
    fnames = os.listdir(basedir+str(cty))
    fnames = [i for i in fnames if i[0]=='0' and i[2]=='0' and i[4]=='0']
    for fname in fnames:
        df = pd.read_csv(basedir+str(cty)+r'//'+fname)
    
        vmt.append(sum(df['SDrop']))
print(sum(vmt)/len(vmt))
