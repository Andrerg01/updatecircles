#Packaged for image manipulation
from PIL import Image, ImageDraw, ImageFont
#mathematical package
import numpy as np
#Package for timinig processes
from datetime import datetime
import time
#Package for executing terminal commands
import os
import sys
#Package for reading ini file
import configparser
#Package to get version number of program
import subprocess
#Package to manage passed arguments from the command line
import argparse
#Package for Gaussian Smoothing
from sklearn.neighbors import KernelDensity

#Opening and Reading config file
config = configparser.ConfigParser()
config.read('config.ini')
#Assigning variables
xshape = eval(config["Configurations"]["xshape"])
yshape = eval(config["Configurations"]["yshape"])
inixRange = eval(config["Configurations"]["inixRange"])
iniyRange = eval(config["Configurations"]["iniyRange"])
inithRange = eval(config["Configurations"]["inithRange"])
iniRes = eval(config["Configurations"]["iniRes"])
iniStd = eval(config["Configurations"]["iniStd"])
iniThreshold = eval(config["Configurations"]["iniThreshold"])
iniNormalization = eval(config["Configurations"]["iniNormalization"])
archivePath = config["Configurations"]["archivePath"]
defaultPath = config["Configurations"]["defaultPath"]
shotsPath = config["Configurations"]["shotsPath"]
tempPath = config["Configurations"]["tempPath"]
cameras = config["Configurations"]["cameras"].split(',')
svgsPath = config["Configurations"]["svgsPath"]
#version = str(subprocess.check_output(["git", "describe"]).strip())[2:-1]
version = '1.0.0-7'
author = config["Configurations"]["author"]

#Defining arguments
parser = argparse.ArgumentParser(description = 'Processes and Images')

parser.add_argument('-c', '--camera', type = str, choices = cameras, metavar = '', help = 'The camera to be considered.')
parser.add_argument('-i', '--images', type = str, nargs = '+', metavar = '',  help = 'The image or images to be processed.')
parser.add_argument('-V', '--vector', type = str, metavar = '', help = 'The SVG file to be processed')
parser.add_argument('-p', '--precision', type = int, default = iniRes, metavar = '', help = 'Overrides initial precision for image matching from config file')
parser.add_argument('-q', '--quiet', action = 'store_true', help = 'Option to supress outputs unless necessary.')
parser.add_argument('-y', '--yes', action = 'store_true', help = 'Automatically responds \"yes\" to any inquiry except for image matching confirmation.')

actionGroup = parser.add_mutually_exclusive_group()
actionGroup.add_argument('-u', '--update', action = 'store_true', help = 'Indicates the program that you are updating circles')
actionGroup.add_argument('-r', '--replace', action = 'store_true', help = 'Indicates the program that you are replacing the current reference image and svg files.')

args = parser.parse_args()
verbose = not args.quiet

def cleanPixels(image):
    """
    Docstring:
    Changes value of pixels in the image above or below `iniThreshold` threshold to 255 or 0.

    Parameters
    ----------
    image : `PIL.Image`
        PIL Image to be cleaned

    Returns
    -------
    image :  `PIL.Image`
        The cleaned image

    Type: method
    """
    #Turns image into 2d array of values
    imarray = np.array(image)
    #runs through every value of the arrays
    for i in range(len(imarray)):
        for j in range(len(imarray[i])):
            #Changes the value to 255 or 0 depending on the value of the pixel and the threshold specified.
            if imarray[i][j] < iniThreshold:
                imarray[i][j] = 0
            else:
                imarray[i][j] = 255
    return Image.fromarray(imarray)

