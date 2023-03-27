import numpy as np
from PIL import Image

def well_pos_to_led_pos_96(well_pos, TL):
    led_pos_x = []
    led_pos_y = []
    leds_pos = []

    led_pos_y = [well_pos[1] * 3 + TL[well_pos[0]][0], well_pos[1] * 3 + TL[well_pos[0]][0] + 1]
    led_pos_x = [well_pos[2] * 3 + TL[well_pos[0]][1], well_pos[2] * 3 + TL[well_pos[0]][1] + 1]

    for x in range(2):
        led = None
        for y in range(2):
            led = (led_pos_x[x], led_pos_y[y])
            leds_pos.append(led)

    return leds_pos

def well_pos_to_led_pos_24(well_pos, TL):
    led_pos_x = []
    led_pos_y = []
    leds_pos = []

    for i in range(5):
        led_pos_temp = well_pos[1]*6+TL[well_pos[0]][0]+i
        led_pos_y.append(led_pos_temp)
    for i in range(5):
        led_pos_temp = well_pos[2]*6+TL[well_pos[0]][1]+i
        led_pos_x.append(led_pos_temp)

    for x in range(5):
        led = None
        if x == 0 or x == 4:
            for y in range(3):
                led = (led_pos_x[x], led_pos_y[y+1])
                leds_pos.append(led)
        else:
            for y in range(5):
                led = (led_pos_x[x], led_pos_y[y]) 
                leds_pos.append(led)

    return leds_pos

def well_pos_to_led_pos_6(well_pos, TL):
    led_pos_x = []
    led_pos_y = []
    leds_pos = []

    for i in range(11):
        led_pos_temp = well_pos[1]*12+TL[well_pos[0]][0]+i
        led_pos_y.append(led_pos_temp)
    for i in range(11):
        led_pos_temp = well_pos[2]*12+TL[well_pos[0]][1]+i
        led_pos_x.append(led_pos_temp)

    for x in range(11):
        led = None
        if x == 0 or x == 10:
            for y in range(5):
                led = (led_pos_x[x], led_pos_y[y+3])
                leds_pos.append(led)
        elif x == 1 or x == 9:
            for y in range(7):
                led = (led_pos_x[x], led_pos_y[y+2])
                leds_pos.append(led)
        elif x == 2 or x == 8:
            for y in range(9):
                led = (led_pos_x[x], led_pos_y[y+1])
                leds_pos.append(led)
        else:
            for y in range(11):
                led = (led_pos_x[x], led_pos_y[y]) 
                leds_pos.append(led)

    return leds_pos

def customShapeLEDpos(customShape):
    leds_pos = []

    for y in range(customShape.shape[1]):
        for x in range(customShape.shape[0]):
            if customShape[y][x] != 0:
                leds_pos.append((x, y))

    return leds_pos


def getAnimationColors(waveType, color, stepLength, framerate, wvMax, wvMin = None, wvStart = None, wvLen = None, dutyCyclePWM = None, periodPWM = None):
    # Const
    intensitys = []
    rgbValues = []
    time = np.arange(0, stepLength, framerate)  

    if waveType == 'const':
        for i in range(int(stepLength/framerate)):
            intensitys.append(wvMax)
    # Sine
    elif waveType == 'sin':
        a = (wvMax - wvMin) / 2
        b = 2 * np.pi / wvLen
        d = a + wvMin
        if wvStart == 'Low':
            c = - (wvLen/4)
        elif wvStart == 'High':
            c = (wvLen/4)
 
        intensitys = a * np.sin(b * (time + c)) + d
    # Tri
    elif waveType == 'tri':
        a = (wvMax - wvMin) / 2
        d = a + wvMin
        if wvStart == 'Low':
            c = - (wvLen/4)
        elif wvStart == 'High':
            c = (wvLen/4)
 
        intensitys = (4 * a/wvLen * abs(((time + c - wvLen/4) % wvLen) - wvLen/2) - a) + d   
    # Square / PWM
    elif waveType in {'sq', 'pwm'}:
        TimePeriod = periodPWM
        percent = dutyCyclePWM

        if waveType == 'sq':
            TimePeriod = wvLen
            percent = 0.5

        if wvStart == 'Low':
            pwm = time % TimePeriod < TimePeriod * percent
            for dp in pwm:
                if dp:
                    intensitys.append(0)
                else:
                    intensitys.append(wvMax)
        elif wvStart == 'High':
            pwm = time % TimePeriod < TimePeriod * percent
            for dp in pwm:
                if dp:
                    intensitys.append(wvMax)
                else:
                    intensitys.append(0)
    # Rise
    elif waveType == 'rise':
        diff = wvMax - wvMin
        dp = wvMin

        for i in range(len(time)):
            intensitys.append(dp)
            dp += diff/(len(time)-1)
    # Fall
    elif waveType == 'fall':
        diff = wvMax - wvMin
        dp = wvMax

        for i in range(len(time)):
            intensitys.append(dp)
            dp -= diff/(len(time)-1)

    for i in range(len(intensitys)):
        rgb = ()
        if color == 'Red':
            rgb = (round(intensitys[i]), 0, 0)
        elif color == 'Green':
            rgb = (0, round(intensitys[i]), 0)
        elif color == 'Blue':
            rgb = (0, 0, round(intensitys[i]))
        rgbValues.append(rgb)

    return rgbValues

