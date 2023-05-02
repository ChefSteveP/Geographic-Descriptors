#Stephen Pasch Uni:ssp2188
#COMS 4735: Visual Interfaces
#Assignment 3

#imports
import cv2
from PIL import Image
import numpy as np

#### Helper Methods ############################################################################

##Given a np.array create a dictionary of {intensity value: [list of coordinates associate with Val]}
def buildingCoordinates(arr, height, width):
    buildings = {}
    for row in range(height):
        for col in range(width):
            if arr[row,col] in buildings.keys():
                buildings[arr[row,col]].append((col,row))
            else:
                buildings[arr[row,col]] = [(col,row)]
    #Deletes blank spaces, this represents non-building area
    del buildings[0]
    return buildings

##Creates a dictionary of {Building #: COM coordinate} given {Building #: Coordinate List}
def CenterOfMass(buildingDict):
    COMass = {}
    for building in buildingDict.keys():
        x=0
        y=0
        temp_coord_list = buildingDict[building]
        pixelCount = len(temp_coord_list)
        for coordinate in temp_coord_list:
            x += coordinate[0]
            y += coordinate[1]
        COMass[building] = (x//pixelCount, y//pixelCount)
    return COMass

##Creates a dictionary of {Building #: Area} given {Building #: Coordinate List}
def Area(buildingDict):
    AreaDict = {}
    for building in buildingDict.keys():
        AreaDict[building] = len(buildingDict[building])
    return AreaDict

##Creates a dictionary of {Building #: [(Upper Left xy coordinate),(Lower Right xy coordinate)]} 
##given {Building #: Coordinate List}
def MBR(buildingDict):
    MBRDict = {}
    for building in buildingDict.keys():
        coord_list = buildingDict[building]
        Upper = 10000
        Lower = -1
        Leftmost = 10000
        RightMost = -1
        for coordinate in coord_list:
            #Find minimal value for each side of the bounding area
            if coordinate[0] <= Leftmost:
                Leftmost = coordinate[0]
            if coordinate[0] >= RightMost:
                RightMost = coordinate[0]
            if coordinate[1] <= Upper:
                Upper = coordinate[1]
            if coordinate[1] >= Lower:
                Lower = coordinate[1]
        #Add UL and LR coordinate that describes the Minimum Bounding Reactangle
        MBRDict[building] = [(Leftmost, Upper),(RightMost, Lower)]
    return MBRDict

##Creates a dictionary of {Building #: MBR diagonal length(float)} 
##given {Building #: [(Upper Left xy coordinate),(Lower Right xy coordinate)]} 
def MBRDiag(MBRDict):
    diagDict = {}
    for building in MBRDict.keys():
        #Grab two points to caluculate eucidean distance
        p1 = MBRDict[building][0]
        p2 = MBRDict[building][1]

        dist = round(np.sqrt(np.square(p2[0]-p1[0])+np.square(p2[1]-p1[1])),2)

        diagDict[building] = dist
    return diagDict

##Creates a dictionary of {Building #: [list of buildings whos MBR intersect target building]} 
##given {Building #: [(Upper Left xy coordinate),(Lower Right xy coordinate)]} 
def MBRIntersect(MBRDict):
    intersectionDict = {}

    #loops through all buildings
    for building_target in MBRDict.keys():
        #temporary storage for intersecting building for each target
        intersection = []

        #defines the x and y range of the Minimum bounding area of target
        xRange = range(MBRDict[building_target][0][0],MBRDict[building_target][1][0]+1)
        yRange = range(MBRDict[building_target][0][1],MBRDict[building_target][1][1]+1)

        #compare all other buildings to target building for intersection
        for building_other in MBRDict.keys():

            #ensures building doesn't think it intersects itself
            if building_target != building_other:

                x1,y1 = MBRDict[building_other][0]
                x2,y2 = MBRDict[building_other][1]

                #Upper left intersects
                if x1 in xRange and y1 in yRange:
                    intersection.append(building_other)
                #Upper Right intersects
                if x2 in xRange and y1 in yRange:
                    intersection.append(building_other)
                #Lower Left Intersescts
                if x1 in xRange and y2 in yRange:
                    intersection.append(building_other)
                #Lower Right Intersects
                if x2 in xRange and y2 in yRange:
                    intersection.append(building_other)

                #get rid of possible duplicate buildings
                intersection = list(set(intersection))
                
        #Store intersection list in dictionary under the target list
        if len(intersection) == 0:
                    intersection = str('None')
        intersectionDict[building_target] = intersection
    return intersectionDict      

###Shape descriptors###
#Smallest
def smallest(num, areaDict):
    #set min area to smallest area
    minArea = min(areaDict.values())
    #compare target area to min
    if areaDict[num] == minArea:
        return True
    else:
        return False      
#small
def small(num, areaDict):
    minArea = min(areaDict.values())
    maxArea = max(areaDict.values())

    #Create a middle value
    midArea = (minArea + maxArea)//2

    smallThreshold = (minArea+midArea)//2
    if areaDict[num] <= smallThreshold:
        return True
    else:
        return False
#medium-size
def mediumSize(num, areaDict):
    minArea = min(areaDict.values())
    maxArea = max(areaDict.values())

    #Create a middle value
    midArea = (minArea + maxArea)//2

    smallThreshold = (minArea+midArea)//2
    largeThreshold = (maxArea+midArea)//2
    #If the area is closer to the middle value on a number line then either
    #of the extrema then consider it medium size.
    if areaDict[num] > smallThreshold and areaDict[num] < largeThreshold:
        return True
    else:
        return False
#large
def large(num, areaDict):
    minArea = min(areaDict.values())
    maxArea = max(areaDict.values())

    #Create a middle value
    midArea = (minArea + maxArea)//2

    largeThreshold = (maxArea+midArea)//2
    #If the area is closer to the middle value on a number line then either
    #of the extrema then consider it medium size.
    if areaDict[num] >= largeThreshold:
        return True
    else:
        return False
#largest
def largest(num, areaDict):
    #set min area to smallest area
    maxArea = max(areaDict.values())
    #compare target area to min
    if areaDict[num] == maxArea:
        return True
    else:
        return False

def size(num, areaDict):
    if smallest(num, areaDict):
        return "Smallest"
    elif largest(num, areaDict):
        return "Largest"
    elif small(num, areaDict):
        return "Small"
    elif mediumSize(num, areaDict):
        return "Meduium"
    elif large(num, areaDict):
        return "Large"
    else:
        return "Ambiguous"
    
#narrow 
def narrow(num, MBRDict):
    UL, LR = MBRDict[num]
    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    if width/height <= 2/3:
        return True
    else:
        return False
#medium width
def mediumWidth(num, MBRDict):
    UL, LR = MBRDict[num]
    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    ratio = width/height

    if ratio > 2/3 and ratio < 3/2:
        return True
    else:
        return False
#wide
def wide(num, MBRDict):
    UL, LR = MBRDict[num]
    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    if width/height >= 3/2:
        return True
    else:
        return False
#square
def squareAspect(num, MBRDict):
    UL, LR = MBRDict[num]
    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])

    ratio = width/height
    if ratio >= 8.5/10 and ratio <= 10/8.5:
        return True
    else:
        return False
    