def gaussianSmooth(image, start = None, header = ''):
    """
    Docstring:
    Smooths an image as if every pixel acts as the peak of a gaussian with standard deviation `iniStd`.
    Essentially a KDE process.

    Parameters
    ----------
    image : `PIL.Image`
        PIL Image to be smoothed.

    start : `int`, optional
        Start time of the operation for calculating ETA. If none given, it will assume the time when the function executes.

    header: `str`, optional
        A header to be displayed before the progress bar.

    Returns
    -------
    image :  `PIL.Image`
        The smoothed image

    Notes
    -----
    Type: method
    """

    if start == None:
        start = datetime.now()
    #Turns image into 2d array of values
    imarray = np.array(image)
    x_pts = []
    y_pts = []
    for i in range(len(imarray)):
        for j in range(len(imarray[i])):
            if imarray[i, j] > 0:
                x_pts += [i]
                y_pts += [j]
    bw = iniStd * (0.5 * xshape + 0.5 * yshape)
    #Sample Points
    x_min = 0
    x_max = len(imarray) - 1
    x_n_bins = len(imarray) * 1j
    y_min = 0
    y_max = len(imarray[0]) - 1
    y_n_bins = len(imarray[0]) * 1j

    # create grid of sample locations
    xx, yy = np.mgrid[x_min : x_max : x_n_bins, y_min : y_max : y_n_bins]

    xy_sample = np.vstack([yy.ravel(), xx.ravel()]).T
    xy_train  = np.vstack([y_pts, x_pts]).T

    kde_skl = KernelDensity(bandwidth = bw)
    kde_skl.fit(xy_train)

    z_pts = kde_skl.score_samples(xy_sample)
    z_pts = np.exp(z_pts)
    gaussianArray = np.reshape(z_pts, xx.shape)
    gaussianArray = gaussianArray / np.max(gaussianArray.flatten()) * iniNormalization
    img_z = Image.fromarray(gaussianArray)
    return img_z

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
        
def transformPoint(point, params):
    x = params[0]
    y = params[1]
    th = params[2]
    pointTemp = point
    return [pointTemp[0]*np.cos(th) - pointTemp[1]*np.sin(th) + x, pointTemp[0]*np.sin(th) + pointTemp[1]*np.cos(th) + y]

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

def transformSVG(svgFilename, cameraName, transf):
    cx, cy, r, l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2 = getPointsSVG(svgFilename)
    """
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
    """
    cx, cy = (transf@np.array([cx,cy,1]))[:2]
    l1x1, l1y1 = (transf@np.array([l1x1, l1y1,1]))[:2]
    l1x2, l1y2 = (transf@np.array([l1x2, l1y2,1]))[:2]
    l2x1, l2y1 = (transf@np.array([l2x1, l2y1,1]))[:2]
    l2x2, l2y2 = (transf@np.array([l2x2, l2y2,1]))[:2]
    """
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
    """
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
                    f.write("     x1=\""+str("%0.2f" % l1x1)+"\"")
                    foundl1x1 = True
                else:
                    f.write("     x1=\""+str("%0.2f" % l2x1)+"\"")
                if '/>' in line:
                    f.write(' />\n')
                else:
                    f.write('\n')
            elif '     y1=' in line:
                if not foundl1y1:
                    f.write("     y1=\""+str("%0.2f" % l1y1)+"\"")
                    foundl1y1 = True
                else:
                    f.write("     y1=\""+str("%0.2f" % l2y1)+"\"")
                if '/>' in line:
                    f.write(' />\n')
                else:
                    f.write('\n')
            elif '     x2=' in line:
                if not foundl1x2:
                    f.write("     x2=\""+str("%0.2f" % l1x2)+"\"")
                    foundl1x2 = True
                else:
                    f.write("     x2=\""+str("%0.2f" % l2x2)+"\"")
                if '/>' in line:
                    f.write(' />\n')
                else:
                    f.write('\n')
            elif '     y2=' in line:
                if not foundl1y2:
                    f.write("     y2=\""+str("%0.2f" % l1y2)+"\"")
                    foundl1y2 = True
                else:
                    f.write("     y2=\""+str("%0.2f" % l2y2)+"\"")
                if '/>' in line:
                    f.write(' />\n')
                else:
                    f.write('\n')
            else:
                f.write(line+"\n")
    return tempPath + "/" + cameraName +"_temp.svg"

