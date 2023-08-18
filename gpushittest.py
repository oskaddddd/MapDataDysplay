import pyopencl as cl
import numpy as np
import matplotlib as plt
from scipy.spatial import Delaunay
import math


class createPixel():
    def __init__(self) -> None:
        self.ctx = cl.create_some_context(interactive=False)
        self.queue = cl.CommandQueue(self.ctx)

        self.mf = cl.mem_flags

        self.pixelBuffer = None
        self.pixels = None
        self.triangles = None
        self.res = None
        self.image = None
        self.destBuffer = None
        self.triBuffer = None
    def createPixelBuffer(self, resolution = None, Points = None, Image =None) -> list: #width, height
        Dots = []
        if resolution != None and Points == None:
            x_coords = np.arange(resolution[0])
            y_coords = np.arange(resolution[1])
            xx, yy = np.meshgrid(x_coords, y_coords)
            Dots = np.dstack((xx, yy, np.zeros_like(xx)))
            self.res = np.ones((resolution[1], resolution[0], 4), dtype=Dots.dtype)
        
        print(self.res.shape, Dots.shape)  
        self.pixels = Dots
        self.pixelBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = Dots.nbytes)
        cl.enqueue_copy(self.queue, self.pixelBuffer, self.pixels)
        
        self.destBuffer = cl.Buffer(self.ctx, flags = self.mf.WRITE_ONLY, size = self.res.nbytes)
        
        imageArr = np.array(Image, dtype=Dots.dtype)
        self.imageBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = imageArr.nbytes)
        cl.enqueue_copy(self.queue, self.imageBuffer, imageArr)
        
        print(Dots.nbytes, self.pixels.nbytes, Dots.nbytes*2, 'lajkshflkahsjl;kkksskkssklalala')
        self.image = Image
        return Dots
    
    def createTriangles(self, points, showTriangles = False):
        ogPoints = points.copy()
        m = max([x[2] for x in points])
        m = 255/m
        points = np.array(points)
        points = np.array([[x[0], x[1]] for x in points])
        p = points.tolist()
        tri = Delaunay(points)
        triangles =points[tri.simplices]
        output = triangles.tolist()    
        if showTriangles:
            plt.triplot(points[:,0], points[:,1], tri.simplices)
            plt.plot(points[:,0], points[:,1], 'o')
            plt.show()
        for i1, x in enumerate(output):
            for i2, point in enumerate(x):
                output[i1][i2].append(ogPoints[p.index(point)][2])
        output = np.array(output)
        self.triangles = output
        self.triBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = output.nbytes)
        cl.enqueue_copy(self.queue, self.triBuffer, self.triangles)
        
        self.size = np.array([self.image.size[0], self.image.size[1], 3, int(self.triangles.size/9), math.floor(m)])
        self.sizeBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = self.size.nbytes)
        cl.enqueue_copy(self.queue, self.sizeBuffer, self.size)
        return output
    
    def compute(self):
        programSource = """
    kernel void Bilinear(global int *triangles, global int *out, global int *size, global int *Image) {
        
        int g1 = get_global_id(1);
        int g0 = get_global_id(0);

        int index = g1 * size[0] * size[2] + g0 * size[2];
        int indexOut = g1*size[0]*4+g0*4;
        int i = 0;
        for (i = 0; i < size[3]; i++){
            int tri[9];
            int i1 = 0;
            for (i1 = 0; i1 < 9; i1++){
                tri[i1] = triangles[i1+i*9];
            }

            float a = fabs((float)tri[0]*(tri[4]-tri[7]) + tri[3]*(tri[7]-tri[1]) + tri[6]* (tri[1]-tri[4]));
            float a1 = fabs((float)g0*(tri[4]-tri[7]) + tri[3]*(tri[7]-g1) + tri[6]* (g1-tri[4]));
            float a2 = fabs((float)tri[0]*(g1-tri[7]) + g0*(tri[7]-tri[1]) + tri[6]* (tri[1]-g1));
            float a3 = fabs((float)tri[0]*(tri[4]-g1) + tri[3]*(g1-tri[1]) + g0* (tri[1]-tri[4]));
            
            if(fabs((a1 + a2 + a3) -a) < 0.0001){
                int A = tri[2];
                int B = tri[5];
                int C = tri[8];
                
                out[indexOut] = round((A*a1+B*a2+C*a3)/(a1+a2+a3)*size[4]);
                out[indexOut+1] = round((A*a1+B*a2+C*a3)/(a1+a2+a3)*size[4]);
                out[indexOut+2] = round((A*a1+B*a2+C*a3)/(a1+a2+a3)*size[4]);
                out[indexOut+3] = 255;
                break;
            }
        }
        if(out[indexOut+3] != 255){
            out[indexOut] = Image[indexOut];
            out[indexOut+1] = Image[indexOut+1];
            out[indexOut+2] = Image[indexOut+2];
            out[indexOut+3] = Image[indexOut+3];
        }
    }
"""
        prg = cl.Program(self.ctx, programSource).build()
        
        prg.Bilinear(self.queue, (self.size[0], self.size[1]), None, self.triBuffer, self.destBuffer, self.sizeBuffer, self.imageBuffer)
        cl.enqueue_copy(self.queue, self.res, self.destBuffer)
        return self.res