import time
import pandas as pd 
import numpy as np
from datetime import datetime
import os

def soc_drop_func(num0, num1):
    import pandas as pd 
    import numpy as np
    from datetime import datetime
    import os
    basedir = '/home/jiahuic/Ford_CC'
    outdir = '/nfs/turbo/seas-parthtv/jiahuic/Ford_CC'
    df_loc = pd.read_csv(outdir + r'//Scipts/2020_Gaz_counties_national_0728_tempreg.csv')
    for county_num in range(num0,num1):
            ind = df_loc.index[county_num]
            region = df_loc['Region'][ind]
            driving_profile_foldername = basedir+r'//Driving_profile_simu//Results//'+region+'//'
            outputdir = outdir+r'//Energy consumption_1//'+str(county_num)+'//'
            yr = pd.read_csv(outdir+'//temp//'+str(county_num)+'.csv').to_numpy()
            if os.path.exists(outdir+r'//Energy consumption_1//'+str(county_num)):
                nlst = [i for i in os.listdir(driving_profile_foldername) 
                        if os.path.isfile(outputdir+i[:-4]+'_0'+'_soc.csv')!=True]
                if len(nlst)>0:
                    hr = pd.Timedelta(value=1,unit='hours')

                    
                    driving_profile_foldername = basedir+r'//Driving_profile_simu//Results//'+region+'//'
                    # MPGe fuel economy from fuel economy
                    cty_lst = [129,78]
                    hwy_lst = [116,63]
                    # URB mix, city and hwy
                    urbmix = [0.55,0.45]

                    # temp function
                    def tempimpact(tem1):
                        # temperature threshold cold
                        TC = 15.5
                        # temperature hot
                        TH = 23.9
                        if tem1 < TC:
                            coeT1 = 0.0242*(TC-tem1) + 1
                        elif TC <=tem1<=TH:
                            coeT1 = 1
                        elif TH <= tem1:
                            coeT1 = 0.0210*(tem1-TH) + 1
                        return coeT1
                    for fname in nlst:
                        if fname[0]==fname[2]==fname[4]=='0':
                            df = pd.read_csv(driving_profile_foldername+fname)
                            trp_num = df.shape[0] # total trip number

                            cari = int(fname[2])
                            urbi = int(fname[0])
                            urban = urbi
                            #fe calculation
                            # change MPGe to kWh/mile
                            # change from lab to real-world (exclude temp impact)
                            if urban == 0:
                                cityOR = 33.70/cty_lst[cari]
                                # hwyOR = 33.70/hwy_lst[cari]
                                cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
                                comb = cityNT
                            elif urban ==1:
                                hwyOR = 33.70/hwy_lst[cari]
                                hwyNT = 33.70/hwy_lst[cari]*0.7 + 0.87*(hwyOR - 33.70/hwy_lst[cari]*0.7)
                                cityOR = 33.70/cty_lst[cari]
                                # hwyOR = 33.70/hwy_lst[cari]
                                cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
                                comb = hwyNT*0.55+cityNT*0.45
                            elif urban ==2: # not in use
                                cityOR = 33.70/cty_lst[cari]
                                hwyOR = 33.70/hwy_lst[cari]
                                cityNT = 33.70/cty_lst[cari]*0.7 + 0.67*(cityOR-33.70/cty_lst[cari]*0.7)
                                hwyNT = 33.70/hwy_lst[cari]*0.7 + 0.87*(hwyOR - 33.70/hwy_lst[cari]*0.7)
                                comb = 0.45* hwyNT + 0.55*cityNT
                            SDrops = []
                            strhrs = []
                            endhrs = []
                            for ev_i in range(trp_num):
                                # divide tripmiles equally to hours
                                # tripmiles
                                trpmile = df['TRPMILES'][ev_i]
                                
                                # trip time
                                trpt = df['TRVLCMIN'][ev_i]
                                # to deltatime hour
                                trpt = hr * trpt/60

                                starttime = str(df['STRTTIME'][ev_i])
                                endtime = str(df['ENDTIME'][ev_i])
                                day = df['DAY'][ev_i]
                                if len(starttime)>=3:
                                    strhr = int(starttime[:-2])
                                    
                                    strmin = int(starttime[-2:])
                                    if len(endtime)>=3:
                                        endhr = int(endtime[:-2])
                                        endmin = int(endtime[-2:])
                                    else:
                                        endhr = 0
                                        endmin = int(endtime)
                                else:
                                    strhr = 0
                                    strmin = int(starttime)
                                    if len(endtime)>=3:
                                        endhr = int(endtime[:-2])
                                        endmin = int(endtime[-2:])
                                    else:
                                        endhr = 0
                                        endmin = int(endtime)
                                # hour number (8760)
                                strhrnum = day*24+int(strhr)
                                

                                if endhr - strhr == 0:
                                    # temperature of the hour
                                    tem = yr[strhrnum]
                                    try:
                                        coeT = tempimpact(tem)
                                    except:print(tem,county_num,strhrnum)   
                                    SDrop = trpmile * comb *coeT

                                elif endhr - strhr >= 1:
                                    # time percentage
                                    time_perc = np.ones(int(endhr - strhr)+1)*60
                                    time_perc[0]=60-strmin
                                    time_perc[-1] = endmin
                                    mile_perc = np.array([trpmile*time_perc[k]/np.sum(time_perc) for k in range(int(endhr - strhr)+1)])
                                    # temperature of the hours
                                    tem = [yr[strhrnum+k] for k in range(int(endhr - strhr)+1)]
                                    coeT_lst = np.array([tempimpact(tem[k]) for k in range(int(endhr - strhr)+1)])
                                    SDrop_sub = coeT_lst * mile_perc * comb
                                    SDrop = np.sum(SDrop_sub)
                                SDrops.append(SDrop)
                                strhrs.append(strhrnum)
                                endhrs.append(strhrnum+endhr-strhr)
                            df['SDrop'] = SDrops
                            df['EndHr'] = endhrs
                            df['StrHr'] = strhrs
                            # df.drop(df.loc[df['VMT_MILE']==-1].index, inplace=True)
                            df.sort_values(by='StrHr',axis=0,inplace=True)
                            # df.drop(df['Unnamed: 0'])
                            df.reset_index(inplace=True)
                            try: df.drop(columns=['Unnamed: 0','Unnamed: 0.1', 'Unnamed: 0.1.1','index'], inplace=True)
                            except: pass
                            try: df.drop(columns=['Unnamed: 0'], inplace=True)
                            except: pass
                            try: os.mkdir(outdir+r'//Energy consumption_1//')
                            except: pass                
                            try: os.mkdir(outdir+r'//Energy consumption_1//'+str(county_num))
                            except: pass
                            outputdir = outdir+r'//Energy consumption_1//'+str(county_num)+'//'
                            df.to_csv(outputdir+fname[:-4]+'_0'+'_soc.csv')
                            print(str(county_num)+'_'+fname)

    