def createFrame(turned_on_wells, TL, plate_nr_type , filename, caliKi, video, customShape = None):

    rgbArray = np.zeros((64,64,3), 'uint8')

    for plate in range(len(turned_on_wells)):
        for well in turned_on_wells[plate]:
            leds_pos = None
            caliID = None
            Ki = None
            if customShape is None:
                #Getting CaliID c-t-n
                if well[1][0] != 0:
                    c = 'R'
                elif well[1][1] != 0:
                    c = 'G'
                elif well[1][2] != 0:
                    c = 'B'
                else:
                    Ki = 1

                if well[0][0] == 0:
                    n = str(1)
                elif well[0][0] == 1:
                    n = str(2)

                if plate_nr_type[plate] == 96:
                    t = str(96)
                    leds_pos = well_pos_to_led_pos_96(well[0], TL)
                elif plate_nr_type[plate] == 24:
                    t = str(24)
                    leds_pos = well_pos_to_led_pos_24(well[0], TL)
                elif plate_nr_type[plate] == 6:
                    t = str(6)
                    leds_pos = well_pos_to_led_pos_6(well[0], TL)
                if Ki != 1:
                    caliID = c + '-' + t + '-' + n
                    if caliKi[caliID] is None:
                        Ki = 1
                    else:
                        Ki = caliKi[caliID][well[0][1], well[0][2]]
            else:
                leds_pos = customShapeLEDpos(customShape)
                Ki = 1

            for led_pos in leds_pos:
                for rgb in range(3):
                    if well[1][rgb] != 0:
                        if rgb == 0:
                            rgbArray[led_pos[1], led_pos[0], rgb] = well[1][rgb] * Ki
                        elif rgb == 1:
                            rgbArray[led_pos[1], led_pos[0], rgb] = well[1][rgb] * Ki
                        elif rgb == 2:
                            rgbArray[led_pos[1], led_pos[0], rgb] = well[1][rgb] * Ki
            
            # Multipölikative
            # for led_pos in leds_pos:
            #     for rgb in range(3):
            #         if well[1][rgb] != 0:
            #             if rgb == 0:
            #                 rgbArray[led_pos[1], led_pos[0], rgb] = well[1][rgb] + caliR[led_pos[1], led_pos[0]]
            #             elif rgb == 1:
            #                 rgbArray[led_pos[1], led_pos[0], rgb] = well[1][rgb] + caliG[led_pos[1], led_pos[0]]
            #             elif rgb == 2:
            #                 rgbArray[led_pos[1], led_pos[0], rgb] = well[1][rgb] + caliB[led_pos[1], led_pos[0]]

    if video:
        return rgbArray
    else:
        img = Image.fromarray(rgbArray)
        img.save(filename)

def createImage(plateinfo, TL, filename, caliKi, maxIntensity, customShape = None):
    positionColorP1 = {}
    positionColorP2 = {}
    plate_nr_type = {0: plateinfo['Plate 1 Type'], 1: plateinfo['Plate 2 Type']}

    for well in plateinfo['Plate 1 Wells']:
        color = plateinfo['Plate 1 Wells'][well]['color']
        position = plateinfo['Plate 1 Wells'][well]['position']
        if maxIntensity:
            intensity = plateinfo['Plate 1 Wells'][well]['maxVal']
        else:
            try:
                intensity = plateinfo['Plate 1 Wells'][well]['minVal']
            except:
                intensity = plateinfo['Plate 1 Wells'][well]['maxVal']

        rgb = ()
        if color == 'Red':
            rgb = (round(intensity), 0, 0)
        elif color == 'Green':
            rgb = (0, round(intensity), 0)
        elif color == 'Blue':
            rgb = (0, 0, round(intensity))
        positionColorP1[position] = rgb

    for well in plateinfo['Plate 2 Wells']:
        color = plateinfo['Plate 2 Wells'][well]['color']
        position = plateinfo['Plate 2 Wells'][well]['position']

        if maxIntensity:
            intensity = plateinfo['Plate 2 Wells'][well]['maxVal']
        else:
            try:
                intensity = plateinfo['Plate 2 Wells'][well]['minVal']
            except:
                intensity = plateinfo['Plate 2 Wells'][well]['maxVal']
        
        rgb = ()
        if color == 'Red':
            rgb = (round(intensity), 0, 0)
        elif color == 'Green':
            rgb = (0, round(intensity), 0)
        elif color == 'Blue':
            rgb = (0, 0, round(intensity))
        positionColorP2[position] = rgb

    turned_on_wells = []
    turned_on_wellsP1 = []
    turned_on_wellsP2 = []
    for pos, color in positionColorP1.items():
        turned_on_wellsP1.append((pos, color))
    turned_on_wells.append(turned_on_wellsP1)
    for pos, color in positionColorP2.items():
        turned_on_wellsP2.append((pos, color))
    turned_on_wells.append(turned_on_wellsP2)
    createFrame(turned_on_wells, TL, plate_nr_type, filename, caliKi, video = False, customShape = customShape)

