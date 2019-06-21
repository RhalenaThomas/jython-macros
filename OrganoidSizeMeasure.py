
import os, sys, math
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.process import ImageProcessor
from ij.process import ImageConverter
from ij.gui import WaitForUserDialog
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer


bud_roundness_threshold = 0.75


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

# 		inputDirectory = subfolder 

	log.write("File Name,Feret,MinFeret,Average Feret,Area,Equivalent Circle Diameter, Ellipse Major, Ellipse Minor, Circularity,Roundness,Solidity,Number of Buds\n")

	for filename in os.listdir(inputDirectory): 
		if filename.endswith(".jpg"):
			imp = IJ.openImage(inputDirectory + filename)
					
			IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	
			ic = ImageConverter(imp);
			ic.convertToGray8();
			IJ.setAutoThreshold(imp, "Default dark")
			#IJ.setThreshold(100, 255)
			#WaitForUserDialog("Title", "Adjust Threshold").show()
			IJ.run(imp, "Convert to Mask", "")
			IJ.run(imp, "Invert", "")
			IJ.run(imp, "Fill Holes", "")
			IJ.run(imp, "Watershed", "")

			
			table = ResultsTable()
			pa = ParticleAnalyzer(ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES, Measurements.AREA | Measurements.FERET | Measurements.CIRCULARITY | Measurements.SHAPE_DESCRIPTORS | Measurements.CENTROID | Measurements.ELLIPSE, table, 3000, 9999999999999999, 0.1, 1.0)
			pa.setHideOutputImage(True)
			pa.analyze(imp)

			maxArea = 0;
			index = 0;
			buds = -1;

			for i, area in enumerate(table.getColumn(table.getColumnIndex("Area"))):
				if area > maxArea:
					maxArea = area
					index = i
					
			for i, rou in enumerate(table.getColumn(table.getColumnIndex("Round"))):
				if rou > bud_roundness_threshold:
					if abs(table.getColumn(table.getColumnIndex("X"))[i]- table.getColumn(table.getColumnIndex("X"))[index]) < table.getColumn(table.getColumnIndex("Feret"))[index]:
						if abs(table.getColumn(table.getColumnIndex("Y"))[i]- table.getColumn(table.getColumnIndex("Y"))[index]) < table.getColumn(table.getColumnIndex("Feret"))[index]:
							buds = buds +1


			#WaitForUserDialog("Title", "Look").show()

			if maxArea > 0:				

				diameter = 2* math.sqrt( float(table.getValue("Area", index)) / (2* math.pi)) 
				
				log.write(filename + ',' + str(table.getValue("Feret", index)) + ',' + str(table.getValue("MinFeret", index)) + ',' + str((table.getValue("MinFeret", index)+table.getValue("Feret", index))/2) + ','  + str(table.getValue("Area", index)) + ',' + str(diameter) + ',' + str(table.getValue("Major", index)) + ','+ str(table.getValue("Minor", index)) + ','+ str(table.getValue("Circ.", index)) + ',' +str(table.getValue("Round", index)) + ',' + str(table.getValue("Solidity", index)) + ',' + str(buds))
			else:
				log.write(filename + ',' + 0 + ',' + 0 + ',' + 0 + ',' + 0)
			
			log.write('\n')

			imp.changes = False
			imp.close()

	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)