def progressBar(pct, time0 = 0, header = ''):
    time1 = datetime.now()
    if time0 == 0:
        eta = ''
    else:
        deltaT = (time1-time0).total_seconds()
        try:
            eta = 100.*deltaT/pct - deltaT
        except:
            eta = ''
    numberOfHashtags = int(pct/2) + 1
    numberOfdots = 50-numberOfHashtags
    outString = "[" + "#"*numberOfHashtags + '.'*numberOfdots + '] '
    if eta != '':
        #outString += '(approx ' + '%0.2f' % eta + ' seconds)'
        if eta/(60*60*24) > 1:
            outString += '(approx > 1d)'
        elif eta/(60*60) > 1:
            outString += '(approx ' + time.strftime('%Hh %Mm %Ss', time.gmtime(eta)) +  ')'
        elif eta/60 > 0:
            outString += '(approx ' + time.strftime('%Mm %Ss', time.gmtime(eta)) +  ')'
        else:
            outString += '(approx ' + time.strftime('%Ss', time.gmtime(eta)) +  ')'
    return header + outString

def writeToLog(message):
    try:
        if message == 'break':
            with open("log.txt",'a') as f:
                f.write("----------------------------------------------------------------\n")
        elif message == '':
            pass
        else:
            with open("log.txt",'a') as f:
                f.write(datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ' - ' + message + "\n")
    except:
        if verbose: print("Could not open log file!")

def promptUser(validAnswers, ErrorMessage, LogErrorMessage, forcedInput = ''):
    if forcedInput == '':
        userAnswer = input()
    else:
        userAnswer = forcedInput
    while userAnswer not in validAnswers:
        if userAnswer.lower() == 'exit':
            writeToLog("Program exited by user.")
            if verbose: print('bye bye!')
            os._exit(0)
        elif userAnswer not in validAnswers:
            print(ErrorMessage + " [" + userAnswer + "]")
            writeToLog(LogErrorMessage + " [" + userAnswer + "]")
            userAnswer = input()
    return userAnswer
    
def replaceFiles(filename_Old, filename_New):
    try:
        open(filename_Old, 'r')
        oldExists = True
    except:
        oldExists = False
    if oldExists and filename_Old != filename_New:
        backupFile(filename_Old)
        writeToLog("Replacing \"" + filename_Old + "\" with \"" + filename_New)
        if verbose: print("Replacing \"" + filename_Old + "\" with \"" + filename_New)
        os.system("mv " + filename_New + " " + filename_Old)
    
def backupFile(filename):
    try:
        filename_new = archivePath + "/" + filename.split("/")[-1].split(".")[0] + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + filename.split("/")[-1].split(".")[-1]
        os.system("mv " + filename + " " + filename_new)
        writeToLog("Backed up file \"" + filename + "\" to \"" + filename_new + "\"" )
    except:
        if verbose: print("Backup of \"" + filename + "\" has failed!")
        writeToLog("Failed to back up file \"" + filename + "\" to \"" + filename_new + "\"")
        exit()
        
def rotationMatrix(angle):
    step1 = translationMatrix([xshape/2,yshape/2]).dot(np.array([[np.cos(angle), -np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]]))
    step2 = step1.dot(translationMatrix([-xshape/2,-yshape/2]))
    return step2

def translationMatrix(vec):
    return np.array([[1,0,vec[0]],[0,1,vec[1]],[0,0,1]])

def matrixToAffine(mat):
    a = mat[0][0]
    b = mat[0][1]
    c = mat[0][2]
    d = mat[1][0]
    e = mat[1][1]
    f = mat[1][2]
    return (a,b,c,d,e,f)

