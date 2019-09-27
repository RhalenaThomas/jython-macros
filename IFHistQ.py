'''
		IFHistQ 			- ImageJ Macro written in  Python 
		
		Input		- Directory containing IF Histology images
		
		Output		- CSV file containing number of each marker measured and intensity

		Written by: 						Eddie Cai and Rhalena Thomas - NeuroEDDU 
'''

# Import required packages

import os, sys, csv, math, datetime
from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.process import ImageProcessor
from ij.process import ImageConverter
from ij.gui import WaitForUserDialog
from ij.gui import GenericDialog
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer
from ij.plugin import ChannelSplitter


# Set Threshold mode

thresholdMode = False


gd = GenericDialog("Set Threshold Mode")
gd.addChoice("Would you like to enable thresholding mode?", ["No, run the normal macro", "Yes, enable thresholding mode"], "No")
gd.showDialog()
if gd.getNextChoice() == "Yes, enable thresholding mode":
	thresholdMode = True

gd = GenericDialog("Set Thresholds")
gd.addStringField("Lower bound for Red", "100")
gd.addStringField("Lower bound for Green", "100")
gd.addStringField("Lower bound for Blue", "100")
gd.showDialog()


thresholds = {}
thresholds["Red"] = int(gd.getNextString()
)
thresholds["Green"] = int(gd.getNextString()
)
thresholds["Blue"] = int(gd.getNextString())


# Set default thresholds:
#	minimum_size is the minimum area to be considered an ROI

gd = GenericDialog("Other Thresholds.")
gd.addMessage("Ajust after you have determined if new thresholds are needed.")
gd.addStringField("Minimum Size of ROI", "20")
gd.addStringField("Maximum Size of ROI", "1000")

gd.showDialog()


minimum_size = float(gd.getNextString())
maximum_size = float(gd.getNextString())

#set pix_width and pix_height to real dimensions per pixel 

gd = GenericDialog("Dimension Options")
gd.addMessage("Conversion from pixles to uM :Evos 10X pixle width/height = 0.8777017 uM")
gd.addMessage("Conversion from pixles to uM :Evos 4X  pixle width/height = 2.1546047 uM")
gd.addMessage("Conversion from pixles to uM :Calculate for your objective and enter below")
gd.addStringField("Pixel Width:", "0.8777017")
gd.addStringField("Pixel Height:", "0.8777017")
gd.showDialog()

pix_width = gd.getNextString()
pix_height = gd.getNextString()


# Get input and output directories with GUI 

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()

output_name = outputDirectory + "output_"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")+".csv"

open(output_name, "w").close

# set the output column names for the csv sheet

subfolders = []

# Finds subfolders in input directory

for subfolder in os.listdir(inputDirectory):
	if os.path.isdir(inputDirectory + subfolder):
		subfolders.append(subfolder)

# If there are no subfolders, runs on images in input directory instead

if len(subfolders) == 0:
	subfolders = [""]

for subfolder in subfolders:

	#Opens each image

	for filename in os.listdir(inputDirectory + subfolder): 
		imp = IJ.openImage(inputDirectory + subfolder + '/' + filename)	

		if imp:
			IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=" +str(pix_width)+ " pixel_height=" +str(pix_height)+" voxel_depth=25400.0508001")			


			# Splits channels

			channels = ChannelSplitter.split(imp);

			# Measures each channel

			summary = {}
			summary['Directory'] = inputDirectory + subfolder
			summary['Filename'] = filename

			color = ["Red", "Green", "Blue"]

			for i, channel in enumerate(channels):
			
				
				summary[color[i] + "-intensity"] = "NA"
				summary[color[i] + "-ROI-count"] = "NA"
				
				summary[color[i] + "-intensity"] = channel.getStatistics(Measurements.MEAN).mean

				channel.show()
				IJ.setThreshold(channel, thresholds[color[i]], 255)

				if thresholdMode:
					channel.show()
					IJ.run("Threshold...")
					WaitForUserDialog("Title", "Adjust threshold for " + color[i]).show()

				summary[color[i] + "-threshold-used"] = ImageProcessor.getMinThreshold(channel.getProcessor())

				IJ.run(channel, "Convert to Mask", "")
				IJ.run(channel, "Watershed", "")
				
				table = ResultsTable()
				roim = RoiManager(True)
				ParticleAnalyzer.setRoiManager(roim)
				pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER | ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES, Measurements.AREA, table, minimum_size, maximum_size, 0.1, 1.0)
				pa.setHideOutputImage(True)
				pa.analyze(channel)
				
				if thresholdMode:
					channel.show()
					WaitForUserDialog("Title", "Look at threshold for" + color[i]).show()
				
				if table.getColumnIndex("Area") != -1:
					summary[color[i] + "-ROI-count"] = len(table.getColumn(table.getColumnIndex("Area")))


				channel.changes = False
				channel.close()

				roim.reset()
				roim.close()

			# Writes everything in the output file

			fieldnames = ["Directory", "Filename", "Red-intensity", "Red-threshold-used", "Red-ROI-count", "Green-intensity", "Green-threshold-used", "Green-ROI-count", "Blue-intensity", "Blue-threshold-used", "Blue-ROI-count"]
			with open(output_name, 'a') as csvfile:		

				writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', lineterminator = '\n')
				if os.path.getsize(output_name) < 1:
					writer.writeheader()
				writer.writerow(summary)

			
			
# End of macro

cat = """

      \    /\           Macro completed!    
       )  ( ')   meow!
      (  /  )
       \(__)|"""

print(cat)

