# import pandas as pd
# import numpy as np
# import os
# for region in ['Pacific',
#     'East North Central',
#     'Mountain',
#     'Middle Atlantic',
#     'South Atlantic',
#     'East South Central',
#     'West North Central',
#     'New England',
#     'West South Central']:
#     for err in range(1):
#         vmt=[]
#         basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Driving_profile_simu\Results'+['','_1'][err]+'\\'+region+'\\'
#         fnames = os.listdir(basedir)
#         fnames = [i for i in fnames if i[0]=='0' and i[2]=='0' and i[4]=='0']
#         for fname in fnames:
#             df = pd.read_csv(basedir+fname)
            
            
#             try:
#                 df['TRPMILES_1'] = df['TRPMILES']
#                 df['TRVLCMIN_1'] = df['TRVLCMIN']
#                 df['STRTTIME'] = df.apply(lambda row: int(float(row['STRTTIME']+2400)) if row['STRTTIME']<100 else int(float(row['STRTTIME'])), axis=1)
#                 df['ENDTIME'] = df.apply(lambda row: int(float(row['ENDTIME']+2400)) if row['ENDTIME']<100 else int(float(row['ENDTIME'])), axis=1)
#                 df['TRVLCMIN'] = df.apply(lambda row: ((int(float(str(row['ENDTIME'])[:-2]))-int(float(str(row['STRTTIME'])[-2:])))*60
#                                         + (int(float(str(row['ENDTIME'])[-2:]))-int(float(str(row['STRTTIME'])[-2:]))))
#                                         if row['TRVLCMIN_1']<=0
#                                         else row['TRVLCMIN_1'],axis=1)
#             except:
#                 print(fname+region)
#                 print(df['STRTTIME'].index)
#                 print(df['ENDTIME'].index)
#                 # print(df[df['ENDTIME'][-2:]=='.0'].index)
#                 # print(df[df['STRTTIME'][-2:]=='.0'].index)

#             df['TRVLCMIN'] = df.apply(lambda row: 1
#                                         if row['TRVLCMIN'] == 0
#                                         else row['TRVLCMIN'],axis=1)
#             if len(np.unique(df.loc[df['TRVLCMIN']<=0])) >0:
#                 print(fname+region+'---')
#             df['Speed'] = df.apply(lambda row: 
#                                             row['TRPMILES']/(float(row['TRVLCMIN'])/60)
#                                             ,axis=1)
#             #print(df['Speed'])
#             if err==0:
#                 df.to_csv(basedir+fname)
#             else:
#                 pass
#             spd = df['Speed'].to_numpy()
#             if err ==1:
#                 if len(np.where(spd>200)[0])+len(np.where(spd<0)[0])==0:
#                     vmt.append(np.sum(df['TRPMILES']))
#                 else:
#                     vmt.append(0)
#             elif err ==0:
#                 if len(np.where(spd>200)[0])+len(np.where(spd<0)[0])==0:
#                     vmt.append(np.sum(df['TRPMILES']))
#                 else:
#                     vmt.append(0)
#         # (pd.DataFrame(vmt)).to_csv(r'/home/jiahuic/Ford_CC/Analysis//'+region+'_vmt'+['','_err'][err]+'.csv')
#         # print(region+str(err)+fnames[np.where(np.array(vmt)==max(vmt))[0][0]])
#         print(region+'_'+['','_1'][err]+': '+str(np.median(np.array(vmt))))
import pandas as pd
import numpy as np
import os
import numpy as np
import sys
import pandas as pd
import os
from multiprocessing import Pool
from os import getpid
import time
from multiprocessing import Process, Queue
from analysis_func import ana_func
def regfunc(region):
    for err in range(1):
        vmt=[]
        basedir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC\Raw\trip_regions\\'+region+'\\'
        fnames = os.listdir(basedir)
        # fnames = [i for i in fnames if i[0]=='0' and i[2]=='0' and i[4]=='0']
        for fname in fnames:
            df = pd.read_csv(basedir+fname)
            
            
            try:
                df['TRPMILES_1'] = df['TRPMILES']
                df['TRVLCMIN_1'] = df['TRVLCMIN']
                df['STRTTIME'] = df.apply(lambda row: int(float(row['STRTTIME']+2400)) if row['STRTTIME']<100 else int(float(row['STRTTIME'])), axis=1)
                df['ENDTIME'] = df.apply(lambda row: int(float(row['ENDTIME']+2400)) if row['ENDTIME']<100 else int(float(row['ENDTIME'])), axis=1)
                df['TRVLCMIN'] = df.apply(lambda row: ((int(float(str(row['ENDTIME'])[:-2]))-int(float(str(row['STRTTIME'])[-2:])))*60+24*60
                                        + (int(float(str(row['ENDTIME'])[-2:]))-int(float(str(row['STRTTIME'])[-2:]))))
                                        if row['TRVLCMIN_1']<=0
                                        else row['TRVLCMIN_1'],axis=1)
            except:
                print(fname+region)
                print(df['STRTTIME'].index)
                print(df['ENDTIME'].index)
                # print(df[df['ENDTIME'][-2:]=='.0'].index)
                # print(df[df['STRTTIME'][-2:]=='.0'].index)

            df['TRVLCMIN'] = df.apply(lambda row: 1
                                        if row['TRVLCMIN'] == 0
                                        else row['TRVLCMIN'],axis=1)
            # if len(np.unique(df.loc[df['TRVLCMIN']<=0]['TRVLCMIN'])) >0:
            #     print(fname+region+'---')
            df['Speed'] = df.apply(lambda row: 
                                            row['TRPMILES']/(float(row['TRVLCMIN'])/60)
                                            ,axis=1)
            #print(df['Speed'])
            if err==0:
                df.to_csv(basedir+fname)
            else:
                pass
            spd = df['Speed'].to_numpy()
            if err ==1:
                if len(np.where(spd>200)[0])+len(np.where(spd<0)[0])==0:
                    vmt.append(np.sum(df['TRPMILES']))
                else:
                    vmt.append(0)
            elif err ==0:
                if len(np.where(spd>200)[0])+len(np.where(spd<0)[0])==0:
                    vmt.append(np.sum(df['TRPMILES']))
                else:
                    vmt.append(0)
        # for i in range(len(df['TRPMILES'].to_list())):

        #     if df['TRPMILES'][i] != df['TRPMILES_1'][i]:
        #         print(i)
        #     if df['Speed'][i] >120 or df['Speed'][i]<0:
        #         print(i,fname,region)
        # (pd.DataFrame(vmt)).to_csv(r'/home/jiahuic/Ford_CC/Analysis//'+region+'_vmt'+['','_err'][err]+'.csv')
        # print(region+str(err)+fnames[np.where(np.array(vmt)==max(vmt))[0][0]])
        print(region+'_'+['','_1'][err]+': '+str(np.median(np.array(vmt))*365))
        # print(region+'_'+['','_1'][err]+': '+str(np.median(np.array(vmt))))

regions =  ['Pacific',
    'East North Central',
    'Mountain',
    'Middle Atlantic',
    'South Atlantic',
    'East South Central',
    'West North Central',
    'New England',
    'West South Central']
if __name__ == '__main__':
    procs = []
    for i in range(9):
        p = Process(target=regfunc, args=([regions[i]]))
        p.start()
        procs.append(p)
    for p in procs:
        p.join() # this bl