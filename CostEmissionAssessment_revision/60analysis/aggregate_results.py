import pandas as pd
import numpy as np
outputdir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
# outputdir = r'E:\Dropbox (University of Michigan)\Ford_CC'
a=48
b=9
for cc_ip in range(3):
# for cc_ip in range(1):
    for year in [2024,2030,2040]:
        urb,car,lcc = 0,0,0
        df0 = pd.read_csv(outputdir+r'\Server_168h\csv_trb_60\\'+str(0)+'_'+str(9)+'_'+str(year)+'_'
                    +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_1.csv')

        for i in range(1,a):
            if i != a-1:
                num0 = i*b
                num1 = i*b+b
            else:
                num0=i*b
                num1=432
            df = pd.read_csv(outputdir+r'\Server_168h\csv_trb_60\\'+str(num0)+'_'+str(num1)+'_'+str(year)+'_'
                    +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_1.csv')
            df0 = df0.merge(df, how='outer')
        df0.to_csv(outputdir+r'\Server_168h\res_trb_60\\'+str(year)+'_'
                    +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+'_2.csv')