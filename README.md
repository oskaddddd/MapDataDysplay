# Mapplot

Mapplot makes it easy to represent your data on a map. 
![map](https://github.com/oskaddddd/Mapplot/assets/105368582/d3d9f0df-0452-479b-9621-d726b2a179ca)


# How to use 

Currently, the project is still abit of a mess. To run it you download the source and run **mainGUI.py**. 

You need to have these libraries installed:

    pip install pyqt6 pyqtdarktheme pillow numpy pyopencl scipy 
   
  Now in the GUI (Setup / Make mask) press **Select mask image** and select an image of the map for the region you want to create the map of. Then move the slider until the main region of your map is colored white. After that's done, simply press **Save mask**. 

The next step is to calibrate the mask, so the program knows how to map real world coordinates onto it. You can do that in the (Setup / Calibration) section of the GUI. You will need to select 2 points on the newly created mask of the map, and find the real world coordinates for that location. Do this by clicking on the map to select a point, then enter the coordinates for said point. You can switch between points by pressing the **Point 1** or **Point 2** button. Next press  **Calibrate**, select the file containing your data and you're done. 

All you have to do now is go to the (Create map) section and press **Create**

# About
This project is like a year school project. I've been working on this for almost as year at the time of writing this and learned alot while doing so. I might still update it and add new features, altho it'll never be as powerfull as some other open-source tools. It solely focuses on creating one type of data map - Gradient maps, the kind that temprature is ussually dysplayed with. Currently it only works with delauny interpolation, which, in a nut shell, causes the there to be visible triangles between data points, but technically the representation of the data is more accurate since it has less distortion. I've started work on an IDW interpolation which should eliminate this problem, but i don't know how long it'll take for me to finish it.
