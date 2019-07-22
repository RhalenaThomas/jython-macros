'''
		OSM: Organoid Size Measurer 			- ImageJ Macro written in  Python 
		
		Input 		- Directory containing Organoid bright field images
		
		Output		- CSV file containing size and shape descriptors for each organoid image

		Written by: 						Eddie Cai
'''

# Import required packages

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

# Set default thresholds:
#	bud_roundness_threshold is the minimum roundness a roi must have to be considered a bud
#	round_threshold is the minimum roundness a roi must have to be considered an organoid
#	area_threshold is the minimum area a roi must have to be considered an organoid

bud_roundness_threshold = 0.75
round_threshold = 0.62
area_threshold = 50000

pix_width = 0.8777017
pix_height = 0.8777017

# Get input and output directories with GUI 

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()

# Defines a function that returns the sorted ranks of a list.

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)



with open(outputDirectory + "output.csv", "w") as output:


	output.write("Subfolder, File Name,Feret,MinFeret,Average Feret,Area,Equivalent Circle Diameter, Ellipse Major, Ellipse Minor, Circularity,Roundness,Solidity,Number of Buds\n")
	subfolders = []
	
	# Finds subfolders in input directory
	
	for subfolder in os.listdir(inputDirectory):
		if os.path.isdir(inputDirectory + subfolder):
			subfolders.append(subfolder)

	# If there are no subfolders, runs on images in input directory instead

	if len(subfolders) == 0:
		subfolders = [""]

	for subfolder in subfolders:

		#Opens each image that ends with .TIF and contains TR (stitched)
	
		for filename in os.listdir(inputDirectory + subfolder): 
			if filename.endswith(".TIF") and "TR" in filename:      							# add file name thing here eg if 4x.TIF
				imp = IJ.openImage(inputDirectory + subfolder + '/' + filename)	

				# 10X objective
				IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=" +str(pix_width)+ " pixel_height=" +str(pix_height)+" voxel_depth=25400.0508001")			# Change to a GUI option later?
				
				# 4X objective 
				# IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")


				# Threshold, fills hole and watershed
				
				ic = ImageConverter(imp);
				ic.convertToGray8();
				IJ.setAutoThreshold(imp, "Default dark")
				IJ.run(imp, "Convert to Mask", "")
				IJ.run(imp, "Invert", "")
				IJ.run(imp, "Fill Holes", "")
				IJ.run(imp, "Watershed", "")
	

				
				#Measure particles (Size > 3000)
				
				table = ResultsTable()
				pa = ParticleAnalyzer(ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES, Measurements.AREA | Measurements.FERET | Measurements.CIRCULARITY | Measurements.SHAPE_DESCRIPTORS | Measurements.CENTROID | Measurements.ELLIPSE, table, 3000, 9999999999999999, 0.1, 1.0)
				pa.setHideOutputImage(True)
				pa.analyze(imp)
	
				minRank = 9999999
				index = 0
				buds = -1	#-1 to not count itself

				# Check if Column even exists (in case it didn't measure anything)
				
				if table.getColumnIndex("Area") != -1:

					# Gets a list of ranks for area and roundness
				
					area_sorted_indexes = sorted(range(len(table.getColumn(table.getColumnIndex("Area")))), key=lambda k: table.getColumn(table.getColumnIndex("Area"))[k])
					round_sorted_indexes = sorted(range(len(table.getColumn(table.getColumnIndex("Round")))), key=lambda k: table.getColumn(table.getColumnIndex("Round"))[k])

					area_array = area_sorted_indexes
					area_order = argsort(area_array)
					area_ranks = argsort(area_order)

					round_array = round_sorted_indexes
					round_order = argsort(round_array)
					round_ranks = argsort(round_order)


					# Finds the biggest and most round ROI (with more importance allocated to size). The smallest Rank will be defined as the organoid

					for i, area in enumerate(table.getColumn(table.getColumnIndex("Area"))):
					
						if area > area_threshold and table.getColumn(table.getColumnIndex("Round"))[i] > round_threshold:
							if 2* area_ranks[i] + round_ranks[i] - 100 < minRank:
								minRank = 2* area_ranks[i] + round_ranks[i] - 100
								index = i
						else:
							if 2* area_ranks[i] + round_ranks[i] < minRank:
	
								minRank = 2* area_ranks[i] + round_ranks[i]
								index = i

					# Counts buds as number of ROI that is within a diameter distance from the center of the organoid and has a roundness level higher than bud_roundness_threshold.
					
					for i, rou in enumerate(table.getColumn(table.getColumnIndex("Round"))):
						if rou > bud_roundness_threshold:
							if abs(table.getColumn(table.getColumnIndex("X"))[i]- table.getColumn(table.getColumnIndex("X"))[index]) < table.getColumn(table.getColumnIndex("Feret"))[index]:
								if abs(table.getColumn(table.getColumnIndex("Y"))[i]- table.getColumn(table.getColumnIndex("Y"))[index]) < table.getColumn(table.getColumnIndex("Feret"))[index]:
									buds = buds +1
	
				#imp.show()
				#WaitForUserDialog("Title", "Look").show()

				# Writes everything in the output file
	
				if minRank < 10:				
	
					diameter = 2* math.sqrt( float(table.getValue("Area", index)) / (2* math.pi)) 

					isOrganoid = table.getValue("Area", index) > area_threshold and table.getValue("Area", index) > round_threshold
					
					output.write(str(subfolder) + ',' + filename + ',' + str(table.getValue("Feret", index)) + ',' + str(table.getValue("MinFeret", index)) + ',' + str((table.getValue("MinFeret", index)+table.getValue("Feret", index))/2) + ','  + str(table.getValue("Area", index)) + ',' + str(diameter) + ',' + str(table.getValue("Major", index)) + ','+ str(table.getValue("Minor", index)) + ','+ str(table.getValue("Circ.", index)) + ',' +str(table.getValue("Round", index)) + ',' + str(table.getValue("Solidity", index)) + ',' + str(buds) + ',' + str(isOrganoid))
				else:
					output.write(str(subfolder) + ',' + filename + ",NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA")
				
				output.write('\n')
	
				imp.changes = False
				imp.close()


	# End of macro
	
	cat = """
	
	      \    /\           Macro completed!    
	       )  ( ')   meow!
	      (  /  )
	       \(__)|"""
		
	print(cat)
	
