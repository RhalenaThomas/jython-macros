import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv

root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

outputName = "combined.csv"


fields = ["Ch1, Ch2, Ch3"]

d1,d2,d3 = "zzz"

channels = {}

files = os.listdir(directory)

for filename in files: 
	if "output" in filename:
		with open(directory + '/' + filename) as csvfile:
			reader = csv.DictReader(csvfile)
			for i, name in enumerate(reader.fieldnames):

				if i == 17:
					d1 = name.replace("-positive", "")
				if i == 22:
					d2 = name.replace("-positive", "")
				if i == 26:
					d3 = name.replace("-positive", "")

				name = name.replace(d1, "Ch1")
				name = name.replace(d2, "Ch2")
				name = name.replace(d3, "Ch3")

				if name not in fields:
					fields.append(name)

		channels[filename] = [d1, d2, d3]


with open(directory + '/' + outputName, 'w') as csvfile:		
	writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', lineterminator = '\n')
	writer.writeheader()
	for filename in files:
		if "output" in filename:
			with open(directory + '/' + filename) as csvfile:
				reader = csv.DictReader(csvfile)
				for row in reader:
					row["Ch1"] = channels[filename][0]
					row["Ch2"] = channels[filename][1]
					row["Ch3"] = channels[filename][2]
					writer.writerow(row)

