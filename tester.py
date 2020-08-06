from util import *
from PIL import ImageFilter

img1 = Image.open("Reference_Images/ETMX3/ETMX3_Overlayed.tiff")
img2 = Image.open("Test_Images/L1_CAM_ETMX_Test_0.tiff")
img2 = cleanPixels(img2)
#im2 = im.filter(ImageFilter.MinFilter(3))
#img2 = cleanPixels(img2)
#img2_g = gaussianSmooth(img2)
#img2 = imgOverlay(img2, img2_g)
img1.show()
img2.show()

transf, params = minimizeDifference(img1, img2)

img2.transform(img2.size, Image.AFFINE, matrixToAffine(transf)).show()