import pandas as pd
import numpy as np
outputdir = r'C:\jiahuic\Dropbox (University of Michigan)\Ford_CC'
for cc_ip in range(2):
    if cc_ip==0:
        for year in [2024,2030,2035,2040]:
            urb,car,lcc = 0,0,0
            df0 = pd.read_csv(outputdir+r'\\Analysis\\'+str(0)+'_'+str(9)+'_'+str(year)+'_'
                        +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')

            for i in range(1,48):
                if i != 47:
                    num0 = i*9
                    num1 = i*9+9
                else:
                    num0=i*9
                    num1=432
                df = pd.read_csv(outputdir+r'\\Analysis\\'+str(num0)+'_'+str(num1)+'_'+str(year)+'_'
                        +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')
                df0 = df0.merge(df, how='outer')
            df0.to_csv(outputdir+r'\\Analysis\\'+str(year)+'_'
                        +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')
    else:
        urb,car,lcc = 0,0,0
        for year in [2024,2030,2035,2040]:
            df0 = pd.read_csv(outputdir+r'\\Analysis\\'+str(0)+'_'+str(9)+'_'+str(year)+'_'
                        +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')

            for i in range(1,48):
                if i != 47:
                    num0 = i*9
                    num1 = i*9+9
                else:
                    num0=i*9
                    num1=432
                df = pd.read_csv(outputdir+r'\\Analysis\\'+str(num0)+'_'+str(num1)+'_'+str(year)+'_'
                        +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')
                df0 = df0.merge(df, how='outer')
            df0.to_csv(outputdir+r'\\Analysis\\'+str(year)+'_'
                        +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_median.csv')