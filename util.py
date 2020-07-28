#Packaged for image manipulation
from PIL import Image, ImageDraw, ImageFont
#mathematical package
import numpy as np
#Package for timinig processes
from datetime import datetime
#Package for executing terminal commands
import os
#Package for reading ini file
import configparser
#Opening and Reading config file
config = configparser.ConfigParser()
config.read('config.ini')
#Assigning variables
xshape = eval(config["Configurations"]["xshape"])
yshape = eval(config["Configurations"]["yshape"])
iniPixels = eval(config["Configurations"]["iniPixels"])
iniStd = eval(config["Configurations"]["iniStd"])
iniThreshold = eval(config["Configurations"]["iniThreshold"])
archivePath = config["Configurations"]["archivePath"]
defaultPath = config["Configurations"]["defaultPath"]
shotsPath = config["Configurations"]["shotsPath"]
tempPath = config["Configurations"]["tempPath"]
cameras = config["Configurations"]["cameras"].split(',')
svgsPath = config["Configurations"]["svgsPath"]

def cleanPixels(image):
    """
    Retunrs a copy of the image changing the value of pixels in the image above or below a given threshold to 255 or 0.
    """
    #Turns image into 2d array of values
    imarray = np.array(image)
    #runs through every value of the arrays
    for i in range(len(imarray)):
        for j in range(len(imarray[i])):
            #Changes the value to 255 or 0 depending on the value of the pixel and the threshold specified.
            if imarray[i][j] >= iniThreshold:
                imarray[i][j] = 255
            else:
                imarray[i][j] = 0
    return Image.fromarray(imarray)
def gaussianSmooth(image):
    """
    Returns a copy of the image where every pixel acts as the peak of a gaussian with standard deviation "iniStd".
    """
    #Turns image into 2d array of values
    imarray = np.array(image)
    #Creates an array of zeroes of same shape and dimensions as the image array
    gaussianArray = np.zeros(imarray.shape)
    #runs through the image array
    totalNonZeroes = sum(imarray.flatten())/255
    count = 0
    for i in range(len(imarray)):
        os.system("clear")
        print("Processing Input Image.")
        pct = 100.*count/totalNonZeroes
        #print(str("%0.2f" % pct) + "%")
        print(progressBar(pct))
        for j in range(len(imarray[i])):
            #If a particular pixel value is non-zero
            if imarray[i][j] > 0:
                count += 1
                #Runs through every pixel of the array of zeroes and calculates the value as if a gaussian peaked at (i,j). Adds that value to the new array.
                for m in range(len(gaussianArray)):
                    for n in range(len(gaussianArray[m])):
                        gaussianArray[m][n] += np.exp(-(((m-i)/xshape)**2 + ((n-j)/yshape)**2)/(2*iniStd**2))
    return Image.fromarray(gaussianArray)

def imgOverlay(img1, img2):
    """
    Returns an overlay of the two images where each pixel value is the greatest between the two images.
    """
    imArray1 = np.array(img1)
    imArray2 = np.array(img2)
    imArrayOut = np.zeros(imArray1.shape)
    for i in range(len(imArray1)):
        for j in range(len(imArray1[i])):
            imArrayOut[i][j] = np.max([imArray1[i][j],imArray2[i][j]])
    return Image.fromarray(imArrayOut)
    
def imgDifference(img1, img2):
    """
    Returns the difference between two images.
    Requires arguments to be PIL Image classes
    The difference is defined here as the absolute value of the difference between the values of each pixel.
    """
    img1Array = np.array(img1)
    img2Array = np.array(img2)
    dif = img1Array - img2Array
    total = 0
    for i in range(len(dif)):
        for j in range(len(dif[i])):
            dif[i][j] = abs(dif[i][j])
            total += dif[i][j]
    return total/(255*xshape*yshape)

