
import os, sys
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.process import ImageProcessor
from ij.process import ImageConverter
from ij.gui import WaitForUserDialog
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer


# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()


# Finds all the subfolders in the main directory

with open(outputDirectory + "output.csv", "w") as log:
		
#	for subfolder in os.listdir(inputDirectory):
#		if os.path.isdir(inputDirectory + subfolder):
#			subfolders.append(subfolder)

#	for subfolder in subfolders:

	log.write("File Name,Feret,MinFeret,Average Feret,Area,Circularity,Number of Buds\n")

	for filename in os.listdir(inputDirectory): 
		if filename.endswith(".jpg"):
			imp = IJ.openImage(inputDirectory + filename)
					
			IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	
			imp.show()
			ic = ImageConverter(imp);
			ic.convertToGray8();
			imp.updateAndDraw()
			IJ.run("Threshold...")
			IJ.setThreshold(100, 255)
			#WaitForUserDialog("Title", "Adjust Threshold").show()
			IJ.run(imp, "Convert to Mask", "")
			IJ.run(imp, "Invert", "")
			IJ.run(imp, "Fill Holes", "")
			IJ.run(imp, "Watershed", "")

			
			table = ResultsTable()
			roim = RoiManager()
			pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA | Measurements.FERET | Measurements.CIRCULARITY, table, 3000, 9999999999999999, 0.2, 1.0)
			pa.setHideOutputImage(True)
			pa.analyze(imp)

			maxArea = 0;
			index = 0;
			
			for i, area in enumerate(table.getColumn(0)):
				if area > maxArea:
					maxArea = area
					index = i
	
			#WaitForUserDialog("Title", "Look").show()

			if maxArea > 0:				
				log.write(filename + ',' + str(table.getValue("Feret", index)) + ',' + str(table.getValue("MinFeret", index)) + ',' + str((table.getValue("MinFeret", index)+table.getValue("Feret", index))/2) + ','  + str(table.getValue("Area", index)) + ',' + str(table.getValue("Circ.", index)) + ',' + str(len(table.getColumn(0))-1))
			else:
				log.write(filename + ',' + 0 + ',' + 0 + ',' + 0 + ',' + 0)
			
			log.write('\n')

			imp.changes = False
			imp.close()
			roim.close()

	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)

