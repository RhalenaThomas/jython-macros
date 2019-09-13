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

		IJ.run(imp, "Enhance Contrast", "saturated=0.35");
		//IJ.run("Brightness/Contrast...");
		IJ.run(imp, "Enhance Contrast", "saturated=0.35");
		IJ.run(imp, "Merge Channels...", "c1=scan_Plate_TR_p00_0_B12f00d0.TIF c2=scan_Plate_TR_p00_0_B12f00d1.TIF create");
	
		IJ.saveAs(imp, "Tiff", "/export03/data/12CellLinesPaper/data/Annotation_Input/4weeks_B12f00.tif");
		imp.close();


		
	IJ.run("Images to Stack", "name=Stack title=[] use")
   	imp2 = WindowManager.getCurrentImage() # the Stack
	#WaitForUserDialog("Title", "Try adjust balance").show()
	#try:
	#IJ.run(imp2, "Make Montage...", "co	lumns=5 rows=1 scale=0.5, border=3) 
	imp3 = WindowManager.getCurrentImage() # the Montage
			
	#FileSaver(imp2).saveAsTiff(outputDirectory  + time + '_' + column + '_' + condition + "superstack.tif")
	FileSaver(imp3).saveAsTiff(outputDirectory  + name + "_tile.TIF")
	#IJ.run(imp2, "Save", "save=" + outputDirectory  + time + '_' + column + '_' + condition + "superstack.tif")
	#IJ.run(imp3, "Save", "save=" + outputDirectory  + time + '_' + column + '_' + condition + "supermontage.tif")
	imp3.close()
	IJ.run("Close All", "")

print("Done!")