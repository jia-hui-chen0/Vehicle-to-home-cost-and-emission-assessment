# check for 0.051 *f_emi
import pandas as pd
import numpy as np
import os
# def ana_func(num0,num1,year,cc_ip,urb,car,lcc):

    # check for 0.051 *f_emi
def ana_func(num0,num1,year,cc_ip,urb,car,lcc):
    outputdir = r'E:\Dropbox (University of Michigan)\Ford_CC'
    root_loc =outputdir
    ctydf = pd.read_csv(root_loc+r'\\2020_Gaz_counties_national_0728_tempreg.csv')
    ctydf.set_index(keys=ctydf['county_num'],inplace=True)
    uqlst = np.unique(ctydf['tempreg'].to_numpy())
    # number of columns:
    lenc = 7

    # UC urb car lcc
    lst = [[] for i in range(lenc)]
    cc_hand = ['','_opt'][cc_ip]
    for county_num in range(len(uqlst)):
        countyBA = ctydf[ctydf['tempreg']==uqlst[county_num]]['reeds_ba'].to_list()[0]
        if cc_ip ==0:
            yr = 2026
        else: yr = year
        fnames = os.listdir(outputdir+r'\\Results'+cc_hand+r'\\Results_'+str(yr)+r'\\'+str(county_num))
        fnames = [i for i in fnames if r'.csv' in i and i[0]==str(urb) and i[2]==str(car) and i[4]==str(lcc)]
        cambium_df = pd.read_csv(outputdir+r'\Cambium\\hourly_balancingArea\\' + countyBA +'_'+str(year)+'.csv')
        f_cost = cambium_df['total_cost_enduse'].to_numpy()/1000
        f_emi = cambium_df['srmer_co2e'].to_numpy()/1000
        c_lst = [[] for i in range(lenc-1)]
        if len(fnames) > 0:
            for fname in fnames:
                cari = int(fname[2])
                urbi = int(fname[0])
                lcci = int(fname[4])
                if cari==0 and urbi ==0 and lcci==0:
                    # result
                    res = pd.read_csv(outputdir+r'\\Results'+cc_hand+r'\\Results_'+str(yr)+r'\\'+str(county_num)+'\\'+fname)
                    energy = pd.read_csv(outputdir+r'\\Energy consumption_adjusted_3\\'+str(county_num)+'\\'+fname)
                    sc = res['slowCR'].to_numpy()
                    fc = res['fastCR'].to_numpy()
                    SDrop = energy['SDrop'].to_numpy()
                    mile = energy['TRPMILES'].to_numpy()

                    carbprice = 0.051*f_emi #0.051*f_emi
                    # battery degradation
                    evec = pd.read_csv(r'E:\Dropbox (University of Michigan)\Ford_CC\Energy consumption_adjusted_3\\'+str(county_num)+fname)
                    driving=evec['SOC'].to_list()*15
                    socdf = res
                    socar = socdf['vSOC'].to_list()*15
                    disc = socdf['sd'].to_list()*15
                    deg=0

                    for h in range(365*10):
                        n_cycle=sum(disc[h*24:h*24+24])/((28*3.3))+sum(driving[h*24:h*24+24])/((28*3.3))/0.7
                        SOC =np.mean( socar[h*24:h*24+24])
                        # total degradation, calendar + cycling
                        total =1 -(7.543*(3.32+SOC/(28*3.3)*(4.1-3.32))-23.75)*10**6*np.exp(-6976/(298.15))*(h)**0.75
                        -(7.348*10**(-3)*((3.32+SOC/(28*3.3)*(4.1-3.32))-3.667)**2+7.6*10**(-4)+4.081*10**(-3)*n_cycle)*np.sqrt((2.15* n_cycle))
                        dailysoh

                    
                    # aggregate
                    if sum(sc)+sum(fc)>1300:
                        c_lst[0].append(np.sum((f_cost+carbprice+0.075)*sc))
                        c_lst[1].append(np.sum((f_cost+0.1+carbprice+0.075)*fc))
                        c_lst[2].append(np.sum(f_emi*sc))#kg
                        c_lst[3].append(np.sum(f_emi*fc))#kg
                        c_lst[4].append(np.sum(SDrop))#SDrop
                        c_lst[5].append(np.sum(mile))#mileage
                        
                        
                    else:
                        c_lst[0].append(np.sum((f_cost+carbprice+0.075)*sc))
                        c_lst[1].append(np.sum((f_cost+0.1+carbprice+0.075)*fc))
                        c_lst[2].append(np.sum(f_emi*sc))#kg
                        c_lst[3].append(np.sum(f_emi*fc))#kg
                        c_lst[4].append(np.sum(SDrop))#SDrop
                        c_lst[5].append(np.sum(mile))#mileage
                        
            for k in range(lenc-1):
                lst[k].append(np.median(c_lst[k]))
            lst[lenc-1].append(county_num)
    df1 = pd.DataFrame(data=lst)
    df2 = df1.transpose()
    df2.columns = ['SC cost','FC cost','SC emissions','FC emissions','SDrop','mileage','county_num']
    # os.mkdir(outputdir+r'/Analysis_1/')
    df2.to_csv(outputdir+r'\\Analysis_0501\\'+str(year)+'_'
                +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')