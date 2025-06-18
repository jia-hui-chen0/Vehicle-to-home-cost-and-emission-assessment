import os

outputdir = r'F:\University of Michigan Dropbox\Jiahui Chen\Ford_CC\\'
all_fnames = []
for county_num in range(432):
    fnames = os.listdir(outputdir + r'\\Energy consumption_adjusted_1_2_Y60_db\\' + str(county_num))
    fnames = [i for i in fnames if i[:6] == '0_0_0_']
    fnames = [i for i in fnames if r'.csv' in i][:15]
    all_fnames.append(set(fnames))

# Check if all sets in all_fnames are the same
all_same = all(f == all_fnames[0] for f in all_fnames)
if all_same:
    print("All fnames are the same for all counties.")
    print(sorted(list(all_fnames[0])))
else:
    print("Not all fnames are the same for all counties.")