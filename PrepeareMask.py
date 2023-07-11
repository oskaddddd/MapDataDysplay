import PIL.Image
import numpy as np




#raise the threshold not the entire region is green and lower it if pixels outside the region are green
#If inverse = True, will select the above the threashold (lighter regions), if False will select bellow threashold (Darker regions)
inverse = False
threashhold = 255
imageName = ''
with open('ImageName.txt', 'r') as f:
    imageName = f.read()


image = PIL.Image.open(imageName).convert('RGBA')

defImageArr = np.array(image)

threashhold *=3

print("Coloring region... this might take abit")
def color():
    
    if inverse == False:
        for i1, y in enumerate(defImageArr):
            for i2, x in enumerate(y):
                if sum(x) < threashhold:
                    defImageArr[i1][i2] = np.array([0, 0, 0, 255])
                else:
                    defImageArr[i1][i2] = np.array([0, 0, 0, 0])
    else:
        for i1, y in enumerate(defImageArr):
            for i2, x in enumerate(y):
                if sum(x) > threashhold:
                    defImageArr[i1][i2] = np.array([0, 0, 0, 255])
                else:
                    defImageArr[i1][i2] = np.array([0, 0, 0, 0])
    image2 = PIL.Image.fromarray(defImageArr)
    return image2
im = color()
im.show()
i = input('Was the entirety of your wanted region colored? (Y/N) If no Lower or raise the threashold, \
the higher the threashold the lihter colors will be incluted in the region, the lower - the darker. \
The max threashold is 255 and the minimum is 0. \
This action is not reversable, your mask image will be changed. -- ').lower()
print(i)
if i == 'y': 
    im.save(imageName[:imageName.index('.')+1]+'png' \
    if imageName[imageName.index('.')+1:] != 'png' \
    else imageName)
    print('Updated mask saved')
else: print('Discarded Channges')
