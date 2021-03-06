# UpdateCircles

A python script which matches images of certain cameras within LIGO Livingston with a default and changes to corresponding svg file to correctly align the crosshair and circle to features of the picture.

## Setup

### Changing default paths

Firstly change the paths in the *config.ini* file to the appropriate paths of the image. The paths to be changed should be:

**shotsPath** -> The path of where all the snapshots from the camera automatically go to. To be added to input images in case no path detected.

**svgsPath** -> The path of where all the svg files used by the camera are located.

### Setting up reference images and svg's

To set up an image and svg pair as a reference for comparison with all future images, type in the command line:

`python updateCircles.py -r -c [Camera Name] -i [Reference Image File #1] [Reference Image File #2] ... -V [Reference svg File]`

**-r** Indicates the program that you are replacing the current reference image and svg files.
   
**-c** Indicates the program which camera you are refering to.

**-i** Indicates the program that you are about to pass the path of image files as inputs (can be as many as are needed).
   
**-V** Indicates the program that you are about to pass the path of an svg file.

*Example:*
`python updatecirCles.py -r -c ITMY4 -i Some/Path/ITMY4_Reference_Image_1.tiff Some/Path/ITMY4_Reference_Image_2.tiff -V Some/Other/Path/ITMY4_Reference_SVG.svg`

The program will overlay the input images if more than one is passed.

## Using the program

### Updating Circles Witout command line options

*It is recommended that the original svg file be backed up manually before trying this for the first time.*

The "circle update" process can be done thorugh the command line by calling:

`python updateCircles.py -u -c [Camera Name] -i [Reference Image File #1] [Reference Image File #2] ...`

**-u** Indicates the program that you are updating circles

**-c** Indicates the program which camera you are refering to.

**-i** Indicates the program that you are about to pass the path of image files as inputs (can be as many as are needed).
   
*Example:*
`python updateCircles.py -u -c EMTX3 -i Some/Path/Or/Just/The/Name/ETMX3_Snapshot_I_Just_took.tiff`

The user will then be presented with a side by side comparison of the reference and inputed images with updated svg files, and prompted to approve and replace the current svg file.

### Updating Circles Witout command line options (not recommended)

By simply calling `python updateCircles.py`. The program will prompt the user about what is to be done and which files are needed.

### All Options

**-c** Indicates the program which camera you are refering to.

**-h** Help page, essentially the same information displayed here but in different wording.

**-i** Indicates the program that you are about to pass the path of image files as inputs (can be as many as are needed).

**-p** Indicates the program the precision to be used when matching the images. Larger precisions will take longer. Defaulted to the parameter "iniRes" in the file "config.ini".

**-q** Indicates the program to surpress much of the output text, except for inquiries.

**-r** Indicates the program that you are replacing the current reference image and svg files.

**-u** Indicates the program that you are updating circles

**-V** Indicates the program that you are about to pass the path of an svg file.

**-y** Indicates the program that answers to inquiries are always yes, except for except for image matching confirmation

**-s** Indicates the program that a gaussian smoothing is to be applied to the input image before minimization. Only has an effect with the -u option but is not tethered to it.


## Authors

* **Andre Guimaraes** - https://github.com/Andrerg01

## Acknowledgments

* **Anamaria Effler**
* **Gabriela Gonzalez**
