#!/usr/bin/env python3
#Script to find offset of camera pictures and adjust sgv file accordingly to match 
#the relative position of the circle and crosshairs to the features of the picture.
#I'm not sure how to write this header properly, but hopefully I'll learn before I release this.
#For questions, contact me! aguima1@lsu.edu

from util import *

writeToLog("break")
writeToLog("Program initialized.")

#This will preceed almost every print and proceed every screen clearing.
header = \
"""
######################################################
#                   Update Circles                   #
#       Version: """ + version + " "*(36 - len(version)) + """#
#       Author: """ + author + " "*(37 - len(author)) + """#
#       License: Probably LSC or LSU or something    #
######################################################
"""
if verbose: clear(); print(header)

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
    
if verbose: clear(); print(header)

#If no camera is specified, the user will be prompted to the camera name
if args.camera == None:
    args.camera = promptCamera()
writeToLog("Camera selected: " + args.camera)
header += "Camera selected: " + args.camera + "\n"
if verbose: clear(); print(header)

#If no images are specified, the user will be prompted to the image paths
if args.images == None:
    args.images = promptImages()
#If not, then the program will ensure that the image files exist, and will prompt the user in case they do not.
else:
    args.images = confirmImages(inferPath(args.images))
writeToLog("Input Images: " + str(args.images)[1:-1])
header += "Input Images: \"" + str(args.images)[1:-1]+ "\"\n"
if verbose: clear(); print(header)

if args.update:
    print("Importing Original Reference Image.")
    reference_Image_Original, reference_Image_Overlayed = getReferenceImages(args.camera)
    
    print("Importing Input Images.")
    input_Images = [Image.open(img) for img in args.images]
    
    print("Combining Input Images.")
    input_Image_Original = overlayImages(input_Images)
    print("Cleaning Combined Image.")
    input_Image_Clean = cleanPixels(input_Image_Original)
    print("Smoothing and Overlaying Input Images.")
    input_Image_Smooth = gaussianSmooth(input_Image_Clean)
    input_Image_Clean = overlayImages([input_Image_Clean, input_Image_Smooth])
    approvedSVG = False
    while not approvedSVG:
        print("Starting Optimization.")
        transf, params = minimizeDifference(reference_Image_Overlayed, input_Image_Clean, header = header, n = args.precision)
        reference_Image_Original_Drawn = reference_Image_Original.copy()
        input_Image_Original_Drawn = input_Image_Original.copy()
        header += "Image Optimization Successfull!\n"
        if verbose: clear(); print(header)

        old_SVG_name = defaultPath + "/" + args.camera + "/" + args.camera + ".svg"
        new_SVG_name = transformSVG(old_SVG_name, args.camera, transf)

        drawImageAndSVG(reference_Image_Original_Drawn, old_SVG_name, args.camera, text = "Reference (Target)")
        drawImageAndSVG(input_Image_Original_Drawn, new_SVG_name, args.camera, text = "Current (Input)")
        reference_Image_Original_Drawn.show()
        input_Image_Original_Drawn.show()

        if verbose: clear(); print(header)
        approvedSVG = promptSVGApproval()

        if approvedSVG:
            writeToLog("Optimization approved by user.")
            if verbose: clear(); print(header)
            approvedSVGUpdate = promptSVGUpdateApproval()
            if approvedSVGUpdate:
                writeToLog("SVG replacement approved by the user.")
                if verbose: clear(); print(header)
                old_SVG_name = svgsPath + "/L1-CAM-" + args.camera + ".svg"
                if not (args.yes or args.quiet):
                    print("The file to be replaced is \"" + old_SVG_name + "\"\nPress Enter to continue or specify correct file name.")
                    alt_svg_Name = confirmVector(input(), bypass = '')
                    if alt_svg_Name != '':
                        old_SVG_name = alt_svg_Name

                replaceFiles(old_SVG_name, new_SVG_name)

            else:
                writeToLog("SVG replacement not approved by the user.")
                exit()        
        else:
            writeToLog("Optimization not approved by user.")
            precisionChangeApproval = True
            if verbose or not args.yes:
                precisionChangeApproval = promtPrecisionChangeApproval()
            if precisionChangeApproval:
                if verbose or args.yes:
                    args.precision = promptPrecision()
                else:
                    args.precision = args.precision + 1
            else:
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
    
    if verbose: print("Importing Input Images.")
    input_Images = [Image.open(img) for img in args.images]
    if verbose: print("Combining Input Images.")
    input_Image_Original = overlayImages(input_Images)
    if verbose: print("Cleaning Combined Image.")
    input_Image_Clean = cleanPixels(input_Image_Original)
    input_Image_Smoothed = gaussianSmooth(input_Image_Clean, header = header)
    input_Image_Overlayed = overlayImages([input_Image_Smoothed, input_Image_Clean])
    
    if len(args.images) > 1:
        for i in range(len(args.images)):
            temp = Image.open(args.images[i])
            newTiffName = tempPath + "/" + args.camera + "_Original_" + str(i) + ".tiff"
            oldTiffName = defaultPath + "/" + args.camera + "/" + args.camera + "_Original_" + str(i) + ".tiff"
            temp.save(newTiffName)
            replaceFiles(oldTiffName, newTiffName, copy = True)
    temp = input_Image_Original
    newTiffName = tempPath + "/" + args.camera + "_Original.tiff"
    oldTiffName = defaultPath + "/" + args.camera + "/" + args.camera + "_Original.tiff"
    temp.save(newTiffName)
    replaceFiles(oldTiffName, newTiffName, copy = True)
    
    temp = input_Image_Overlayed
    newTiffName = tempPath + "/" + args.camera + "_Overlayed.tiff"
    oldTiffName = defaultPath + "/" + args.camera + "/" + args.camera + "_Overlayed.tiff"
    temp.save(newTiffName)
    replaceFiles(oldTiffName, newTiffName, copy = True)

    newSVGName = args.vector
    oldSVGName = defaultPath + "/" + args.camera + "/" + args.camera + ".svg"
    replaceFiles(oldSVGName, newSVGName, copy. = True)


else:
    print("This should not have happened, if you're reading this please contact me at aguima1@lsu.edu")
