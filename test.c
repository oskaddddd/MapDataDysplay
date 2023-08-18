    kernel void Bilinear(global int *pix, global int *triangles, global int *out, global int *size, global int *triSize) {
        
        int g0 = get_global_id(1);
        int g1 = get_global_id(0);

        int index = g0 * size[0] * size[2] + g1 * size[2];
        int i = 0;
        for (i = 0; i <  triSize; i++){
            int tri[9];
            int i1 = 0;
            for (i1 = 0; i1 < 9; i1++){
                tri[i1] = triangles[i1+i*9];
                
            }
            tri[2] = triangles[2+i*9];
            if (tri[2] == 0){
                    out[index+1] = triangles[2];
                }
            float a = fabs((float)tri[0]*(tri[4]-tri[7]) + tri[3]*(tri[7]-tri[1]) + tri[6]* (tri[1]-tri[4]));
            float a1 = fabs((float)pix[index]*(tri[4]-tri[7]) + tri[3]*(tri[7]-pix[index+1]) + tri[6]* (pix[index+1]-tri[4]));
            float a2 = fabs((float)tri[0]*(pix[index+1]-tri[7]) + pix[index]*(tri[7]-tri[1]) + tri[6]* (tri[1]-pix[index+1]));
            float a3 = fabs((float)tri[0]*(tri[4]-pix[index+1]) + tri[3]*(pix[index+1]-tri[1]) + pix[index]* (tri[1]-tri[4]));
            //if(fabs(a1 + a2 + a3 - a) < 0.001)
            if(a1+a2+a3 == a){
                int A = tri[2];
                int B = tri[5];
                int C = tri[8];
                float o = 3.4f;
                out[index+2] = A;
                if (tri[2] == 0){
                    out[index+2] = 56;
                }
                else{
                    out[index+2] = tri[2];
                }
                //out[index] = pix[index];
                //out[index+1] = pix[index+1];
                break;
                
            }

        }

    }