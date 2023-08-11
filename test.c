kernel void Bilinear(global float *pix,global float *tri, global float *out){
    int gid = get_global_id(0);
    out[gid] = gid;
}