#!/usr/bin/env python3
#Script to find offset of camera pictures and adjust sgv file accordingly to match 
#the relative position of the circle and crosshairs to the features of the picture.
#I'm not sure how to write this header properly, but hopefully I'll learn before I release this.
#For questions, contact me! aguima1@lsu.edu

from util import *
import argparse

writeToLog("break")
writeToLog("Program initialized.")

parser = argparse.ArgumentParser(description = 'Processes and Images')

parser.add_argument('-c', '--camera', type = str, choices = cameras, metavar = '', help = 'The camera to be considered.')
parser.add_argument('-i', '--images', type = str, nargs='+', metavar = '',  help = 'The image or images to be processed.')
parser.add_argument('-V', '--vector', type = str, metavar = '', help = 'The SVG file to be processed')

verboseGroup = parser.add_mutually_exclusive_group()
verboseGroup.add_argument('-q', '--quiet', action = 'store_true')
verboseGroup.add_argument('-v', '--verbose', action = 'store_true')

actionGroup = parser.add_mutually_exclusive_group()
actionGroup.add_argument('-u', '--update', action = 'store_true')
actionGroup.add_argument('-r', '--replace', action = 'store_true')

args = parser.parse_args()

#This will preceed almost every print and proceed every screen clearing.
header = \
"""
#####################################################
#                 Update Circles.py                 #
#       Version: No Clue                            #
#       Author: Andre Guimaraes                     #
#       License: Probably LSC or LSU or something   #
#####################################################
"""

#If no update or replace option is specified, the user will be prompted as to what he/she wants the program to do
if not args.update and not args.replace:
    menuChoice = promptMenu()
    if menuChoice == '1':
        args.update = True
    elif menuChoice == '2':
        print(header)
        args.replace = True
if args.update:
    writeToLog("Circle Update Request Made.")
    header += "Operation: Circle Update.\n"
elif args.replace:
    writeToLog("Reference Update Request Made.")
    header += "Operation: Reference Image/SVG Replacement.\n"
    
clear()
print(header)

#If no camera is specified, the user will be prompted to the camera name
if args.camera == None:
    args.camera = promptCamera()
writeToLog("Camera selected: " + args.camera)
header += "Camera selected: " + args.camera + "\n"
clear()
print(header)

#If no images are specified, the user will be prompted to the image paths
if args.images == None:
    args.images = promptImages()
#If not, then the program will ensure that the image files exist, and will prompt the user in case they do not.
else:
    args.images = confirmImages(inferPath(args.images))
writeToLog("Input Images: " + str(args.images)[1:-1])
header += "Input Images: \"" + str(args.images)[1:-1]+ "\"\n"
clear()
print(header)

if args.update:
    print("Importing Original Reference Image.")
    reference_Image_Original, reference_Image_Overlayed = getReferenceImages(args.camera)
    
    print("Importing Input Images.")
    input_Images = [Image.open(img) for img in args.images]
    
    print("Combining Input Images.")
    input_Image_Original = overlayImages(input_Images)
    print("Cleaning Combined Image.")
    input_Image_Clean = cleanPixels(input_Image_Original)
    
    print("Starting Optimization.")
    transf, params = minimizeDifference(reference_Image_Overlayed, input_Image_Clean, header = header)
    header += "Image Optimization Successfull!\n"
    clear()
    print(header)
    
    old_SVG_name = defaultPath + "/" + args.camera + "/" + args.camera + ".svg"
    new_SVG_name = transformSVG(old_SVG_name, args.camera, transf)
    
    drawImageAndSVG(reference_Image_Original, old_SVG_name, args.camera)
    drawImageAndSVG(input_Image_Original, new_SVG_name, args.camera)
    
    reference_Image_Original.show()
    input_Image_Original.show()
    clear()
    print(header)
    approvedSVG = promptSVGApproval()
    
    if approvedSVG:
        writeToLog("Optimization approved by user.")
        clear()
        print(header)
        approvedSVGUpdate = promptSVGUpdateApproval()
        if approvedSVGUpdate:
            writeToLog("SVG replacement approved by the user.")
            clear()
            print(header)
            print('The file to be replaced is \"' + svgsPath + "/L1_CAM_" + args.camera + ".svg\"\nPress Enter to continue or specify correct file name.")
            svgFileName = confirmVector(input(), bypass = '')
            if svgFileName == '':
                svgFileName = svgsPath + "/L1_CAM_" + args.camera + ".svg"
                
            if replaceSVG(newSVG, svgFileName):
                header += "Cirlce update successfull!\n"
                clear()
                print(header)
                print("Cirlce update successfull!")
                writeToLog("Circle update successfull.")
                exit()
            else:
                print("Could not replace svg files.")
                writeToLog("Failure to replace svg files.")
                exit()
            
        else:
            writeToLog("SVG replacement not approved by the user.")
            exit()        
    else:
        writeToLog("Optimization not approved by user.")
        exit()
    
#These commands will only happen if the user is replacing the reference images/svgs
elif args.replace:
    #If no svg file is specified, the user will be prompted to it
    if args.vector == None:
        args.vector = promptVector()
    else:
        args.vector = confirmVector(args.vector)
    writeToLog("Input SVG: \"" + args.vector + "\"")
    header += "Input SVG: \"" + args.vector + "\"\n"
    
    print("Importing Input Images.")
    input_Images = [Image.open(img) for img in args.images]
    print("Combining Input Images.")
    input_Image_Original = overlayImages(input_Images)
    print("Cleaning Combined Image.")
    input_Image_Clean = cleanPixels(input_Image_Original)
    input_Image_Smoothed = gaussianSmooth(input_Image_Clean, header = header)
    input_Image_Overlayed = overlayImages([input_Image_Smoothed, input_Image_Clean])
    
    if len(args.images) > 1:
        for i in range(len(args.images)):
            temp = Image.open(args.images[i])
            newTiffName = tempPath + "/" + args.camera + "_Original_" + str(i) + ".tiff"
            oldTiffName = defaultPath + "/" + args.camera + "/" + args.camera + "_Original_" + str(i) + ".tiff"
            temp.save(newTiffName)
            replaceFiles(oldTiffName, newTiffName)
    temp = input_Image_Original
    newTiffName = tempPath + "/" + args.camera + "_Original.tiff"
    oldTiffName = defaultPath + "/" + args.camera + "/" + args.camera + "_Original.tiff"
    temp.save(newTiffName)
    replaceFiles(oldTiffname, newTiffName)
    
    temp = input_Image_Overlayed
    newTiffName = tempPath + "/" + args.camera + "_Overlayed.tiff"
    oldTiffName = defaultPath + "/" + args.camera + "/" + args.camera + "_Overlayed.tiff"
    temp.save(newTiffName)
    replaceFiles(oldTiffname, newTiffName)

    newSVGName = args.vector
    oldSVGName = defaultPath + "/" + args.camera + "/" + args.camera + ".svg"
    replaceFiles(oldSVGName, newSVGName)


else:
    print("This should not have happened, if you're reading this please contact me at aguima1@lsu.edu")