import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv

root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

outputName = "combined.csv"


fields = ["Ch1", "Ch2", "Ch3"]

channels = {}

d1,d2,d3 = "zzz"

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
				if i == 27:
					d3 = name.replace("-positive", "")

				name = name.replace(d1, "Ch1")
				name = name.replace(d2, "Ch2")
				name = name.replace(d3, "Ch3")

				if name not in fields:
					fields.append(name)

		channels[filename] = [d1, d2, d3]


with open(directory + '/' + outputName, 'w') as csvfile:		
	writer = csv.writer(csvfile)
	writer.writerow(fields)
	for filename in files:
		if "output" in filename:
			with open(directory + '/' + filename) as csvfile:
				reader = csv.reader(csvfile)

				for i, row in enumerate(reader):

					if i != 0:
						row.insert(0,channels[filename][0])
						row.insert(1,channels[filename][1])
						row.insert(2,channels[filename][2])

						writer.writerow(row)

