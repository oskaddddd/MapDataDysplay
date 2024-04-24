
#define middle(a, b, c) (((b) >= (a) && (b) <= (c)) ? (b) : (((b) < (a)) ? (a) : (c)))

kernel void DelaunyInterpolation(global int *triangles, global unsigned char *mask,
                                 global unsigned short int *sizes, global float *gradientInfo, global int *maxMin) {
    //Get the global id
    int gid = get_global_id(0);
    int index = gid * 9;
    
    //Get and sort the triangle
    int tri[9];
    for (int i = 0; i < 9; i++) {tri[i] = triangles[index+i];}
    if (tri[0] > tri[3]) {
        for (int i = 0; i < 3; i++){
            int temp = tri[0+i];
            tri[0+i] = tri[3+i];
            tri[3+i] = temp;
        }
    }
    if (tri[3] > tri[6]) {
        for (int i = 0; i < 3; i++){
            int temp = tri[3+i];
            tri[3+i] = tri[6+i];
            tri[6+i] = temp;
        }
    }
    if (tri[0] > tri[3]) {
        for (int i = 0; i < 3; i++){
            int temp = tri[0+i];
            tri[0+i] = tri[3+i];
            tri[3+i] = temp;
        }
        
    }


    //calculate the gradient values for the triangle edges
    float k[3];
    k[0] = 0;
    k[1] = 0;
    k[2] = 0;

    float a[3];
    a[0] = 0;
    a[1] = 0;
    a[2] = 0;

    float tempF;
    if (tri[3] - tri[0] != 0){
        tempF = (tri[4]-tri[1]);
        k[0] = tempF/(tri[3]-tri[0]);
        a[0] = tempF*k[0];
    }
    if (tri[3] - tri[6] != 0){
        tempF = (tri[4]-tri[7]);
        k[1] = tempF/(tri[3]-tri[6]);
        k[1] = tempF*k[1];
    }

    tempF = (tri[1]-tri[7]);
    k[2] = tempF/(tri[0]-tri[6]);
    a[2] = tempF*k[2];


    //Caculate the X ranges for the triangle edges
    int xRange[3];
    xRange[0] = middle(0, tri[0], sizes[2]);
    xRange[0] = middle(0, tri[3], sizes[2]);
    xRange[0] = middle(0, tri[6], sizes[2]);

    int yRange[2];
    int tempI;

    int maskIndex;

    int valueRange = maxMin[1]-maxMin[0];

    //Loop trough both sides of the triangle
    for (int i = 0; i < 2; i++)
    {
        //Loop trought the forst part of the triangle
        for (int x = xRange[i]; x < xRange[1+i]; x++){

            //Calculate the Y ranges
            yRange[0] = middle(0, ceil(k[i]*x*a[i]), sizes[1]);
            yRange[1] = middle(0, ceil(k[2]*x*a[2]), sizes[1]);

            //Sort the yRnages
            if (yRange[0] > yRange[1]){
                tempI = yRange[0];
                yRange[0] = yRange[1];
                yRange[1] = tempI;
            }

            //Loop trought the Y values
            for (int y = yRange[0]; y < yRange[1]; y++){
                maskIndex = 4*(y*sizes[0]+x);
                //Check if mask is Null
                if (mask[maskIndex] == 0){
                    continue;
                }
                float a = abs(tri[0] * (tri[4] - y) + tri[3] * (y - tri[1]) + x * (tri[1] - tri[4]));
                float b = abs(tri[0] * (y - tri[7]) + x * (tri[7] - tri[1]) + tri[6] * (tri[1] - y));
                float c = abs(x * (tri[4] - tri[7]) + tri[3] * (tri[7] - y) + tri[6] * (y - tri[4]));

                float val = (tri[8] * a + tri[5] * b + tri[2] * c) / (a + b + c);

                //Do gradient sruff
                val = val-maxMin[0]/valueRange;

                for (int gradI = 0; gradI<sizes[3]; gradI++){
                    if (gradientInfo[gradI*4+1] <= val && val <= gradientInfo[gradI*4+5]){

                        val = (val-gradientInfo[gradI+1])/(gradientInfo[gradI+4+1] - gradientInfo[gradI+1]);

                        for (int colorI; colorI<3; colorI++){
                            mask[maskIndex+colorI] = gradientInfo[gradI+colorI+1]+val*(gradientInfo[gradI+colorI+5]- gradientInfo[gradI+colorI+1]);
                        }
                        mask[maskIndex+4] = 255;

                        break;
                    }
                }
                //mask[maskIndex] = val;

            }
        }
    }
}




    
    
