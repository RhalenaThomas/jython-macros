'''
		EMCC: Evos Marker Cell Counter 			- ImageJ Macro written in  Python 
		
		Input 		- Folders containing split channel images for Organoids
					- The filenames of the images must end in ch00, ch01, ch02, ch03
					- Optional thresholding can be loaded as well
		
		Output		- CSV file containing nuclei counts and marker colocalization data for each image 

		Written by: 						Eddie Cai & Rhalena A. Thomas & Vince & Valerio
'''


import os, sys, math, csv, datetime
from ij import IJ, Prefs, ImagePlus
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
from ij.plugin.filter import MaximumFinder
from ij.plugin.filter import ThresholdToSelection
from ij.WindowManager import getImage
from ij.WindowManager import setTempCurrentImage

MF = MaximumFinder()

# To enable displayxImages mode (such as for testing thresholds), make displayImages = True
displayImages = False


# Function to get the markers needed with a generic dialog for each subfolder, as well as the name of the output for that subfolder
def getChannels(subFolder):  
  	gd = GenericDialog("Channel Options")  

	gd.addStringField("Brain Region:", "")

	gd.addMessage("Name the markers associated with this directory:")
	gd.addMessage(inputDirectory + subFolder)  
	gd.addMessage("(Leave empty to ignore)")
	gd.addMessage("")
  	gd.addStringField("Channel 2:", "DAB")
  	gd.addStringField("Channel 1:", "HEMO")
  	gd.addStringField("Channel 3:", "")
  	
  	gd.showDialog()

	channelNames = []

	region = gd.getNextString()
  	
  	channelNames.append([gd.getNextString(), 0])
  	channelNames.append([gd.getNextString(), 1])
	channelNames.append([gd.getNextString(), 2])

	channels = []
	for i,v in enumerate(channelNames):
		if v[0] != "":
			channels.append(v)

  	if gd.wasCanceled():  
		print "User canceled dialog!"  
		return
		
  	return region, channels

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

def getNames():
	info = []
	
	gd = GenericDialog("Naming options")
	gd.addChoice("How would you like to output your results?", ["default", "use information csv file"], "default")
	gd.showDialog()

	choice = gd.getNextChoice()

	log.write("Option: " + choice + "\n")

	if choice == "use information csv file":
		path = OpenDialog("Open the names csv file")
		log.write("File used: " + path.getPath() + "\n")
		
		with open(path.getPath()) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				info.append(row)
	
	return info

############# Main loop, will run for every image. ##############

