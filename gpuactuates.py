import pyopencl as cl
import numpy as np
import time


inputArr = np.arange(1, 1000)
print(inputArr)

ctx = cl.create_some_context(interactive=False)
queue = cl.CommandQueue(ctx)
mf = cl.mem_flags

inBuffer = cl.Buffer(ctx, flags = mf.READ_ONLY, size = inputArr.nbytes)
destBuffer = cl.Buffer(ctx, flags = mf.WRITE_ONLY, size = inputArr.nbytes)

cl.enqueue_copy(queue, inBuffer,inputArr)
cl.enqueue_copy(queue, destBuffer, np.empty_like(inputArr), )

source = """
kernel void Test(global int *in, global float *out){
    int gid = get_global_id(0);
    float o = round(in[gid]+0.5);
    out[gid] = round(in[gid]+0.5);
    }"""

program = cl.Program(ctx, source).build()

program.Test(queue, (1000,), None, inBuffer, destBuffer)

output = np.empty_like(inputArr)
cl.enqueue_copy(queue, output, destBuffer)

print(output)