def createFrames(plateinfo, TL, framerate, path, caliKi, video = False, customShape = None):
    frames = []
    for step in plateinfo:
        stepLength = plateinfo[step][0][0]*60 + plateinfo[step][0][1] + plateinfo[step][0][2]/60
        frameAmount = int(stepLength/framerate)
        positionColorP1 = {}
        positionColorP2 = {}
        plate_nr_type = {0: plateinfo[step][1]['Plate 1 Type'], 1: plateinfo[step][1]['Plate 2 Type']}

        for well in plateinfo[step][1]['Plate 1 Wells']:
            wvType = plateinfo[step][1]['Plate 1 Wells'][well]['waveType']
            color = plateinfo[step][1]['Plate 1 Wells'][well]['color']
            wvMax = plateinfo[step][1]['Plate 1 Wells'][well]['maxVal']
            position = plateinfo[step][1]['Plate 1 Wells'][well]['position']
            wvMin = None
            wvLen = None
            wvStart = None
            periodPWM = None
            dutyCyclePWM = None
            if wvType in {'sin', 'tri', 'sq', 'rise', 'fall'}:
                wvMin = plateinfo[step][1]['Plate 1 Wells'][well]['minVal']
            if wvType in {'sin', 'tri', 'sq'}:
                wvLen = plateinfo[step][1]['Plate 1 Wells'][well]['wvLen']
            if wvType in {'sin', 'tri', 'sq', 'pwm'}:
                wvStart = plateinfo[step][1]['Plate 1 Wells'][well]['start']
            if wvType == 'pwm':
                periodPWM = plateinfo[step][1]['Plate 1 Wells'][well]['periodPWM']
                dutyCyclePWM = plateinfo[step][1]['Plate 1 Wells'][well]['dutyCyclePWM']
            positionColorP1[position] = getAnimationColors(wvType, color, stepLength, framerate, wvMax, wvMin, wvStart, wvLen, dutyCyclePWM, periodPWM)
        for well in plateinfo[step][1]['Plate 2 Wells']:
            wvType = plateinfo[step][1]['Plate 2 Wells'][well]['waveType']
            color = plateinfo[step][1]['Plate 2 Wells'][well]['color']
            wvMax = plateinfo[step][1]['Plate 2 Wells'][well]['maxVal']
            position = plateinfo[step][1]['Plate 2 Wells'][well]['position']
            wvMin = None
            wvLen = None
            wvStart = None
            periodPWM = None
            dutyCyclePWM = None
            if wvType in {'sin', 'tri', 'sq', 'rise', 'fall'}:
                wvMin = plateinfo[step][1]['Plate 2 Wells'][well]['minVal']
            if wvType in {'sin', 'tri', 'sq'}:
                wvLen = plateinfo[step][1]['Plate 2 Wells'][well]['wvLen']
            if wvType in {'sin', 'tri', 'sq', 'pwm'}:
                wvStart = plateinfo[step][1]['Plate 2 Wells'][well]['start']
            if wvType == 'pwm':
                periodPWM = plateinfo[step][1]['Plate 2 Wells'][well]['periodPWM']
                dutyCyclePWM = plateinfo[step][1]['Plate 2 Wells'][well]['dutyCyclePWM']
            positionColorP2[position] = getAnimationColors(wvType, color, stepLength, framerate, wvMax, wvMin, wvStart, wvLen, dutyCyclePWM, periodPWM)
        for frame in range(frameAmount):
            filename = path + '/step-' + str(step) + '-frame-' + str(frame) + '.tiff'
            turned_on_wells = []
            turned_on_wellsP1 = []
            turned_on_wellsP2 = []
            for pos, color in positionColorP1.items():
                turned_on_wellsP1.append((pos, color[frame]))
            turned_on_wells.append(turned_on_wellsP1)
            for pos, color in positionColorP2.items():
                turned_on_wellsP2.append((pos, color[frame]))
            turned_on_wells.append(turned_on_wellsP2)
            if video:
                frames.append(createFrame(turned_on_wells, TL, plate_nr_type, filename, caliKi, video, customShape))
            else:
                createFrame(turned_on_wells, TL, plate_nr_type, filename, caliKi, video, customShape)
    if video:
        return np.array(frames)

def createVideo(plateinfo, TL, framerate, filename, caliKi, customShape = None):
    frames = createFrames(plateinfo, TL, framerate, filename, caliKi, video = True, customShape = customShape)
    fps = 1/(framerate * 60)

    return frames, fps
    #write_gif(frames, filename, fps=fps)



