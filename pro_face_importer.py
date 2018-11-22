# Brekel Pro Face Animation Unit Importer
# The way I made this script it needs a null selected that has user data with these exact names:

# Brows Inner Up
# Brows Inner Down
# Brows Outer Up
# Brows Outer Down
# Lip Stretch
# Lip Kiss
# Lip Corners Up
# Lip Corners Down
# Upper Lip Up
# Upper Lip Down
# Jaw Open
# 
# The user data should be formated to real and you can restrict it's values to 0-1 with and increment of .1
# 
# After you've created the user data run the script, it will ask you to select a text file that has the Amination Unit data extracted from a Brekel Pro Face txt export. 
# This data is naturally tab delimited so all you need to do is copy the 'frame	values' line all the way down to the end of the last frame of data
# 
# The script with create key frames for you and then you can use the data just as you would in the maya pipeline

import c4d
from c4d import gui

import csv

startKeyingFrame=0 # change this value to specify which frame the keys will begin
keyBrowsInnerUp=[]
keyBrowsInnerDown=[]
keyBrowsOuterUp=[]
keyBrowsOuterDown=[]
keyLipStretch=[]
keyLipKiss=[]
keyLipCornersUp=[]
keyLipCornersDown=[]
keyUpperLipUp=[]
keyUpperLipDown=[]
keyJawOpen=[]

def readFile(path):
    file = open(path, 'rb')
    next(file) #skip the csv headers
    reader = csv.reader(file,delimiter='\t')
    
    for frame, BrowsInnerUp, BrowsInnerDown, BrowsOuterUp, BrowsOuterDown, LipStretch, LipKiss, LipCornersUp, LipCornersDown, UpperLipUp, UpperLipDown, JawOpen in reader:
        keyBrowsInnerUp.append(BrowsInnerUp)
        keyBrowsInnerDown.append(BrowsInnerDown)
        keyBrowsOuterUp.append(BrowsOuterUp)
        keyBrowsOuterDown.append(BrowsOuterDown)
        keyLipStretch.append(LipStretch)
        keyLipKiss.append(LipKiss)
        keyLipCornersUp.append(LipCornersUp)
        keyLipCornersDown.append(LipCornersDown)
        keyUpperLipUp.append(UpperLipUp)
        keyUpperLipDown.append(UpperLipDown)
        keyJawOpen.append(JawOpen)

    file.close

def insertKeys(id, keyArray):
    keyCount = len(keyBrowsInnerUp) #Finding the length of one to the AU arrays finds the length of them all, as well as the number of frames in the imported animation
    FPS = doc.GetFps() #Get the frames per second of the current scene 
    
    uDataTrack = c4d.CTrack(op,id) #Save the animation track, we'll need it to insert keys
    uDataCurve = uDataTrack.GetCurve()

    i=0
            
    while (i<keyCount): #loop through the values of the AUs and insert keys        
        frameNo = (startKeyingFrame+i)
        frameTime = c4d.BaseTime(frameNo, FPS)
        auKey = c4d.CKey() #Create a key
        auKey.SetTime(uDataCurve, frameTime)
        auKey.SetValue(uDataCurve, float(keyArray[i]))
        uDataCurve.InsertKey(auKey)
        i+=1
            
    op.InsertTrackSorted(uDataTrack)

def main():
    animFile = c4d.storage.LoadDialog()# open the C4D file browser to allow the user to choose a text file to read
    readFile(animFile)# run the read file proc
        
    for id, bc in op.GetUserDataContainer(): #get the userdata ids and desc
        if bc[c4d.DESC_NAME] == 'Brows Inner Up':
            insertKeys(id, keyBrowsInnerUp)
        elif bc[c4d.DESC_NAME] == 'Brows Inner Down':
            insertKeys(id, keyBrowsInnerDown)
        elif bc[c4d.DESC_NAME] == 'Brows Outer Up':
            insertKeys(id, keyBrowsOuterUp)
        elif bc[c4d.DESC_NAME] == 'Brows Outer Down':
            insertKeys(id, keyBrowsOuterDown)
        elif bc[c4d.DESC_NAME] == 'Lip Stretch':
            insertKeys(id, keyLipStretch)
        elif bc[c4d.DESC_NAME] == 'Lip Kiss':
            insertKeys(id, keyLipKiss)
        elif bc[c4d.DESC_NAME] == 'Lip Corners Up':
            insertKeys(id, keyLipCornersUp)
        elif bc[c4d.DESC_NAME] == 'Lip Corners Down':
            insertKeys(id, keyLipCornersDown)
        elif bc[c4d.DESC_NAME] == 'Upper Lip Up':
            insertKeys(id, keyUpperLipUp)
        elif bc[c4d.DESC_NAME] == 'Upper Lip Down':
            insertKeys(id, keyUpperLipDown)
        elif bc[c4d.DESC_NAME] == 'Jaw Open':
            insertKeys(id, keyJawOpen)      
    
    c4d.EventAdd()
    c4d.CallCommand(12147) #redraw the scene
    
if __name__=='__main__':
    main()
