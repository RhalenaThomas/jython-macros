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

for row in filenames
	for time in ["NPC", "2w", "4w"]:
	
		filename = inputDirectory + time + '/' + row[time]
		print(filename)
		if row[time] != "" and os.path.isfile(filename):



			#d0 image, blue color
			
			imp = IJ.openImage(filename)
			imp.show()
			
			#IJ.run(imp, "Enhance Contrast", "saturated=0.35");
			#imp.setDisplayRange(94, 738);
			#IJ.run(imp, "Apply LUT", "");
			IJ.run(imp, "Blue", "");
			IJ.run(imp, "RGB Color", "");
			imp.setTitle("Blue")



			#d1 image, green color
	
			if os.path.isfile(filename.replace("d0.TIF", "d1.TIF")):
				imp = IJ.openImage(filename.replace("d0.TIF", "d1.TIF"))
				imp.show()
				
				IJ.run(imp, "Enhance Contrast", "saturated=0.35");
				imp.setDisplayRange(94, 738);
				IJ.run(imp, "Apply LUT", "");
				IJ.run(imp, "Green", "");
				IJ.run(imp, "RGB Color", "");
				imp.setTitle("Green")


			#d3 image, magenta color
			
			if os.path.isfile(filename.replace("d0.TIF", "d2.TIF")):			
				imp = IJ.openImage(filename.replace("d0.TIF", "d2.TIF"))
				imp.show()
				
				IJ.run(imp, "Enhance Contrast", "saturated=0.35");
				imp.setDisplayRange(94, 738);
				IJ.run(imp, "Apply LUT", "");
				IJ.run(imp, "Magenta", "");
				IJ.run(imp, "RGB Color", "");
				imp.setTitle("Magenta")


			#d3 image, yellow color

			if os.path.isfile(filename.replace("d0.TIF", "d3.TIF")):
				imp = IJ.openImage(filename.replace("d0.TIF", "d3.TIF"))
				imp.show()
				IJ.run(imp, "Enhance Contrast", "saturated=0.35");
				imp.setDisplayRange(94, 738);
				IJ.run(imp, "Apply LUT", "");
				IJ.run(imp, "Yellow", "");
				IJ.run(imp, "RGB Color", "");
				imp.setTitle("Yellow")
				IJ.run(imp, "Merge Channels...", "c2=Green c3=Blue c6=Magenta c7=Yellow create keep");
			else:
				IJ.run(imp, "Merge Channels...", "c2=Green c3=Blue c6=Magenta create keep");


			
			imp = WindowManager.getCurrentImage() 
			IJ.run(imp, "RGB Color", "");
			#IJ.openImage(filename.replace("_R_", "_M_")).show()

			IJ.run(imp, "Images to Stack", "name=Stack title=[] use")
   			imp2 = WindowManager.getCurrentImage() # the Stack
			#WaitForUserDialog("Title", "Try adjust balance").show()
#			try:
			IJ.run(imp2, "Make Montage...", "columns=5 rows=1 scale=0.5")
			imp3 = WindowManager.getCurrentImage() # the Montage
			IJ.run(imp2, "Save", "save=" + outputDirectory + '/' + time + '_' + row['Row'] + row['Column'] + '_' + row['Condition'] + "stack.tif")
			IJ.run(imp3, "Save", "save=" + outputDirectory + '/' + time + '_' + row['Row'] + row['Column'] + '_' + row['Condition'] + "montage.tif")
#			except:
#				print("a")
    			
    		IJ.run(imp, "Close All", "")

print("Done!")