def imgTransform(image, transformation, pixels, center = [0,0]):
    """
    Returns a version of the image transformed.
    Rotations require a center to be rotated about, default is 0,0. The image will be rotated by 2*pixel/(shapex+shapey) radians.
    Translation will translate the image by "pixels".
    """
    temp = image
    if transformation == "RC":
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, -center[0], 0, 1, 0))
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, 0, 0, 1, center[1]))
        temp = temp.rotate(-4*pixels/(xshape + yshape)*180/np.pi)
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, center[0], 0, 1, 0))
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, 0, 0, 1, -center[1]))
    elif transformation == "RCC":
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, -center[0], 0, 1, 0))
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, 0, 0, 1, center[1]))
        temp = temp.rotate(4*pixels/(xshape + yshape)*180/np.pi)
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, center[0], 0, 1, 0))
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, 0, 0, 1, -center[1]))
    elif transformation == "TR":
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, -pixels, 0, 1, 0))
    elif transformation == "TL":
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, pixels, 0, 1, 0))
    elif transformation == "TU":
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, 0, 0, 1, pixels))
    elif transformation == "TD":
        temp = temp.transform(temp.size, Image.AFFINE, (1, 0, 0, 0, 1, -pixels))
    return temp

def makeTestImage(originalImage, allowedOperations = ["RC","RCC","TU","TD","TL","TR"]):
    """
    Returns a copy of the original image after applying a random set of transformations.
    """
    #Randomizes a number of transformations
    ntrans = np.random.randint(5,20)
    #Randomly chooses a number "Ntransformations" of transformations out of the possible ones
    trans = np.random.choice(allowedOperations, ntrans)
    #Randomly determines the magnitudes (in pixels) of each transformation.
    mags = np.random.choice(range(20), ntrans)
    img = originalImage
    #Runs thorugh the transformations and applies each
    for i in range(len(trans)):
        img = imgTransform(img,trans[i],mags[i])
    return img

def replaceSVG(svgNew, svgOld):
    backedUp = False
    try:
        newFilePath = archivePath + '/' + svgOld.split("/")[-1] + '_' + datetime.now().strftime("%m_%d_%Y %H_%M_%S")+".bak"
        os.rename(svgOld, newFilePath)
        print("Old svg backed up as " + newFilePath)
        writeToLog("Old svg backed up as " + newFilePath)
        backedUp = True
    except:
        print("Could not backup file " + svgOld)
        writeToLog("Failure to backup file " + svgOld + " to " + newFilePath)
    if backedUp:
        newFileInPlace = False
        try:
            newFilePath2 = svgsPath + '/' + "L1_CAM_" + svgNew.split("/")[-1].split("_")[0] + ".svg"
            os.rename(svgNew, newFilePath2)
            print("New svg put in place as " + newFilePath2)
            writeToLog("New svg successfully put in place as " + newFilePath2)
            return True
        except:
            print("Could not put new SVG file in place as " + newFilePath2)
            writeToLog("Failure to rename file " + svgNew + ' to ' + newFilePath2)
            return False
            
    else:
        return False
        
def optimizeImg(providedImage, cameraName):
    moves = [["RC"],["RCC"],["TU"],["TD"],["TL"],["TR"]]
    start = datetime.now()
    recordedMoves = []
    recordedPixels = []
    recordedDiffs = []
    pixelIntensity = iniPixels
    print("Importing Target Image.")
    imgTarget = Image.open(defaultPath + "/" + cameraName + "/" + cameraName + "_Overlayed.tiff")
    os.system("clear")
    print("Importing Input Image.")
    imgInput = Image.open(providedImage)
    os.system("clear")
    print("Cleaning Input Image")
    imgInput_Clean = cleanPixels(imgInput)
    os.system("clear")
    print("Processing Input Image.")
    imgInput_Smoothed = gaussianSmooth(imgInput_Clean)
    imgInput_Overlayed = imgOverlay(imgInput_Clean,imgInput_Smoothed)
    imgOutput_Overlayed = imgInput_Overlayed
    os.system("clear")
    print("Optimizing")
    oneMore = False
        
    while pixelIntensity > 0:
        diffs = []
        for move in moves:
            imgTemp = imgOutput_Overlayed
            for transf in move:
                imgTemp = imgTransform(imgTemp, transf, pixelIntensity)
            diffs += [imgDifference(imgTarget, imgTemp)]
        argMinDiff = np.argmin(diffs)
        recordedMoves += moves[argMinDiff]
        recordedPixels += [pixelIntensity]
        recordedDiffs += [np.min(diffs)]
        for transf in moves[argMinDiff]:
            imgOutput_Overlayed = imgTransform(imgOutput_Overlayed, transf, pixelIntensity)
        os.system("clear")
        print("Optimizing")
        print("Image Difference: " + str(np.min(diffs)) + "\nTransformations so far: " + str(recordedMoves) + "\nPixel Resolution: " + str(pixelIntensity))
        if oneMore:
            oneMore = False
            pixelIntensity -= 1
        if len(recordedDiffs) > 1 and recordedDiffs[-1] >= recordedDiffs[-2]:
            oneMore = True
    imgOutput = imgInput
    for i in range(len(recordedMoves)):
        imgOutput = imgTransform(imgOutput, recordedMoves[i], recordedPixels[i])
    end = datetime.now()
    os.system("clear")
    print("Done!")
    print("Total Processing Time: " + str((end-start).total_seconds()) + " seconds.")
    return recordedMoves, recordedPixels, imgTarget, imgOutput_Overlayed