def minimizeDifference(img1, img2, rangex = inixRange, rangey = iniyRange, rangeth = inithRange, n = args.precision, cycles = 0, start = 0, minDiff = 1, header = ''):
    if cycles == 0:
        start = datetime.now()
    ncycles = cycles + int(np.ceil(np.log(rangex[1]-rangex[0])/(np.log(n/2))))
    if rangex[1] - rangex[0] < 1:
        x = (rangex[1] + rangex[0])/2
        y = (rangey[1] + rangey[0])/2
        th = (rangeth[1] + rangeth[0])/2
        return rotationMatrix(th).dot(translationMatrix([x,y])), (x,y,th)
    
    xs = [i for i in np.linspace(rangex[0], rangex[1], n)]
    ys = [j for j in np.linspace(rangey[0], rangey[1], n)]
    ths = [k for k in np.linspace(rangeth[0], rangeth[1], n)]
    transfs = []
    for x in xs:
        for y in ys:
            for th in ths:
                transfs += [[rotationMatrix(th).dot(translationMatrix([x,y])), (x,y,th)]]
    
    minDiff = 1
    minDiffArg = 0
    for i in range(len(transfs)):
        os.system("clear")
        postHeader = "Minimizing Image Difference.\n - Optimizing Cycles: " + str(cycles+1) + "/" + str(ncycles) + "\n - Least Difference so far: " + str(minDiff) + "\n - Pixel Range: " + str(rangex[1] - rangex[0]) + " Pixels\n - Precision Number: " + str(n) + '\n'
        pct = 100./(ncycles)*cycles + 100./(ncycles+1)*i/len(transfs)
        if verbose: print(progressBar(pct, time0 = start, header = header + postHeader))
        diff = imgDifference(img1, img2.transform(img2.size, Image.AFFINE, matrixToAffine(transfs[i][0])))
        if diff < minDiff:
            minDiff = diff
            minDiffArg = i
    
    args = transfs[minDiffArg][1]
    spanx = rangex[1]-rangex[0]
    spany = rangey[1]-rangey[0]
    spanth = rangeth[1]-rangeth[0]
    rangex = [args[0] - spanx/n, args[0] + spanx/n]
    rangey = [args[1] - spany/n, args[1] + spany/n]
    rangeth = [args[2] - spanth/n, args[2] + spanth/n]
    return minimizeDifference(img1, img2, rangex = rangex, rangey = rangey, rangeth = rangeth, n = n, cycles = cycles + 1, start = start, header = header)

def promptMenu():
    print('What would you like to do?')
    print('1 - Update Circle (Update SVG file) for a camera.')
    print('2 - Change Reference Image/SVG file for a camera.')
    return promptUser(['1','2'], 'Choice not recognized, please chose a valid option.', 'User inputed unknown menu choice.')

def promptCamera():
    print("Please speficy the camera name from (" + str(cameras)[1:-1] + ")")
    return promptUser(cameras, "Please specify a valid camera name from (" + str(cameras)[1:-1] + ") instead of ", "Unknown Camera Specified")

def promptImages():
    print("Please specify the images to be processed.")
    ans = confirmImages(inferPath(input().split(" ")))
    if ans == [inferPath('exit')]:
        exit()
    return ans

def confirmImages(images):
    if False in fileTest(images):
        for i in range(len(images)):
            while not fileTest(images[i], image = True):
                print("Image file \"" + images[i] + "\" could not be opened, please speficy a correct image file.")
                images[i] = inferPath(input())
                if images[i] == inferPath('exit'):
                    exit()
    return images

def promptVector():
    print("Please specity the svg file to be processed.")
    ans = confirmVector(input())
    return ans
   
def confirmVector(vecFile, bypass = None):
    if bypass != None and vecFile == bypass:
        return vecFile
    while not fileTest(vecFile):
        print("SVG file \"" + vecFile + "\" could not be opened, please specify a correct svg file.")
        vecFile = input()
        if vecFile == 'exit':
            exit()
    return vecFile
    
def inferPath(file):
    if isinstance(file, list):
        return [inferPath(f) for f in file]
    if "/" not in file:
        file = shotsPath + '/' + file
        writeToLog("Inferred File Path " + file)
    return file
        
