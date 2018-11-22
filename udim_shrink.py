import c4d, math
from c4d import gui
from math import modf

# This script takes a multitile uv layout and squashes it into 0 to 1
# space. Very useful for baking noise effects that can't be baked into
# udims, or saving HD space for simple multitile masks
def main():
    # this magic number holds the number of columns we want our new
    # 0 to 1 udim to have
    cols = 4
    uvwtag = op.GetTag(c4d.Tuvw)
    
    for i in xrange(uvwtag.GetDataCount()):
        # get current uvs for polygon
        uvwdict = uvwtag.GetSlow(i)
        
        # take the decimal portion away from the first point, the 
        # value you get is the tile(udim), we are multiplying by 1.0
        # here because in Python 2 this int operation will an int
        # and if we divide it later by other ints we won't get proper
        # decimal remainders which we need
        curudim = int(uvwdict["a"].x) * 1.0
        
        # If we divide the udim by the number of columns the whole
        # number part will tell us what row were on, and the decimal
        # part will tell us the start u
        startu = curudim / cols
        startu, startv = modf(startu)
        #print str(startu) + " " + str(startv) #debug
        
        #The start v simply comes from dividing the whole
        # number part by the number of columns
        startv = startv / cols
        
        #print "UDIM: " + str(curudim) + " Start U " + str(startu) +  " Start V " + str(startv) #debug
        # dividing the uvs by the cols will shink the uvs down to the size
        # we want, at this point all the u vaules are perfect, the v is wrong
        # and some of the u values are still outside 0 to 1, so we do modf to get
        # only the decimal parts of the uv cords and offset the v by startv
        pt1 = uvwdict["a"] / cols
        pt1 = c4d.Vector(modf(pt1.x)[0], modf(pt1.y)[0] + startv, modf(pt1.z)[0])
        pt2 = uvwdict["b"] / cols
        pt2 = c4d.Vector(modf(pt2.x)[0], modf(pt2.y)[0] + startv, modf(pt2.z)[0])
        pt3 = uvwdict["c"] / cols
        pt3 = c4d.Vector(modf(pt3.x)[0], modf(pt3.y)[0] + startv, modf(pt3.z)[0])
        pt4 = uvwdict["d"] / cols
        pt4 = c4d.Vector(modf(pt4.x)[0], modf(pt4.y)[0] + startv, modf(pt4.z)[0])
        
        uvwtag.SetSlow(i, pt1, pt2, pt3, pt4)
        
        # To stop the loop early for quick tests
        #if i == 1000:
            #break
            
    print "Done"
    c4d.EventAdd()

if __name__=='__main__':
    main()
