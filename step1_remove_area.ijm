// Written by Vince Soubannier & Eddie Cai
// Adjusted by Rhalena Thomas
//  
//Step 1 cut the bad parts out the the image and make a folder with the tiff to input into a batch



function action(input, output, filename)
{	
		open(input + filename);

		

		// remove parts of sections
			// This will cut away the selected area and make it white

		setTool("rectangle");
		makeRectangle(0, 0, 1, 1); //selects one pixel in case there is nothing to remove
		setTool("freehand");

		waitForUser( "Pause","Please isolate manually the region to REMOVE.  \n If you do not select anything, nothing will be removed. \n  \n Press OK when you are done");
		setBackgroundColor(255, 255, 255);
		run("Clear", "slice");
		run("Select None");

		saveAs(filename, output + filename + "_cut.TIF");
		
	    close();



}


input = getDirectory("Choose Input Directory");

output = getDirectory("Choose Output Directory");

list = getFileList(input);
for (i = 0; i < list.length; i++)
{

		if (endsWith(list[i], ".TIF")) {
			action(input, output, list[i]);	
		}

}


waitForUser("Finished!", "Analysis Complete!");
