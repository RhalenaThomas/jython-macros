'''
		EMCC: Evos Marker Cell Counter 			- ImageJ Macro written in  Python 
		
		Input 		- A main directory containing Folders containing split channel images from the EVOS Cell Imaging System
					- The filenames of the images must be in it's original format, starting with scan_Plate_R and ending with d0, d1, etc.
					- Optional thresholding and naming convention file can be loaded as well
					- The scans in each subfolder must have the same markers
		
		Output		- CSV file containing nuclei counts and marker colocalization data for each image 

		Written by: 						Eddie Cai & Rhalena A. Thomas 	
'''


import os, sys, math, csv, datetime
from ij import IJ, Prefs
from ij.io import DirectoryChooser  
from ij.io import OpenDialog
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.process import ImageProcessor
from ij.process import ImageConverter
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer
from ij.gui import GenericDialog
from ij.gui import WaitForUserDialog

# To enable displayImages mode (such as for testing thresholds), make displayImages = True
displayImages = False


# Function to get the markers needed with a generic dialog for each subfolder, as well as the name of the output for that subfolder
def getChannels(subFolder):  
  	gd = GenericDialog("Channel Options")  

	gd.addMessage("Name the markers associated with this directory:")
	gd.addMessage(inputDirectory + subFolder)  
	gd.addMessage("(Leave empty to ignore)")
	gd.addMessage("")
  	gd.addStringField("Channel d0:", "Dapi")
  	gd.addStringField("Channel d1:", "MAP2")
  	gd.addStringField("Channel d2:", "")
  	gd.addStringField("Channel d3:", "")
  	gd.addMessage("")
	gd.addStringField("What would you like the output file to be named:", "output_"+ subFolder)
  	
  	gd.showDialog()

	channelNames = []
  	
  	channelNames.append([gd.getNextString(), 0])
  	channelNames.append([gd.getNextString(), 1])
	channelNames.append([gd.getNextString(), 2])
	channelNames.append([gd.getNextString(), 3])
  	outputName = gd.getNextString()

	channels = []
	for i,v in enumerate(channelNames):
		if v[0] != "":
			channels.append(v)

  	if gd.wasCanceled():  
		print "User canceled dialog!"  
		return
		
  	return channels, outputName

# Function to get the names for each well

def getNames():
	names = {}
	
	gd = GenericDialog("Naming options")
	gd.addChoice("How would you like to name your results for each well?", ["default", "use name convention csv file"], "default")
	gd.showDialog()

	choice = gd.getNextChoice()

	log.write("Option: " + choice + "\n")

	if choice == "use name convention csv file":
		path = OpenDialog("Open the names csv file")
		log.write("File used: " + path.getPath() + "\n")
		
		with open(path.getPath()) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				names[row['Row']] = row 
	
	return names

# Function to get the thresholds.

def getThresholds():
	thresholds = {}
	
	gd = GenericDialog("Threshold options")
	gd.addChoice("How would you like to set your thresholds?", ["default", "use threshold csv file"], "default")
	gd.showDialog()

	choice = gd.getNextChoice()
	log.write("Option: " + choice + "\n")

	if choice == "use threshold csv file":
		path = OpenDialog("Open the thresholds csv file")
		log.write("File used: " + path.getPath() + "\n")
		with open(path.getPath()) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				thresholds = row
	return thresholds


############# Main loop, will run for every image. ##############

