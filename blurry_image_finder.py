
import os, sys
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import Measurements


# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()


# Finds all the subfolders in the main directory

with open(outputDirectory + "blurry-output.csv", "w") as log:
	
	
	subfolders = []
		
#	for subfolder in os.listdir(inputDirectory):
#		if os.path.isdir(inputDirectory + subfolder):
#			subfolders.append(subfolder)

#	for subfolder in subfolders:
	for filename in os.listdir(inputDirectory): 
		if filename.endswith(".TIF"):
			imp = IJ.openImage(inputDirectory + filename)
				
			IJ.run(imp, "Convolve...", "text1=[-1 -1 -1 -1 -1\n-1 -1 -1 -1 -1\n-1 -1 24 -1 -1\n-1 -1 -1 -1 -1\n-1 -1 -1 -1 -1\n] normalize");
			stats = imp.getStatistics(Measurements.MEAN | Measurements.MIN_MAX | Measurements.STD_DEV)
			imp.close()			
			blurry = (stats.mean < 20 and stats.stdDev < 25) or  stats.max < 250
			log.write(filename + ',' + str(stats.mean) + ',' + str(stats.stdDev) + ',' + str(stats.max) + ',' + str(blurry))
			log.write('\n')



	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)