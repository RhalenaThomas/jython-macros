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


for image in os.listdir(inputDirectory):
	print(image)
	if "stack" in image:
		imp = IJ.openImage(inputDirectory + "/" + image)
		imp2 = IJ.openImage(inputDirectory + "/" + image.replace("stack", "montage"))
		imp.show()
		imp2.show()
		
		
		gd = GenericDialog("?")
		gd.addChoice("Would you like to adjust this one?", ["No", "Yes"], "No")
		gd.showDialog()
		if gd.getNextChoice() == "Yes":
			imp2.close();
			IJ.run("Brightness/Contrast...");
			WaitForUserDialog("Title", "Adjust intensities").show()
			IJ.run("Stack to Images", "");
			Magenta.show()
			Magenta.close();
			IJ.run(imp, "Merge Channels...", "c2=Green c3=Blue c7=Yellow create keep");
			imp = WindowManager.getCurrentImage() 
			IJ.run(imp, "RGB Color", "");
			IJ.run(imp, "Images to Stack", "name=Stack title=[] use")
			#WaitForUserDialog("Title", "Now you should have a stack check it out ").show()
			imp = WindowManager.getCurrentImage() # the Stack

			imp.show()
			IJ.setForegroundColor(255, 255, 255)
			IJ.run(imp, "Make Montage...", "columns=5 rows=1 scale=0.5 borderWidth = 2 useForegroundColor = True")
			#WaitForUserDialog("Title", "Now we should have the montage").show()
			IJ.run("Save", "save=" + outputDirectory + '/' + image.replace("stack", "newmontage"))

		IJ.run("Close All", "")

print("Done!")