def aspectRatio(num, MBRDict):
    if squareAspect(num, MBRDict):
        return "Square"
    elif narrow(num, MBRDict):
        return "Narrow"
    elif wide(num, MBRDict):
        return "Wide"
    elif mediumWidth(num, MBRDict):
        return "Medium width"
    else:
        return "Ambiguous aspect ratio"
###Geometry###
def squareShape(num,MBRDict,AreaDict):
    UL, LR = MBRDict[num]
    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    boundedArea = width * height
    if AreaDict[num]/boundedArea >.80 and squareAspect(num,MBRDict):
        return True
    else:
        return False
#rectangular
def rectangular(num,MBRDict,AreaDict):
    UL, LR = MBRDict[num]
    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    boundedArea = width * height

    if AreaDict[num]/boundedArea >.85 and not squareAspect(num,MBRDict):
        return True
    else:
        return False
#I-shaped
def IShaped(num, coordMap, MBRDict):
    UL, LR = MBRDict[num]
    leftMost = UL[0]
    rightMost = LR[0]
    upper = UL[1]
    lower = LR[1]
    midY = (upper+lower) //2
    midX = (leftMost+rightMost) //2

    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    
    isIShaped = True

    if narrow(num, MBRDict):
        xStretch = width // 6
        yStretch = height // 5
        for x in range(leftMost, leftMost + xStretch+1):
            for y in range(midY - yStretch, midY+yStretch):
                if (x,y) in coordMap[num]:
                    isIShaped = False
        for x in range(rightMost - xStretch, rightMost+1):
            for y in range(midY - yStretch, midY+yStretch):
                if (x,y) in coordMap[num]:
                    isIShaped = False

    elif wide(num, MBRDict):
        xStretch = width // 5
        yStretch = height // 6
        for x in range(midX-xStretch, midX + xStretch+1):
            for y in range(upper, upper+yStretch+1):
                if (x,y) in coordMap[num]:
                    isIShaped = False
        for x in range(midX-xStretch, midX + xStretch+1):
            for y in range(lower - yStretch, lower+1):
                if (x,y)in coordMap[num]:
                    isIShaped = False
    else:
        isIShaped = False
    

    return isIShaped

