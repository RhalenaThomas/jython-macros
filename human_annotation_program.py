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

with open(outputDirectory + "annotations_" + name + ".csv", "w") as log:
	
	
	subfolders = []
		
#	for subfolder in os.listdir(inputDirectory):
#		if os.path.isdir(inputDirectory + subfolder):
#			subfolders.append(subfolder)

#	for subfolder in subfolders:
	for filename in os.listdir(inputDirectory): 
		if filename.endswith(".TIF"):
			imp = IJ.openImage(inputDirectory + filename)
			imp.show()
			
			gd = NonBlockingGenericDialog("Channel Options")  
			gd.addMessage("Type in the number for how good you think the neurons are:")
			gd.addMessage("1 = Very Bad, 2 = Bad, 3 = Mediocre, 4 = Good, 5 = Very Good")
			gd.addStringField( ":", "")
			gd.showDialog()
			log.write(filename + ',' + gd.getNextString())
			log.write('\n')

			imp.close()


	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)