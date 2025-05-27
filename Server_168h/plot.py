# ICEV kg
# EV kg
import numpy as np
import pandas as pd
ctdf = pd.read_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\2020_Gaz_counties_national_0728_tempreg.csv')
costlst = []
for i in range(80):
    costlst = costlst + pd.read_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\Server_168h\csv_db\\'+str(i)+'__2040_0_0_0_0.csv')['Cost'].to_list()

import matplotlib.pyplot as plt
f,ax = plt.subplots(1,1,figsize=(7,4))
ax.hist(costlst,label=['Uncontrolled charging','V2H'])
ax.set_xlabel('Lifetime charging costs (USD)')
plt.savefig(r'G:\Dropbox (University of Michigan)\FordDashboard\flask\static\images\dist.png',dpi=1300)