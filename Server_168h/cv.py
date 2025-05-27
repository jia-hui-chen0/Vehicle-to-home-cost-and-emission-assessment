import pandas as pd 
import numpy as np
ctdf = pd.read_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\2020_Gaz_counties_national_0728_tempreg.csv')
ctdf1 = ctdf.loc[ctdf['Region'].isin(['West South Central'])]
ctdf2 = ctdf.loc[~ctdf['Region'].isin(['South Atlantic'])]
import os 
location = r'G:\Dropbox (University of Michigan)\Ford_CC\Result_v2h\Results_80_Y82_2030\\'
# location = r'G:\Dropbox (University of Michigan)\Ford_CC\Result_cc\Results_Y82_2024\\'
# slowcharg ratio
ratio = []
for county_num in np.unique(ctdf2['tempreg']):
    for fnm in os.listdir(location+str(county_num)+'_0_0'):
        df = pd.read_csv(location+str(county_num)+'_0_0'+'\\'+fnm)
        ratio.append(sum(df['slowCR'])/(sum(df['slowCR'])+sum(df['fastCR'])))
ratio1 =np.mean(ratio)
# year = '24'
# mean_0 = []
# for county_num in np.unique(ctdf2['reeds_ba']):
#     df = pd.read_csv(r'G:\Dropbox (University of Michigan)\Ford_CC\Cambium\hourly_balancingArea\\'+str(county_num)+'_20'+year+'.csv')
#     price = df['srmer_co2e'].to_numpy()/1000*0.051+df['total_cost_enduse'].to_numpy()/1000
#     # mean_0.append(np.mean(np.array([np.mean(price[24*i+15:24*i+24]) for i in range(365)])))
#     mean_0.append(np.std(price))
# # mean_0/len(np.unique(ctdf2['reeds_ba']))
# print(np.mean(mean_0))
import warnings
    warnings.filterwarnings("ignore")
    procs = []
    # a=16
    # b=432//a
    for i in range(421,432):
        p = Process(target=CC, args=([i,i+1,[2024]]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this blocks until the process terminates