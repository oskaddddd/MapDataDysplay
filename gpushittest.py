import pyopencl as cl
import numpy as np
import time
import matplotlib as plt
from scipy.spatial import Delaunay
import PIL.Image


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
        #self.b_buf = cl.Buffer(ctx, flags = mf.READ_ONLY, size = b.nbytes)
        self.destBuffer = None
        self.triBuffer = None
    def createPixelBuffer(self, resolution = None, Points = None, Image =None) -> list: #width, height
        Dots = []
        if resolution != None and Points == None:
            x_coords = np.arange(resolution[0])
            y_coords = np.arange(resolution[1])
            xx, yy = np.meshgrid(x_coords, y_coords)
            Dots = np.dstack((xx, yy, np.zeros_like(xx)))

        else:
            Dots = np.array(Points)
        
        self.pixels = Dots
        self.pixelBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = Dots.nbytes)
        cl.enqueue_copy(self.queue, self.pixelBuffer, self.pixels)
        self.res = np.empty_like(self.pixels)
        self.destBuffer = cl.Buffer(self.ctx, flags = self.mf.WRITE_ONLY, size = Dots.nbytes)
        #cl.enqueue_copy(self.queue, self.destBuffer, self.res)

        print(Dots.nbytes, self.pixels.nbytes, Dots.nbytes*2, 'lajkshflkahsjl;kkksskkssklalala')
        self.image = Image
        return Dots
    
    def createTriangles(self, points, showTriangles = False):
        ogPoints = points.tolist()
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
                #print(ogPoints[p.index(point)][2],triangles[i1][i2],point, "wahahaha")
                output[i1][i2].append(ogPoints[p.index(point)][2])
        output = np.array(output)
        self.triangles = output
        self.triBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = output.nbytes)
        return output
    
    def compute(self):
        programSource = """
    kernel void Bilinear(global float *pix, global float *tri, global float *out) {
        int g0 = get_global_id(1);
        int g1 = get_global_id(0);


        int nx = 1280;
        int ny = 961;
        int nz = 3;
        int index = g0 * nx * 3 + g1 * 3;
        out[index] = pix[index]+1;
        out[index+1] = pix[index+1];
        out[index+2] = pix[index+2];
    }
"""


        prg = cl.Program(self.ctx, programSource).build()

        # Calculate the global work size
        width, height = self.pixels.shape[:2]
        global_work_size = np.prod(self.pixels.shape)


        prg.Bilinear(self.queue, (self.image.size[0], self.image.size[1]), None, self.pixelBuffer, self.triBuffer, self.destBuffer)
        cl.enqueue_copy(self.queue, self.res, self.destBuffer)
        print(self.res.nbytes, 'ohh yee')
        self.pixels
        print(self.pixelBuffer, 'fuck this')
        print(self.pixels.shape, self.res.shape,'asd', self.pixels[960][0], 'asd',self.res[960][0], 'asd')
        return self.res





#res = np.empty_like(a)
#
#ctx = cl.create_some_context(interactive=True)
#queue = cl.CommandQueue(ctx)
#
#mf = cl.mem_flags
#
#a_buf = cl.Buffer(ctx, flags = mf.READ_ONLY, size = a.nbytes)
#b_buf = cl.Buffer(ctx, flags = mf.READ_ONLY, size = b.nbytes)
#dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, res.nbytes)
#t = time.time()
#
#programSource = """
#kernel void Bilinear(global float *a,global float *b, global float *c){
#    int gid = get_global_id(0);
#    c[gid] = a[gid]*b[gid]*b[gid]*a[gid];
#}"""
##prg = cl.Program(ctx, """
##    __kernel void CreatePixel(__global const float *a, __global float *c)
##    {
##      int gid = get_global_id(0);
##      c[gid] = a[gid]+1;
##    }
##    """).build()
#
#
#cl.enqueue_copy(queue, res, dest_buf)
#
#prg = cl.Program(ctx, programSource).build()
#
#prg.Bilinear(queue, a.shape, (32,), a_buf,b_buf,  dest_buf)
#
#print(time.time()-t)
#print(a[:10], b[:10], 'wawa', res[:10])
#