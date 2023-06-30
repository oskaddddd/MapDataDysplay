from PIL import Image
import json
name = 'mask1.png'
image = Image.open(name)
s = image.size

scale = input('Enter a numebr for how much to upscale. For example if you want to upscale it by 2X, enter - 2: ')

try:
    scale =float(scale)
except:
    print(f"Didn't recogniza {scale} as a number")
    exit()

print(s[0]*scale, s[0]*scale, s)
image = image.resize((int(s[0]*scale), int(s[1]*scale)))
print('res', image.size)
a = input(f'Upscaled image from {s} to {image.size}, would you like to keep the changes? y/n:').lower()

if a == 'y':
    image.save(name)
    print('Saved changed')
else:
    print('Discarded changed')
    exit()

a = input(f'Would you like to update your calibration data to reflect the upscaled image? y/n:').lower()


if a == 'y':
    defjson = [{"GPS": [0, 0], "Pixel" :[0, 0]} for _ in range(2)]
    data = []
    try: 
        with open('CoordinateCalibration.json',) as f:
            data=json.load(f)
            print(data)
        for i in range(2):
            for i1 in range(2):
                data[i]['Pixel'][i1] = round(data[i]['Pixel'][i1]*scale)
        print(data)
    except Exception as e:
        print(e)
        with open('CoordinateCalibration.json', 'w') as f:
            json.dump(defjson, f, indent=1)
    with open('CoordinateCalibration.json', 'w') as f:
        json.dump(data, f, indent=1)
    
    print('Saved changed')
else:
    print('Discarded changed')
    exit()

