import os, sys
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import Measurements, ResultsTable
from ij.gui import NonBlockingGenericDialog, GenericDialog
from ij.gui import WaitForUserDialog, Toolbar
from ij.plugin import ImageCalculator, Duplicator

# Get input and output directories

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()


# Finds all the subfolders in the main directory

with open(outputDirectory + "measurements.csv", "w") as log:
	
	subfolders = []
		
#	for subfolder in os.listdir(inputDirectory):
#		if os.path.isdir(inputDirectory + subfolder):
#			subfolders.append(subfolder)

#	for subfolder in subfolders:

	IJ.run("Set Measurements...", "  redirect=None decimal=1");

	for filename in os.listdir(inputDirectory): 
		imp = IJ.openImage(inputDirectory + filename)
		if imp:
			imp.show()
			
			
			gd = NonBlockingGenericDialog("Name")  
			gd.addStringField("Filename (if empty, uses original name): ", "")
			gd.showDialog()
			name = gd.getNextString()
			if name == "":
				name = filename.rsplit( ".", 1 )[ 0 ]
			if gd.wasCanceled():
			    name = filename.rsplit( ".", 1 )[ 0 ]
			
			
			IJ.setTool(Toolbar.LINE)
			WaitForUserDialog("Measure 1/3", "Measure a cm, then press OK").show()
   			IJ.run(imp, "Measure", "");
   			
			IJ.setTool(Toolbar.LINE)
			WaitForUserDialog("Measure 2/3", "Measure a cm, then, press OK").show()
   			IJ.run(imp, "Measure", "");
   			
			IJ.setTool(Toolbar.LINE)
			WaitForUserDialog("Measure 3/3", "Measure a cm, then press OK").show()
   			IJ.run(imp, "Measure", "");

			table = ResultsTable.getResultsTable()

			print(table.getColumn(table.getColumnIndex("Length")))

   			measure = 1/(sum(table.getColumn(table.getColumnIndex("Length")))/len(table.getColumn(table.getColumnIndex("Length"))))

			log.write(name +','+ str(measure))

			IJ.selectWindow("Results")
			IJ.run("Close")

			

			carry = 'True'
			i = 1
			while carry == 'True':
				i = i+1
				IJ.setTool(Toolbar.RECTANGLE)
				WaitForUserDialog("Title", "Select organoid area").show() 
	
				cropped_imp = Duplicator().run(imp)
				cropped_imp.show()
				IJ.run(cropped_imp, "Properties...", "unit=cm pixel_width="+str(measure)+" pixel_height="+str(measure))
				IJ.run("Save", "save=" + outputDirectory  + name + "_" + str(i) + ".tif" )
				cropped_imp.close()
	
				gd = GenericDialog("Crop")  
				gd.addChoice("keep going?", ['False', 'True'], 'True')
				gd.showDialog()
				carry = gd.getNextChoice()
				if gd.wasCanceled():
					carry = 'False'
			
			imp.close()

	cat = """

      \    /\           Macro completed!
       )  ( ')   meow!
      (  /  )
       \(__)|"""
	
print(cat)