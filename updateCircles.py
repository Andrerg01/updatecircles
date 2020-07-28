#!/usr/bin/env python3
#Script to find offset of camera pictures and adjust sgv file accordingly to match 
#the relative position of the circle and crosshairs to the features of the picture.
#I'm not sure how to write this header properly, but hopefully I'll learn before I release this.
#For questions, contact me! aguima1@lsu.edu

from util import *

menuChoice = ''
while menuChoice != '1' and menuChoice != '2' and menuChoice != '3' and menuChoice != '4':
    writeToLog("break")
    writeToLog("Program initialized.")
    print('What would you like to do?')
    print('1 - Update Circle (Update SVG file).')
    print('2 - Change Reference Image/SVG file for a camera.')
    
    menuChoice = input()
    if menuChoice.lower() == 'exit':
        writeToLog("Program exited by user.")
        print('bye bye!')
        os._exit(0)
    elif menuChoice != '1' and menuChoice != '2' and menuChoice != '3' and menuChoice != '4':
        print('Choice not recognized, please chose a valid option.')
    

if menuChoice == '1':
    writeToLog("Update Cirlce Request Made.")
    cameraName = ''
    fileOpen = False
    while cameraName not in cameras or cameraName == '' or not fileOpen:
        print("Please speficy camera " + str(cameras))
        cameraName = input()
        cameraName = cameraName.upper()
        if cameraName.lower() == 'exit':
            writeToLog("Program exited by user.")
            print('bye bye!')
            os._exit(0)
        elif cameraName not in cameras:
            print("Camera name " + cameraName + " is not a known camera.")
            writeToLog("Unknown Camera Specified: " + cameraName)
        else:
            writeToLog("Selected Camera " + cameraName)
            try:
                referenceImage = Image.open(defaultPath + "/" + cameraName + "/" + cameraName+"_Original.tiff")
                print("Reference Image successfully imported.")
                writeToLog("Reference Image Imported " + defaultPath + "/" + cameraName + "/" + cameraName+"_Original.tiff")
                fileOpen = True
            except:
                print("Error: Could not find reference image for " + cameraName)
                writeToLog("No Reference Image Found for " + cameraName)
            
    fileOpen = False
    while not fileOpen:
        print("Please specify the path or name of the current camera image.")
        imageName = input()
        if imageName.lower() == 'exit':
            writeToLog("Program exited by user.")
            print('bye bye!')
            os._exit(0)
        elif '/' not in imageName:
            writeToLog("Current Image Inputed by User " + imageName)
            imageName = shotsPath + '/' + imageName
            writeToLog("Deduced Inputed Image Path " + imageName)
        else:
            writeToLog("Current Image Inputed by User " + imageName)
        try:
            inputImage = Image.open(imageName)
            print("Input Image successfully imported.")
            writeToLog("Input Image Successfully Imported " + imageName)
            fileOpen = True
        except:
            print("Error: Could not Find Input Image " + imageName)
            writeToLog("Could not Find Input Image " + imageName)
            
    recMoves, recPixels, imgDefault, imgOutput = optimizeImg(imageName, cameraName)
    writeToLog("Image Optimization Successfull.")
    
    font = ImageFont.truetype("fonts/arial.ttf", 20)
    oldSVG = defaultPath + "/" + cameraName + "/" + cameraName + ".svg"
    newSVG = transformSVG(oldSVG, cameraName, recMoves, recPixels)
    cx, cy, r, l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2 = getPointsSVG(oldSVG)
    imgDraw1 = ImageDraw.Draw(referenceImage)
    imgDraw1.line((l1x1,l1y1,l1x2,l1y2), fill=128)
    imgDraw1.line((l2x1,l2y1,l2x2,l2y2), fill=128)
    imgDraw1.ellipse([cx-r,cy-r,cx+r,cy+r], outline = 128, width = 1)
    imgDraw1.text((xshape/2,yshape*.1), "Reference (Default) " + cameraName, font = font, fill = 128)
    
    cx, cy, r, l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2 = getPointsSVG(newSVG)
    imgDraw2 = ImageDraw.Draw(inputImage)
    imgDraw2.line((l1x1,l1y1,l1x2,l1y2), fill=128)
    imgDraw2.line((l2x1,l2y1,l2x2,l2y2), fill=128)
    imgDraw2.ellipse([cx-r,cy-r,cx+r,cy+r], outline = 128, width = 1)
    imgDraw2.text((xshape/2,yshape*.1), "Inputed (Current) " + cameraName, font = font ,fill = 128)
    
    referenceImage.show()
    inputImage.show()
    
    answer = ''
    while answer.lower() != 'y' and answer.lower() != 'yes' and answer.lower() != 'n' and answer.lower() != 'no':
        print("Is the svg matching satisfactory? (y/n)")
        answer = input()
        if answer.lower() == 'exit':
            writeToLog("Program exited by user.")
            print('bye bye!')
            os._exit(0)
        elif answer.lower() != 'y' and answer.lower() != 'yes' and answer.lower() != 'n' and answer.lower() != 'no':
            print("Answer not recognized, please try again.")
            writeToLog("Uncertain Approval Answer 1 From The User " + answer.lower())
    if answer.lower() == 'y' or answer.lower() == 'yes':
        writeToLog("Optimization approved by user.")
        answer2 = ''
        while answer2.lower() != 'y' and answer2.lower() != 'yes' and answer2.lower() != 'n' and answer2.lower() != 'no':
            print("Do you wish to replace the current svg file (y/n)? (A backup will be made.)")
            answer2 = input()
            if answer2.lower() == 'exit':
                writeToLog("Program exited by user.")
                print('bye bye!')
                os._exit(0)
            elif answer2.lower() != 'y' and answer2.lower() != 'yes' and answer2.lower() != 'n' and answer2.lower() != 'no':
                print("Answer not recognized, please try again.")
                writeToLog("Uncertain Approval Answer 2 From The User " + answer2.lower())
        if answer2.lower() == 'y' or answer2.lower() == 'yes':
            writeToLog("SVG replacement approved by the user.")
            print('The file to be replaced is ' + svgsPath + "/L1_CAM_" + cameraName + ".svg\nPress Enter to continue or specify correct file name.")
            svgFileName = input()
            if svgFileName == 'exit':
                writeToLog("Program exited by user.")
                print('bye bye!')
                os._exit(0)
            elif svgFileName == '':
                svgFileName = svgsPath + "/L1_CAM_" + cameraName + ".svg"
            if replaceSVG(newSVG, svgFileName):
                print("Cirlce update successfull!")
                writeToLog("Circle update successfull.")
                os._exit(0)
            else:
                print("Could not replace svg files.")
                writeToLog("Failure to replace svg files.")
                os._exit(0)
            
        else:
            writeToLog("SVG replacement not approved by the user.")
            print("Understood, bye bye!")
            os._exit(0)        
    else:
        writeToLog("Optimization not approved by user.")
        print("Understood, bye bye!")
        os._exit(0)
    
elif menuChoice == '2':
    print("Todo")
elif menuChoice == '3':
    print("Todo")
elif menuChoice == '4':
    print("Todo")
else:
    print("This should not have happened, if you're reading this please contact me at aguima1@lsu.edu")