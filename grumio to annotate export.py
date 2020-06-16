import shutil
import sys
import os 
import Tkinter, tkFileDialog, tkSimpleDialog
import pandas
import random

root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

subfolders, subsubfolders, subsubsubfolders = []


#timeset layer
subfolders = [ f.path for f in os.scandir(directory) if f.is_dir() ]

for subfolder in subfolders:
	#Media + date layer
	subsubfolders += [ f.path for f in os.scandir(subfolder) if f.is_dir() ]

for subsubfolder in subsubfolders:
	#Rows layer
	subsubsubfolders += [ f.path for f in os.scandir(subsubfolder) if f.is_dir() ]


d = {'Original Path': [], 'Decode': [], 'Line':[], 'Row':[], 'Media':[]}
df = pd.DataFrame(data=d)

decoder = {1 : 'AJC001-5',
           2 : 'AJD002-3',
           3 : 'AJG001-C4',
           4 : 'AIW001-02',
           5 : 'AIW002-02',
           6 : 'NCRM1',
           7 : 'KYOU',
           8 : 'TD02',
           9 : 'TD03',
           10 : 'TD10',
           11 : '3448',
           12 : '3450'}


output_dir = os.join(directory, "to_annotate")

os.mkdir(output_dir)

for subsubsubfolder in subsubsubfolders:
	for filename in os.listdir(subsubsubfolder): 
		if 'd0.TIF' in filename:
			if filename[24:25] == '05' or filename[24:25] == '06'

				path = os.path.join(subsubsubfolder, filename)

				if 'E8' in path:
					media = 'E8'
				elif 'mTeSR' in path:
					media = 'mTeSR'

				df.append([path, None, decoder[filename[21:22]], filename[24:25], media])



df = df.sample(frac=1).reset_index(drop=True)
df.to_csv(os.join(output_dir, "to_annotate_decoder"))

for i, row in enumerate(df):
	paths = row['Original Path']
	shutil.copy2(path, os.join(output_dir, "to_annotate" + str(i)+"d0.TIF"))
	shutil.copy2(path.replace('d0.TIF', 'd1.TIF'), os.join(output_dir, "to_annotate" + str(i)+"d1.TIF"))