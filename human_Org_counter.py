import os, sys
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import Measurements
from ij.gui import NonBlockingGenericDialog
from ij.gui import WaitForUserDialog

# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()


gd = NonBlockingGenericDialog("Channel Options")  
gd.addStringField("Enter your name: ", "")
gd.showDialog()
name = gd.getNextString()

if gd.wasCanceled():  
	print "User canceled dialog!"  

# Finds all the subfolders in the main directory

with open(outputDirectory + "manual_counts_" + name + ".csv", "w") as log:
	
	
	subfolders = []
		
#	for subfolder in os.listdir(inputDirectory):
#		if os.path.isdir(inputDirectory + subfolder):
#			subfolders.append(subfolder)

#	for subfolder in subfolders:
	for filename in os.listdir(inputDirectory): 
		if filename.endswith(".tif"):
			imp = IJ.openImage(inputDirectory + filename)
			imp.show()
			WaitForUserDialog("Title", "Count everything and fill in the dialogue boxes").show()
			print("an images was shown")

			
			gd = NonBlockingGenericDialog("Time to count things")  
			gd.addStringField("Number of nuclei: ", "")
			gd.addStringField("Number of MAP2 positive cells: ", "")
			gd.addStringField("Number of syn positive cells: ", "")
			gd.addStringField("Number of p-syn positive cells: ", "")
			gd.addStringField("Number of p-syn depositives in OR out of a cell: ", "")
			gd.showDialog()
			log.write(filename + ',' + gd.getNextString() + ',' + gd.getNextString() + ',' + gd.getNextString()+ ',' + gd.getNextString()+ ',' + gd.getNextString())
			log.write('\n')

			imp.close()



	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)