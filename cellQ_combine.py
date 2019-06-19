import sys, os, Tkinter, tkFileDialog, tkSimpleDialog, csv

root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

outputName = "combined.csv"


fields = ["Ch1", "Ch2", "Ch3", "Media", "Growth", "Viability", "Differentiation", "Attachment", "Score"]

info = {}

d1,d2,d3 = ""

med = ""

growths = {"mTeSR1":[1.5, 0, 2.25, 0.75, 0.5, 1.5, 0.5, 2, 1.5, 2, 0.5, 1], "E8":[0.5, 1.75, 1.25, 1.75, 1.75, 2, 2, 1.75, 1.5, 1.75, 1.5, 1.5]}
viabilities = {"mTeSR1":[1.75, 1.5, 1.5, 1.75, 1.5, 2, 1.25, 1.5, 1.75, 1.75, 1. 1,5], "E8":[1.5, 1.25, 1.75, 1.5, 1.75, 1.5, 1.5, 1.75, 1.5, 1.75, 1.5, 1.5]}
differentiations = {"mTeSR1":[2.5, 2.5, 2.5, 2, 2, 2.5, 2.25, 2, 1.5, 1.75, 0, 0.5], "E8":[2.5, 2.5, 2.25, 2,2,2.5, 2.25, 2.25, 1.5, 1.75, 1.75, 1.5]}
attachments = {"mTeSR1":[2.25, 1.75, 2.25, 1.5, 1.5, 2.5, 2.25, 1.75, 1.75, 1.75, 1.75, 1.25, 1.5], "E8":[1.25, 1.25, 1.75, 1, 1, 2, 1.75, 1.25, 1.25, 1.25, 0, 1.25]}
scores = {"mTeSR1":[6, 3.75, 6.5, 4, 3.5, 6.5, 4.25, 5.25, 4.5, 5.25, 0.75, 2.5],"E8":[3.75, 4.75, 5, 4.25, 4.5, 6, 5.5, 5, 4.25, 4.5, 3, 4]}


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

					if i == 0:
						for j in range(6, len(fields)-1):
							row.append(row[j] + "_per_nuclei")

					else:
						
						for j in range(6, len(fields)-1):
							row.append(row[j]/row[10])

						row.insert(0, channels[filename][0])
						row.insert(1, channels[filename][1])
						row.insert(2, channels[filename][2])
						row.insert(3, channels[filename][3])
						
						line = int(row[9])

						row.insert(4, growths[m][line-1])
						row.insert(5, viabilities[m][line-1])
						row.insert(6, differentiations[m][line-1])
						row.insert(7, attachments[m][line-1])
						row.insert(8, scores[m][line-1])

						writer.writerow(row)

