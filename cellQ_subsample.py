import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv, random


seed = 42


root = Tkinter.Tk()
path = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))

outputName = "sampled.csv"
subsampleName = "subsample.csv"


data = []
fields = []

with open(path) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		data.append(row)
	fields = reader.fieldnames

random.Random(seed).shuffle(data)

with open(path.replace(".csv", "_" + outputName + ".csv"), 'w') as csvfile:		
	writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', lineterminator = '\n')
	writer.writeheader()

	with open(path.replace(".csv", "_" + subsampleName + ".csv"), 'w') as csvfile2:		
		writer2 = csv.DictWriter(csvfile2, fieldnames=fields, extrasaction='ignore', lineterminator = '\n')
		writer2.writeheader()

		for i in range(len(data)):
			if i < len(data)*0.5:
				writer.writerow(data[i])
			else:
				writer2.writerow(data[i])

