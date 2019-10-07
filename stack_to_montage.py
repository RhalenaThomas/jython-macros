# this is the macro to quickly go through image stacks and choose which ones to make into a montage
# the input is sets of stacks and montages that match all in one folder

import os, csv
from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser  
from ij.io import OpenDialog
from ij.io import FileSaver
from ij.gui import WaitForUserDialog
from ij.plugin import MontageMaker
from ij.gui import GenericDialog


dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory()


dc = DirectoryChooser("Select an output directory")
outputDirectory = dc.getDirectory()

filename = []


for image in os.listdir(inputDirectory):
	print(image)
	if "stack" in image:
		imp = IJ.openImage(inputDirectory + "/" + image)
		imp2 = IJ.openImage(inputDirectory + "/" + image.replace("stack", "montage"))



		
		gd = GenericDialog("?")
		gd.addChoice("Would you like to adjust this one?", ["No", "Yes"], "No")
		gd.showDialog()
		if gd.getNextChoice() == "Yes":
			WaitForUserDialog("Title", "Adjust intensities").show()
			IJ.run("Stack to Images", "");
			IJ.run(imp, "Merge Channels...", "c2=Green c3=Blue c6=Magenta c7=Yellow create keep");
			imp = WindowManager.getCurrentImage() 
			IJ.run(imp, "RGB Color", "");
		
			IJ.run(imp, "Images to Stack", "name=Stack title=[] use")
			imp = WindowManager.getCurrentImage() # the Stack

		IJ.setForegroundColor(255, 255, 255)
		IJ.run(imp2, "Make Montage...", "columns=5 rows=1 scale=0.5, borderWidth = 2, useForegroundColor = True")

		imp3 = WindowManager.getCurrentImage() # the Montage

		
		IJ.run(imp3, "Save", "save=" + outputDirectory + '/' + time + '_' + row['Row'] + row['Column'] + '_' + row['Condition'] + "montage.tif")

		IJ.run(imp, "Close All", "")

print("Done!")