#C-shaped
def CShaped(num, coordMap, MBRDict):
    UL, LR = MBRDict[num]
    leftMost = UL[0]
    rightMost = LR[0]
    upper = UL[1]
    lower = LR[1]
    midY = (upper+lower) //2
    midX = (leftMost+rightMost) //2

    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    xStretch = width // 6
    yStretch = height // 5
    isCShaped = False

    if narrow(num, MBRDict):
        rightGap = True
        LeftGap = True
        xStretch = width // 6
        yStretch = height // 5
        for x in range(leftMost, leftMost + xStretch+1):
            for y in range(midY - yStretch, midY+yStretch):
                if (x,y) in coordMap[num]:
                    LeftGap = False
        for x in range(rightMost - xStretch, rightMost+1):
            for y in range(midY - yStretch, midY+yStretch):
                if (x,y) in coordMap[num]:
                    rightGap = False
        if (LeftGap and not rightGap) or (rightGap and not LeftGap):
            isCShaped = True

    elif wide(num, MBRDict):
        TopGap = True
        BottomGap = True
        xStretch = width // 6
        yStretch = height // 6
        for x in range(midX-xStretch, midX + xStretch+1):
            for y in range(upper, upper+yStretch+1):
                if (x,y) in coordMap[num]:
                    TopGap = False
        for x in range(midX-xStretch, midX + xStretch+1):
            for y in range(lower - yStretch, lower+1):
                if (x,y)in coordMap[num]:
                    BottomGap = False
        if (TopGap and not BottomGap) or (BottomGap and not TopGap):
            isCShaped = True
 
    return isCShaped

