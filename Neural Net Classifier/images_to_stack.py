
import os, sys
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser  

# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()


# Finds all the subfolders in the main directory

subfolders = []


	
for subfolder in os.listdir(inputDirectory):
	if os.path.isdir(inputDirectory + subfolder):
		subfolders.append(subfolder)

for i, subfolder in enumerate(subfolders):
	
	subsubfolders = []

	

	for subsubfolder in os.listdir(inputDirectory + subfolder):
		if os.path.isdir(inputDirectory + subfolder + '/' + subsubfolder):
			subsubfolders.append(subsubfolder)

	for i, subsubfolder in enumerate(subsubfolders):
	
		subsubsubfolders = []
	
		for subsubsubfolder in os.listdir(inputDirectory + subfolder + '/' + subsubfolder):
			if os.path.isdir(inputDirectory + subfolder + '/' + subsubfolder + '/' + subsubsubfolder):
				subsubsubfolders.append(subsubsubfolder)
	
		# Loop that goes through each sub folder. 
		
		for index, subsubsubfolder in enumerate(subsubsubfolders):
	
			images = []
			stack = ImageStack(1936, 1456)


			for filename in os.listdir(inputDirectory + subfolder + '/' + subsubfolder + '/' + subsubsubfolder): 
				if filename.endswith(".jpg"):
					stack.addSlice(filename, IJ.openImage(inputDirectory + subfolder + '/' + subsubfolder + '/' + subsubsubfolder + '/' +  filename).getProcessor()) 
			
			IJ.save(ImagePlus(subfolder, stack), outputDirectory + '/' + subfolder + '_' + subsubfolder + '.tif')

	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)