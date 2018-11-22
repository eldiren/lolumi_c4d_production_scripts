import c4d
from c4d import gui
# with a Genesis 1 chacter this script will automatically expand
# the uvs from zero to one space allowing for an easy transition
# to udims


def main():
    limbs_sels = ["3_SkinFoot_Selection", "3_SkinArm_Selection"]
    torso_sels = ["2_SkinTorso_Selection", ]
    eyelash_sels = ["6_Eyelash_Selection"]
    mouth_sels= ["4_Tongue_Selection", "4_Teeth_Selection", "4_InnerMouth_Selection", "4_Gums_Selection"]
    eyes_sels = ["5_Sclera_Selection", "5_Pupil_Selection", "5_Iris_Selection", "5_Cornea_Selection"]
    
    uvwtag = op.GetTag(c4d.Tuvw)
    tags = op.GetTags()
    
    for tag in tags:
        if tag.GetType() == c4d.Tpolygonselection:
            polySel = tag.GetBaseSelect()
            # torso isudim 2, or uv space 1
            if "2_" in tag.GetName():
                udimOffsetPolySelection(polySel, uvwtag, 1, 0)
            
            # limbs are udim 3, or uv space 2
            if "3_" in tag.GetName():
                udimOffsetPolySelection(polySel, uvwtag, 2, 0)
              
            # the mouth is udim 4, or uv space 3
            if "4_" in tag.GetName():
                udimOffsetPolySelection(polySel, uvwtag, 3, 0)
            
            # eyes are udim 5, or uv space 4
            if "5_" in tag.GetName():
                udimOffsetPolySelection(polySel, uvwtag, 4, 0)
                
            # eyelashes are udim 6, or uv space 5
            if "6_" in tag.GetName():
                udimOffsetPolySelection(polySel, uvwtag, 5, 0)
                   
            # tears are udim 7, or uv space 6
            if "7_" in tag.GetName():
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
