
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


    float k01 = 0;
    float k12 = 0;
    float k02 = 0;

    bool b01 = true;
    bool b12 = true;

    float a01 = 0;
    float a12 = 0;
    float a02 = 0;

    float tempF;
    if (tri[3] - tri[0] != 0){
        tempF = (tri[4]-tri[1]);
        k01 = tempF/(tri[3]-tri[0]);
        a01 = tempF*k01;
    }
    else{
        b01 = false;
    }
    if (tri[3] - tri[6] != 0){
        tempF = (tri[4]-tri[7]);
        k12 = tempF/(tri[3]-tri[6]);
        a12 = tempF*k12;
    }
    else{
        b12 = false;
    }

    tempF = (tri[1]-tri[7]);
    k02 = tempF/(tri[0]-tri[6]);
    a02 = tempF*k02;

    int xRange[3];
    xRange[0] = middle(0, tri[0], sizes[2]);
    xRange[0] = middle(0, tri[3], sizes[2]);
    xRange[0] = middle(0, tri[6], sizes[2]);

    int yRange[2];
    int tempI;

    int maskIndex;
    //Loop trought the forst part of the triangle
    for (int x = xRange[0]; x < xRange[1]; x++){
        
        //Calculate the Y ranges
        yRange[0] = middle(0, ceil(k01*x*a01), sizes[1]);
        yRange[1] = middle(0, ceil(k02*x*a02), sizes[1]);
        if (yRange[0] > yRange[1]){
            tempI = yRange[0];
            yRange[0] = yRange[1];
            yRange[1] = tempI;
        }

        //Loop trought the Y values
        for (int y =yRange[0]; y < yRange[1]; y++){
            maskIndex = 4*(y*sizes[0]+x);
            //Check if mask is Null
            if (mask[maskIndex] == 0){
                continue;
            }
            unsigned float a = fabs(tri[0] * (tri[4] - y) + tri[3] * (y - tri[1]) + x * (tri[1] - tri[4]));
            unsigned float b = fabs(tri[0] * (y - tri[7]) + x * (tri[7] - tri[1]) + tri[6] * (tri[1] - y));
            unsigned float c = fabs(x * (tri[4] - tri[7]) + tri[3] * (tri[7] - y) + tri[6] * (y - tri[4]));

            unsigned float val = (tri[8] * a + tri[5] * b + tri[2] * c) / (a + b + c);

            mask[maskIndex] = val;

        }
    }
    for (int x = xRange[1]; x < xRange[2]; x++){
        
        //Calculate the Y ranges
        yRange[0] = middle(0, ceil(k12*x*a12), sizes[1]);
        yRange[1] = middle(0, ceil(k02*x*a02), sizes[1]);
        if (yRange[0] > yRange[1]){
            tempI = yRange[0];
            yRange[0] = yRange[1];
            yRange[1] = tempI;
        }

        //Loop trought the Y values
        for (int y =yRange[0]; y < yRange[1]; y++){
            maskIndex = 4*(y*sizes[0]+x);
            //Check if mask is Null
            if (mask[maskIndex] == 0){
                continue;
            }
            unsigned float a = fabs(tri[0] * (tri[4] - y) + tri[3] * (y - tri[1]) + x * (tri[1] - tri[4]));
            unsigned float b = fabs(tri[0] * (y - tri[7]) + x * (tri[7] - tri[1]) + tri[6] * (tri[1] - y));
            unsigned float c = fabs(x * (tri[4] - tri[7]) + tri[3] * (tri[7] - y) + tri[6] * (y - tri[4]));

            unsigned float val = (tri[8] * a + tri[5] * b + tri[2] * c) / (a + b + c);

            mask[maskIndex] = val;

        }
    }




    
    
