import os, csv
from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser  
from ij.io import OpenDialog
from ij.io import FileSaver
from ij.gui import WaitForUserDialog
from ij.plugin import MontageMaker


empty = "/home/bic/rthomas/Desktop/Link to 12CellLinesPaper/emptymontage.tif"

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory()


dc = DirectoryChooser("Select an output directory")
outputDirectory = dc.getDirectory()


for condition in ["E8-1", "E8-2", "mTeSR-1", "mTeSR-2"]:
	for column in ["A","B","C","D","E","F","G","H"]:
		for time in ["NPC", "2w", "4w"]:
			for row in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:
				filename = inputDirectory + time + "_" + column + row + "_" + condition +"montage.tif"
				print(filename)
				if os.path.isfile(filename):
					imp = IJ.openImage(filename)
				else:
					imp = IJ.openImage(empty)
				imp.show()

			IJ.run("Images to Stack", "name=Stack title=[] use")
   			imp2 = WindowManager.getCurrentImage() # the Stack
			#WaitForUserDialog("Title", "Try adjust balance").show()
#			try:
			IJ.run(imp2, "Make Montage...", "columns=1 rows=12 scale=1")
			imp3 = WindowManager.getCurrentImage() # the Montage
			IJ.run(imp2, "Save", "save=" + outputDirectory  + time + '_' + row + '_' + condition + "superstack.tif")
			IJ.run(imp3, "Save", "save=" + outputDirectory  + time + '_' + row + '_' + condition + "supermontage.png")
			imp3.close()
			IJ.run("Close All", "")
			


print("Done!")