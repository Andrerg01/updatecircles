#!/usr/bin/env python3
#Script to find offset of camera pictures and adjust sgv file accordingly to match 
#the relative position of the circle and crosshairs to the features of the picture.
#I'm not sure how to write this header properly, but hopefully I'll learn before I release this.
#For questions, contact me! aguima1@lsu.edu

from util import *

writeToLog("break")
writeToLog("Program initialized.")

args = sys.argv
cameraNameArg = ''
cameraArg = False
inputImagesArg = []
inputSvgArg = ''
inputImgArg = False
inputSvgArg = False
updateCirclesArg = False
changeReferenceImageArg = False
for i in range(len(args)):
    if args[i] == '-u':
        print("Circle updating requested by user through argument")
        updateCirclesArg = True
    elif args[i] == '-r':
        changeReferenceImageArg = True
    elif args[i] == '-h':
        print('TODO')
    elif args[i] == '-c':
        cameraArg = True
        cameraNameArg = args[i+1]
        writeToLog("User Inputed Camera Name Through Arguments As " + cameraNameArg)
        print('Argument Inputed Camera Name: ' + cameraNameArg)
    elif args[i] == '-v':
        inputSvgArg = True
        inputSvg = args[i+1]
    elif args[i] == '-i':
        inputImgArg = True
        j = i + 1
        while j < len(args) and len(args[j]) > 2:
            inputImagesArg += [args[j]]
            j = j + 1
        writeToLog("User Inputed Input Images Through Arguments As " + str(inputImagesArg))
        print('Argument Inputed Input Image(s) ' + str(inputImagesArg))

if updateCirclesArg:
    menuChoice = '1'
elif changeReferenceImageArg:
    menuChoice = '2'
else:
    print('What would you like to do?')
    print('1 - Update Circle (Update SVG file).')
    print('2 - Change Reference Image/SVG file for a camera.')
    menuChoice = promptUser(['1','2'], 'Choice not recognized, please chose a valid option.', 'User inputed unknown menu choice.')
    
if not cameraArg:
    print("Please speficy camera " + str(cameras))
    cameraName = promptUser(cameras, "Please specify a valid camera name. camera name provided is not a known camera", "Unknown Camera Specified")
else:
    cameraName = promptUser(cameras, "Camera name provided is not a known camera", "Unknown Camera Specified", forcedInput = cameraNameArg)
    
