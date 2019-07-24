import os, csv
from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser  
from ij.io import OpenDialog
from ij.io import FileSaver
from ij.gui import WaitForUserDialog
from ij.plugin import MontageMaker

filenames = []
	
path = OpenDialog("Open the filenames csv file")
	
with open(path.getPath()) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		filenames.append(row) 


dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory()


dc = DirectoryChooser("Select an output directory")
outputDirectory = dc.getDirectory()

for row in filenames:
	for time in ["NPC", "2w", "4w"]:
	
		filename = inputDirectory + time + '/' + row[time]
		print(filename)
		if row[time] != "" and os.path.isfile(filename):

			
			imp = IJ.openImage(filename)
			imp.show()
			IJ.run(imp, "Blue", "");

			if os.path.isfile(filename.replace("d0.TIF", "d1.TIF")):
				imp = IJ.openImage(filename.replace("d0.TIF", "d1.TIF"))
				imp.show()
				IJ.run(imp, "Green", "");
			
			if os.path.isfile(filename.replace("d0.TIF", "d2.TIF")):			
				imp = IJ.openImage(filename.replace("d0.TIF", "d2.TIF"))
				imp.show()
				IJ.run(imp, "Red Hot", "");

			if os.path.isfile(filename.replace("d0.TIF", "d3.TIF")):
				imp = IJ.openImage(filename.replace("d0.TIF", "d3.TIF"))
				imp.show()
				IJ.run(imp, "Red", "");


			IJ.openImage(filename.replace("_R_", "_M_")).show()

			IJ.run(imp, "Images to Stack", "name=Stack title=[] use")
   			imp2 = WindowManager.getCurrentImage() # the Stack

#			try:
			IJ.run(imp2, "Make Montage...", "columns=5 rows=1 scale=0.25  label")
			imp3 = WindowManager.getCurrentImage() # the Montage
			IJ.run(imp2, "Save", "save=" + outputDirectory + '/' + time + '_' + row['Row'] + row['Column'] + '_' + row['Condition'] + "stack.tif")
			IJ.run(imp3, "Save", "save=" + outputDirectory + '/' + time + '_' + row['Row'] + row['Column'] + '_' + row['Condition'] + "montage.tif")
#			except:
#				print("a")
    			
    		IJ.run(imp, "Close All", "")

print("Done!")