def transformPoint(point, moves, pixels):
    moves = moves[::-1]
    pixels = pixels[::-1]
    for i in range(len(moves)):
        #Move opposite to undo transformations
        if moves[i] == "TU":
            point[1] -= pixels[i]
        elif moves[i] == "TD":
            point[1] += pixels[i]
        elif moves[i] == "TR":
            point[0] -= pixels[i]
        elif moves[i] == "TL":
            point[0] += pixels[i]
        elif moves[i] == "RC":
            pointTemp = point
            point[0] = pointTemp[0]*np.cos(-4*pixels[i]/(xshape + yshape)) - pointTemp[1]*np.sin(-4*pixels[i]/(xshape + yshape))
            point[1] = pointTemp[1]*np.cos(-4*pixels[i]/(xshape + yshape)) + pointTemp[0]*np.sin(-4*pixels[i]/(xshape + yshape))
        elif moves[i] == "RCC":
            pointTemp = point
            point[0] = pointTemp[0]*np.cos(4*pixels[i]/(xshape + yshape)) - pointTemp[1]*np.sin(4*pixels[i]/(xshape + yshape))
            point[1] = pointTemp[1]*np.cos(4*pixels[i]/(xshape + yshape)) + pointTemp[0]*np.sin(4*pixels[i]/(xshape + yshape))
    return point[0], point[1]

def getPointsSVG(svgFilename):
    cx = 0
    cy = 0
    r = 0
    l1x1 = 0
    l1y1 = 0
    l1x2 = 0
    l1y2 = 0
    l2x1 = 0
    l2y1 = 0
    l2x2 = 0
    l2y2 = 0
    foundLine = False
    with open(svgFilename,'r') as f:
        lines = f.read().split("\n")
    for i in range(len(lines)):
        if '<circle' in lines[i]:
            for j in range(6):
                if 'cx=' in lines[i+j]:
                    cx = eval(lines[i+j].split("\"")[1])
                elif 'cy=' in lines[i+j]:
                    cy = eval(lines[i+j].split("\"")[1])
                elif 'r=' in lines[i+j]:
                    r = eval(lines[i+j].split("\"")[1])
        elif '<line' in lines[i]:
            for j in range(7):
                if 'x1=' in lines[i+j]:
                    if not foundLine:
                        l1x1 = eval(lines[i+j].split("\"")[1])
                    else:
                        l2x1 = eval(lines[i+j].split("\"")[1])
                elif 'y1=' in lines[i+j]:
                    if not foundLine:
                        l1y1 = eval(lines[i+j].split("\"")[1])
                    else:
                        l2y1 = eval(lines[i+j].split("\"")[1])
                elif 'x2=' in lines[i+j]:
                    if not foundLine:
                        l1x2 = eval(lines[i+j].split("\"")[1])
                    else:
                        l2x2 = eval(lines[i+j].split("\"")[1])
                elif 'y2=' in lines[i+j]:
                    if not foundLine:  
                        l1y2 = eval(lines[i+j].split("\"")[1])
                    else:
                        l2y2 = eval(lines[i+j].split("\"")[1])
            foundLine = True
    return cx, cy, r, l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2

