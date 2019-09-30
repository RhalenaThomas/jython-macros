import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv

root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

outputName = "combined.csv"


fields = ["Ch1", "Ch2", "Ch3", "Media"]

info = {}

d1,d2,d3 = "   "

med = ""

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

		if "E8" in filename:
			med = "E8"
		if "mTeSR" in filename:
			med = "mTeSR1"

		info[filename] = [d1, d2, d3, med]

with open(directory + '/' + outputName, 'w') as csvfile:		
	writer = csv.writer(csvfile)
	writer.writerow(fields)
	for filename in files:
		if "output" in filename:

			m = info[filename][3]
			
			with open(directory + '/' + filename) as csvfile:
				reader = csv.reader(csvfile)

				for i, row in enumerate(reader):

					if i != 0:

						if row[35] != "":

							if row[7] == "False":

								del row[7]

								for j in range(6, len(row)-1):
									if float(row[11]) == 0:
										row.append("")
									else:
										row.append(float(row[j])/float(row[11]))

								row.insert(0, info[filename][0])
								row.insert(1, info[filename][1])
								row.insert(2, info[filename][2])
								row.insert(3, info[filename][3])

								writer.writerow(row)

