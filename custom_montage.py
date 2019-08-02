import os, csv
from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser  
from ij.io import OpenDialog
from ij.io import FileSaver
from ij.gui import WaitForUserDialog
from ij.plugin import MontageMaker


empty = "/home/bic/rthomas/Desktop/Link to 12CellLinesPaper/emptymontage.tif"

files = []

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory()


dc = DirectoryChooser("Select an output directory")
outputDirectory = dc.getDirectory()



path = OpenDialog("Open the filenames csv file")
	
with open(path.getPath()) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		files.append(row) 

for sets in files:
	name = ""

	for filename in sets:
		if os.path.isfile(inputDirectory + filename):
			imp = IJ.openImage(inputDirectory + filename)
		else:
			imp = IJ.openImage(empty)
		imp.show()		
		name = filename
		
	IJ.run("Images to Stack", "name=Stack title=[] use")
   	imp2 = WindowManager.getCurrentImage() # the Stack
	#WaitForUserDialog("Title", "Try adjust balance").show()
	#try:
	IJ.setForegroundColor(255, 255, 255)
	IJ.run(imp2, "Make Montage...", "co	lumns=5 rows=1 scale=0.5, borderWidth = 2, useForegroundColor = True") 
	imp3 = WindowManager.getCurrentImage() # the Montage
			
	#FileSaver(imp2).saveAsTiff(outputDirectory  + time + '_' + column + '_' + condition + "superstack.tif")
	FileSaver(imp3).saveAsPng(outputDirectory  + name + "_custommontage.png")
	#IJ.run(imp2, "Save", "save=" + outputDirectory  + time + '_' + column + '_' + condition + "superstack.tif")
	#IJ.run(imp3, "Save", "save=" + outputDirectory  + time + '_' + column + '_' + condition + "supermontage.tif")
	imp3.close()
	IJ.run("Close All", "")

print("Done!")