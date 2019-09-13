import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv



directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

subdirectories = os.listdir(directory)

for subdirectory in subdirectories:
	subsubdirectories = os.listdir(subdirectory)
	for subsubdirectory in subssubdirectories:
		files = os.listdir(subdirectory)
		for filename in files:
			if "