from util import *
from PIL import ImageFilter

img1 = Image.open("Reference_Images/ETMX3/ETMX3_Overlayed.tiff")
svg = "Reference_Images/ETMX3/ETMX3.svg"
drawImageAndSVG(img1, svg, 'ETMX3')
img1.show()