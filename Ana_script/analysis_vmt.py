import pandas as pd
import numpy as np
import os
for region in ['Mountain','East South Central']:
    for err in range(2):
        vmt=[]
        basedir = r'/home/jiahuic/Ford_CC/Driving_profile_simu/Results'+['','_1'][err]+'//'+region+'/'
        fnames = os.listdir(basedir)
        fnames = [i for i in fnames if i[0]=='0' and i[2]=='0' and i[4]=='0']
        for fname in fnames:
            df = pd.read_csv(basedir+fname)
            
            if err ==1:
                try:
                    df['TRPMILES_1'] = df['TRPMILES']
                    df['TRVLCMIN_1'] = df['TRVLCMIN']
                    df['STRTTIME'] = df.apply(lambda row: int(float(row['STRTTIME']+2400)) if row['STRTTIME']<100 else int(float(row['STRTTIME'])), axis=1)
                    df['ENDTIME'] = df.apply(lambda row: int(float(row['ENDTIME']+2400)) if row['ENDTIME']<100 else int(float(row['ENDTIME'])), axis=1)
                    df['TRVLCMIN'] = df.apply(lambda row: ((int(float(str(row['ENDTIME'])[:-2]))-int(float(str(row['STRTTIME'])[-2:])))*60
                                            + (int(float(str(row['ENDTIME'])[-2:]))-int(float(str(row['STRTTIME'])[-2:]))))
                                            if row['TRVLCMIN_1']<=0
                                            else row['TRVLCMIN_1'],axis=1)
                except:
                    print(fname+region)
                    print(df['STRTTIME'].index)
                    print(df['ENDTIME'].index)
                    print(d)
                    # print(df[df['ENDTIME'][-2:]=='.0'].index)
                    # print(df[df['STRTTIME'][-2:]=='.0'].index)

                df['TRVLCMIN'] = df.apply(lambda row: 1
                                            if row['TRVLCMIN'] == 0
                                            else row['TRVLCMIN'],axis=1)
                if len(np.unique(df.loc[df['TRVLCMIN']<=0])) >0:
                    print(fname+region+'---')
            df['Speed'] = df.apply(lambda row: 
                                            row['TRPMILES']/(float(row['TRVLCMIN'])/60)
                                            ,axis=1)
            #print(df['Speed'])
            if err==0:
                df.to_csv(basedir+fname)
            else:
                pass
            spd = df['Speed'].to_numpy()
            if len(np.where(spd>200)[0])==0:
                vmt.append(np.sum(df['TRPMILES']))
            else:
                vmt.append(0)
        # (pd.DataFrame(vmt)).to_csv(r'/home/jiahuic/Ford_CC/Analysis//'+region+'_vmt'+['','_err'][err]+'.csv')
        # print(region+str(err)+fnames[np.where(np.array(vmt)==max(vmt))[0][0]])
        print(region+'_'+['','_1'][err]+': '+str(np.median(np.array(vmt))))