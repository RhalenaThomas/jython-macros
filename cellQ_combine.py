import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv

root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

outputName = "combined.csv"


fields = []

files = os.listdir(directory)

for filename in files: 
	if "output" in filename:
	    with open(directory + '/' + filename) as csvfile:
			reader = csv.DictReader(csvfile)
			for name in reader.fieldnames:
				if name not in fields:
					fields.append(name)


with open(directory + '/' + outputName, 'w') as csvfile:		
	writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', lineterminator = '\n')
	writer.writeheader()
	for filename in files:
		if "output" in filename:
			with open(directory + '/' + filename) as csvfile:
				reader = csv.DictReader(csvfile)
				for row in reader:
					writer.writerow(row)

