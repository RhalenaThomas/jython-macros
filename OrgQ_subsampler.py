
'''
		EMCC: Evos Marker Cell Counter 			- ImageJ Macro written in  Python 
		
		Input 		- Folders containing split channel images for Organoids
					- The filenames of the images must end in ch00, ch01, ch02, ch03
					- Optional thresholding can be loaded as well
		
		Output		- CSV file containing nuclei counts and marker colocalization data for each image 

		Written by: 						Eddie Cai & Rhalena A. Thomas & Vince & Valerio
'''


import os, sys, math, csv, datetime, random
from ij import IJ, Prefs, ImagePlus
from ij.io import DirectoryChooser  
from ij.io import OpenDialog
from ij.io import FileSaver
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
MF = MaximumFinder()

# To enable displayImages mode (such as for testing thresholds), make displayImages = True
displayImages = False


# Function to get the markers needed with a generic dialog for each subfolder, as well as the name of the output for that subfolder
def getChannels(subFolder):  
  	gd = GenericDialog("Channel Options")  

	gd.addMessage("Name the markers associated with this directory:")
	gd.addMessage(inputDirectory + subFolder)  
	gd.addMessage("(Leave empty to ignore)")
	gd.addMessage("")
  	gd.addStringField("Channel ch00:", "Dapi")
  	gd.addStringField("Channel ch01:", "pSYN")
  	gd.addStringField("Channel ch02:", "MAP2")
  	gd.addStringField("Channel ch03:", "SYN")
  	gd.addMessage("")
	gd.addStringField("What would you like the output file to be named:", "output")
  	
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


	roim = RoiManager()
	roim.close()
	
	imp = IJ.openImage(inputDirectory + subFolder + '/' +  filename.replace("_ch00.tif",".tif"))
	imp.show()
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=0.8777017 pixel_height=0.8777017 voxel_depth=25400.0508001")
	ic = ImageConverter(imp);
	ic.convertToGray8();
	imp.updateAndDraw()
	IJ.run("Threshold...")
	IJ.setThreshold(2, 255)
	IJ.run(imp, "Convert to Mask", "")
	IJ.run(imp, "Remove Outliers...", "radius=5" + " threshold=50" + " which=Dark")
	IJ.run(imp, "Remove Outliers...", "radius=5" + " threshold=50" + " which=Bright")
	
	imp.getProcessor().invert()

	imp.show()
	
	WaitForUserDialog("Title", "aDJUST tHRESHOLD").show()

	l = 0
	k = 0
	while l < 5:
		while k < 5:
			roim = RoiManager()
			imp.show()
			copy = imp.duplicate()  
			copy.show()
			Xposition = (int)(round(imp.width/5*l))
			Yposition = (int)(round(imp.width/5*k))
			IJ.makeRectangle(Xposition, Yposition, (int)round(imp.width/5) - 1, (int)round(imp.width/5) - 1)
			roi1 = copy.getRoi()
			copy.setRoi(roi1)
			roim.addRoi(roi1)
			for roi in roim.getRoiManager().getRoisAsArray():
		  		copy.setRoi(roi)
		  		stats = copy.getStatistics(Measurements.MEAN)
			if stats.mean < 128:
				copy.show()
				IJ.run("Crop")
				copy.show()
				FileSaver(copy).saveAsTiff(outputDirectory + '/' +  filename + "_crop_" + str(l) + ".tif")  
				copy.changes = False
				copy.close()
	
				for chan in channels:
					v, x = chan
					image = IJ.openImage(inputDirectory + subFolder + '/' +  filename.replace("ch00.tif", "ch0" + str(x) + ".tif")) 
					image.show()
					IJ.makeRectangle(Xposition, Yposition, 1000, 1000)
					IJ.run("Crop")
					FileSaver(image).saveAsTiff(outputDirectory + '/'  + filename + "_crop_" + str(l) + "_ch0" + str(x) + ".tif")  
					image.changes = False
					image.close()
			else:
				copy.changes = False
				copy.close()
			roim.close()
			k = k + 1
		l = l + 1
		
	imp.getProcessor().setThreshold(0, 0, ImageProcessor.NO_LUT_UPDATE)
	boundroi = ThresholdToSelection.run(imp)

	rm = RoiManager()	
	rm.addRoi(boundroi)

	images = [None] * 5
	intensities = [None] * 5
	blobsarea = [None] * 5
	blobsnuclei = [None] * 5
	areas = [None] * 5

	
	for chan in channels:
		v, x = chan
		images[x] = IJ.openImage(inputDirectory + subFolder + '/' +  filename.replace("ch00.tif", "ch0" + str(x) + ".tif")) 
		imp = images[x]
		for roi in rm.getRoiManager().getRoisAsArray():
			imp.setRoi(roi)
			stats = imp.getStatistics(Measurements.MEAN | Measurements.AREA)
			intensities[x] = stats.mean
			areas[x] = stats.area

	rm.close()

	# Creates the summary dictionary which will correspond to a single row in the output csv, with each key being a column

	summary = {}
			
	summary['Image'] = filename
	summary['Directory'] = subFolder
	
	# Creates the fieldnames variable needed to create the csv file at the end.

	fieldnames = ['Name','Directory', 'Image']

	# Adds the columns for each individual marker (ignoring Dapi since it was used to count nuclei)

	summary["organoid-area"] = areas[x]
	fieldnames.append("organoid-area")
	
	for chan in channels:
  		v, x = chan
	  	
	  	summary[v+"-intensity"] = intensities[x]
	  	fieldnames.append(v+"-intensity")


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
	
	areaFractionThreshold = [0.7, 0.2, 0.7, 0.2, 0.2]		#you can change these
	tooSmallThreshold = 50
	tooBigThreshold = 700
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
		lowerBounds = [40, 20, 35, 50, 40]
		for chan in channels:
			v, x = chan
			if v in thresholds:
				lowerBounds[x] = int(thresholds[v])
	
		log.write("Lower Bound Thresholds: "+ str(lowerBounds) +"\n")
	
		# Finds all correct EVOS split channel ch0 files and runs through them one at a time (see main loop process() on top)
	
		log.write("_________________________\n")
		log.write("Begining loop for each image \n")
		
		for filename in os.listdir(inputDirectory + subFolder): 
			if filename.endswith("ch00.tif"):
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