def fileTest(file, image = False):
    if isinstance(file, list):
        return [fileTest(f, image = image) for f in file]
    if file == 'exit':
        exit()
    try:
        if image:
            Image.open(file)
        else:
            open(file, 'r')
    except:
        writeToLog("Could not find file " + file)
        return False
    return True

def clear():
    os.system("clear")
    
def exit():
    writeToLog("Program exited by user.")
    if verbose: print('bye bye!')
    os._exit(0)
    
def overlayImages(images):
    imgOut = images[0]
    for i in range(1,len(images)):
        imgOut = imgOverlay(imgOut, images[i])
    return imgOut

def getReferenceImages(camera):
    reference_Image_Original_name = defaultPath + "/" + camera + "/" + camera + "_Original.tiff"
    try:
        reference_Image_Original = Image.open(reference_Image_Original_name)
        writeToLog("Original Reference Image Successfully Imported + \"" + reference_Image_Original_name + "\"")
        if verbose: print("Original Reference Image Successfully Imported!")
    except:
        writeToLog("Failed to import Original Reference Image + \"" + reference_Image_Original_name + "\"")
        print("Error! Failed to import Original Reference Image!")
        exit()
        
    reference_Image_Overlayed_name = defaultPath + "/" + camera + "/" + camera + "_Overlayed.tiff"
    try:
        reference_Image_Overlayed = Image.open(reference_Image_Overlayed_name)
        writeToLog("Overlayed Reference Image Successfully Imported + \"" + reference_Image_Overlayed_name + "\"")
        if verbose: print("Overlayed Reference Image Successfully Imported!")
    except:
        writeToLog("Failed to import Overlayed Reference Image + \"" + reference_Image_Overlayed_name + "\"")
        print("Error! Failed to import Overlayed Reference Image!")
        exit()
    return reference_Image_Original, reference_Image_Overlayed

def drawImageAndSVG(image, svg, camera, text = ''):
    font = ImageFont.truetype("fonts/arial.ttf", 20)
    cx, cy, r, l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2 = getPointsSVG(svg)
    imgDraw1 = ImageDraw.Draw(image)
    imgDraw1.line((l1x1,l1y1,l1x2,l1y2), fill = 128)
    imgDraw1.line((l2x1,l2y1,l2x2,l2y2), fill = 128)
    imgDraw1.ellipse([cx-r,cy-r,cx+r,cy+r], outline = 128, width = 1)
    imgDraw1.text((xshape/2,yshape*.1), text + camera, font = font, fill = 128)
    return image

def promptSVGApproval():
    print("Is the svg matching satisfactory? (y/n)")
    answer = promptUser(['y','yes','Y','YES','Yes','n','no','N','NO','No'], 'Answer not recognized, please try again', 'Uncertain Approval or Disproval for Answer 1 From The User')
    if answer.lower().startswith('y'):
        return True
    else:
        return False

def promptSVGUpdateApproval():
    print("Do you wish to replace the current svg file (y/n)? (A backup will be made.)")
    answer = promptUser(['y','yes','Y','YES','Yes','n','no','N','NO','No'], 'Answer not recognized, please try again', 'Uncertain Approval or Disproval for Answer 2 From The User')
    if answer.lower().startswith('y'):
        return True
    else:
        return False
    
def promtPrecisionChangeApproval():
    if verbose: print("Would you like to change the precision of matching and try again?")
    answer = promptUser(['y','yes','Y','YES','Yes','n','no','N','NO','No'], 'Answer not recognized, please try again', 'Uncertain Approval or Disproval for Precision Change Inquiry From The User')
    if answer.lower().startswith('y'):
        return True
    else:
        return False

def promptPrecision():
    if verbose: print("What would you like to change the precision to? (current: " + str(args.precision) + ")")
    ans = eval(input())
    while not isinstance(ans, int) or ans < 3:
        print("Please provide an integer answer greater than or equal to 3.")
        ans = eval(input())
    return ans