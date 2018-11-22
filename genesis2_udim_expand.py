import c4d
from c4d import gui
# with a Genesis 1 chacter this script will automatically expand
# the uvs from zero to one space allowing for an easy transition
# to udims


def main():
    
    limbs_sels = ['Legs', 'Toenails', 'Fingernails', 'Hands', 'Forearms', 'Feet']
    torso_sels = ['Head', 'Ears', 'Shoulders', 'Neck', 'Hips', 'Torso', 'Nipples' ]
    eyelash_sels = ['Eyelashes']
    mouth_sels= ['Gums', 'Teeth', 'Tongue', 'InnerMouth']
    eyes_sels = ['EyeReflection', 'Lacrimals', 'Pupils', 'Irises', 'Cornea', 'Sclera']
    tear_sels = ['Tear']
    
    uvwtag = op.GetTag(c4d.Tuvw)
    tags = op.GetTags()
    
    for tag in tags:
        if tag.GetType() == c4d.Tpolygonselection:
            polySel = tag.GetBaseSelect()
            # torso is udim 2, or uv space 1
            for group in torso_sels:
                if group in tag.GetName():
                    udimOffsetPolySelection(polySel, uvwtag, 1, 0)
            
            # limbs are udim 3, or uv space 2
            for group in limbs_sels:
                if group in tag.GetName():
                    udimOffsetPolySelection(polySel, uvwtag, 2, 0)
              
            # the mouth is udim 4, or uv space 3
            for group in mouth_sels:
                if group in tag.GetName():
                    udimOffsetPolySelection(polySel, uvwtag, 3, 0)
            
            # eyes are udim 5, or uv space 4
            for group in eyes_sels:
                if group in tag.GetName():
                    udimOffsetPolySelection(polySel, uvwtag, 4, 0)
                
            # eyelashes are udim 6, or uv space 5
            for group in eyelash_sels:
                if group in tag.GetName():
                    udimOffsetPolySelection(polySel, uvwtag, 5, 0)
                   
            # tears are udim 7, or uv space 6
            for group in tear_sels:
                if group in tag.GetName():
                    udimOffsetPolySelection(polySel, uvwtag, 6, 0)
    
    #update
    op.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()

def udimOffsetPolySelection(sel, uvwTag, offsetx, offsety):
    # if you check the poly count against the uv GetDataCount you'll find that they match,
    # this means we can check our BaseSelect and if the index is selected we'll have the 
    # proper UVs to move
    count = op.GetPolygonCount()
    for i in xrange(count):
        if sel.IsSelected(i):
            uvwdict = uvwTag.GetSlow(i)
            pt1 =  c4d.Vector(uvwdict["a"].x + offsetx, uvwdict["a"].y + offsety, uvwdict["a"].z)
            pt2 =  c4d.Vector(uvwdict["b"].x + offsetx, uvwdict["b"].y + offsety, uvwdict["b"].z)
            pt3 =  c4d.Vector(uvwdict["c"].x + offsetx, uvwdict["c"].y + offsety, uvwdict["c"].z)
            pt4 =  c4d.Vector(uvwdict["d"].x + offsetx, uvwdict["d"].y + offsety, uvwdict["d"].z)
            uvwTag.SetSlow(i, pt1, pt2, pt3, pt4) 
            
if __name__=='__main__':
    main()