def transformSVG(svgFilename, cameraName, recMoves, recPixels):
    cx, cy, r, l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2 = getPointsSVG(svgFilename)
    cx = cx - xshape/2
    cy = -cy + yshape/2
    l1x1 = l1x1 - xshape/2
    l1y1 = -l1y1 + yshape/2
    l1x2 = l1x2 - xshape/2
    l1y2 = -l1y2 + yshape/2
    l2x1 = l2x1 - xshape/2
    l2y1 = -l2y1 + yshape/2
    l2x2 = l2x2 - xshape/2
    l2y2 = -l2y2 + yshape/2
    cx, cy = transformPoint([cx,cy], recMoves, recPixels)
    l1x1, l1y1 = transformPoint([l1x1,l1y1], recMoves, recPixels)
    l1x2, l1y2 = transformPoint([l1x2,l1y2], recMoves, recPixels)
    l2x1, l2y1 = transformPoint([l2x1,l2y1], recMoves, recPixels)
    l2x2, l2y2 = transformPoint([l2x2,l2y2], recMoves, recPixels)
    cx = cx + xshape/2
    cy = -cy + yshape/2
    l1x1 = l1x1 + xshape/2
    l1y1 = -l1y1 + yshape/2
    l1x2 = l1x2 + xshape/2
    l1y2 = -l1y2 + yshape/2
    l2x1 = l2x1 + xshape/2
    l2y1 = -l2y1 + yshape/2
    l2x2 = l2x2 + xshape/2
    l2y2 = -l2y2 + yshape/2
    
    with open(svgFilename, 'r') as f:
        lines = f.read().split("\n")
    
    with open(tempPath + "/" + cameraName + "_temp.svg", 'w+') as f:
        foundl1x1 = False
        foundl1y1 = False
        foundl1x2 = False
        foundl1y2 = False
        for line in lines:
            if '     cx=' in line:
                f.write("     cx=\""+str("%0.2f" % cx)+"\"\n")
            elif '     cy=' in line:
                f.write("     cy=\""+str("%0.2f" % cy)+"\"\n")
            elif '     x1=' in line:
                if not foundl1x1:
                    f.write("     x1=\""+str("%0.2f" % l1x1)+"\"\n")
                    foundl1x1 = True
                else:
                    f.write("     x1=\""+str("%0.2f" % l2x1)+"\"\n")
            elif '     y1=' in line:
                if not foundl1y1:
                    f.write("     y1=\""+str("%0.2f" % l1y1)+"\"\n")
                    foundl1y1 = True
                else:
                    f.write("     y1=\""+str("%0.2f" % l2y1)+"\"\n")
            elif '     x2=' in line:
                if not foundl1x2:
                    f.write("     x2=\""+str("%0.2f" % l1x2)+"\"\n")
                    foundl1x2 = True
                else:
                    f.write("     x2=\""+str("%0.2f" % l2x2)+"\"\n")
            elif '     y2=' in line:
                if not foundl1y2:
                    f.write("     y2=\""+str("%0.2f" % l1y2)+"\"\n")
                    foundl1y2 = True
                else:
                    f.write("     y2=\""+str("%0.2f" % l2y2)+"\"\n")
            
            else:
                f.write(line+"\n")
    return tempPath + "/" + cameraName +"_temp.svg"

def progressBar(pct):
    numberOfHashtags = int(pct/2) + 1
    numberOfdots = 50-numberOfHashtags
    return "[" + "#"*numberOfHashtags + "."*numberOfdots + "]"

def writeToLog(message):
    try:
        if message == 'break':
            with open("log.txt",'a') as f:
                f.write("----------------------------------------------------------------\n")
        else:
            with open("log.txt",'a') as f:
                f.write(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + ' - ' + message + "\n")
    except:
        print("Could not open log file!")