def process(subFolder, outputDirectory, filename):


	imp = IJ.openImage(inputDirectory + subFolder + '/' +  filename)
	imp.show()
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	ic = ImageConverter(imp);
	dup = imp.duplicate()
	dup_title = dup.getTitle() 
	ic.convertToGray8();
	imp.updateAndDraw()
	IJ.run("Threshold...")

	
	IJ.setThreshold(218, 245)

	IJ.run(imp, "Convert to Mask", "")

	rm = RoiManager()
	imp.getProcessor().setThreshold(0, 0, ImageProcessor.NO_LUT_UPDATE)
	boundroi = ThresholdToSelection.run(imp)
	rm.addRoi(boundroi)

	if not displayImages:
		imp.changes = False
		imp.close()

	images = [None] * 5
	intensities = [None] * 5
	blobsarea = [None] * 5
	blobsnuclei = [None] * 5
	bigareas = [None] * 5

	IJ.run(dup, "Colour Deconvolution", "vectors=[H DAB]")

	images[0] = getImage(dup_title+ "-(Colour_2)")
	images[1] = getImage(dup_title+ "-(Colour_1)")
	images[2] = getImage(dup_title+ "-(Colour_3)")

	images[2].close()
	
	for chan in channels:
		v, x = chan
		imp = images[x]
		imp.show()
		for roi in rm.getRoiManager().getRoisAsArray():
			imp.setRoi(roi)
			stats = imp.getStatistics(Measurements.MEAN | Measurements.AREA)
			intensities[x] = stats.mean
			bigareas[x] = stats.area

	rm.close()
	# Opens the ch00 image and sets default properties
	
	imp = images[0].duplicate()
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	
	# Sets the threshold and watersheds. for more details on image processing, see https://imagej.nih.gov/ij/developer/api/ij/process/ImageProcessor.html 

	imp.show()
	setTempCurrentImage(imp)
	ic = ImageConverter(imp);
	imp.updateAndDraw()
	IJ.run(imp,"Gaussian Blur...","sigma="+str(blur))
	imp.updateAndDraw()
	
	IJ.run("Threshold...")
	IJ.setThreshold(30, lowerBounds[0])
	if displayImages:
		WaitForUserDialog("Title", "aDJUST tHRESHOLD aaaaaaaaaaaaa").show()
	IJ.run(imp, "Convert to Mask", "")

	
	# Counts and measures the area of particles and adds them to a table called areas. Also adds them to the ROI manager

	table = ResultsTable()
	roim = RoiManager()
	pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA, table, 5, 9999999999999999, 0.05, 1.0)
	
	
	
	
	pa.setHideOutputImage(True)
	imp = IJ.getImage() 
	# imp.getProcessor().invert()
	pa.analyze(imp)

	if not displayImages:
		imp.changes = False
		imp.close()

	areas = table.getColumn(0)

	# This loop goes through the remaining channels for the other markers, by replacing the ch00 at the end with its corresponding channel
	# It will save all the area fractions into a 2d array called areaFractionsArray
	
	areaFractionsArray = [None] * 5
	for chan in channels:
		v, x = chan
		# Opens each image and thresholds
		
		imp = images[x]
		IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")

		imp.show()

		setTempCurrentImage(imp)
		
		ic = ImageConverter(imp);
		ic.convertToGray8();
		imp.updateAndDraw()
		IJ.run("Threshold...")
		IJ.setThreshold(20, lowerBounds[0])
		if displayImages:
			WaitForUserDialog("Title", "aDJUST tHRESHOLD aaaaaaaaaaaaa").show()
		IJ.run(imp, "Convert to Mask", "")
	
		# Measures the area fraction of the new image for each ROI from the ROI manager.
		areaFractions = []
		for roi in roim.getRoiManager().getRoisAsArray():
	  		imp.setRoi(roi)
	  		stats = imp.getStatistics(Measurements.AREA_FRACTION)
	  		areaFractions.append(stats.areaFraction)
	
		# Saves the results in areaFractionArray
	  			
		areaFractionsArray[x] = areaFractions

	roim.close()

	
	for chan in channels:
		v, x = chan
		
		imp = images[x]
		imp.deleteRoi()
		imp.updateAndDraw()
		setTempCurrentImage(imp)
		roim = RoiManager()
		pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA, table, 15, 9999999999999999, 0.2, 1.0)
		pa.analyze(imp)
		
		blobs = []
		for roi in roim.getRoiManager().getRoisAsArray():
	  		imp.setRoi(roi)
	  		stats = imp.getStatistics(Measurements.AREA)
	  		blobs.append(stats.area)

		blobsarea[x] = sum(blobs)
		blobsnuclei[x] = len(blobs)
	 


		if not displayImages:
			imp.changes = False
			imp.close()
		roim.reset()
		roim.close()

	# Creates the summary dictionary which will correspond to a single row in the output csv, with each key being a column

	summary = {}
			
	summary['Image'] = filename
	summary['Directory'] = subFolder

	# Adds usual columns
	
	summary['size-average'] = 0
	summary['#nuclei'] = 0
	summary['all-negative'] = 0

	summary['too-big-(>'+str(tooBigThreshold)+')'] = 0
	summary['too-small-(<'+str(tooSmallThreshold)+')'] = 0

	for row in info:
		if row['Animal ID'] == filename[:5]:
			for key, value in row.items():
				summary[key] = value;

	
	# Creates the fieldnames variable needed to create the csv file at the end.

	fieldnames = ['E', 'PFFs', 'Animal ID', 'Time treatment', 'Treatment', 'Name','Directory', 'Image', 'size-average', 'too-big-(>'+str(tooBigThreshold)+')','too-small-(<'+str(tooSmallThreshold)+')',  '#nuclei', 'all-negative']

	# Adds the columns for each individual marker (ignoring Dapi since it was used to count nuclei)

	summary["organoid-area"] = bigareas[0]
	fieldnames.append("organoid-area")
	
	for chan in channels:
  		v, x = chan
	  	summary[v+"-positive"] = 0
	  	fieldnames.append(v+"-positive")
	  	
	  	summary[v+"-intensity"] = intensities[x]
	  	fieldnames.append(v+"-intensity")

	  	summary[v+"-blobsarea"] = blobsarea[x]
	  	fieldnames.append(v+"-blobsarea")

	  	summary[v+"-blobsnuclei"] = blobsnuclei[x]
	  	fieldnames.append(v+"-blobsnuclei")


	  	
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
	for z, area  in enumerate(areas):

		log.write(str(area))
		log.write("\n")
		
		if area > tooBigThreshold:
			summary['too-big-(>'+str(tooBigThreshold)+')'] += 1		
		elif area < tooSmallThreshold:
			summary['too-small-(<'+str(tooSmallThreshold)+')'] += 1
		else:

			summary['#nuclei'] += 1
			areaCounter += area

			temp = 0
			for chan in channels:
				v, x = chan
				if areaFractionsArray[x][z] > areaFractionThreshold[0]:				
					summary[chan[0]+'-positive'] += 1
					if x != 0:
						temp += 1

			if temp == 0:
				summary['all-negative'] += 1
		
			if len(channels) > 2:
				if areaFractionsArray[1][z] > areaFractionThreshold[1]:	
					if areaFractionsArray[2][z] > areaFractionThreshold[2]:
						summary[channels[1][0]+'-'+channels[2][0]+'-positive'] += 1
	
			if len(channels) > 3:
				if areaFractionsArray[1][z] > areaFractionThreshold[1]:	
					if areaFractionsArray[3][z] > areaFractionThreshold[3]:
						summary[channels[1][0]+'-'+channels[3][0]+'-positive'] += 1
				if areaFractionsArray[2][z] > areaFractionThreshold[2]:	
					if areaFractionsArray[3][z] > areaFractionThreshold[3]:
						summary[channels[2][0]+'-'+channels[3][0]+'-positive'] += 1
						if areaFractionsArray[1][z] > areaFractionThreshold[1]:
							summary[channels[1][0]+'-'+channels[2][0]+'-' +channels[3][0]+ '-positive'] += 1

	# Calculate the average of the particles sizes

  	if float(summary['#nuclei']) > 0: 
			summary['size-average'] = round( areaCounter / summary['#nuclei'], 2)

	# Opens and appends one line on the final csv file for the subfolder (remember that this is still inside the loop that goes through each image)

	with open(outputDirectory + "/output.csv", 'a') as csvfile:		
	
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', lineterminator = '\n')
		if os.path.getsize(outputDirectory + "/output.csv") < 1:
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
	
	areaFractionThreshold = [0.2, 0.2, 0.2, 0.2, 0.2]		#you can change these
	tooSmallThreshold = 24
	tooBigThreshold = 500
	blur = 2
	maxima = 20
	
	log.write("________________________\n")
	log.write("Default calculation thresholds: \n")
	log.write("	areaFractionThreshold:" + str(areaFractionThreshold) + "\n")
	log.write("	tooSmallThreshold:" + str(tooSmallThreshold)+"\n")
	log.write("	tooBigThreshold:" + str(tooBigThreshold)+"\n")
	
	# Get options from user. (see functions written on top)
	
	log.write("________________________\n")
	log.write("Getting thresholds...\n")
	thresholds = getThresholds()

	info = getNames()
	
	# Set arrays to store data for each subfolder
	
	allChannels = []
	allRegions = []
	for subFolder in directories:
		region, chan = getChannels(subFolder)
		allChannels.append(chan)
		allRegions.append(region)


	
	# Loop that goes through each sub folder. 
	
	log.write("_______________________________________________________________________\n")
	log.write("Beginning main directory loop: \n")
	log.write("\n")

	open(outputDirectory + "/output.csv", 'w').close
	
	for inde, subFolder in enumerate(directories):
	
		log.write("______________________________________\n")
		log.write("Subfolder: "+ subFolder +"\n")
		log.write("\n")
		
		channels = allChannels[inde]
		region = allRegions[inde]

	
		log.write("Channels: "+ str(channels) +"\n")
		
		lowerBounds = [200, 200, 205, 205, 205]
		for chan in channels:
			v, x = chan
			if (v + '-' + region) in thresholds:
				lowerBounds[x] = int(thresholds[v])
	
		log.write("Lower Bound Thresholds: "+ str(lowerBounds) +"\n")
	
		# Finds all correct EVOS split channel ch0 files and runs through them one at a time (see main loop process() on top)
	
		log.write("_________________________\n")
		log.write("Begining loop for each image \n")


		
		for filename in os.listdir(inputDirectory + subFolder): 
			if filename.endswith(".TIF"):
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