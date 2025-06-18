import pandas as pd
import numpy as np
# outputdir = r'C:\Users\jiahuic\Dropbox (University of Michigan)\Ford_CC'
outputdir = r'F:\University of Michigan Dropbox\Jiahui Chen\Ford_CC'
a=48
b=9
# done running cases: cc, v2hnoelec, v2h_nocarb,cc60, v2hcons60,  v2h_nocarb60
for scenid in range(10):
    cc_ip = [0,0,1,1,2,2,2,2,2,2][scenid]
    suffix = ['_rev','_60_rev','_60','','_cons_60','_cons','_60','','_noelec_60','_noelec'][scenid]
    for year in [2024,2030,2040]:
        urb,car,lcc = 0,0,0
        df0 = pd.read_csv(outputdir+r'\CostEmissionAssessment_revision\csv_trb\\'+str(0)+'_'+str(9)+'_'+str(year)+'_'
                    +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+suffix+'.csv')

        for i in range(1,a):
            if i != a-1:
                num0 = i*b
                num1 = i*b+b
            else:
                num0=i*b
                num1=432
            df = pd.read_csv(outputdir+r'\CostEmissionAssessment_revision\csv_trb\\'+str(num0)+'_'+str(num1)+'_'+str(year)+'_'
                    +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+suffix+'.csv')
            df0 = df0.merge(df, how='outer')
        df0.to_csv(outputdir+r'\CostEmissionAssessment_revision\res_trb\\'+str(year)+'_'
                    +str(cc_ip)+'_'+str(urb)+'_'+str(car)+'_'+str(lcc)+suffix+'.csv')