def process(subFolder, outputDirectory, filename):

	# Opens the d0 image and sets default properties
	
	imp = IJ.openImage(inputDirectory + subFolder + '/' + filename)
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	
	# Sets the threshold and watersheds. for more details on image processing, see https://imagej.nih.gov/ij/developer/api/ij/process/ImageProcessor.html 

	imp.show()
	ic = ImageConverter(imp);
	ic.convertToGray8();
	imp.updateAndDraw()
	dup = imp.duplicate()
	IJ.run(dup, "Convolve...", "text1=[-1 -1 -1 -1 -1\n-1 -1 -1 -1 -1\n-1 -1 24 -1 -1\n-1 -1 -1 -1 -1\n-1 -1 -1 -1 -1\n] normalize");
	stats = dup.getStatistics(Measurements.MEAN | Measurements.MIN_MAX | Measurements.STD_DEV)
	dup.close()			
	blurry = (stats.mean < 20 and stats.stdDev < 25) or  stats.max < 250
	
	IJ.run("Threshold...")
	IJ.setThreshold(lowerBounds[0], 255)
	if displayImages:
		WaitForUserDialog("Title", "aDJUST tHRESHOLD").show()
	IJ.run(imp, "Convert to Mask", "")
	IJ.run(imp, "Watershed", "")

	# Counts and measures the area of particles and adds them to a table called areas. Also adds them to the ROI manager

	table = ResultsTable()
	roim = RoiManager()
	pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA, table, 15, 9999999999999999, 0.2, 1.0)
	pa.setHideOutputImage(True)
	pa.analyze(imp)

	if not displayImages:
		imp.changes = False
		imp.close()

	areas = table.getColumn(0)

	# This loop goes through the remaining channels for the other markers, by replacing the d0 at the end with its corresponding channel
	# It will save all the area fractions into a 2d array called areaFractionsArray
	
	areaFractionsArray = []
	means = []
	areas = []
	for chan in channels:
		v, x = chan
		# Opens each image and thresholds
		
		imp = IJ.openImage(inputDirectory + subFolder + '/' +  filename.replace("d0.TIF", "d" + str(x) + ".TIF"))
		IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")

		imp.show()
		ic = ImageConverter(imp);
		ic.convertToGray8();
		imp.updateAndDraw()

		stats = imp.getStatistics(Measurements.MEAN)
		means.append(stats.mean)

		IJ.run("Threshold...")
		IJ.setThreshold(lowerBounds[x], 255)
		if displayImages:
			WaitForUserDialog("Title", "aDJUST tHRESHOLD").show()
		IJ.run(imp, "Convert to Mask", "")
		
		stats = imp.getStatistics(Measurements.AREA)
		areas.append(stats.area)
	
		# Measures the area fraction of the new image for each ROI from the ROI manager.
		areaFractions = []
		for roi in roim.getRoiManager().getRoisAsArray():
	  		imp.setRoi(roi)
	  		stats = imp.getStatistics(Measurements.AREA_FRACTION)
	  		areaFractions.append(stats.areaFraction)
	
		# Saves the results in areaFractionArray
	  			
		areaFractionsArray.append(areaFractions)

		if not displayImages:
			imp.changes = False
			imp.close()
	roim.close()
	
	# Figures out what well the image is a part of

	ind = filename.index("p00_0_")
	row = filename[ind + 6: ind + 7]
	column = str(int(filename[ind + 7:ind + 9]))

	# Creates the summary dictionary which will correspond to a single row in the output csv, with each key being a column

	summary = {}

	# Finds the name of the well from the nameArray 2d array
	
	if row in nameArray:
		if column in nameArray[row]:
			summary['Name'] = nameArray[row][column]
			
	summary['Image'] = filename
	summary['Directory'] = subFolder
	summary['Row'] = row
	summary['Column'] = column

	# Adds usual columns
	
	summary['size-average'] = 0
	summary['#nuclei'] = 0
	summary['all-negative'] = 0

	summary['too-big-(>'+str(tooBigThreshold)+')'] = 0
	summary['too-small-(<'+str(tooSmallThreshold)+')'] = 0

	summary['image-quality'] = blurry
	
	# Creates the fieldnames variable needed to create the csv file at the end.

	fieldnames = ['Name','Directory', 'Image', 'Row', 'Column', 'size-average', 'image-quality', 'too-big-(>'+str(tooBigThreshold)+')','too-small-(<'+str(tooSmallThreshold)+')',  '#nuclei', 'all-negative']

	# Adds the columns for each individual marker (ignoring Dapi since it was used to count nuclei)
	
	for chan in channels:
  		v, x = chan
	  	summary[v+"-positive"] = 0
	  	summary[v+"-intensity"] = means[x]
	  	summary[v+"-area"] = areas[x]
	  	fieldnames.append(v+"-positive")
	  	fieldnames.append(v+"-intensity")
	  	fieldnames.append(v+"-area")

	# Adds the column for colocalization between first and second marker
  
	if len(channels) > 2:
		summary[channels[1][0]+'-'+channels[2][0]+'-positive'] = 0
		fieldnames.append(channels[1][0]+'-'+channels[2][0]+'-positive')
		
	# Adds the columns for colocalization between all three markers
	
	if len(channels) > 3:
		summary[channels[1][0]+'-'+channels[3][0]+'-positive'] = 0
		summary[channels[2][0]+'-'+channels[3][0]+'-positive'] = 0
		summary[channels[1][0]+'-'+channels[2][0]+'-' +channels[3][0]+ '-positive'] = 0

		fieldnames.append(channels[1][0]+'-'+channels[3][0]+'-positive')
		fieldnames.append(channels[2][0]+'-'+channels[3][0]+'-positive')
		fieldnames.append(channels[1][0]+'-'+channels[2][0]+'-' +channels[3][0]+ '-positive')
	 
	# Loops through each particle and adds it to each field that it is True for. 

	areaCounter = 0

	if not (areas is None):
		for z, area  in enumerate(areas):
			if not (area is None or summary is None):
				if area > tooBigThreshold:
					summary['too-big-(>'+str(tooBigThreshold)+')'] += 1		
				elif area < tooSmallThreshold:
					summary['too-small-(<'+str(tooSmallThreshold)+')'] += 1
				else:
		
					summary['#nuclei'] += 1
					areaCounter += area
		
					temp = 0
					for y, chan in enumerate(channels):
						v, x = chan
						if areaFractionsArray[y][z] > areaFractionThreshold:
							summary[chan[0]+'-positive'] += 1
							if x != 0:
								temp += 1
		
					if temp == 0:
						summary['all-negative'] += 1
				
					if len(channels) > 2:
						if areaFractionsArray[1][z] > areaFractionThreshold:	
							if areaFractionsArray[2][z] > areaFractionThreshold:
								summary[channels[1][0]+'-'+channels[2][0]+'-positive'] += 1
			
					if len(channels) > 3:
						if areaFractionsArray[1][z] > areaFractionThreshold:	
							if areaFractionsArray[3][z] > areaFractionThreshold:
								summary[channels[1][0]+'-'+channels[3][0]+'-positive'] += 1
						if areaFractionsArray[2][z] > areaFractionThreshold:	
							if areaFractionsArray[3][z] > areaFractionThreshold:
								summary[channels[2][0]+'-'+channels[3][0]+'-positive'] += 1
								if areaFractionsArray[1][z] > areaFractionThreshold:
									summary[channels[1][0]+'-'+channels[2][0]+'-' +channels[3][0]+ '-positive'] += 1

	# Calculate the average of the particles sizes 

  	if float(summary['#nuclei']) > 0: 
			summary['size-average'] = round( areaCounter / summary['#nuclei'], 2)

	# Opens and appends one line on the final csv file for the subfolder (remember that this is still inside the loop that goes through each image)

	with open(outputDirectory + "/" + outputName +".csv", 'a') as csvfile:		
	
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', lineterminator = '\n')
		if os.path.getsize(outputDirectory + "/" + outputName +".csv") < 1:
			writer.writeheader()
		writer.writerow(summary)