#L-Shaped
def LShaped(num, coordMap, MBRDict):
    UL, LR = MBRDict[num]
    leftMost = UL[0]
    rightMost = LR[0]
    upper = UL[1]
    lower = LR[1]
    midY = (upper+lower) //2
    midX = (leftMost+rightMost) //2

    width = np.abs(UL[0]-LR[0])
    height = np.abs(UL[1]-LR[1])
    isLShaped = False

    #if squareAspect(num, MBRDict):
    URGap = True
    ULGap = True
    LRGap = True
    LLGap = True
    stretch = width // 6
        
    for x in range(leftMost, leftMost + stretch+1):
        for y in range(upper, upper+stretch+1):
            if (x,y) in coordMap[num]:
                ULGap = False
    for x in range(leftMost, leftMost + stretch+1):
        for y in range(lower-stretch, lower+1):
            if (x,y) in coordMap[num]:
                LLGap = False
    for x in range(rightMost-stretch, rightMost+1):
        for y in range(upper,upper+stretch+1):
            if (x,y) in coordMap[num]:
                URGap = False
    for x in range(rightMost-stretch, rightMost+1):
        for y in range(lower-stretch, lower+1):
            if (x,y) in coordMap[num]:
                LRGap = False
    #XOR of all corner gaps, meaning if 3 are covered and one is not then it is an L-shape
    if (URGap^ULGap^LRGap^LLGap):
        isLShaped = True
 
    return isLShaped