if menuChoice == '1':
    writeToLog("Update Cirlce Request Made.")
    try:
        referenceImage = Image.open(defaultPath + "/" + cameraName + "/" + cameraName+"_Original.tiff")
        referenceImage_Overlayed = Image.open(defaultPath + "/" + cameraName + "/" + cameraName+"_Overlayed.tiff")
        print("Reference Image successfully imported.")
        writeToLog("Reference Image Imported " + defaultPath + "/" + cameraName + "/" + cameraName+"_Original.tiff")
        fileOpen = True
    except:
        print("Error: Could not find reference image for " + cameraName)
        writeToLog("No Reference Image Found for " + cameraName)
    
    inputIamges = []
    if not inputImgArg:
        print("Please specify the path or name of the current camera image(s).")
        imageNames = input().split(' ')
    else:
        imageNames = inputImagesArg
    if imageNames[0].lower() == 'exit':
        writeToLog("Program exited by user.")
        print('bye bye!')
        os._exit(0)
    for i in range(len(imageNames)):
        if '/' not in imageNames[i]:
            writeToLog("Current Image Inputed by User " + imageNames[i])
            imageNames[i] = shotsPath + '/' + imageNames[i]
            writeToLog("Deduced Inputed Image Path " + imageNames[i])
        else:
            writeToLog("Current Image Inputed by User " + imageNames[i])
        fileOpen = False
        while not fileOpen:
            try:
                #inputIamges += [Image.open(imageNames[i])]
                print(imageNames[i])
                Image.open(imageNames[i])
                print("Input Image successfully imported.")
                writeToLog("Input Image Successfully Imported " + imageNames[i])
                fileOpen = True
            except:
                print("Error: Could not Find Input Image " + imageNames[i] + ". Please specify correct path/name")
                writeToLog("Could not Find Input Image " + imageNames[i])
                imageNames[i] = input()
                if imageNames[0].lower() == 'exit':
                    writeToLog("Program exited by user.")
                    print('bye bye!')
                    os._exit(0)
                elif '/' not in imageNames[i]:
                    writeToLog("Current Image Inputed by User " + imageNames[i])
                    imageNames[i] = shotsPath + '/' + imageNames[i]
                    writeToLog("Deduced Inputed Image Path " + imageNames[i])
    
    if isinstance(imageNames, list):
        inputImage = Image.open(imageNames[0])
        for i in range(1, len(imageNames)):
            inputImage = Image.open(imageNames[i])
            inputImage = imgOverlay(imgInput, imageNames[i])
    else:
        inputImage = Image.open(imageNames)
    
    inputImage_Clean = cleanPixels(inputImage)
    
    transf, params = minimizeDifference(referenceImage_Overlayed, inputImage_Clean)
    referenceImage_Overlayed.show()
    inputImage_Clean.transform(inputImage_Clean.size, Image.AFFINE, matrixToAffine(transf)).show()
    writeToLog("Image Optimization Successfull.")
            
    font = ImageFont.truetype("fonts/arial.ttf", 20)
    oldSVG = defaultPath + "/" + cameraName + "/" + cameraName + ".svg"
    newSVG = transformSVG(oldSVG, cameraName, transf)
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
    
    
    print("Is the svg matching satisfactory? (y/n)")
    answer = promptUser(['y','yes','Y','YES','Yes','n','no','N','NO','No'], 'Answer not recognized, please try again', 'Uncertain Approval or Disproval for Answer 1 From The User')
    
    if answer.lower() == 'y' or answer.lower() == 'yes':
        writeToLog("Optimization approved by user.")
        print("Do you wish to replace the current svg file (y/n)? (A backup will be made.)")
        answer2 = promptUser(['y','yes','Y','YES','Yes','n','no','N','NO','No'], 'Answer not recognized, please try again', 'Uncertain Approval or Disproval for Answer 2 From The User')
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
    writeToLog("Change Reference Image Request Made.")
    if cameraArg and inputImgArg and inputSvgArg:
        replaceReferenceTiff(cameraName, inputImagesArg)
        replaceReferenceSVG(cameraName, inputSvg)
    if not cameraArg:
        print("Please speficy camera " + str(cameras))
        cameraName = promptUser(cameras, "Please specify a valid camera name. camera name provided is not a known camera", "Unknown Camera Specified")
    else:
        cameraName = promptUser(cameras, "Camera name provided is not a known camera", "Unknown Camera Specified", forcedInput = cameraNameArg)
    if not inputImgArg:
        print("Please specify the path or name of the current camera image(s).")
        imageNames = input().split(' ')
    else:
        imageNames = inputImagesArg
        
    if imageNames[0].lower() == 'exit':
        writeToLog("Program exited by user.")
        print('bye bye!')
        os._exit(0)
    for i in range(len(imageNames)):
        if '/' not in imageNames[i]:
            writeToLog("Current Image Inputed by User " + imageNames[i])
            imageNames[i] = shotsPath + '/' + imageNames[i]
            writeToLog("Deduced Inputed Image Path " + imageNames[i])
        else:
            writeToLog("Current Image Inputed by User " + imageNames[i])
        fileOpen = False
        while not fileOpen:
            try:
                print(imageNames[i])
                Image.open(imageNames[i])
                print("Input Image successfully imported.")
                writeToLog("Input Image Successfully Imported " + imageNames[i])
                fileOpen = True
            except:
                print("Error: Could not Find Input Image " + imageNames[i] + ". Please specify correct path/name")
                writeToLog("Could not Find Input Image " + imageNames[i])
                imageNames[i] = input()
                if imageNames[0].lower() == 'exit':
                    writeToLog("Program exited by user.")
                    print('bye bye!')
                    os._exit(0)
                elif '/' not in imageNames[i]:
                    writeToLog("Current Image Inputed by User " + imageNames[i])
                    imageNames[i] = shotsPath + '/' + imageNames[i]
                    writeToLog("Deduced Inputed Image Path " + imageNames[i])
    if isinstance(imageNames, list):
        inputImage = Image.open(imageNames[0])
        for i in range(1, len(imageNames)):
            inputImage = Image.open(imageNames[i])
            inputImage = imgOverlay(imgInput, imageNames[i])
    else:
        inputImage = Image.open(imageNames)
    
    replaceReferenceTiff(cameraName, inputImagesArg)
    replaceReferenceSVG(cameraName, inputSvg)
    
    #if vectorArg:
    #    replaceReferenceSVG(cameraName, inputSVGArg)
else:
    print("This should not have happened, if you're reading this please contact me at aguima1@lsu.edu")