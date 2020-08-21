from sklearn.neighbors import KernelDensity
from util import *
img = Image.open("Reference_Images/ETMX3/ETMX3_Original.tiff")
img = cleanPixels(img)
img_arr = np.array(img)
x_pts = []
y_pts = []
for i in range(len(img_arr)):
    for j in range(len(img_arr[i])):
        if img_arr[i, j] > 0:
            x_pts += [i]
            y_pts += [j]
bw = iniStd*(0.5*xshape + 0.5*yshape)
#Sample Points
x_min = 0
x_max = len(img_arr)-1
x_bin_size = len(img_arr)*1j
y_min = 0
y_max = len(img_arr[0])-1
y_bin_size = len(img_arr[0])*1j
    
# create grid of sample locations
xx, yy = np.mgrid[x_min:x_max:x_bin_size, y_min:y_max:y_bin_size]
 
xy_sample = np.vstack([yy.ravel(), xx.ravel()]).T
xy_train  = np.vstack([y_pts, x_pts]).T

kde_skl = KernelDensity(bandwidth = bw)
kde_skl.fit(xy_train)

z_pts = kde_skl.score_samples(xy_sample)
z_pts = np.exp(z_pts)
z_arr = []
count = 0
zz = np.reshape(z_pts, xx.shape)
zz = zz/np.max(zz.flatten())*iniNormalization
img_z = Image.fromarray(zz)
img_z = imgOverlay(img_z, img)
img_Def = Image.open("Reference_Images/ETMX3/ETMX3_Overlayed.tiff")
img_Def.show()
img_z.show()