#asymmetric
def asymmetric(num, coordMap,MBRDict):
    topHalf = 0
    bottomHalf = 0
    leftHalf = 0
    rightHalf = 0
    UL, LR = MBRDict[num]
    for x in range(UL[0],LR[0]+1):
        for y1 in range(UL[1], LR[1]//2+1):
            if (x,y1) in coordMap[num]:
                topHalf += 1
        for y2 in range(LR[1]//2+1, LR[1]+1):
            if (x,y2) in coordMap[num]:
                bottomHalf += 1
    
    for x in range(UL[0],LR[0]//2+1):
        for y1 in range(UL[1], LR[1]+1):
            if (x,y1) in coordMap[num]:
                leftHalf += 1
    for x in range(LR[0]//2+1,LR[0]+1):          
        for y2 in range(UL[1], LR[1]+1):
            if (x,y2) in coordMap[num]:
                rightHalf += 1
    LRSymmetric = np.abs(leftHalf-rightHalf) < 50
    TBSymmetric = np.abs(topHalf-bottomHalf) < 50

    asymmetric = not LRSymmetric and not TBSymmetric

    return asymmetric

def Geometry(num, coordMap, MBRDict, areaDict):
    if LShaped(num,coordMap,MBRDict):
        return "L-"
    elif CShaped(num, coordMap, MBRDict):
        return "C-"
    elif IShaped(num, coordMap, MBRDict):
        return "I-"
    elif squareShape(num,MBRDict,areaDict):
        return "Square"
    elif rectangular(num,MBRDict, areaDict):
        return "Rectangular"
    elif asymmetric(num,coordMap,MBRDict):
        return "Asymmetric"
    else:
        return "Symmetric"

###Absolute Space descriptors###
#Uppermost
def uppermost(num,COMDict):
    #Make intial min much larger than map
    minY = 100000
    for coordinate in COMDict.values():
        if coordinate[1] < minY:
            minY = coordinate[1]
    if minY == COMDict[num][1]:
        return True
    else:
        return False
#upper
def upper(num, COMDict):
    upperMostHeight = +10000
    lowerMostHeight = -1

    for coordinate in COMDict.values():
        if coordinate[1] > lowerMostHeight:
            lowerMostHeight = coordinate[1]
        if coordinate[1] < upperMostHeight:
            upperMostHeight = coordinate[1]

    #Create a middle value
    midH= (lowerMostHeight + upperMostHeight)//2

    upperThreshold = (upperMostHeight+midH)//2
    #If the height is closer to the upper extrema value on a number line then the middle
    # then consider it upper height.
    if COMDict[num][1] <= upperThreshold:
        return True
    else:
        return False
#mid-height
def midHeight(num, COMDict):
    upperMostHeight = +10000
    lowerMostHeight = -1

    for coordinate in COMDict.values():
        if coordinate[1] > lowerMostHeight:
            lowerMostHeight = coordinate[1]
        if coordinate[1] < upperMostHeight:
            upperMostHeight = coordinate[1]

    #Create a middle value
    midH= (lowerMostHeight + upperMostHeight)//2

    lowThreshold = (lowerMostHeight+midH)//2
    upperThreshold = (upperMostHeight+midH)//2
    #If the height is closer to the middle value on a number line then either
    #of the extrema then consider it medium height.
    if COMDict[num][1] < lowThreshold and COMDict[num][1] > upperThreshold:
        return True
    else:
        return False
#lower
def lower(num, COMDict):
    upperMostHeight = +10000
    lowerMostHeight = -1

    for coordinate in COMDict.values():
        if coordinate[1] > lowerMostHeight:
            lowerMostHeight = coordinate[1]
        if coordinate[1] < upperMostHeight:
            upperMostHeight = coordinate[1]

    #Create a middle value
    midH= (lowerMostHeight + upperMostHeight)//2

    lowThreshold = (lowerMostHeight+midH)//2
   
    #If the height is closer to the lowest value on a number line then the middle
    #  then consider it lower height.
    if COMDict[num][1] >= lowThreshold:
        return True
    else:
        return False
#lowermost
def lowermost(num,COMDict):
    maxY = COMDict[num][1]
    for coordinate in COMDict.values():
        if coordinate[1] > maxY:
            maxY = coordinate[1]
    if maxY == COMDict[num][1]:
        return True
    else:
        return False
def verticallity(num, COMDict):
    if uppermost(num, COMDict):
        return "Uppermost"
    elif lowermost(num, COMDict):
        return "Lowermost"
    elif upper(num, COMDict):
        return "Upper"
    elif midHeight(num, COMDict):
        return "Middle-Range"
    elif lower(num, COMDict):
        return "Lower"
    
#leftmost
def leftmost(num,COMDict):
    minX = COMDict[num][0]
    for coordinate in COMDict.values():
        if coordinate[0] < minX:
            minX = coordinate[0]
    if minX == COMDict[num][0]:
        return True
    else:
        return False
#left
def left(num, COMDict):
    minWidth = +10000
    maxWidth = -1

    for coordinate in COMDict.values():
        if coordinate[0] > maxWidth:
            maxWidth = coordinate[0]
    for coordinate in COMDict.values():
        if coordinate[0] < minWidth:
            minWidth = coordinate[0]

    #Create a middle value
    midWid= (minWidth + maxWidth)//2

    leftThreshold = (minWidth+midWid)//2
    #If the area is closer to the left extrema value on a number line then the 
    # middle value then consider it left aligned.
    if COMDict[num][0] <= leftThreshold:
        return True
    else:
        return False
#mid-width
def midWidth(num, COMDict):
    minWidth = +10000
    maxWidth = -1

    for coordinate in COMDict.values():
        if coordinate[0] > maxWidth:
            maxWidth = coordinate[0]
    for coordinate in COMDict.values():
        if coordinate[0] < minWidth:
            minWidth = coordinate[0]

    #Create a middle value
    midWid= (minWidth + maxWidth)//2

    leftThreshold = (minWidth+midWid)//2
    rightThreshold = (maxWidth+midWid)//2
    #If the area is closer to the middle value on a number line then either
    #of the extrema then consider it middle aligned.
    if COMDict[num][0] > leftThreshold and COMDict[num][0] < rightThreshold:
        return True
    else:
        return False
#right
def right(num, COMDict):
    minWidth = +10000
    maxWidth = -1

    for coordinate in COMDict.values():
        if coordinate[0] > maxWidth:
            maxWidth = coordinate[0]
    for coordinate in COMDict.values():
        if coordinate[0] < minWidth:
            minWidth = coordinate[0]

    #Create a middle value
    midWid= (minWidth + maxWidth)//2

    rightThreshold = (maxWidth+midWid)//2
    #If the x value is closer to the rightmost extrema on a number line then the middle
    #then consider it right aligned.
    if COMDict[num][0] >= rightThreshold:
        return True
    else:
        return False
#rightmost
def rightmost(num,COMDict):
    maxX = COMDict[num][0]
    for coordinate in COMDict.values():
        if coordinate[0] > maxX:
            maxX = coordinate[0]
    if maxX == COMDict[num][0]:
        return True
    else:
        return False
def horizontallity(num, COMDict):
    if leftmost(num, COMDict):
        return "Leftmost"
    elif rightmost(num, COMDict):
        return "Rightmost"
    elif left(num, COMDict):
        return "Left Aligned"
    elif midWidth(num, COMDict):
        return "Middle-Range"
    elif right(num, COMDict):
        return "Right Aligned"
#vertically-oriented
def verticallyOriented(num,MBRDict,AreaDict):
    if rectangular(num,MBRDict,AreaDict) and narrow(num,MBRDict):
        return True
    else:
        return False
#horizontally-oriented
def horizontallyOriented(num,MBRDict,AreaDict):
    if rectangular(num,MBRDict,AreaDict) and wide(num,MBRDict):
        return True
    else:
        return False
#non-Oriented
def nonOriented(num,MBRDict,AreaDict):
    if not verticallyOriented(num,MBRDict,AreaDict) and not horizontallyOriented(num,MBRDict,AreaDict):
        return True
    else:
        return False
def orientation(num,MBRDict,AreaDict):
    if verticallyOriented(num,MBRDict,AreaDict):
        return "Vertical"
    elif horizontallyOriented(num,MBRDict,AreaDict):
        return "Horizontal"
    elif nonOriented(num,MBRDict,AreaDict):
        return "Non Specific"
###Relative SPace Descriptiors

######Five Steps of Project#########################################################
###Part1###
def RawData(image, table):
    im = Image.open(image)
    IntensityVals = np.array(im)
    ImgHeight, ImgWidth = np.shape(IntensityVals)
    #create coordinate map dictionary from intesity values
    buildingMap = buildingCoordinates(IntensityVals, ImgHeight, ImgWidth)

    #Derived information from coordinate map
    area = Area(buildingMap)
    centerOfMass = CenterOfMass(buildingMap)
    mbr = MBR(buildingMap)
    diagonal = MBRDiag(mbr)
    intersectingMBR = MBRIntersect(mbr)

    print("Part One: Raw Data, ((0,0) is top left of image)\n")
    with open(table, 'r') as file:
        for line in file:
            # Process the line
            num, name = line.strip().split(' ')
            num = int(num)
            print( "Name:", name,',', "Building Number:", num)
            print('COM:', centerOfMass[num], "Area:",area[num], "px")
            print("MBR (UL),(LR):", mbr[num], "MBR Diagonal:", diagonal[num])
            print("Buildings that intersect",name+'\'s MBR:',intersectingMBR[num],'\n')

###Part2###
def whatDescription(image, table):

    im = Image.open(image)
    IntensityVals = np.array(im)
    ImgHeight, ImgWidth = np.shape(IntensityVals)
    #create coordinate map dictionary from intesity values
    buildingMap = buildingCoordinates(IntensityVals, ImgHeight, ImgWidth)

    #Derived information from coordinate map
    area = Area(buildingMap)
    mbr = MBR(buildingMap)
    infoDict = {}
    print("Part Two: Shape Description, ((0,0) is top left of image)\n")
    nameDict = {}

    #Read through the table.txt file and calculate 'what' features
    with open(table, 'r') as file:
        for line in file:
            # Process the line
            num, name = line.strip().split(' ')
            num = int(num)
            #print( "Name:", name,',', "Building Number:", num)
            nameDict[num] = name
            infoDeck = [size(num, area),aspectRatio(num, mbr),Geometry(num,buildingMap, mbr,area)]
            #print("Geometry:", size(num, area),'size',aspectRatio(num, mbr),'aspect',Geometry(num,buildingMap, mbr,area),'shaped','\n')
            infoDict[num] = infoDeck
    similarityDict={}
    
    #Find out what buildings have the same defining 'what' features
    for num in infoDict.keys():
        for other in infoDict.keys():
            if num != other:
                if infoDict[num] == infoDict[other]:
                    if num not in similarityDict.keys():
                        similarityDict[num] = [other]
                    else:
                        similarityDict[num].append(other)

    ##Printout the 'what' Information formated
    for num in infoDict.keys():
        print( "Name:", nameDict[num],',', "Building Number:", num)
        print("Geometry:", infoDict[num][0],'size',',',infoDict[num][1],'aspect',',',infoDict[num][2],'shaped')
        if num not in similarityDict.keys():
            similarityDict[num] = 'None'
        print('Confusion:', similarityDict[num])
        if infoDict[num][0] == "Smallest":
            print('Minimization: Smallest','\n')
        elif infoDict[num][0] == "Largest":
            print('Minimization: Largest','\n')
        else:
            print('Minimization: None','\n')
                
###Part3
def whereDescription(image, table):
    im = Image.open(image)
    IntensityVals = np.array(im)
    ImgHeight, ImgWidth = np.shape(IntensityVals)
    #create coordinate map dictionary from intesity values
    buildingMap = buildingCoordinates(IntensityVals, ImgHeight, ImgWidth)

    #Derived information from coordinate map
    area = Area(buildingMap)
    centerOfMass = CenterOfMass(buildingMap)
    mbr = MBR(buildingMap)
    diagonal = MBRDiag(mbr)
    intersectingMBR = MBRIntersect(mbr)
    infoDict = {}
    print("Part Three: Absolute Space Description, ((0,0) is top left of image)\n")
    nameDict = {}
    print(centerOfMass)
    #Read through the table.txt file and calculate 'what' features
    with open(table, 'r') as file:
        for line in file:
            # Process the line
            num, name = line.strip().split(' ')
            num = int(num)
            #print( "Name:", name,',', "Building Number:", num)
            nameDict[num] = name
            infoDeck = [verticallity(num, centerOfMass),horizontallity(num, centerOfMass),orientation(num,mbr,area)]
            infoDict[num] = infoDeck
    similarityDict={}
    
    #Find out what buildings have the same defining 'where' features
    for num in infoDict.keys():
        for other in infoDict.keys():
            if num != other:
                if infoDict[num] == infoDict[other]:
                    if num not in similarityDict.keys():
                        similarityDict[num] = [other]
                    else:
                        similarityDict[num].append(other)
    
    ##Printout the 'what' Information formated
    for num in infoDict.keys():
        print( "Name:", nameDict[num],',', "Building Number:", num)
        print("Geometry:", infoDict[num][0],'verticallity',',',infoDict[num][1],'horizontality',',',infoDict[num][2],'orientation')
        if num not in similarityDict.keys():
            similarityDict[num] = 'None'
        print('Confusion:', similarityDict[num])
        if infoDict[num][0] == "Uppermost":
            print('Minimization: Uppermost','\n')
        elif infoDict[num][0] == "Lowermost":
            print('Minimization: Lowermost','\n')
        else:
            print('Minimization: None','\n')


###### Main Method ########################################################
# Load the PGM file using PIL
image_path = "Labeled.pgm"
#im = Image.open("Labeled.pgm")
table_path = "Table.txt"

#Calls Part 1 for printout data
RawData(image_path, table_path)

#Calls Part 2 for Shape printout data
whatDescription(image_path, table_path)

#Calls Part 3 for Absolute position data
whereDescription(image_path,table_path)

#Map Visualization
'''
# Convert the image to OpenCV format
im = Image.open(image_path)
IntensityVals = np.array(im)

cv_image = cv2.cvtColor(IntensityVals, cv2.COLOR_RGB2BGR)
# Create a window to display the image
cv2.namedWindow("Image")
# Register the mouse event callback function
# Display the image
cv2.imshow("Image", cv_image)
# Wait for a key press to exit
cv2.waitKey(0)
# Destroy the window
cv2.destroyAllWindows()
'''