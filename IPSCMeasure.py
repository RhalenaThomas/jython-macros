'''
		CellQ: Evos Cell Quantification 			- ImageJ Macro written in  Python 
		
		Input 		- A main directory containing Folders containing split channel images from the EVOS Cell Imaging System
					- The filenames of the images must be in it's original format, starting with scan_Plate_R and ending with d0, d1, etc.
					- Optional thresholding and naming convention file can be loaded as well
					- The scans in each subfolder must have the same markers
		
		Output		- CSV file containing nuclei counts and marker colocalization data for each image 

		Written by: 						Eddie Cai & Rhalena A. Thomas 	
'''


import os, sys, csv
from ij import IJ
from ij.io import DirectoryChooser  
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.process import ImageProcessor
from ij.process import ImageConverter
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer
from ij.gui import WaitForUserDialog

# To enable displayImages mode (such as for testing thresholds), make displayImages = True
displayImages = False

outputname = "output"

t1 = 20

############# Main loop, will run for every image. ##############

def process(inputpath, outputpath):
	
	imp = IJ.openImage(inputpath)
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	
	
	IJ.setThreshold(imp, t1, 255)
	#imp.show()
	#WaitForUserDialog("Title", "Look at image").show()
	IJ.run(imp, "Convert to Mask", "")
	IJ.run(imp, "Watershed", "")

	# Counts and measures the area of particles and adds them to a table called areas. Also adds them to the ROI manager

	table = ResultsTable()
	roim = RoiManager(True)
	ParticleAnalyzer.setRoiManager(roim); 
	pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA, table, 50, 9999999999999999, 0.2, 1.0)
	pa.setHideOutputImage(True)
	pa.analyze(imp)

	imp.changes = False
	imp.close()

	areas = table.getColumn(0)

	summary = {}

	if areas:
	
		summary['Image'] = filename
		summary['Nuclei.count'] = len(areas)
		summary['Area.Covered'] = sum(areas)

	fieldnames = list(summary.keys())

	with open(outputpath, 'a') as csvfile:		
	
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', lineterminator = '\n')
		if os.path.getsize(outputDirectory + "/" + outputname +".csv") < 1:
			writer.writeheader()
		writer.writerow(summary)

		

########################## code begins running here ##############################


# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()


open(outputDirectory + "/" + outputname +".csv", 'w').close
	
for filename in os.listdir(inputDirectory): 
	if "d0.TIF" in filename:
		process(inputDirectory + '/' + filename, outputDirectory + "/" + outputname +".csv")


cat = """

      \    /\           Macro completed!
       )  ( ')   meow!	
      (  /  )
       \(__)|"""
	

print(cat)