########################## code begins running here ##############################


# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()

# Opens log file

with open(outputDirectory + "log.txt", "w") as log:
	
	log.write("log: "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	log.write("\n")
	
	log.write("________________________\n")
	log.write("Input directory selected: " + inputDirectory + "\n")
	
	log.write("________________________\n")
	log.write("Output directory selected: " + outputDirectory + "\n")
	
	# Finds all the subfolders in the main directory
	
	directories = []
	
	for subFolder in os.listdir(inputDirectory):
		if os.path.isdir(inputDirectory + subFolder):
			directories.append(subFolder)
	
	# A few default options
	
	areaFractionThreshold = 0.1
	tooSmallThreshold = 75
	tooBigThreshold = 250
	
	log.write("________________________\n")
	log.write("Default calculation thresholds: \n")
	log.write("	areaFractionThreshold:" + str(areaFractionThreshold) + "\n")
	log.write("	tooSmallThreshold:" + str(tooSmallThreshold)+"\n")
	log.write("	tooBigThreshold:" + str(tooBigThreshold)+"\n")
	
	# Get options from user. (see functions written on top)
	
	log.write("________________________\n")
	log.write("Getting names...\n")
	nameArray = getNames()
	
	log.write("________________________\n")
	log.write("Getting thresholds...\n")
	thresholds = getThresholds()
	
	# Set arrays to store data for each subfolder
	
	allChannels = []
	allOutputNames = []
	for subFolder in directories:
		chan, outputName = getChannels(subFolder)
		allChannels.append(chan)
		allOutputNames.append(outputName)
	
	
	# Loop that goes through each sub folder. 
	
	log.write("_______________________________________________________________________\n")
	log.write("Beginning main directory loop: \n")
	log.write("\n")
	for inde, subFolder in enumerate(directories):
	
		log.write("______________________________________\n")
		log.write("Subfolder: "+ subFolder +"\n")
		log.write("\n")
		
		channels = allChannels[inde]
		outputName = allOutputNames[inde]
	
		log.write("Channels: "+ str(channels) +"\n")
		log.write("Output Name: "+ outputName +"\n")
	
		
		open(outputDirectory + "/" + outputName +".csv", 'w').close
		lowerBounds = [33, 33, 33, 33]
		for chan in channels:
			v, x = chan
			if v in thresholds:
				lowerBounds[x] = int(thresholds[v])
	
		log.write("Lower Bound Thresholds: "+ str(lowerBounds) +"\n")
	
		# Finds all correct EVOS split channel d0 files and runs through them one at a time (see main loop process() on top)
	
		log.write("_________________________\n")
		log.write("Begining loop for each image \n")
		
		for filename in os.listdir(inputDirectory + subFolder): 
			if "Plate_R" in filename and filename.endswith("d0.TIF"):
				log.write("Processing: " + filename +" \n")
				process(subFolder, outputDirectory, filename);
		log.write("_________________________\n")
		log.write("Completed subfolder " + subFolder + ".  \n")
		log.write("\n")

	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
	log.write(cat)

print(cat)