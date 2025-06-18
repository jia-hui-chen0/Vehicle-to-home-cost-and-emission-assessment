import pandas as pd
import numpy as np
import os
outdir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\\'
dirlst = [r'Results\\',r'Result_cc\\',r'Result_v2h\\']
yearlst = ['2024','2030','2040']
lst = [[] for i in range(9)]
for sceni in range(3):
    for yeari in range(3):
        yearlst_1 = [r'Results_80_82_1',r'Results_Y82_'+yearlst[yeari],r'Results_80_Y82_'+yearlst[yeari]+'_1']
        for countyi in range(432):
            filenm = os.listdir(outdir+dirlst[sceni]+yearlst_1[sceni]+r'\\'+str(countyi)+['','_0_0','_0_0'][sceni])
            for nm in filenm:
                df = pd.read_csv(outdir+dirlst[sceni]+yearlst_1[sceni]+r'\\'+str(countyi)+['','_0_0','_0_0'][sceni]+r'\\'+nm)
                lst[sceni * 3 + yeari].append(np.mean(df['vSOC']))

import matplotlib.pyplot as plt
f,ax = plt.subplots(1,1, figsize=(4, 4),sharex=False, sharey=True)### figure config
ax.boxplot(lst)